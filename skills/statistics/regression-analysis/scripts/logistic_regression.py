#!/usr/bin/env python3
"""
logistic_regression.py — Binary logistic regression with odds ratios and ROC.

Fits a binary logistic regression model and reports odds ratios with 95%
confidence intervals, classification metrics, and optionally a ROC curve.

Dependencies:
    numpy, scipy, pandas, statsmodels, scikit-learn, matplotlib (optional)

Example usage:
    python logistic_regression.py --input data.csv --target outcome --predictors age sex bmi
    python logistic_regression.py --input data.csv --target disease --predictors x1 x2 --roc roc.png
    python logistic_regression.py --input data.csv --target y --predictors x1 x2 --output results.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Binary logistic regression with odds ratios, ROC, and classification report.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input data.csv --target outcome --predictors age sex bmi
  %(prog)s --input data.csv --target disease --predictors x1 x2 --roc roc_curve.png
        """,
    )
    parser.add_argument("--input", "-i", required=True, help="Path to CSV file.")
    parser.add_argument("--target", "-t", required=True, help="Binary target variable (0/1).")
    parser.add_argument("--predictors", "-p", nargs="+", required=True, help="Predictor variables.")
    parser.add_argument("--output", "-o", default=None, help="Save OR table to CSV.")
    parser.add_argument("--roc", default=None, help="Save ROC curve plot to file.")
    parser.add_argument("--threshold", type=float, default=0.5, help="Classification threshold (default: 0.5).")
    parser.add_argument("--separator", "--sep", default=",", help="CSV delimiter.")
    args = parser.parse_args()

    try:
        import statsmodels.api as sm
    except ImportError:
        print("Error: statsmodels required. pip install statsmodels", file=sys.stderr)
        sys.exit(1)

    try:
        from sklearn.metrics import (
            classification_report,
            confusion_matrix,
            roc_auc_score,
            roc_curve,
        )
    except ImportError:
        print("Error: scikit-learn required. pip install scikit-learn", file=sys.stderr)
        sys.exit(1)

    # --- Load data -----------------------------------------------------------
    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    df = pd.read_csv(input_path, sep=args.separator)

    cols_needed = [args.target] + args.predictors
    missing = [c for c in cols_needed if c not in df.columns]
    if missing:
        print(f"Error: Columns not found: {missing}", file=sys.stderr)
        sys.exit(1)

    sub = df[cols_needed].dropna()
    y = sub[args.target].astype(float)

    # Validate binary
    unique_vals = sorted(y.unique())
    if set(unique_vals) - {0.0, 1.0}:
        print(f"Error: Target must be binary (0/1). Found values: {unique_vals}", file=sys.stderr)
        sys.exit(1)

    X = sub[args.predictors].astype(float)
    X_const = sm.add_constant(X)

    n = len(sub)
    n_events = int(y.sum())
    print(f"Observations: {n}")
    print(f"Events (y=1): {n_events} ({100 * n_events / n:.1f}%)")
    print(f"Target       : {args.target}")
    print(f"Predictors   : {args.predictors}")
    print()

    # --- Fit model -----------------------------------------------------------
    try:
        model = sm.Logit(y, X_const).fit(disp=0)
    except Exception as exc:
        print(f"Error fitting model: {exc}", file=sys.stderr)
        sys.exit(1)

    print("=" * 70)
    print("LOGISTIC REGRESSION RESULTS")
    print("=" * 70)
    print(model.summary())
    print()

    # --- Odds Ratios ---------------------------------------------------------
    params = model.params
    conf = model.conf_int()
    or_df = pd.DataFrame(
        {
            "Variable": params.index,
            "Coefficient": params.values,
            "OR": np.exp(params.values),
            "OR 95% CI Lower": np.exp(conf[0].values),
            "OR 95% CI Upper": np.exp(conf[1].values),
            "p-value": model.pvalues.values,
        }
    )

    print("Odds Ratios:")
    print(f"  {'Variable':<20} {'OR':>8} {'95% CI':>20} {'p-value':>10}")
    print(f"  {'-'*60}")
    for _, row in or_df.iterrows():
        ci_str = f"[{row['OR 95% CI Lower']:.3f} - {row['OR 95% CI Upper']:.3f}]"
        sig = " *" if row["p-value"] < 0.05 else ""
        print(f"  {row['Variable']:<20} {row['OR']:>8.3f} {ci_str:>20} {row['p-value']:>10.4f}{sig}")
    print()

    # --- Predictions and classification --------------------------------------
    y_prob = model.predict(X_const)
    y_pred = (y_prob >= args.threshold).astype(int)

    print(f"Classification (threshold = {args.threshold}):")
    cm = confusion_matrix(y, y_pred)
    print(f"  Confusion Matrix:")
    print(f"    {'':>10} Pred 0  Pred 1")
    print(f"    {'Actual 0':>10}  {cm[0, 0]:>5}   {cm[0, 1]:>5}")
    print(f"    {'Actual 1':>10}  {cm[1, 0]:>5}   {cm[1, 1]:>5}")
    print()
    print(classification_report(y, y_pred, digits=4))

    # --- ROC AUC -------------------------------------------------------------
    auc = roc_auc_score(y, y_prob)
    print(f"ROC AUC: {auc:.4f}")
    print()

    # --- Hosmer-Lemeshow goodness of fit -------------------------------------
    try:
        # Simple implementation: split into deciles of predicted probability
        decile_df = pd.DataFrame({"prob": y_prob, "obs": y})
        decile_df["decile"] = pd.qcut(decile_df["prob"], 10, duplicates="drop")
        grouped = decile_df.groupby("decile", observed=True).agg(
            obs_events=("obs", "sum"),
            obs_n=("obs", "count"),
            pred_prob=("prob", "mean"),
        )
        grouped["exp_events"] = grouped["pred_prob"] * grouped["obs_n"]
        grouped["exp_non"] = (1 - grouped["pred_prob"]) * grouped["obs_n"]
        grouped["obs_non"] = grouped["obs_n"] - grouped["obs_events"]

        hl_stat = (
            ((grouped["obs_events"] - grouped["exp_events"]) ** 2 / grouped["exp_events"]).sum()
            + ((grouped["obs_non"] - grouped["exp_non"]) ** 2 / grouped["exp_non"]).sum()
        )
        from scipy.stats import chi2

        hl_p = 1 - chi2.cdf(hl_stat, df=len(grouped) - 2)
        print(f"Hosmer-Lemeshow test: chi2 = {hl_stat:.4f}, p = {hl_p:.4f}", end="")
        if hl_p >= 0.05:
            print(" (adequate fit)")
        else:
            print(" (poor fit)")
    except Exception:
        pass  # Skip HL if data does not support decile grouping

    # --- ROC plot ------------------------------------------------------------
    if args.roc:
        try:
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            fpr, tpr, _ = roc_curve(y, y_prob)
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.plot(fpr, tpr, color="steelblue", linewidth=2, label=f"AUC = {auc:.3f}")
            ax.plot([0, 1], [0, 1], "k--", linewidth=0.8, label="Random")
            ax.set_xlabel("False Positive Rate")
            ax.set_ylabel("True Positive Rate")
            ax.set_title("ROC Curve")
            ax.legend(loc="lower right")
            fig.tight_layout()
            fig.savefig(args.roc, dpi=150)
            plt.close(fig)
            print(f"\nROC curve saved to {args.roc}")
        except ImportError:
            print("Warning: matplotlib not installed; skipping ROC plot.", file=sys.stderr)

    # --- Save ----------------------------------------------------------------
    if args.output:
        or_df.to_csv(args.output, index=False)
        print(f"Odds ratio table saved to {args.output}")


if __name__ == "__main__":
    main()

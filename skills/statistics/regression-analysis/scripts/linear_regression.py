#!/usr/bin/env python3
"""
linear_regression.py — OLS linear regression with diagnostics.

Fits an OLS model and reports coefficients, standard errors, p-values,
R-squared, and adjusted R-squared. Produces diagnostic outputs including
VIF (variance inflation factors), Cook's distance, and optional residual
plots.

Dependencies:
    numpy, scipy, pandas, statsmodels, matplotlib (optional, for plots)

Example usage:
    python linear_regression.py --input data.csv --target y --predictors x1 x2 x3
    python linear_regression.py --input data.csv --target bmi \
        --predictors age sex height --plots residuals.png
    python linear_regression.py --input data.csv --target score \
        --predictors age income --output results.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


def compute_vif(features: pd.DataFrame) -> pd.DataFrame:
    """Compute Variance Inflation Factors for each predictor.

    Parameters
    ----------
    features : pd.DataFrame
        Design matrix (without intercept).

    Returns
    -------
    pd.DataFrame with columns ['Variable', 'VIF'].
    """
    from statsmodels.stats.outliers_influence import variance_inflation_factor

    vif_data = []
    feat_arr = features.values.astype(float)
    for i, col in enumerate(features.columns):
        try:
            vif_val = variance_inflation_factor(feat_arr, i)
        except Exception:
            vif_val = np.nan
        vif_data.append({"Variable": col, "VIF": vif_val})
    return pd.DataFrame(vif_data)


def generate_diagnostic_plots(model, output_path: str) -> None:
    """Generate a 2x2 diagnostic plot panel and save to disk.

    Panels: (1) residuals vs fitted, (2) Q-Q plot, (3) scale-location,
    (4) residuals vs leverage with Cook's distance contours.
    """
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("Warning: matplotlib not installed; skipping plots.", file=sys.stderr)
        return

    fitted = model.fittedvalues
    resid = model.resid
    std_resid = model.get_influence().resid_studentized_internal

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # 1. Residuals vs Fitted
    ax = axes[0, 0]
    ax.scatter(fitted, resid, alpha=0.5, s=20, edgecolors="k", linewidths=0.3)
    ax.axhline(0, color="firebrick", linestyle="--", linewidth=0.8)
    ax.set_xlabel("Fitted values")
    ax.set_ylabel("Residuals")
    ax.set_title("Residuals vs Fitted")

    # 2. Q-Q plot
    ax = axes[0, 1]
    stats.probplot(std_resid, plot=ax)
    ax.set_title("Normal Q-Q")

    # 3. Scale-Location
    ax = axes[1, 0]
    ax.scatter(fitted, np.sqrt(np.abs(std_resid)), alpha=0.5, s=20, edgecolors="k", linewidths=0.3)
    ax.set_xlabel("Fitted values")
    ax.set_ylabel("sqrt(|Standardised Residuals|)")
    ax.set_title("Scale-Location")

    # 4. Residuals vs Leverage
    ax = axes[1, 1]
    influence = model.get_influence()
    leverage = influence.hat_matrix_diag
    cooks_d = influence.cooks_distance[0]
    ax.scatter(leverage, std_resid, alpha=0.5, s=20, edgecolors="k", linewidths=0.3)
    ax.axhline(0, color="firebrick", linestyle="--", linewidth=0.8)
    ax.set_xlabel("Leverage")
    ax.set_ylabel("Standardised Residuals")
    ax.set_title("Residuals vs Leverage")

    # Annotate high Cook's distance points
    threshold = 4 / len(resid)
    high_cook = np.where(cooks_d > threshold)[0]
    for idx in high_cook[:5]:  # label at most 5
        ax.annotate(str(idx), (leverage[idx], std_resid[idx]), fontsize=7)

    fig.suptitle("OLS Regression Diagnostics", fontsize=14, y=1.01)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Diagnostic plots saved to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="OLS linear regression with diagnostics "
        "(VIF, Cook's distance, residual plots).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input data.csv --target y --predictors x1 x2 x3
  %(prog)s --input data.csv --target bmi --predictors age sex height --plots diag.png
        """,
    )
    parser.add_argument("--input", "-i", required=True, help="Path to CSV file.")
    parser.add_argument("--target", "-t", required=True, help="Target (dependent) variable.")
    parser.add_argument("--predictors", "-p", nargs="+", required=True, help="Predictor variables.")
    parser.add_argument("--output", "-o", default=None, help="Save coefficient table to CSV.")
    parser.add_argument(
        "--plots", default=None, help="Save diagnostic plots to file (e.g. diag.png)."
    )
    parser.add_argument("--separator", "--sep", default=",", help="CSV delimiter.")
    args = parser.parse_args()

    try:
        import statsmodels.api as sm
    except ImportError:
        print(
            "Error: statsmodels is required. Install with: pip install statsmodels", file=sys.stderr
        )
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
    n = len(sub)
    print(f"Observations (complete cases): {n}")
    print(f"Target    : {args.target}")
    print(f"Predictors: {args.predictors}")
    print()

    if n < len(args.predictors) + 2:
        print("Error: Insufficient observations for regression.", file=sys.stderr)
        sys.exit(1)

    y = sub[args.target].astype(float)
    features = sub[args.predictors].astype(float)
    features_const = sm.add_constant(features)

    # --- Fit model -----------------------------------------------------------
    model = sm.OLS(y, features_const).fit()

    print("=" * 70)
    print("OLS REGRESSION RESULTS")
    print("=" * 70)
    print(model.summary())
    print()

    # --- VIF -----------------------------------------------------------------
    if len(args.predictors) > 1:
        print("Variance Inflation Factors (VIF):")
        vif_df = compute_vif(features)
        for _, row in vif_df.iterrows():
            flag = " *** HIGH" if row["VIF"] > 10 else (" * moderate" if row["VIF"] > 5 else "")
            print(f"  {row['Variable']:<20} VIF = {row['VIF']:.2f}{flag}")
        print()

    # --- Cook's distance -----------------------------------------------------
    influence = model.get_influence()
    cooks_d = influence.cooks_distance[0]
    threshold = 4 / n
    n_influential = (cooks_d > threshold).sum()
    print(f"Cook's distance: {n_influential} observation(s) exceed threshold ({threshold:.4f})")
    if n_influential > 0 and n_influential <= 10:
        high_idx = np.where(cooks_d > threshold)[0]
        for idx in high_idx:
            print(f"  Row {idx}: Cook's D = {cooks_d[idx]:.4f}")
    print()

    # --- Durbin-Watson -------------------------------------------------------
    from statsmodels.stats.stattools import durbin_watson

    dw = durbin_watson(model.resid)
    print(f"Durbin-Watson statistic: {dw:.4f}", end="")
    if 1.5 < dw < 2.5:
        print(" (no strong autocorrelation)")
    else:
        print(" (possible autocorrelation in residuals)")
    print()

    # --- Diagnostic plots ----------------------------------------------------
    if args.plots:
        generate_diagnostic_plots(model, args.plots)

    # --- Save coefficients ---------------------------------------------------
    if args.output:
        coef_df = pd.DataFrame(
            {
                "Variable": model.params.index,
                "Coefficient": model.params.values,
                "Std Error": model.bse.values,
                "t-value": model.tvalues.values,
                "p-value": model.pvalues.values,
                "CI Lower": model.conf_int()[0].values,
                "CI Upper": model.conf_int()[1].values,
            }
        )
        coef_df.to_csv(args.output, index=False)
        print(f"Coefficient table saved to {args.output}")


if __name__ == "__main__":
    main()

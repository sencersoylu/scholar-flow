#!/usr/bin/env python3
"""
cox_regression.py — Cox proportional hazards regression with Kaplan-Meier curves.

Fits a Cox PH model using the lifelines library and reports hazard ratios
with 95% confidence intervals. Optionally generates Kaplan-Meier survival
curves stratified by a categorical variable.

Dependencies:
    numpy, pandas, lifelines, matplotlib (optional, for plots)

Example usage:
    python cox_regression.py --input data.csv --duration time \
        --event status --predictors age treatment
    python cox_regression.py --input data.csv --duration os_months --event os_event \\
        --predictors age stage grade --km-strata treatment --km-plot km.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cox proportional hazards regression with Kaplan-Meier curves.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input data.csv --duration time --event status --predictors age treatment
  %(prog)s --input data.csv --duration os_months --event os_event \\
      --predictors age stage --km-strata treatment --km-plot km.png
        """,
    )
    parser.add_argument("--input", "-i", required=True, help="Path to CSV file.")
    parser.add_argument("--duration", "-d", required=True, help="Time-to-event column.")
    parser.add_argument(
        "--event", "-e", required=True, help="Event indicator column (1=event, 0=censored)."
    )
    parser.add_argument("--predictors", "-p", nargs="+", required=True, help="Predictor variables.")
    parser.add_argument("--output", "-o", default=None, help="Save hazard ratio table to CSV.")
    parser.add_argument(
        "--km-strata", default=None, help="Categorical variable for KM stratification."
    )
    parser.add_argument("--km-plot", default=None, help="Save Kaplan-Meier plot to file.")
    parser.add_argument("--separator", "--sep", default=",", help="CSV delimiter.")
    args = parser.parse_args()

    try:
        from lifelines import CoxPHFitter, KaplanMeierFitter
        from lifelines.statistics import logrank_test
    except ImportError:
        print(
            "Error: lifelines is required. Install with: pip install lifelines",
            file=sys.stderr,
        )
        sys.exit(1)

    # --- Load data -----------------------------------------------------------
    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    df = pd.read_csv(input_path, sep=args.separator)

    required_cols = [args.duration, args.event] + args.predictors
    if args.km_strata:
        required_cols.append(args.km_strata)
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        print(f"Error: Columns not found: {missing}", file=sys.stderr)
        sys.exit(1)

    sub = df[required_cols].dropna()
    n = len(sub)
    n_events = int(sub[args.event].sum())

    print(f"Observations : {n}")
    print(f"Events       : {n_events} ({100 * n_events / n:.1f}%)")
    print(f"Duration     : {args.duration}")
    print(f"Event        : {args.event}")
    print(f"Predictors   : {args.predictors}")
    print()

    # --- Fit Cox PH model ----------------------------------------------------
    cph = CoxPHFitter()
    fit_cols = [args.duration, args.event] + args.predictors
    try:
        cph.fit(
            sub[fit_cols],
            duration_col=args.duration,
            event_col=args.event,
        )
    except Exception as exc:
        print(f"Error fitting Cox model: {exc}", file=sys.stderr)
        sys.exit(1)

    print("=" * 70)
    print("COX PROPORTIONAL HAZARDS REGRESSION")
    print("=" * 70)
    cph.print_summary()
    print()

    # --- Hazard ratios -------------------------------------------------------
    summary = cph.summary
    hr_df = pd.DataFrame(
        {
            "Variable": summary.index,
            "Coefficient": summary["coef"].values,
            "HR": summary["exp(coef)"].values,
            "HR 95% CI Lower": summary["exp(coef) lower 95%"].values,
            "HR 95% CI Upper": summary["exp(coef) upper 95%"].values,
            "p-value": summary["p"].values,
        }
    )

    print("Hazard Ratios:")
    print(f"  {'Variable':<20} {'HR':>8} {'95% CI':>22} {'p-value':>10}")
    print(f"  {'-' * 62}")
    for _, row in hr_df.iterrows():
        ci = f"[{row['HR 95% CI Lower']:.3f} - {row['HR 95% CI Upper']:.3f}]"
        sig = " *" if row["p-value"] < 0.05 else ""
        print(f"  {row['Variable']:<20} {row['HR']:>8.3f} {ci:>22} {row['p-value']:>10.4f}{sig}")
    print()

    # --- Concordance index ---------------------------------------------------
    print(f"Concordance index: {cph.concordance_index_:.4f}")

    # --- Proportional hazards assumption check --------------------------------
    print("\nProportional hazards test (Schoenfeld residuals):")
    try:
        ph_test = cph.check_assumptions(sub[fit_cols], p_value_threshold=0.05, show_plots=False)
        if not ph_test:
            print("  All covariates satisfy the PH assumption.")
    except Exception as exc:
        print(f"  Could not complete PH test: {exc}")
    print()

    # --- Kaplan-Meier curves -------------------------------------------------
    if args.km_strata and args.km_plot:
        try:
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError:
            print("Warning: matplotlib not installed; skipping KM plot.", file=sys.stderr)
            args.km_plot = None

    if args.km_strata:
        strata_vals = sorted(sub[args.km_strata].unique())
        print(f"Kaplan-Meier analysis stratified by: {args.km_strata}")
        print(f"  Strata: {strata_vals}")

        # Log-rank test
        if len(strata_vals) == 2:
            g1 = sub[sub[args.km_strata] == strata_vals[0]]
            g2 = sub[sub[args.km_strata] == strata_vals[1]]
            lr = logrank_test(
                g1[args.duration],
                g2[args.duration],
                event_observed_A=g1[args.event],
                event_observed_B=g2[args.event],
            )
            print(f"  Log-rank test: chi2 = {lr.test_statistic:.4f}, p = {lr.p_value:.6f}")

        if args.km_plot:
            fig, ax = plt.subplots(figsize=(8, 6))
            kmf = KaplanMeierFitter()
            for val in strata_vals:
                mask = sub[args.km_strata] == val
                kmf.fit(
                    sub.loc[mask, args.duration],
                    event_observed=sub.loc[mask, args.event],
                    label=f"{args.km_strata} = {val}",
                )
                kmf.plot_survival_function(ax=ax)

            ax.set_xlabel("Time")
            ax.set_ylabel("Survival Probability")
            ax.set_title("Kaplan-Meier Survival Curves")
            ax.legend()
            fig.tight_layout()
            fig.savefig(args.km_plot, dpi=150)
            plt.close(fig)
            print(f"  KM plot saved to {args.km_plot}")
        print()

    # --- Save ----------------------------------------------------------------
    if args.output:
        hr_df.to_csv(args.output, index=False)
        print(f"Hazard ratio table saved to {args.output}")


if __name__ == "__main__":
    main()

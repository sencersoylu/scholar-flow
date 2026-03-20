#!/usr/bin/env python3
"""
chi_square.py — Chi-square test of independence with Cramer's V.

Automatically falls back to Fisher's exact test when any expected cell count
is below 5 (2x2 tables). Reports observed and expected frequency tables,
test statistic, p-value, and Cramer's V effect size.

Dependencies:
    numpy, scipy, pandas

Example usage:
    python chi_square.py --input data.csv --row treatment --col outcome
    python chi_square.py --input data.csv --row sex --col response --alpha 0.01
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


def cramers_v(chi2: float, n: int, k: int, r: int) -> float:
    """Compute Cramer's V from chi-square statistic.

    Parameters
    ----------
    chi2 : float  Chi-square statistic.
    n : int        Total sample size.
    k : int        Number of columns.
    r : int        Number of rows.

    Returns
    -------
    float  Cramer's V.
    """
    min_dim = min(k - 1, r - 1)
    if min_dim == 0 or n == 0:
        return 0.0
    return float(np.sqrt(chi2 / (n * min_dim)))


def interpret_v(v: float) -> str:
    """Interpret Cramer's V magnitude (Cohen's benchmarks)."""
    if v < 0.1:
        return "negligible"
    if v < 0.3:
        return "small"
    if v < 0.5:
        return "medium"
    return "large"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chi-square test of independence (or Fisher's exact for small samples).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input data.csv --row treatment --col outcome
  %(prog)s --input data.csv --row sex --col response --alpha 0.01
        """,
    )
    parser.add_argument("--input", "-i", required=True, help="Path to CSV file.")
    parser.add_argument("--row", "-r", required=True, help="Row variable (categorical).")
    parser.add_argument("--col", "-c", required=True, help="Column variable (categorical).")
    parser.add_argument("--alpha", "-a", type=float, default=0.05, help="Significance level.")
    parser.add_argument("--separator", "--sep", default=",", help="CSV delimiter.")
    args = parser.parse_args()

    # --- Load data -----------------------------------------------------------
    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    df = pd.read_csv(input_path, sep=args.separator)

    for v in [args.row, args.col]:
        if v not in df.columns:
            print(f"Error: Column '{v}' not found.", file=sys.stderr)
            sys.exit(1)

    sub = df[[args.row, args.col]].dropna()
    n = len(sub)

    print("=" * 60)
    print("CHI-SQUARE TEST OF INDEPENDENCE")
    print("=" * 60)
    print(f"Row variable   : {args.row}")
    print(f"Column variable: {args.col}")
    print(f"N (complete)   : {n}")
    print(f"Alpha          : {args.alpha}")
    print()

    # --- Contingency table ---------------------------------------------------
    ct = pd.crosstab(sub[args.row], sub[args.col], margins=True, margins_name="Total")
    print("Observed frequencies:")
    print(ct.to_string())
    print()

    ct_no_margins = pd.crosstab(sub[args.row], sub[args.col])
    r_dim, k_dim = ct_no_margins.shape

    # --- Expected frequencies ------------------------------------------------
    chi2, p_chi, dof, expected = stats.chi2_contingency(ct_no_margins)
    expected_df = pd.DataFrame(
        expected,
        index=ct_no_margins.index,
        columns=ct_no_margins.columns,
    )
    print("Expected frequencies:")
    print(expected_df.round(2).to_string())
    print()

    low_expected = (expected < 5).sum()
    if low_expected > 0:
        print(f"Warning: {low_expected} cell(s) have expected count < 5.")
        print()

    # --- Select test ---------------------------------------------------------
    use_fisher = False
    if r_dim == 2 and k_dim == 2 and low_expected > 0:
        use_fisher = True

    if use_fisher:
        odds_ratio, p_val = stats.fisher_exact(ct_no_margins.values)
        test_name = "Fisher's exact test"
        print(f"Test       : {test_name}")
        print(f"Odds ratio : {odds_ratio:.4f}")
        print(f"p-value    : {p_val:.6f}")
        # Use chi2 from chi2_contingency for Cramer's V
        v = cramers_v(chi2, n, k_dim, r_dim)
    else:
        test_name = "Pearson's chi-square"
        p_val = p_chi
        print(f"Test       : {test_name}")
        print(f"Chi-square : {chi2:.4f}")
        print(f"df         : {dof}")
        print(f"p-value    : {p_val:.6f}")
        v = cramers_v(chi2, n, k_dim, r_dim)

    print(f"Cramer's V : {v:.4f} ({interpret_v(v)})")
    print()

    if p_val < args.alpha:
        print(f"Result: Statistically significant association (p < {args.alpha}).")
    else:
        print(f"Result: No significant association (p >= {args.alpha}).")

    # --- Contribution to chi-square ------------------------------------------
    print()
    print("Cell contributions to chi-square (standardised residuals):")
    std_resid = (ct_no_margins.values - expected) / np.sqrt(expected)
    resid_df = pd.DataFrame(
        std_resid, index=ct_no_margins.index, columns=ct_no_margins.columns
    )
    print(resid_df.round(3).to_string())


if __name__ == "__main__":
    main()

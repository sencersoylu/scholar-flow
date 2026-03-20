#!/usr/bin/env python3
"""
mann_whitney.py — Mann-Whitney U test with rank-biserial correlation.

Non-parametric test for comparing two independent groups. Reports the U
statistic, p-value, and rank-biserial correlation as the effect size measure.

Dependencies:
    numpy, scipy, pandas

Example usage:
    python mann_whitney.py --input data.csv --column score --group-column treatment
    python mann_whitney.py --input data.csv --column pain --group-column drug --alpha 0.01
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


def rank_biserial(u: float, n1: int, n2: int) -> float:
    """Compute rank-biserial correlation from Mann-Whitney U.

    r = 1 - (2U) / (n1 * n2)

    Returns a value in [-1, 1].
    """
    product = n1 * n2
    if product == 0:
        return 0.0
    return 1.0 - (2.0 * u) / product


def interpret_r(r: float) -> str:
    """Interpret rank-biserial correlation magnitude."""
    ar = abs(r)
    if ar < 0.1:
        return "negligible"
    if ar < 0.3:
        return "small"
    if ar < 0.5:
        return "medium"
    return "large"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Mann-Whitney U test with rank-biserial correlation effect size.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input data.csv --column score --group-column treatment
  %(prog)s --input data.csv --column pain --group-column drug --alternative less
        """,
    )
    parser.add_argument("--input", "-i", required=True, help="Path to CSV file.")
    parser.add_argument("--column", "-c", required=True, help="Numeric variable to compare.")
    parser.add_argument("--group-column", "-g", required=True, help="Grouping variable (must have exactly 2 levels).")
    parser.add_argument("--alpha", "-a", type=float, default=0.05, help="Significance level.")
    parser.add_argument(
        "--alternative",
        choices=["two-sided", "less", "greater"],
        default="two-sided",
        help="Alternative hypothesis (default: two-sided).",
    )
    parser.add_argument("--separator", "--sep", default=",", help="CSV delimiter.")
    args = parser.parse_args()

    # --- Load data -----------------------------------------------------------
    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    df = pd.read_csv(input_path, sep=args.separator)

    for col in [args.column, args.group_column]:
        if col not in df.columns:
            print(f"Error: Column '{col}' not found.", file=sys.stderr)
            sys.exit(1)

    sub = df[[args.column, args.group_column]].dropna()
    groups = sorted(sub[args.group_column].unique())
    if len(groups) != 2:
        print(f"Error: Expected 2 groups, found {len(groups)}: {groups}", file=sys.stderr)
        sys.exit(1)

    a = sub.loc[sub[args.group_column] == groups[0], args.column].values.astype(float)
    b = sub.loc[sub[args.group_column] == groups[1], args.column].values.astype(float)

    print("=" * 60)
    print("MANN-WHITNEY U TEST")
    print("=" * 60)
    print(f"Variable   : {args.column}")
    print(f"Groups     : {groups[0]} (n={len(a)}) vs {groups[1]} (n={len(b)})")
    print(f"Alternative: {args.alternative}")
    print(f"Alpha      : {args.alpha}")
    print()

    # --- Descriptives --------------------------------------------------------
    print("Descriptives (median [IQR]):")
    for label, d in [(groups[0], a), (groups[1], b)]:
        q1, med, q3 = np.percentile(d, [25, 50, 75])
        print(f"  {label}: median = {med:.4f}, IQR = [{q1:.4f} - {q3:.4f}], mean rank will follow")
    print()

    # --- Mean ranks ----------------------------------------------------------
    combined = np.concatenate([a, b])
    ranks = stats.rankdata(combined)
    rank_a = ranks[: len(a)]
    rank_b = ranks[len(a) :]
    print(f"Mean rank ({groups[0]}): {np.mean(rank_a):.2f}")
    print(f"Mean rank ({groups[1]}): {np.mean(rank_b):.2f}")
    print()

    # --- Test ----------------------------------------------------------------
    u_stat, p_val = stats.mannwhitneyu(a, b, alternative=args.alternative)
    r = rank_biserial(u_stat, len(a), len(b))

    print(f"U statistic       : {u_stat:.1f}")
    print(f"p-value           : {p_val:.6f}")
    print(f"Rank-biserial r   : {r:.4f} ({interpret_r(r)})")
    print()

    if p_val < args.alpha:
        print(f"Result: Statistically significant (p < {args.alpha}).")
    else:
        print(f"Result: Not statistically significant (p >= {args.alpha}).")

    # Hodges-Lehmann estimator (median of pairwise differences)
    if len(a) * len(b) <= 10_000_000:  # only compute for manageable sizes
        pairwise = np.subtract.outer(a, b).ravel()
        hl = np.median(pairwise)
        print(f"\nHodges-Lehmann estimate of location shift: {hl:.4f}")
    else:
        print("\nHodges-Lehmann estimate skipped (sample sizes too large for pairwise computation).")


if __name__ == "__main__":
    main()

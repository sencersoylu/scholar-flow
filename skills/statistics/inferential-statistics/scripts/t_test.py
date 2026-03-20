#!/usr/bin/env python3
"""
t_test.py — Perform independent or paired t-tests from CSV data.

Checks assumptions (normality via Shapiro-Wilk, equal variance via Levene's
test) and automatically falls back to Welch's t-test or Mann-Whitney U when
assumptions are violated. Reports Cohen's d effect size and confidence
intervals.

Dependencies:
    numpy, scipy, pandas

Example usage:
    python t_test.py --input data.csv --column score --group-column treatment
    python t_test.py --input data.csv --column1 pre_score --column2 post_score --paired
    python t_test.py --input data.csv --column value --group-column group --alpha 0.01
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


# ---------------------------------------------------------------------------
# Effect size
# ---------------------------------------------------------------------------

def cohens_d_independent(a: np.ndarray, b: np.ndarray) -> float:
    """Compute Cohen's d for independent samples using pooled SD."""
    n1, n2 = len(a), len(b)
    var1, var2 = np.var(a, ddof=1), np.var(b, ddof=1)
    pooled_sd = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_sd == 0:
        return 0.0
    return float((np.mean(a) - np.mean(b)) / pooled_sd)


def cohens_d_paired(diff: np.ndarray) -> float:
    """Compute Cohen's d for paired samples (d_z)."""
    sd = np.std(diff, ddof=1)
    if sd == 0:
        return 0.0
    return float(np.mean(diff) / sd)


def interpret_d(d: float) -> str:
    """Interpret Cohen's d magnitude."""
    ad = abs(d)
    if ad < 0.2:
        return "negligible"
    if ad < 0.5:
        return "small"
    if ad < 0.8:
        return "medium"
    return "large"


def mean_diff_ci(a: np.ndarray, b: np.ndarray, alpha: float = 0.05) -> tuple:
    """Compute CI for difference in means (independent, equal var assumed)."""
    n1, n2 = len(a), len(b)
    diff = np.mean(a) - np.mean(b)
    var1, var2 = np.var(a, ddof=1), np.var(b, ddof=1)
    se = np.sqrt(var1 / n1 + var2 / n2)
    df = n1 + n2 - 2
    t_crit = stats.t.ppf(1 - alpha / 2, df)
    return diff - t_crit * se, diff + t_crit * se


def paired_diff_ci(diff: np.ndarray, alpha: float = 0.05) -> tuple:
    """Compute CI for mean of paired differences."""
    n = len(diff)
    mean_d = np.mean(diff)
    se = np.std(diff, ddof=1) / np.sqrt(n)
    t_crit = stats.t.ppf(1 - alpha / 2, n - 1)
    return mean_d - t_crit * se, mean_d + t_crit * se


# ---------------------------------------------------------------------------
# Assumption checks
# ---------------------------------------------------------------------------

def check_normality(data: np.ndarray, label: str, alpha: float = 0.05) -> bool:
    """Run Shapiro-Wilk and print result. Returns True if normal."""
    if len(data) < 3:
        print(f"  {label}: n < 3, cannot test normality")
        return False
    sample = data[:5000] if len(data) > 5000 else data
    stat, p = stats.shapiro(sample)
    normal = p >= alpha
    verdict = "PASS (normal)" if normal else "FAIL (non-normal)"
    print(f"  {label}: W = {stat:.4f}, p = {p:.4f} -> {verdict}")
    return normal


def check_equal_variance(a: np.ndarray, b: np.ndarray, alpha: float = 0.05) -> bool:
    """Run Levene's test. Returns True if equal variance."""
    stat, p = stats.levene(a, b)
    equal = p >= alpha
    verdict = "PASS (equal)" if equal else "FAIL (unequal)"
    print(f"  Levene's test: F = {stat:.4f}, p = {p:.4f} -> {verdict}")
    return equal


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Perform t-tests (independent or paired) with assumption checks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples (independent):
  %(prog)s --input data.csv --column score --group-column treatment

Examples (paired):
  %(prog)s --input data.csv --column1 pre --column2 post --paired
        """,
    )
    parser.add_argument("--input", "-i", required=True, help="Path to CSV file.")
    # Independent mode
    parser.add_argument("--column", "-c", help="Numeric column (independent mode).")
    parser.add_argument("--group-column", "-g", help="Grouping column (independent mode).")
    # Paired mode
    parser.add_argument("--column1", help="First measurement column (paired mode).")
    parser.add_argument("--column2", help="Second measurement column (paired mode).")
    parser.add_argument("--paired", action="store_true", help="Perform a paired t-test.")
    # Common
    parser.add_argument(
        "--alpha", "-a", type=float, default=0.05, help="Significance level (default: 0.05)."
    )
    parser.add_argument("--separator", "--sep", default=",", help="CSV delimiter.")
    args = parser.parse_args()

    # --- Validate arguments --------------------------------------------------
    if args.paired:
        if not args.column1 or not args.column2:
            parser.error("Paired mode requires --column1 and --column2.")
    else:
        if not args.column or not args.group_column:
            parser.error("Independent mode requires --column and --group-column.")

    # --- Load data -----------------------------------------------------------
    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    df = pd.read_csv(input_path, sep=args.separator)

    alpha = args.alpha

    if args.paired:
        # ---- Paired t-test --------------------------------------------------
        for col in [args.column1, args.column2]:
            if col not in df.columns:
                print(f"Error: Column '{col}' not found.", file=sys.stderr)
                sys.exit(1)

        valid = df[[args.column1, args.column2]].dropna()
        a = valid[args.column1].values.astype(float)
        b = valid[args.column2].values.astype(float)
        diff = a - b

        print("=" * 60)
        print("PAIRED T-TEST")
        print("=" * 60)
        print(f"Column 1: {args.column1} (n = {len(a)})")
        print(f"Column 2: {args.column2}")
        print(f"Alpha   : {alpha}")
        print()

        # Descriptives
        print("Descriptives:")
        print(f"  {args.column1}: mean = {np.mean(a):.4f}, SD = {np.std(a, ddof=1):.4f}")
        print(f"  {args.column2}: mean = {np.mean(b):.4f}, SD = {np.std(b, ddof=1):.4f}")
        print(f"  Difference : mean = {np.mean(diff):.4f}, SD = {np.std(diff, ddof=1):.4f}")
        print()

        # Assumption check
        print("Assumption Checks:")
        normal = check_normality(diff, "Differences", alpha)
        print()

        if normal:
            stat, p = stats.ttest_rel(a, b)
            test_name = "Paired t-test"
        else:
            stat, p = stats.wilcoxon(diff)
            test_name = "Wilcoxon signed-rank (fallback)"

        d = cohens_d_paired(diff)
        ci_low, ci_high = paired_diff_ci(diff, alpha)

        print(f"Test: {test_name}")
        print(f"Statistic: {stat:.4f}")
        print(f"p-value  : {p:.6f}")
        print(f"Cohen's d: {d:.4f} ({interpret_d(d)})")
        print(f"{100 * (1 - alpha):.0f}% CI for mean difference: [{ci_low:.4f}, {ci_high:.4f}]")
        print()
        if p < alpha:
            print(f"Result: Statistically significant (p < {alpha}).")
        else:
            print(f"Result: Not statistically significant (p >= {alpha}).")

    else:
        # ---- Independent t-test ---------------------------------------------
        if args.column not in df.columns:
            print(f"Error: Column '{args.column}' not found.", file=sys.stderr)
            sys.exit(1)
        if args.group_column not in df.columns:
            print(f"Error: Column '{args.group_column}' not found.", file=sys.stderr)
            sys.exit(1)

        sub = df[[args.column, args.group_column]].dropna()
        groups = sorted(sub[args.group_column].unique())
        if len(groups) != 2:
            print(
                f"Error: Expected exactly 2 groups, found {len(groups)}: {groups}",
                file=sys.stderr,
            )
            sys.exit(1)

        a = sub.loc[sub[args.group_column] == groups[0], args.column].values.astype(float)
        b = sub.loc[sub[args.group_column] == groups[1], args.column].values.astype(float)

        print("=" * 60)
        print("INDEPENDENT SAMPLES T-TEST")
        print("=" * 60)
        print(f"Variable: {args.column}")
        print(f"Groups  : {groups[0]} (n={len(a)}) vs {groups[1]} (n={len(b)})")
        print(f"Alpha   : {alpha}")
        print()

        # Descriptives
        print("Descriptives:")
        print(f"  {groups[0]}: mean = {np.mean(a):.4f}, SD = {np.std(a, ddof=1):.4f}")
        print(f"  {groups[1]}: mean = {np.mean(b):.4f}, SD = {np.std(b, ddof=1):.4f}")
        print()

        # Assumption checks
        print("Assumption Checks:")
        norm_a = check_normality(a, f"Group '{groups[0]}'", alpha)
        norm_b = check_normality(b, f"Group '{groups[1]}'", alpha)
        both_normal = norm_a and norm_b

        if both_normal:
            eq_var = check_equal_variance(a, b, alpha)
        else:
            eq_var = False
        print()

        # Select test
        if both_normal and eq_var:
            stat, p = stats.ttest_ind(a, b, equal_var=True)
            test_name = "Student's t-test"
        elif both_normal and not eq_var:
            stat, p = stats.ttest_ind(a, b, equal_var=False)
            test_name = "Welch's t-test (unequal variances)"
        else:
            stat, p = stats.mannwhitneyu(a, b, alternative="two-sided")
            test_name = "Mann-Whitney U (non-normal data)"

        d = cohens_d_independent(a, b)
        ci_low, ci_high = mean_diff_ci(a, b, alpha)

        print(f"Test     : {test_name}")
        print(f"Statistic: {stat:.4f}")
        print(f"p-value  : {p:.6f}")
        print(f"Cohen's d: {d:.4f} ({interpret_d(d)})")
        print(f"{100 * (1 - alpha):.0f}% CI for difference in means: [{ci_low:.4f}, {ci_high:.4f}]")
        print()
        if p < alpha:
            print(f"Result: Statistically significant (p < {alpha}).")
        else:
            print(f"Result: Not statistically significant (p >= {alpha}).")


if __name__ == "__main__":
    main()

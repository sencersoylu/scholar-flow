#!/usr/bin/env python3
"""
anova.py — One-way and two-way ANOVA with post-hoc tests.

Performs one-way or two-way ANOVA from CSV data. Reports F-statistic,
p-value, and eta-squared effect size. For significant results, runs Tukey
HSD and/or Bonferroni-corrected pairwise comparisons.

Dependencies:
    numpy, scipy, pandas, statsmodels

Example usage:
    python anova.py --input data.csv --dependent score --factor treatment
    python anova.py --input data.csv --dependent score --factor treatment --posthoc tukey
    python anova.py --input data.csv --dependent score --factors treatment sex --two-way
"""

from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


def eta_squared(ss_between: float, ss_total: float) -> float:
    """Compute eta-squared effect size."""
    if ss_total == 0:
        return 0.0
    return ss_between / ss_total


def interpret_eta(es: float) -> str:
    if es < 0.01:
        return "negligible"
    if es < 0.06:
        return "small"
    if es < 0.14:
        return "medium"
    return "large"


# ---------------------------------------------------------------------------
# One-way ANOVA
# ---------------------------------------------------------------------------


def oneway_anova(
    df: pd.DataFrame,
    dependent: str,
    factor: str,
    alpha: float,
    posthoc: str,
) -> None:
    """Run a one-way ANOVA and optional post-hoc tests."""
    sub = df[[dependent, factor]].dropna()
    groups = sorted(sub[factor].unique())
    k = len(groups)
    if k < 2:
        print("Error: Need at least 2 groups for ANOVA.", file=sys.stderr)
        sys.exit(1)

    group_data = [sub.loc[sub[factor] == g, dependent].values.astype(float) for g in groups]

    print("=" * 65)
    print("ONE-WAY ANOVA")
    print("=" * 65)
    print(f"Dependent variable: {dependent}")
    print(f"Factor            : {factor} ({k} levels: {groups})")
    print(f"Alpha             : {alpha}")
    print()

    # Descriptives
    print("Group descriptives:")
    for g, d in zip(groups, group_data):
        print(f"  {g}: n = {len(d)}, mean = {np.mean(d):.4f}, SD = {np.std(d, ddof=1):.4f}")
    print()

    # Assumption: Levene's test for homogeneity of variance
    lev_stat, lev_p = stats.levene(*group_data)
    print(f"Levene's test: F = {lev_stat:.4f}, p = {lev_p:.4f}", end="")
    if lev_p < alpha:
        print(" -> FAIL (unequal variances; consider Welch's ANOVA)")
    else:
        print(" -> PASS (equal variances)")
    print()

    # ANOVA
    f_stat, p_val = stats.f_oneway(*group_data)

    # Compute SS for eta-squared
    grand_mean = np.mean(sub[dependent])
    ss_between = sum(len(d) * (np.mean(d) - grand_mean) ** 2 for d in group_data)
    ss_total = np.sum((sub[dependent].values - grand_mean) ** 2)
    es = eta_squared(ss_between, ss_total)

    n_total = sum(len(d) for d in group_data)
    df_between = k - 1
    df_within = n_total - k

    print("ANOVA Table:")
    print(f"  {'Source':<15} {'SS':>12} {'df':>6} {'MS':>12} {'F':>10} {'p':>10}")
    print(f"  {'-' * 65}")
    ms_between = ss_between / df_between if df_between > 0 else 0
    ss_within = ss_total - ss_between
    ms_within = ss_within / df_within if df_within > 0 else 0
    print(
        f"  {'Between':<15} {ss_between:>12.4f} {df_between:>6}"
        f" {ms_between:>12.4f} {f_stat:>10.4f} {p_val:>10.6f}"
    )
    print(f"  {'Within':<15} {ss_within:>12.4f} {df_within:>6} {ms_within:>12.4f}")
    print(f"  {'Total':<15} {ss_total:>12.4f} {n_total - 1:>6}")
    print()
    print(f"Eta-squared: {es:.4f} ({interpret_eta(es)})")
    print()

    if p_val < alpha:
        print(
            f"Result: Statistically significant "
            f"(F({df_between},{df_within}) = {f_stat:.4f}, p = {p_val:.6f})."
        )
        print()

        # Post-hoc tests
        if posthoc in ("tukey", "both"):
            _tukey_hsd(sub, dependent, factor, groups, alpha)
        if posthoc in ("bonferroni", "both"):
            _bonferroni(group_data, groups, alpha)
    else:
        print(f"Result: Not statistically significant (p = {p_val:.6f}).")


def _tukey_hsd(df: pd.DataFrame, dependent: str, factor: str, groups: list, alpha: float) -> None:
    """Tukey HSD post-hoc test."""
    try:
        from statsmodels.stats.multicomp import pairwise_tukeyhsd
    except ImportError:
        print("Warning: statsmodels not installed; skipping Tukey HSD.", file=sys.stderr)
        return

    result = pairwise_tukeyhsd(df[dependent], df[factor], alpha=alpha)
    print("Tukey HSD Post-Hoc Comparisons:")
    print(result)
    print()


def _bonferroni(group_data: list, groups: list, alpha: float) -> None:
    """Bonferroni-corrected pairwise t-tests."""
    pairs = list(itertools.combinations(range(len(groups)), 2))
    n_comparisons = len(pairs)
    adj_alpha = alpha / n_comparisons

    print(f"Bonferroni-corrected pairwise t-tests (adjusted alpha = {adj_alpha:.4f}):")
    print(f"  {'Comparison':<30} {'t':>10} {'p (raw)':>12} {'p (adj)':>12} {'Sig':>6}")
    print(f"  {'-' * 70}")
    for i, j in pairs:
        t_stat, p_raw = stats.ttest_ind(group_data[i], group_data[j])
        p_adj = min(p_raw * n_comparisons, 1.0)
        sig = "*" if p_adj < alpha else "ns"
        label = f"{groups[i]} vs {groups[j]}"
        print(f"  {label:<30} {t_stat:>10.4f} {p_raw:>12.6f} {p_adj:>12.6f} {sig:>6}")
    print()


# ---------------------------------------------------------------------------
# Two-way ANOVA
# ---------------------------------------------------------------------------


def twoway_anova(
    df: pd.DataFrame,
    dependent: str,
    factors: list[str],
    alpha: float,
) -> None:
    """Run a two-way ANOVA using statsmodels."""
    try:
        import statsmodels.api as sm
        from statsmodels.formula.api import ols
    except ImportError:
        print("Error: statsmodels is required for two-way ANOVA.", file=sys.stderr)
        sys.exit(1)

    if len(factors) != 2:
        print("Error: Two-way ANOVA requires exactly 2 factors.", file=sys.stderr)
        sys.exit(1)

    f1, f2 = factors
    sub = df[[dependent, f1, f2]].dropna()

    print("=" * 65)
    print("TWO-WAY ANOVA")
    print("=" * 65)
    print(f"Dependent: {dependent}")
    print(f"Factors  : {f1}, {f2}")
    print(f"N        : {len(sub)}")
    print(f"Alpha    : {alpha}")
    print()

    # Fit OLS model with interaction
    formula = f"Q('{dependent}') ~ C(Q('{f1}')) * C(Q('{f2}'))"
    model = ols(formula, data=sub).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)

    print("ANOVA Table (Type II SS):")
    print(anova_table.to_string())
    print()

    # Eta-squared for each effect
    ss_total = anova_table["sum_sq"].sum()
    print("Effect sizes (eta-squared):")
    for idx in anova_table.index:
        if idx == "Residual":
            continue
        es = anova_table.loc[idx, "sum_sq"] / ss_total
        p = anova_table.loc[idx, "PR(>F)"]
        sig = "*" if p < alpha else "ns"
        print(f"  {idx}: eta^2 = {es:.4f} ({interpret_eta(es)}), p = {p:.6f} {sig}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="One-way or two-way ANOVA with post-hoc tests.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input data.csv --dependent score --factor treatment
  %(prog)s --input data.csv --dependent score --factor treatment --posthoc both
  %(prog)s --input data.csv --dependent score --factors treatment sex --two-way
        """,
    )
    parser.add_argument("--input", "-i", required=True, help="Path to CSV file.")
    parser.add_argument("--dependent", "-d", required=True, help="Dependent variable column.")
    parser.add_argument("--factor", "-f", help="Factor column (one-way ANOVA).")
    parser.add_argument("--factors", nargs=2, help="Two factor columns (two-way ANOVA).")
    parser.add_argument("--two-way", action="store_true", help="Run two-way ANOVA.")
    parser.add_argument(
        "--posthoc",
        choices=["tukey", "bonferroni", "both"],
        default="both",
        help="Post-hoc method for one-way ANOVA (default: both).",
    )
    parser.add_argument("--alpha", "-a", type=float, default=0.05, help="Significance level.")
    parser.add_argument("--separator", "--sep", default=",", help="CSV delimiter.")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    df = pd.read_csv(input_path, sep=args.separator)

    if args.two_way:
        if not args.factors:
            parser.error("--two-way requires --factors with 2 column names.")
        twoway_anova(df, args.dependent, args.factors, args.alpha)
    else:
        if not args.factor:
            parser.error("One-way ANOVA requires --factor.")
        oneway_anova(df, args.dependent, args.factor, args.alpha, args.posthoc)


if __name__ == "__main__":
    main()

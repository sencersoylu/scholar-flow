#!/usr/bin/env python3
"""
sample_size_calculator.py — Unified sample size / power calculator.

Supports sample size calculation for:
  - Independent t-test
  - Paired t-test
  - One-way ANOVA
  - Chi-square test
  - Correlation (Pearson r)
  - Linear regression (multiple R-squared)

Provides both CLI mode (via argparse) and interactive mode.

Dependencies:
    numpy, scipy, statsmodels

Example usage (CLI):
    python sample_size_calculator.py --test-type t-test-ind --effect-size 0.5 --alpha 0.05 --power 0.80
    python sample_size_calculator.py --test-type anova --effect-size 0.25 --alpha 0.05 --power 0.80 --groups 3
    python sample_size_calculator.py --test-type chi-square --effect-size 0.3 --alpha 0.05 --power 0.80 --df 2
    python sample_size_calculator.py --test-type correlation --effect-size 0.3 --alpha 0.05 --power 0.80
    python sample_size_calculator.py --test-type regression --effect-size 0.15 --alpha 0.05 --power 0.80 --predictors 5

Interactive mode:
    python sample_size_calculator.py --interactive
"""

from __future__ import annotations

import argparse
import math
import sys

import numpy as np
from scipy import stats


# ---------------------------------------------------------------------------
# Effect size guidelines
# ---------------------------------------------------------------------------

EFFECT_SIZE_GUIDE = {
    "t-test-ind": {"small": 0.2, "medium": 0.5, "large": 0.8, "metric": "Cohen's d"},
    "t-test-paired": {"small": 0.2, "medium": 0.5, "large": 0.8, "metric": "Cohen's d_z"},
    "anova": {"small": 0.1, "medium": 0.25, "large": 0.4, "metric": "Cohen's f"},
    "chi-square": {"small": 0.1, "medium": 0.3, "large": 0.5, "metric": "Cohen's w"},
    "correlation": {"small": 0.1, "medium": 0.3, "large": 0.5, "metric": "Pearson r"},
    "regression": {"small": 0.02, "medium": 0.15, "large": 0.35, "metric": "Cohen's f^2"},
}


def print_effect_guide(test_type: str) -> None:
    """Print effect size conventions for a given test."""
    guide = EFFECT_SIZE_GUIDE.get(test_type)
    if guide:
        print(f"  Effect size metric: {guide['metric']}")
        print(f"    Small  = {guide['small']}")
        print(f"    Medium = {guide['medium']}")
        print(f"    Large  = {guide['large']}")


# ---------------------------------------------------------------------------
# Sample size functions
# ---------------------------------------------------------------------------

def ss_ttest_ind(d: float, alpha: float, power: float, ratio: float = 1.0) -> dict:
    """Sample size for independent two-sample t-test.

    Parameters
    ----------
    d : float      Cohen's d effect size.
    alpha : float  Significance level (two-sided).
    power : float  Desired power.
    ratio : float  Allocation ratio n2/n1 (default 1:1).

    Returns
    -------
    dict with n1, n2, total.
    """
    try:
        from statsmodels.stats.power import TTestIndPower
        analysis = TTestIndPower()
        n1 = analysis.solve_power(effect_size=d, alpha=alpha, power=power, ratio=ratio, alternative="two-sided")
        n1 = math.ceil(n1)
        n2 = math.ceil(n1 * ratio)
        return {"n_per_group_1": n1, "n_per_group_2": n2, "total": n1 + n2}
    except ImportError:
        # Fallback: manual calculation
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(power)
        n1 = math.ceil(((z_alpha + z_beta) / d) ** 2 * (1 + 1 / ratio))
        n2 = math.ceil(n1 * ratio)
        return {"n_per_group_1": n1, "n_per_group_2": n2, "total": n1 + n2}


def ss_ttest_paired(d: float, alpha: float, power: float) -> dict:
    """Sample size for paired t-test."""
    try:
        from statsmodels.stats.power import TTestPower
        analysis = TTestPower()
        n = analysis.solve_power(effect_size=d, alpha=alpha, power=power, alternative="two-sided")
        n = math.ceil(n)
        return {"n_pairs": n, "total": n}
    except ImportError:
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(power)
        n = math.ceil(((z_alpha + z_beta) / d) ** 2)
        return {"n_pairs": n, "total": n}


def ss_anova(f: float, alpha: float, power: float, k: int) -> dict:
    """Sample size for one-way ANOVA (per group).

    Parameters
    ----------
    f : float   Cohen's f effect size.
    alpha : float
    power : float
    k : int     Number of groups.
    """
    try:
        from statsmodels.stats.power import FTestAnovaPower
        analysis = FTestAnovaPower()
        n_per = analysis.solve_power(effect_size=f, alpha=alpha, power=power, k_groups=k)
        n_per = math.ceil(n_per)
        return {"n_per_group": n_per, "groups": k, "total": n_per * k}
    except ImportError:
        # Rough approximation using non-central F
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(power)
        n_per = math.ceil(((z_alpha + z_beta) ** 2) / (f ** 2) + (k - 1) / (2 * k))
        return {"n_per_group": n_per, "groups": k, "total": n_per * k}


def ss_chi_square(w: float, alpha: float, power: float, df: int) -> dict:
    """Sample size for chi-square test of independence.

    Parameters
    ----------
    w : float   Cohen's w effect size.
    df : int    Degrees of freedom ( (r-1)*(c-1) ).
    """
    try:
        from statsmodels.stats.power import GofChisquarePower
        analysis = GofChisquarePower()
        n = analysis.solve_power(effect_size=w, alpha=alpha, power=power, n_bins=df + 1)
        n = math.ceil(n)
        return {"total_n": n}
    except ImportError:
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(power)
        n = math.ceil(((z_alpha + z_beta) / w) ** 2)
        return {"total_n": n}


def ss_correlation(r: float, alpha: float, power: float) -> dict:
    """Sample size for testing a Pearson correlation."""
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    # Fisher z-transformation approach
    z_r = 0.5 * np.log((1 + r) / (1 - r))
    n = math.ceil(((z_alpha + z_beta) / z_r) ** 2 + 3)
    return {"total_n": n}


def ss_regression(f2: float, alpha: float, power: float, n_predictors: int) -> dict:
    """Sample size for multiple linear regression (R-squared F-test).

    Parameters
    ----------
    f2 : float          Cohen's f-squared effect size.
    n_predictors : int  Number of predictors in the model.
    """
    try:
        from statsmodels.stats.power import FTestPower
        # Convert f^2 to f for the library
        f = np.sqrt(f2)
        analysis = FTestPower()
        n = analysis.solve_power(
            effect_size=f,
            alpha=alpha,
            power=power,
            df_num=n_predictors,
        )
        n = math.ceil(n)
        return {"total_n": n, "predictors": n_predictors}
    except (ImportError, Exception):
        # Green (1991) rule of thumb: N >= 50 + 8*m for R^2, N >= 104 + m for individual predictors
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(power)
        # Cohen's formula: n = (z_a + z_b)^2 / f^2 + u + 1
        n = math.ceil(((z_alpha + z_beta) ** 2) / f2 + n_predictors + 1)
        return {"total_n": n, "predictors": n_predictors}


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def display_result(test_type: str, params: dict, result: dict) -> None:
    """Pretty-print the sample size calculation result."""
    print()
    print("=" * 55)
    print("SAMPLE SIZE CALCULATION RESULT")
    print("=" * 55)
    print(f"Test type   : {test_type}")
    for k, v in params.items():
        print(f"{k:<13}: {v}")
    print("-" * 55)
    for k, v in result.items():
        label = k.replace("_", " ").title()
        print(f"  {label:<25}: {v}")
    print("=" * 55)
    print()
    print_effect_guide(test_type)
    print()


# ---------------------------------------------------------------------------
# Interactive mode
# ---------------------------------------------------------------------------

def interactive_mode() -> None:
    """Run an interactive session asking the user for parameters."""
    print("=" * 55)
    print("SAMPLE SIZE CALCULATOR — Interactive Mode")
    print("=" * 55)
    print()
    print("Available test types:")
    print("  1. t-test-ind     (independent two-sample t-test)")
    print("  2. t-test-paired  (paired t-test)")
    print("  3. anova          (one-way ANOVA)")
    print("  4. chi-square     (chi-square test of independence)")
    print("  5. correlation    (Pearson correlation)")
    print("  6. regression     (multiple linear regression)")
    print()

    choice = input("Select test type (1-6 or name): ").strip()
    type_map = {
        "1": "t-test-ind",
        "2": "t-test-paired",
        "3": "anova",
        "4": "chi-square",
        "5": "correlation",
        "6": "regression",
    }
    test_type = type_map.get(choice, choice)

    if test_type not in EFFECT_SIZE_GUIDE:
        print(f"Error: Unknown test type '{test_type}'.", file=sys.stderr)
        sys.exit(1)

    print()
    print_effect_guide(test_type)
    print()

    effect_size = float(input("Effect size: ").strip())
    alpha = float(input("Alpha (default 0.05): ").strip() or "0.05")
    power = float(input("Power (default 0.80): ").strip() or "0.80")

    params = {"effect_size": effect_size, "alpha": alpha, "power": power}

    if test_type == "t-test-ind":
        ratio_str = input("Allocation ratio n2/n1 (default 1.0): ").strip() or "1.0"
        ratio = float(ratio_str)
        params["ratio"] = ratio
        result = ss_ttest_ind(effect_size, alpha, power, ratio)
    elif test_type == "t-test-paired":
        result = ss_ttest_paired(effect_size, alpha, power)
    elif test_type == "anova":
        k = int(input("Number of groups: ").strip())
        params["groups"] = k
        result = ss_anova(effect_size, alpha, power, k)
    elif test_type == "chi-square":
        df = int(input("Degrees of freedom (r-1)*(c-1): ").strip())
        params["df"] = df
        result = ss_chi_square(effect_size, alpha, power, df)
    elif test_type == "correlation":
        result = ss_correlation(effect_size, alpha, power)
    elif test_type == "regression":
        n_pred = int(input("Number of predictors: ").strip())
        params["predictors"] = n_pred
        result = ss_regression(effect_size, alpha, power, n_pred)
    else:
        print(f"Error: Unsupported test type.", file=sys.stderr)
        sys.exit(1)

    display_result(test_type, params, result)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Unified sample size / power calculator for common statistical tests.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --test-type t-test-ind --effect-size 0.5 --alpha 0.05 --power 0.80
  %(prog)s --test-type anova --effect-size 0.25 --alpha 0.05 --power 0.80 --groups 3
  %(prog)s --test-type chi-square --effect-size 0.3 --alpha 0.05 --power 0.80 --df 2
  %(prog)s --test-type correlation --effect-size 0.3 --alpha 0.05 --power 0.80
  %(prog)s --test-type regression --effect-size 0.15 --alpha 0.05 --power 0.80 --predictors 5
  %(prog)s --interactive
        """,
    )
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode.")
    parser.add_argument(
        "--test-type",
        choices=["t-test-ind", "t-test-paired", "anova", "chi-square", "correlation", "regression"],
        help="Type of statistical test.",
    )
    parser.add_argument("--effect-size", type=float, help="Expected effect size.")
    parser.add_argument("--alpha", type=float, default=0.05, help="Significance level (default: 0.05).")
    parser.add_argument("--power", type=float, default=0.80, help="Desired power (default: 0.80).")
    # Test-specific
    parser.add_argument("--ratio", type=float, default=1.0, help="Allocation ratio n2/n1 for t-test-ind.")
    parser.add_argument("--groups", type=int, help="Number of groups (ANOVA).")
    parser.add_argument("--df", type=int, help="Degrees of freedom (chi-square).")
    parser.add_argument("--predictors", type=int, help="Number of predictors (regression).")
    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    if not args.test_type or args.effect_size is None:
        parser.error("Provide --test-type and --effect-size, or use --interactive.")

    params = {
        "effect_size": args.effect_size,
        "alpha": args.alpha,
        "power": args.power,
    }

    if args.test_type == "t-test-ind":
        params["ratio"] = args.ratio
        result = ss_ttest_ind(args.effect_size, args.alpha, args.power, args.ratio)

    elif args.test_type == "t-test-paired":
        result = ss_ttest_paired(args.effect_size, args.alpha, args.power)

    elif args.test_type == "anova":
        if not args.groups:
            parser.error("ANOVA requires --groups.")
        params["groups"] = args.groups
        result = ss_anova(args.effect_size, args.alpha, args.power, args.groups)

    elif args.test_type == "chi-square":
        if not args.df:
            parser.error("Chi-square requires --df.")
        params["df"] = args.df
        result = ss_chi_square(args.effect_size, args.alpha, args.power, args.df)

    elif args.test_type == "correlation":
        result = ss_correlation(args.effect_size, args.alpha, args.power)

    elif args.test_type == "regression":
        if not args.predictors:
            parser.error("Regression requires --predictors.")
        params["predictors"] = args.predictors
        result = ss_regression(args.effect_size, args.alpha, args.power, args.predictors)

    else:
        parser.error(f"Unknown test type: {args.test_type}")
        return  # unreachable

    display_result(args.test_type, params, result)


if __name__ == "__main__":
    main()

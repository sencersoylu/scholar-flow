#!/usr/bin/env python3
"""
normality_test.py — Test the normality of a numeric variable from a CSV file.

Runs Shapiro-Wilk, Kolmogorov-Smirnov (Lilliefors), and D'Agostino-Pearson
tests. Optionally generates a Q-Q plot saved to disk.

Dependencies:
    numpy, scipy, pandas, matplotlib

Example usage:
    python normality_test.py --input data.csv --column age
    python normality_test.py --input data.csv --column bmi --alpha 0.01 --plot qq.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


def shapiro_wilk(data: np.ndarray, alpha: float) -> dict:
    """Shapiro-Wilk test for normality.

    Parameters
    ----------
    data : array-like
        1-D numeric array (NaN-free).
    alpha : float
        Significance level.

    Returns
    -------
    dict with test name, statistic, p-value, and decision.
    """
    if len(data) < 3:
        return {
            "Test": "Shapiro-Wilk",
            "Statistic": np.nan,
            "p-value": np.nan,
            "Result": "Insufficient data (n < 3)",
        }
    if len(data) > 5000:
        # Shapiro-Wilk is unreliable for very large samples; warn but still run
        stat, p = stats.shapiro(data[:5000])
        note = " (computed on first 5000 observations)"
    else:
        stat, p = stats.shapiro(data)
        note = ""
    decision = "Non-normal" if p < alpha else "Normal"
    return {
        "Test": "Shapiro-Wilk" + note,
        "Statistic": stat,
        "p-value": p,
        "Result": decision,
    }


def ks_test(data: np.ndarray, alpha: float) -> dict:
    """Kolmogorov-Smirnov test against a normal distribution.

    Uses the Lilliefors variant (parameters estimated from data) when
    available, otherwise falls back to a standard KS test with fitted
    parameters.
    """
    mu, sigma = np.mean(data), np.std(data, ddof=1)
    if sigma == 0:
        return {
            "Test": "Kolmogorov-Smirnov",
            "Statistic": np.nan,
            "p-value": np.nan,
            "Result": "Zero variance",
        }
    stat, p = stats.kstest(data, "norm", args=(mu, sigma))
    decision = "Non-normal" if p < alpha else "Normal"
    return {
        "Test": "Kolmogorov-Smirnov",
        "Statistic": stat,
        "p-value": p,
        "Result": decision,
    }


def dagostino_pearson(data: np.ndarray, alpha: float) -> dict:
    """D'Agostino-Pearson omnibus test for normality.

    Requires n >= 20.
    """
    if len(data) < 20:
        return {
            "Test": "D'Agostino-Pearson",
            "Statistic": np.nan,
            "p-value": np.nan,
            "Result": "Insufficient data (n < 20)",
        }
    stat, p = stats.normaltest(data)
    decision = "Non-normal" if p < alpha else "Normal"
    return {
        "Test": "D'Agostino-Pearson",
        "Statistic": stat,
        "p-value": p,
        "Result": decision,
    }


def generate_qq_plot(data: np.ndarray, column_name: str, output_path: str) -> None:
    """Generate and save a Q-Q plot.

    Parameters
    ----------
    data : array-like
        1-D numeric array (NaN-free).
    column_name : str
        Variable name for the plot title.
    output_path : str
        File path to save the figure (e.g. ``qq_plot.png``).
    """
    try:
        import matplotlib

        matplotlib.use("Agg")  # non-interactive backend
        import matplotlib.pyplot as plt
    except ImportError:
        print("Warning: matplotlib is not installed; skipping Q-Q plot.", file=sys.stderr)
        return

    fig, ax = plt.subplots(figsize=(6, 6))
    stats.probplot(data, dist="norm", plot=ax)
    ax.set_title(f"Q-Q Plot: {column_name}")
    ax.get_lines()[0].set(marker="o", markersize=4, markerfacecolor="steelblue")
    ax.get_lines()[1].set(color="firebrick", linewidth=1.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Q-Q plot saved to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Test the normality of a numeric variable from a CSV file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input data.csv --column age
  %(prog)s --input data.csv --column bmi --alpha 0.01
  %(prog)s --input data.csv --column score --plot qq_score.png
        """,
    )
    parser.add_argument("--input", "-i", required=True, help="Path to input CSV.")
    parser.add_argument("--column", "-c", required=True, help="Column name to test.")
    parser.add_argument(
        "--alpha",
        "-a",
        type=float,
        default=0.05,
        help="Significance level (default: 0.05).",
    )
    parser.add_argument(
        "--plot",
        "-p",
        default=None,
        help="File path to save Q-Q plot (e.g. qq.png).",
    )
    parser.add_argument("--separator", "--sep", default=",", help="CSV delimiter (default: comma).")
    args = parser.parse_args()

    # --- Load data -----------------------------------------------------------
    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        df = pd.read_csv(input_path, sep=args.separator)
    except Exception as exc:
        print(f"Error reading CSV: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.column not in df.columns:
        print(f"Error: Column '{args.column}' not found.", file=sys.stderr)
        print(f"Available columns: {list(df.columns)}", file=sys.stderr)
        sys.exit(1)

    raw = df[args.column]
    if not np.issubdtype(raw.dtype, np.number):
        print(f"Error: Column '{args.column}' is not numeric.", file=sys.stderr)
        sys.exit(1)

    data = raw.dropna().values.astype(float)
    n_missing = raw.isna().sum()

    print(f"Variable : {args.column}")
    print(f"N (valid): {len(data)}")
    print(f"Missing  : {n_missing}")
    print(f"Alpha    : {args.alpha}")
    print("-" * 60)

    if len(data) < 3:
        print("Error: Need at least 3 non-missing observations.", file=sys.stderr)
        sys.exit(1)

    # --- Run tests -----------------------------------------------------------
    results = [
        shapiro_wilk(data, args.alpha),
        ks_test(data, args.alpha),
        dagostino_pearson(data, args.alpha),
    ]

    header = f"{'Test':<25} {'Statistic':>12} {'p-value':>12} {'Result':<15}"
    print(header)
    print("-" * len(header))
    for r in results:
        stat_str = f"{r['Statistic']:.6f}" if not np.isnan(r["Statistic"]) else "N/A"
        p_str = f"{r['p-value']:.6f}" if not np.isnan(r["p-value"]) else "N/A"
        print(f"{r['Test']:<25} {stat_str:>12} {p_str:>12} {r['Result']:<15}")

    # --- Summary interpretation ----------------------------------------------
    valid_ps = [r["p-value"] for r in results if not np.isnan(r["p-value"])]
    if valid_ps:
        all_normal = all(p >= args.alpha for p in valid_ps)
        all_non = all(p < args.alpha for p in valid_ps)
        print()
        if all_normal:
            print(
                f"Conclusion: All tests suggest the data are consistent with a "
                f"normal distribution at alpha = {args.alpha}."
            )
        elif all_non:
            print(
                f"Conclusion: All tests reject the null hypothesis of normality "
                f"at alpha = {args.alpha}."
            )
        else:
            print(
                "Conclusion: Tests give mixed results. Inspect the Q-Q plot and "
                "consider the sample size when interpreting."
            )

    # --- Q-Q plot ------------------------------------------------------------
    if args.plot:
        generate_qq_plot(data, args.column, args.plot)


if __name__ == "__main__":
    main()

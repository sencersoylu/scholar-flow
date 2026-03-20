#!/usr/bin/env python3
"""
summary_stats.py — Compute descriptive summary statistics from a CSV file.

Calculates mean, median, mode, standard deviation, IQR, skewness, and
kurtosis for selected numeric columns. Outputs a formatted table to the
console and optionally to a CSV file.

Dependencies:
    numpy, scipy, pandas, tabulate

Example usage:
    python summary_stats.py --input data.csv
    python summary_stats.py --input data.csv --columns age bmi score
    python summary_stats.py --input data.csv --columns age --output summary.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

try:
    from tabulate import tabulate

    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


def compute_summary(series: pd.Series) -> dict:
    """Compute descriptive statistics for a single numeric pandas Series.

    Parameters
    ----------
    series : pd.Series
        A numeric Series (NaN values are dropped automatically).

    Returns
    -------
    dict
        Dictionary containing count, missing, mean, std, min, Q1, median,
        Q3, max, IQR, mode, skewness, and kurtosis.
    """
    clean = series.dropna()
    n = len(clean)
    n_missing = series.isna().sum()

    if n == 0:
        return {
            "N": 0,
            "Missing": int(n_missing),
            "Mean": np.nan,
            "SD": np.nan,
            "Min": np.nan,
            "Q1": np.nan,
            "Median": np.nan,
            "Q3": np.nan,
            "Max": np.nan,
            "IQR": np.nan,
            "Mode": np.nan,
            "Skewness": np.nan,
            "Kurtosis": np.nan,
        }

    q1, median, q3 = np.percentile(clean, [25, 50, 75])
    mode_result = stats.mode(clean, keepdims=True)
    mode_val = mode_result.mode[0] if len(mode_result.mode) > 0 else np.nan

    return {
        "N": n,
        "Missing": int(n_missing),
        "Mean": np.mean(clean),
        "SD": np.std(clean, ddof=1),
        "Min": np.min(clean),
        "Q1": q1,
        "Median": median,
        "Q3": q3,
        "Max": np.max(clean),
        "IQR": q3 - q1,
        "Mode": mode_val,
        "Skewness": float(stats.skew(clean, bias=False)),
        "Kurtosis": float(stats.kurtosis(clean, bias=False)),
    }


def format_value(val, decimals: int = 4) -> str:
    """Format a numeric value for display."""
    if isinstance(val, (int, np.integer)):
        return str(val)
    if pd.isna(val):
        return "N/A"
    return f"{val:.{decimals}f}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute descriptive summary statistics from a CSV file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input data.csv
  %(prog)s --input data.csv --columns age bmi score
  %(prog)s --input data.csv --output summary.csv --decimals 2
        """,
    )
    parser.add_argument(
        "--input", "-i", required=True, help="Path to the input CSV file."
    )
    parser.add_argument(
        "--columns",
        "-c",
        nargs="+",
        default=None,
        help="Columns to summarise (default: all numeric columns).",
    )
    parser.add_argument(
        "--output", "-o", default=None, help="Optional path to save results as CSV."
    )
    parser.add_argument(
        "--decimals",
        "-d",
        type=int,
        default=4,
        help="Decimal places for display (default: 4).",
    )
    parser.add_argument(
        "--separator",
        "--sep",
        default=",",
        help="CSV delimiter (default: comma).",
    )
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

    print(f"Loaded {len(df)} rows x {len(df.columns)} columns from {input_path}\n")

    # --- Select columns ------------------------------------------------------
    if args.columns:
        missing_cols = [c for c in args.columns if c not in df.columns]
        if missing_cols:
            print(
                f"Error: columns not found in data: {missing_cols}", file=sys.stderr
            )
            print(f"Available columns: {list(df.columns)}", file=sys.stderr)
            sys.exit(1)
        selected = args.columns
    else:
        selected = df.select_dtypes(include=[np.number]).columns.tolist()
        if not selected:
            print("Error: No numeric columns found in the data.", file=sys.stderr)
            sys.exit(1)

    # --- Compute statistics --------------------------------------------------
    results = {}
    for col in selected:
        if not np.issubdtype(df[col].dtype, np.number):
            print(f"Warning: Skipping non-numeric column '{col}'.", file=sys.stderr)
            continue
        results[col] = compute_summary(df[col])

    if not results:
        print("Error: No valid numeric columns to summarise.", file=sys.stderr)
        sys.exit(1)

    results_df = pd.DataFrame(results).T
    results_df.index.name = "Variable"

    # --- Display -------------------------------------------------------------
    display_df = results_df.copy()
    for col in display_df.columns:
        display_df[col] = display_df[col].apply(
            lambda v: format_value(v, args.decimals)
        )

    if HAS_TABULATE:
        print(
            tabulate(
                display_df,
                headers="keys",
                tablefmt="github",
                showindex=True,
            )
        )
    else:
        print(display_df.to_string())

    print(f"\n({len(results)} variable(s) summarised)")

    # --- Save ----------------------------------------------------------------
    if args.output:
        out_path = Path(args.output)
        results_df.to_csv(out_path)
        print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()

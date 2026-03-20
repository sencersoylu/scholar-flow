#!/usr/bin/env python3
"""
table1_generator.py — Generate a "Table 1" of baseline characteristics.

Compares groups on continuous and categorical variables, automatically
selecting the appropriate statistical test:
  - Continuous: t-test (normal + equal variance) or Mann-Whitney U
  - Categorical: Chi-square or Fisher's exact test (when expected counts < 5)

Continuous variables are reported as mean +/- SD (normal) or median [IQR]
(non-normal). Categorical variables are reported as n (%).

Dependencies:
    numpy, scipy, pandas

Example usage:
    python table1_generator.py --input patients.csv --group-column treatment \\
        --continuous age bmi --categorical sex smoking_status --output table1.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
from scipy import stats

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _is_normal(data: np.ndarray, alpha: float = 0.05) -> bool:
    """Return True if the Shapiro-Wilk test does not reject normality."""
    if len(data) < 3:
        return False
    if len(data) > 5000:
        data = data[:5000]
    _, p = stats.shapiro(data)
    return p >= alpha


def _format_mean_sd(series: pd.Series, decimals: int = 1) -> str:
    return f"{series.mean():.{decimals}f} +/- {series.std(ddof=1):.{decimals}f}"


def _format_median_iqr(series: pd.Series, decimals: int = 1) -> str:
    q1, med, q3 = np.nanpercentile(series.dropna(), [25, 50, 75])
    return f"{med:.{decimals}f} [{q1:.{decimals}f}-{q3:.{decimals}f}]"


def _format_n_pct(count: int, total: int, decimals: int = 1) -> str:
    pct = 100 * count / total if total > 0 else 0
    return f"{count} ({pct:.{decimals}f}%)"


# ---------------------------------------------------------------------------
# Row builders
# ---------------------------------------------------------------------------


def continuous_row(
    df: pd.DataFrame,
    var: str,
    group_col: str,
    groups: list,
    decimals: int = 1,
) -> dict:
    """Build a Table 1 row for a continuous variable."""
    row: dict = {"Variable": var}

    # Collect per-group data
    group_data = {}
    for g in groups:
        vals = df.loc[df[group_col] == g, var].dropna()
        group_data[g] = vals

    # Determine normality across groups
    all_normal = all(_is_normal(v.values) for v in group_data.values() if len(v) >= 3)

    # Format each group
    for g in groups:
        vals = group_data[g]
        if all_normal:
            row[str(g)] = _format_mean_sd(vals, decimals)
        else:
            row[str(g)] = _format_median_iqr(vals, decimals)

    # Overall
    overall = df[var].dropna()
    if all_normal:
        row["Overall"] = _format_mean_sd(overall, decimals)
    else:
        row["Overall"] = _format_median_iqr(overall, decimals)

    # Statistical test
    if len(groups) == 2:
        a, b = [group_data[g].values for g in groups]
        if len(a) < 3 or len(b) < 3:
            row["Test"] = "N/A"
            row["p-value"] = "N/A"
        elif all_normal:
            # Check equal variance
            _, lev_p = stats.levene(a, b)
            if lev_p >= 0.05:
                stat, p = stats.ttest_ind(a, b, equal_var=True)
                row["Test"] = "t-test"
            else:
                stat, p = stats.ttest_ind(a, b, equal_var=False)
                row["Test"] = "Welch's t-test"
            row["p-value"] = f"{p:.4f}"
        else:
            stat, p = stats.mannwhitneyu(a, b, alternative="two-sided")
            row["Test"] = "Mann-Whitney U"
            row["p-value"] = f"{p:.4f}"
    else:
        # >2 groups: Kruskal-Wallis or one-way ANOVA
        arrays = [group_data[g].values for g in groups if len(group_data[g]) >= 1]
        if all_normal:
            stat, p = stats.f_oneway(*arrays)
            row["Test"] = "One-way ANOVA"
        else:
            stat, p = stats.kruskal(*arrays)
            row["Test"] = "Kruskal-Wallis"
        row["p-value"] = f"{p:.4f}"

    row["Format"] = "mean +/- SD" if all_normal else "median [IQR]"
    return row


def categorical_row(
    df: pd.DataFrame,
    var: str,
    group_col: str,
    groups: list,
    decimals: int = 1,
) -> list[dict]:
    """Build Table 1 rows for a categorical variable (one header + one row per level)."""
    levels = sorted(df[var].dropna().unique())
    rows: list[dict] = []

    # Contingency table
    ct = pd.crosstab(df[var], df[group_col])

    # Choose test
    if ct.shape[0] == 2 and ct.shape[1] == 2 and (ct.values < 5).any():
        _, p_val = stats.fisher_exact(ct.values[:2, :2])
        test_name = "Fisher's exact"
    else:
        chi2, p_val, dof, expected = stats.chi2_contingency(ct)
        if (expected < 5).any():
            # Use Fisher's exact for 2x2, otherwise note low expected counts
            if ct.shape == (2, 2):
                _, p_val = stats.fisher_exact(ct.values)
                test_name = "Fisher's exact"
            else:
                test_name = "Chi-square*"  # asterisk = low expected counts
        else:
            test_name = "Chi-square"

    # Header row
    header: dict = {"Variable": f"{var}, n (%)", "Test": test_name, "p-value": f"{p_val:.4f}"}
    for g in groups:
        header[str(g)] = ""
    total_n = df[var].notna().sum()
    header["Overall"] = f"n = {total_n}"
    header["Format"] = "n (%)"
    rows.append(header)

    # Level rows
    for level in levels:
        r: dict = {"Variable": f"  {level}"}
        for g in groups:
            sub = df.loc[df[group_col] == g, var]
            count = (sub == level).sum()
            total = sub.notna().sum()
            r[str(g)] = _format_n_pct(count, total, decimals)
        count_all = (df[var] == level).sum()
        r["Overall"] = _format_n_pct(count_all, total_n, decimals)
        r["Test"] = ""
        r["p-value"] = ""
        r["Format"] = ""
        rows.append(r)

    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_table1(
    df: pd.DataFrame,
    group_col: str,
    continuous: Optional[List[str]] = None,
    categorical: Optional[List[str]] = None,
    decimals: int = 1,
) -> pd.DataFrame:
    """Build a complete Table 1 DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
    group_col : str
        Column that defines the comparison groups.
    continuous : list of str, optional
        Continuous variable column names.
    categorical : list of str, optional
        Categorical variable column names.
    decimals : int
        Decimal places for numeric display.

    Returns
    -------
    pd.DataFrame
        Table 1 with one row per variable / category level.
    """
    groups = sorted(df[group_col].dropna().unique())

    # Group sizes header
    all_rows: list[dict] = []
    size_row: dict = {"Variable": "N"}
    for g in groups:
        size_row[str(g)] = str((df[group_col] == g).sum())
    size_row["Overall"] = str(df[group_col].notna().sum())
    size_row["Test"] = ""
    size_row["p-value"] = ""
    size_row["Format"] = ""
    all_rows.append(size_row)

    # Continuous variables
    if continuous:
        for var in continuous:
            all_rows.append(continuous_row(df, var, group_col, groups, decimals))

    # Categorical variables
    if categorical:
        for var in categorical:
            all_rows.extend(categorical_row(df, var, group_col, groups, decimals))

    col_order = ["Variable"] + [str(g) for g in groups] + ["Overall", "Test", "p-value", "Format"]
    table = pd.DataFrame(all_rows)
    # Ensure column order; fill missing cols
    for c in col_order:
        if c not in table.columns:
            table[c] = ""
    return table[col_order]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a Table 1 (baseline characteristics) from a CSV.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input patients.csv --group-column treatment \\
      --continuous age bmi --categorical sex smoking
  %(prog)s --input data.csv --group-column arm \\
      --continuous age weight height --output table1.csv
        """,
    )
    parser.add_argument("--input", "-i", required=True, help="Path to CSV file.")
    parser.add_argument(
        "--group-column", "-g", required=True, help="Column defining comparison groups."
    )
    parser.add_argument("--continuous", nargs="+", default=None, help="Continuous variable names.")
    parser.add_argument(
        "--categorical", nargs="+", default=None, help="Categorical variable names."
    )
    parser.add_argument("--output", "-o", default=None, help="Save table to CSV.")
    parser.add_argument(
        "--decimals", "-d", type=int, default=1, help="Decimal places (default: 1)."
    )
    parser.add_argument("--separator", "--sep", default=",", help="CSV delimiter.")
    args = parser.parse_args()

    # --- Validate ------------------------------------------------------------
    if not args.continuous and not args.categorical:
        parser.error("Provide at least one of --continuous or --categorical.")

    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        df = pd.read_csv(input_path, sep=args.separator)
    except Exception as exc:
        print(f"Error reading CSV: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.group_column not in df.columns:
        print(f"Error: Group column '{args.group_column}' not found.", file=sys.stderr)
        sys.exit(1)

    # Validate column names
    all_vars = (args.continuous or []) + (args.categorical or [])
    missing = [v for v in all_vars if v not in df.columns]
    if missing:
        print(f"Error: Columns not found: {missing}", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(df)} rows from {input_path}")
    groups = sorted(df[args.group_column].dropna().unique())
    print(f"Group column: {args.group_column} -> groups: {groups}\n")

    # --- Build and display ---------------------------------------------------
    table = build_table1(
        df,
        args.group_column,
        continuous=args.continuous,
        categorical=args.categorical,
        decimals=args.decimals,
    )

    try:
        from tabulate import tabulate as _tabulate

        print(_tabulate(table, headers="keys", tablefmt="github", showindex=False))
    except ImportError:
        print(table.to_string(index=False))

    if args.output:
        table.to_csv(args.output, index=False)
        print(f"\nTable saved to {args.output}")


if __name__ == "__main__":
    main()

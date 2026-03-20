"""Dataset loader — read CSV, Excel, TSV into pandas and produce markdown summaries."""

from pathlib import Path

import pandas as pd


def load_dataset(file_path: str) -> pd.DataFrame:
    """Load a dataset from CSV, TSV, or Excel file.

    Args:
        file_path: Path to the data file.

    Returns:
        A pandas DataFrame.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file extension is unsupported.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    elif suffix in (".tsv", ".tab"):
        return pd.read_csv(path, sep="\t")
    elif suffix in (".xlsx", ".xls"):
        return pd.read_excel(path)
    else:
        raise ValueError(
            f"Unsupported file format: {suffix}. Supported: .csv, .tsv, .tab, .xlsx, .xls"
        )


def dataset_summary_markdown(df: pd.DataFrame, name: str = "Dataset") -> str:
    """Generate a markdown summary of a DataFrame.

    Includes shape, dtypes, first 5 rows, summary statistics, and missing value counts.
    """
    lines: list[str] = []

    # Shape
    lines.append(f"## {name}")
    lines.append(f"\n**Shape:** {df.shape[0]} rows x {df.shape[1]} columns\n")

    # Column types
    lines.append("### Column Types\n")
    lines.append("| Column | Type |")
    lines.append("|--------|------|")
    for col in df.columns:
        lines.append(f"| {col} | {df[col].dtype} |")

    # Head
    lines.append("\n### First 5 Rows\n")
    lines.append(df.head(5).to_markdown(index=False))

    # Summary statistics
    lines.append("\n### Summary Statistics\n")
    desc = df.describe(include="all")
    lines.append(desc.to_markdown())

    # Missing values
    missing = df.isnull().sum()
    if missing.sum() > 0:
        lines.append("\n### Missing Values\n")
        lines.append("| Column | Missing |")
        lines.append("|--------|---------|")
        for col in df.columns:
            if missing[col] > 0:
                lines.append(f"| {col} | {missing[col]} |")
    else:
        lines.append("\n### Missing Values\n")
        lines.append("No missing values detected.")

    return "\n".join(lines)


def describe_columns_markdown(
    df: pd.DataFrame, columns: list[str] | None = None
) -> str:
    """Generate detailed descriptive statistics for selected columns.

    For numeric columns: mean, std, min, max, quartiles, skewness, kurtosis.
    For categorical columns: value counts, mode, unique count.
    """
    if columns:
        missing = [c for c in columns if c not in df.columns]
        if missing:
            raise ValueError(f"Columns not found in dataset: {missing}")
        df = df[columns]

    lines: list[str] = []
    lines.append("## Detailed Descriptive Statistics\n")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

    if numeric_cols:
        lines.append("### Numeric Columns\n")
        lines.append(
            "| Column | Mean | Std | Min | 25% | 50% | 75% | Max | Skewness | Kurtosis |"
        )
        lines.append(
            "|--------|------|-----|-----|-----|-----|-----|-----|----------|----------|"
        )
        for col in numeric_cols:
            s = df[col].dropna()
            if len(s) == 0:
                lines.append(f"| {col} | — | — | — | — | — | — | — | — | — |")
                continue
            desc = s.describe()
            skew = s.skew()
            kurt = s.kurtosis()
            lines.append(
                f"| {col} "
                f"| {desc['mean']:.4g} "
                f"| {desc['std']:.4g} "
                f"| {desc['min']:.4g} "
                f"| {desc['25%']:.4g} "
                f"| {desc['50%']:.4g} "
                f"| {desc['75%']:.4g} "
                f"| {desc['max']:.4g} "
                f"| {skew:.4g} "
                f"| {kurt:.4g} |"
            )

    if categorical_cols:
        lines.append("\n### Categorical Columns\n")
        for col in categorical_cols:
            s = df[col].dropna()
            lines.append(f"#### {col}\n")
            lines.append(f"- **Unique values:** {s.nunique()}")
            lines.append(f"- **Mode:** {s.mode().iloc[0] if len(s) > 0 else '—'}")
            lines.append(f"- **Missing:** {df[col].isnull().sum()}\n")
            vc = s.value_counts().head(10)
            lines.append("| Value | Count |")
            lines.append("|-------|-------|")
            for val, count in vc.items():
                lines.append(f"| {val} | {count} |")
            if s.nunique() > 10:
                lines.append(f"\n*Showing top 10 of {s.nunique()} unique values.*")
            lines.append("")

    return "\n".join(lines)

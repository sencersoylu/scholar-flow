"""Python/R statistical analysis runtime MCP Server."""

import tempfile
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from statistics_mcp.executor import execute_python
from statistics_mcp.loader import (
    dataset_summary_markdown,
    describe_columns_markdown,
    load_dataset as _load_dataset,
)

mcp = FastMCP("statistics-mcp")

# Preamble injected before every user script to pre-import common libraries.
_PREAMBLE = """\
import numpy as np
import pandas as pd
import scipy
import scipy.stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.api as sm
"""


@mcp.tool()
async def run_python(script: str, timeout: int = 300) -> str:
    """Execute a Python script for statistical analysis.

    Common libraries are pre-imported: numpy (np), pandas (pd), scipy, matplotlib (plt),
    statsmodels (sm). Stdout and stderr are captured. Any generated files (e.g. plots)
    are reported.
    """
    full_script = _PREAMBLE + "\n" + script
    result = await execute_python(full_script, timeout=timeout)

    parts: list[str] = []
    if result.stdout.strip():
        parts.append("### Output\n```\n" + result.stdout.rstrip() + "\n```")
    if result.stderr.strip():
        parts.append("### Errors / Warnings\n```\n" + result.stderr.rstrip() + "\n```")
    if result.return_code != 0 and result.return_code != -1:
        parts.append(f"**Exit code:** {result.return_code}")
    if result.generated_files:
        parts.append("### Generated Files\n")
        for f in result.generated_files:
            parts.append(f"- `{f}`")

    if not parts:
        parts.append("Script executed successfully (no output).")

    return "\n\n".join(parts)


@mcp.tool()
async def load_dataset(file_path: str) -> str:
    """Load and inspect a dataset (CSV, Excel, TSV).

    Returns a markdown summary including shape, column types, first 5 rows,
    summary statistics, and missing value counts.
    """
    try:
        df = _load_dataset(file_path)
    except FileNotFoundError as e:
        return f"**Error:** {e}"
    except ValueError as e:
        return f"**Error:** {e}"
    except Exception as e:
        return f"**Error loading dataset:** {e}"

    name = Path(file_path).name
    return dataset_summary_markdown(df, name=name)


@mcp.tool()
async def generate_plot(script: str, output_path: str) -> str:
    """Generate a matplotlib plot by executing a Python script.

    The script should create matplotlib figures. The plot is saved to output_path.
    Common libraries are pre-imported (numpy, pandas, scipy, matplotlib, statsmodels).
    """
    # Ensure the output directory exists
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    # Append savefig call to guarantee the plot is written
    save_snippet = f"""
# --- auto-save ---
import matplotlib.pyplot as plt
plt.savefig({output_path!r}, dpi=150, bbox_inches="tight")
plt.close("all")
"""
    full_script = _PREAMBLE + "\n" + script + "\n" + save_snippet
    result = await execute_python(full_script, timeout=120)

    if result.return_code != 0:
        msg = f"**Plot generation failed.**\n\n```\n{result.stderr.rstrip()}\n```"
        if result.stdout.strip():
            msg += f"\n\n```\n{result.stdout.rstrip()}\n```"
        return msg

    if out.exists():
        return f"Plot saved successfully to `{output_path}` ({out.stat().st_size:,} bytes)."
    else:
        return (
            f"**Warning:** Script completed but output file was not created at `{output_path}`.\n\n"
            f"Stdout:\n```\n{result.stdout.rstrip()}\n```\n\n"
            f"Stderr:\n```\n{result.stderr.rstrip()}\n```"
        )


@mcp.tool()
async def describe_dataset(file_path: str, columns: list[str] | None = None) -> str:
    """Generate detailed descriptive statistics for a dataset.

    For numeric columns: mean, std, min, max, quartiles, skewness, kurtosis.
    For categorical columns: value counts, mode, unique count.
    Optionally filter to specific columns.
    """
    try:
        df = _load_dataset(file_path)
    except FileNotFoundError as e:
        return f"**Error:** {e}"
    except ValueError as e:
        return f"**Error:** {e}"
    except Exception as e:
        return f"**Error loading dataset:** {e}"

    try:
        return describe_columns_markdown(df, columns=columns)
    except ValueError as e:
        return f"**Error:** {e}"


if __name__ == "__main__":
    mcp.run()

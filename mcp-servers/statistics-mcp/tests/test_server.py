"""Tests for Statistics MCP Server."""

import csv
import tempfile
from pathlib import Path

import pytest

from statistics_mcp.server import (
    describe_dataset,
    generate_plot,
    load_dataset,
    mcp,
    run_python,
)


# --- Fixtures ---


@pytest.fixture
def sample_csv(tmp_path) -> str:
    """Create a sample CSV file for testing."""
    path = tmp_path / "sample.csv"
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "age", "score", "grade"])
        writer.writerow(["Alice", 25, 88.5, "A"])
        writer.writerow(["Bob", 30, 72.0, "B"])
        writer.writerow(["Charlie", 35, 95.2, "A"])
        writer.writerow(["Diana", 28, 64.8, "C"])
        writer.writerow(["Eve", 22, 91.0, "A"])
    return str(path)


@pytest.fixture
def sample_csv_with_missing(tmp_path) -> str:
    """Create a CSV with missing values."""
    path = tmp_path / "missing.csv"
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["x", "y", "label"])
        writer.writerow([1, 10, "a"])
        writer.writerow([2, "", "b"])
        writer.writerow(["", 30, ""])
        writer.writerow([4, 40, "a"])
    return str(path)


@pytest.fixture
def sample_tsv(tmp_path) -> str:
    """Create a sample TSV file."""
    path = tmp_path / "data.tsv"
    with open(path, "w") as f:
        f.write("col1\tcol2\n")
        f.write("1\ta\n")
        f.write("2\tb\n")
    return str(path)


# --- Server metadata ---


def test_server_name():
    assert mcp.name == "statistics-mcp"


def test_tools_registered():
    assert len(mcp._tool_manager._tools) >= 4


# --- run_python ---


@pytest.mark.asyncio
async def test_run_python_simple():
    result = await run_python("print('hello from mcp')")
    assert "hello from mcp" in result


@pytest.mark.asyncio
async def test_run_python_math():
    result = await run_python("import numpy as np; print(np.mean([1,2,3,4,5]))")
    assert "3.0" in result


@pytest.mark.asyncio
async def test_run_python_pre_imports():
    """Verify that pre-imported libraries are available."""
    result = await run_python("print(type(np).__name__); print(type(pd).__name__)")
    assert "module" in result


@pytest.mark.asyncio
async def test_run_python_syntax_error():
    result = await run_python("def foo(")
    assert "Error" in result or "SyntaxError" in result


@pytest.mark.asyncio
async def test_run_python_timeout():
    result = await run_python("import time; time.sleep(10)", timeout=1)
    assert "timed out" in result.lower()


@pytest.mark.asyncio
async def test_run_python_no_output():
    result = await run_python("x = 42")
    assert "successfully" in result.lower() or "no output" in result.lower()


# --- load_dataset ---


@pytest.mark.asyncio
async def test_load_dataset_csv(sample_csv):
    result = await load_dataset(sample_csv)
    assert "5 rows" in result
    assert "4 columns" in result
    assert "name" in result
    assert "age" in result


@pytest.mark.asyncio
async def test_load_dataset_tsv(sample_tsv):
    result = await load_dataset(sample_tsv)
    assert "2 rows" in result
    assert "col1" in result


@pytest.mark.asyncio
async def test_load_dataset_file_not_found():
    result = await load_dataset("/nonexistent/path/data.csv")
    assert "Error" in result


@pytest.mark.asyncio
async def test_load_dataset_unsupported_format(tmp_path):
    path = tmp_path / "data.xyz"
    path.write_text("hello")
    result = await load_dataset(str(path))
    assert "Error" in result
    assert "Unsupported" in result


@pytest.mark.asyncio
async def test_load_dataset_missing_values(sample_csv_with_missing):
    result = await load_dataset(sample_csv_with_missing)
    assert "Missing" in result


# --- generate_plot ---


@pytest.mark.asyncio
async def test_generate_plot(tmp_path):
    output_path = str(tmp_path / "test_plot.png")
    script = """\
plt.figure()
plt.plot([1, 2, 3], [4, 5, 6])
plt.title("Test Plot")
"""
    result = await generate_plot(script, output_path)
    assert "success" in result.lower() or "saved" in result.lower()
    assert Path(output_path).exists()


@pytest.mark.asyncio
async def test_generate_plot_error(tmp_path):
    output_path = str(tmp_path / "bad_plot.png")
    script = "raise ValueError('bad script')"
    result = await generate_plot(script, output_path)
    assert "failed" in result.lower() or "Error" in result or "ValueError" in result


# --- describe_dataset ---


@pytest.mark.asyncio
async def test_describe_dataset(sample_csv):
    result = await describe_dataset(sample_csv)
    assert "Numeric" in result
    assert "Categorical" in result
    assert "age" in result
    assert "Skewness" in result
    assert "Kurtosis" in result


@pytest.mark.asyncio
async def test_describe_dataset_specific_columns(sample_csv):
    result = await describe_dataset(sample_csv, columns=["age", "score"])
    assert "age" in result
    assert "score" in result
    # Should not include categorical section since we only picked numeric cols
    assert "grade" not in result


@pytest.mark.asyncio
async def test_describe_dataset_invalid_column(sample_csv):
    result = await describe_dataset(sample_csv, columns=["nonexistent"])
    assert "Error" in result


@pytest.mark.asyncio
async def test_describe_dataset_file_not_found():
    result = await describe_dataset("/nonexistent/path.csv")
    assert "Error" in result

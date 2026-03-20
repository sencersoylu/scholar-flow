"""Comprehensive tests for the three descriptive-statistics scripts.

Covers:
  - skills/statistics/descriptive-statistics/scripts/summary_stats.py
  - skills/statistics/descriptive-statistics/scripts/normality_test.py
  - skills/statistics/descriptive-statistics/scripts/table1_generator.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats

# ---------------------------------------------------------------------------
# Resolve script locations so imports work regardless of PYTHONPATH
# ---------------------------------------------------------------------------
SCRIPTS_DIR = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "statistics"
    / "descriptive-statistics"
    / "scripts"
)

sys.path.insert(0, str(SCRIPTS_DIR))

import normality_test as nt  # noqa: E402
import summary_stats as ss  # noqa: E402
import table1_generator as t1  # noqa: E402


# ===================================================================
# summary_stats.py — unit tests
# ===================================================================


class TestComputeSummary:
    """Tests for summary_stats.compute_summary()."""

    def test_known_values(self):
        """Verify statistics against hand-computed values for [1,2,3,4,5]."""
        s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        result = ss.compute_summary(s)
        assert result["N"] == 5
        assert result["Missing"] == 0
        assert result["Mean"] == pytest.approx(3.0)
        assert result["Median"] == pytest.approx(3.0)
        assert result["Min"] == pytest.approx(1.0)
        assert result["Max"] == pytest.approx(5.0)
        assert result["SD"] == pytest.approx(np.std([1, 2, 3, 4, 5], ddof=1))
        assert result["Q1"] == pytest.approx(2.0)
        assert result["Q3"] == pytest.approx(4.0)
        assert result["IQR"] == pytest.approx(2.0)

    def test_single_value(self):
        """A single-element series should return NaN for SD, skewness, kurtosis."""
        s = pd.Series([42.0])
        result = ss.compute_summary(s)
        assert result["N"] == 1
        assert result["Mean"] == pytest.approx(42.0)
        assert result["Median"] == pytest.approx(42.0)
        # std with ddof=1 on single value is NaN
        assert np.isnan(result["SD"])

    def test_all_nan(self):
        """An entirely NaN series should return N=0 and NaN for all stats."""
        s = pd.Series([np.nan, np.nan, np.nan])
        result = ss.compute_summary(s)
        assert result["N"] == 0
        assert result["Missing"] == 3
        assert np.isnan(result["Mean"])
        assert np.isnan(result["Median"])

    def test_with_missing_values(self):
        """Missing values should be dropped; Missing count should be correct."""
        s = pd.Series([1.0, np.nan, 3.0, np.nan, 5.0])
        result = ss.compute_summary(s)
        assert result["N"] == 3
        assert result["Missing"] == 2
        assert result["Mean"] == pytest.approx(3.0)

    def test_skewness_symmetric(self):
        """A symmetric distribution should have skewness close to 0."""
        s = pd.Series([-2.0, -1.0, 0.0, 1.0, 2.0])
        result = ss.compute_summary(s)
        assert result["Skewness"] == pytest.approx(0.0, abs=1e-10)

    def test_mode_returns_most_frequent(self):
        """Mode should return the most frequently occurring value."""
        s = pd.Series([1.0, 2.0, 2.0, 3.0, 3.0, 3.0])
        result = ss.compute_summary(s)
        assert result["Mode"] == pytest.approx(3.0)


class TestFormatValue:
    """Tests for summary_stats.format_value()."""

    def test_integer(self):
        """Integers should be formatted without decimals."""
        assert ss.format_value(5) == "5"

    def test_nan(self):
        """NaN should display as 'N/A'."""
        assert ss.format_value(np.nan) == "N/A"

    @pytest.mark.parametrize(
        "val,decimals,expected",
        [
            (3.14159, 2, "3.14"),
            (3.14159, 4, "3.1416"),
            (0.001, 3, "0.001"),
        ],
    )
    def test_float_rounding(self, val, decimals, expected):
        """Floats should be rounded to the requested decimal places."""
        assert ss.format_value(val, decimals) == expected


class TestSummaryStatsCLI:
    """Test the summary_stats CLI via subprocess."""

    def test_basic_run(self, normal_csv):
        """CLI should run without errors and print a table for a valid CSV."""
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "summary_stats.py"), "--input", str(normal_csv)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Mean" in result.stdout or "mean" in result.stdout.lower()

    def test_specific_columns(self, normal_csv):
        """CLI should only summarise the requested columns."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "summary_stats.py"),
                "--input",
                str(normal_csv),
                "--columns",
                "age",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "1 variable(s) summarised" in result.stdout

    def test_missing_file(self, tmp_path):
        """CLI should exit with error when the file does not exist."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "summary_stats.py"),
                "--input",
                str(tmp_path / "nofile.csv"),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

    def test_output_csv(self, normal_csv, tmp_path):
        """CLI --output should produce a valid CSV file."""
        out = tmp_path / "result.csv"
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "summary_stats.py"),
                "--input",
                str(normal_csv),
                "--output",
                str(out),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert out.exists()
        df = pd.read_csv(out, index_col=0)
        assert "Mean" in df.columns


# ===================================================================
# normality_test.py — unit tests
# ===================================================================


class TestShapiroWilk:
    """Tests for normality_test.shapiro_wilk()."""

    def test_normal_data_not_rejected(self):
        """Normally distributed data should not be rejected at alpha=0.05."""
        rng = np.random.default_rng(0)
        data = rng.normal(0, 1, 200)
        result = nt.shapiro_wilk(data, alpha=0.05)
        assert result["Result"] == "Normal"
        assert 0 < result["p-value"] <= 1

    def test_uniform_data_rejected(self):
        """Clearly non-normal (uniform) data should be rejected."""
        rng = np.random.default_rng(1)
        data = rng.uniform(0, 1, 500)
        result = nt.shapiro_wilk(data, alpha=0.05)
        assert result["Result"] == "Non-normal"

    def test_insufficient_data(self):
        """Fewer than 3 observations should return 'Insufficient data'."""
        data = np.array([1.0, 2.0])
        result = nt.shapiro_wilk(data, alpha=0.05)
        assert "Insufficient" in result["Result"]
        assert np.isnan(result["Statistic"])


class TestKSTest:
    """Tests for normality_test.ks_test()."""

    def test_normal_data(self):
        """Normal data should generally not be rejected by KS test."""
        rng = np.random.default_rng(10)
        data = rng.normal(50, 10, 300)
        result = nt.ks_test(data, alpha=0.05)
        assert result["Test"] == "Kolmogorov-Smirnov"
        assert isinstance(result["Statistic"], float)

    def test_zero_variance(self):
        """Constant data (zero variance) should return 'Zero variance'."""
        data = np.array([5.0] * 20)
        result = nt.ks_test(data, alpha=0.05)
        assert result["Result"] == "Zero variance"


class TestDAgostinoPearson:
    """Tests for normality_test.dagostino_pearson()."""

    def test_insufficient_data(self):
        """Fewer than 20 observations should return 'Insufficient data'."""
        data = np.arange(10, dtype=float)
        result = nt.dagostino_pearson(data, alpha=0.05)
        assert "Insufficient" in result["Result"]

    def test_normal_data(self):
        """Normal data (n>=20) should pass the test."""
        rng = np.random.default_rng(3)
        data = rng.normal(0, 1, 100)
        result = nt.dagostino_pearson(data, alpha=0.05)
        assert result["Result"] == "Normal"
        assert result["p-value"] > 0.05

    def test_highly_skewed_rejected(self):
        """Highly skewed data should be rejected."""
        rng = np.random.default_rng(5)
        data = rng.exponential(1, 200)
        result = nt.dagostino_pearson(data, alpha=0.05)
        assert result["Result"] == "Non-normal"


class TestNormalityCLI:
    """Test the normality_test CLI via subprocess."""

    def test_basic_run(self, normal_csv):
        """CLI should run successfully and print test results."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "normality_test.py"),
                "--input",
                str(normal_csv),
                "--column",
                "age",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Shapiro-Wilk" in result.stdout
        assert "Kolmogorov-Smirnov" in result.stdout

    def test_missing_column(self, normal_csv):
        """CLI should error when the column does not exist."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "normality_test.py"),
                "--input",
                str(normal_csv),
                "--column",
                "nonexistent",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

    def test_custom_alpha(self, normal_csv):
        """CLI should accept a custom alpha value."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "normality_test.py"),
                "--input",
                str(normal_csv),
                "--column",
                "age",
                "--alpha",
                "0.01",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "0.01" in result.stdout

    def test_qq_plot_creation(self, normal_csv, tmp_path):
        """CLI --plot should create a Q-Q plot image file."""
        plot_path = tmp_path / "qq.png"
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "normality_test.py"),
                "--input",
                str(normal_csv),
                "--column",
                "age",
                "--plot",
                str(plot_path),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert plot_path.exists()
        assert plot_path.stat().st_size > 0


# ===================================================================
# table1_generator.py — unit tests
# ===================================================================


class TestHelpers:
    """Tests for table1_generator helper functions."""

    def test_is_normal_with_normal_data(self):
        """_is_normal should return True for normally distributed data."""
        rng = np.random.default_rng(42)
        data = rng.normal(0, 1, 200)
        assert bool(t1._is_normal(data)) is True

    def test_is_normal_with_skewed_data(self):
        """_is_normal should return False for clearly non-normal data."""
        rng = np.random.default_rng(42)
        data = rng.exponential(1, 200)
        assert bool(t1._is_normal(data)) is False

    def test_is_normal_insufficient_data(self):
        """_is_normal should return False when n < 3."""
        assert bool(t1._is_normal(np.array([1.0, 2.0]))) is False

    def test_format_mean_sd(self):
        """_format_mean_sd should produce 'mean +/- SD' string."""
        s = pd.Series([10.0, 20.0, 30.0])
        result = t1._format_mean_sd(s, decimals=1)
        assert "+/-" in result
        assert "20.0" in result  # mean

    def test_format_median_iqr(self):
        """_format_median_iqr should produce 'median [Q1-Q3]' string."""
        s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        result = t1._format_median_iqr(s, decimals=1)
        assert "[" in result and "]" in result
        assert "3.0" in result  # median

    @pytest.mark.parametrize(
        "count,total,expected_pct",
        [
            (25, 100, "25.0%"),
            (0, 50, "0.0%"),
            (50, 50, "100.0%"),
        ],
    )
    def test_format_n_pct(self, count, total, expected_pct):
        """_format_n_pct should produce 'n (pct%)' string."""
        result = t1._format_n_pct(count, total, decimals=1)
        assert str(count) in result
        assert expected_pct in result


class TestBuildTable1:
    """Tests for table1_generator.build_table1()."""

    def _make_df(self):
        """Create a simple test DataFrame."""
        rng = np.random.default_rng(42)
        n = 100
        return pd.DataFrame(
            {
                "group": rng.choice(["A", "B"], n),
                "age": rng.normal(50, 10, n),
                "bmi": rng.normal(25, 4, n),
                "sex": rng.choice(["M", "F"], n),
            }
        )

    def test_continuous_only(self):
        """Table 1 with only continuous variables should have correct structure."""
        df = self._make_df()
        table = t1.build_table1(df, "group", continuous=["age", "bmi"])
        assert "Variable" in table.columns
        assert "p-value" in table.columns
        assert "Test" in table.columns
        # First row is N, then age, then bmi
        assert table.iloc[0]["Variable"] == "N"
        assert table.iloc[1]["Variable"] == "age"
        assert table.iloc[2]["Variable"] == "bmi"

    def test_categorical_only(self):
        """Table 1 with only categorical variables should produce level rows."""
        df = self._make_df()
        table = t1.build_table1(df, "group", categorical=["sex"])
        # Should have N row + header row for sex + level rows for F, M
        vars_col = table["Variable"].tolist()
        assert "N" in vars_col
        assert any("sex" in v for v in vars_col)

    def test_both_types(self):
        """Table 1 with both continuous and categorical variables."""
        df = self._make_df()
        table = t1.build_table1(df, "group", continuous=["age"], categorical=["sex"])
        vars_col = table["Variable"].tolist()
        assert "age" in vars_col
        assert any("sex" in v for v in vars_col)

    def test_group_sizes_in_first_row(self):
        """The first row should show group sizes and overall N."""
        df = self._make_df()
        table = t1.build_table1(df, "group", continuous=["age"])
        n_row = table.iloc[0]
        assert n_row["Variable"] == "N"
        total = int(n_row["A"]) + int(n_row["B"])
        assert total == len(df)

    def test_pvalue_is_numeric_string(self):
        """p-values for continuous rows should be parseable as floats."""
        df = self._make_df()
        table = t1.build_table1(df, "group", continuous=["age"])
        p_str = table.iloc[1]["p-value"]
        p_val = float(p_str)
        assert 0 <= p_val <= 1

    def test_three_groups(self):
        """Table 1 should work with more than 2 groups."""
        rng = np.random.default_rng(42)
        n = 150
        df = pd.DataFrame(
            {
                "group": rng.choice(["A", "B", "C"], n),
                "score": rng.normal(100, 15, n),
            }
        )
        table = t1.build_table1(df, "group", continuous=["score"])
        # Should have columns for all 3 groups
        assert "A" in table.columns
        assert "B" in table.columns
        assert "C" in table.columns


class TestTable1CLI:
    """Test the table1_generator CLI via subprocess."""

    def test_basic_run(self, mixed_csv):
        """CLI should run successfully with continuous and categorical vars."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "table1_generator.py"),
                "--input",
                str(mixed_csv),
                "--group-column",
                "group",
                "--continuous",
                "age",
                "score",
                "--categorical",
                "smoking",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "age" in result.stdout

    def test_output_csv(self, mixed_csv, tmp_path):
        """CLI --output should save the table to a CSV."""
        out = tmp_path / "table1.csv"
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "table1_generator.py"),
                "--input",
                str(mixed_csv),
                "--group-column",
                "group",
                "--continuous",
                "age",
                "--output",
                str(out),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert out.exists()
        df = pd.read_csv(out)
        assert "Variable" in df.columns

    def test_missing_group_column(self, mixed_csv):
        """CLI should error when group column is absent from the data."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "table1_generator.py"),
                "--input",
                str(mixed_csv),
                "--group-column",
                "nonexistent",
                "--continuous",
                "age",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

    def test_no_variables_error(self, mixed_csv):
        """CLI should error when neither --continuous nor --categorical is given."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "table1_generator.py"),
                "--input",
                str(mixed_csv),
                "--group-column",
                "group",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

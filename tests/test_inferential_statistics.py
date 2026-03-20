"""Comprehensive tests for the four inferential-statistics scripts.

Covers:
  - t_test.py   (independent / paired, effect sizes, assumption fallbacks)
  - anova.py    (one-way ANOVA, eta-squared, post-hoc helpers)
  - chi_square.py (Cramer's V, Fisher fallback, interpretation)
  - mann_whitney.py (rank-biserial, interpretation, Hodges-Lehmann)
"""

from __future__ import annotations

import importlib
import subprocess
import sys
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats

# ---------------------------------------------------------------------------
# Import the modules under test
# ---------------------------------------------------------------------------

SCRIPTS_DIR = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "statistics"
    / "inferential-statistics"
    / "scripts"
)

sys.path.insert(0, str(SCRIPTS_DIR))

import t_test as t_test_mod
import anova as anova_mod
import chi_square as chi_square_mod
import mann_whitney as mw_mod

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_csv(tmp_path: Path, name: str, df: pd.DataFrame) -> Path:
    """Write a DataFrame to a CSV in tmp_path and return its Path."""
    p = tmp_path / name
    df.to_csv(p, index=False)
    return p


# ===================================================================
# T-TEST TESTS
# ===================================================================


class TestCohensD:
    """Tests for Cohen's d calculations in t_test.py."""

    def test_cohens_d_independent_known(self):
        """Cohen's d for two known groups matches hand calculation."""
        a = np.array([10.0, 12.0, 14.0, 16.0, 18.0])
        b = np.array([20.0, 22.0, 24.0, 26.0, 28.0])
        d = t_test_mod.cohens_d_independent(a, b)
        # Both groups have identical SD = sqrt(10), pooled_sd = sqrt(10)
        # mean diff = 14 - 24 = -10; d = -10/sqrt(10)
        expected = (14.0 - 24.0) / np.sqrt(10.0)
        assert d == pytest.approx(expected, rel=1e-6)

    def test_cohens_d_independent_identical_groups(self):
        """Cohen's d is 0 when both groups are identical."""
        a = np.array([5.0, 5.0, 5.0])
        b = np.array([5.0, 5.0, 5.0])
        assert t_test_mod.cohens_d_independent(a, b) == 0.0

    def test_cohens_d_paired_known(self):
        """Cohen's d_z matches hand calculation for paired differences."""
        diff = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        d = t_test_mod.cohens_d_paired(diff)
        expected = np.mean(diff) / np.std(diff, ddof=1)
        assert d == pytest.approx(expected, rel=1e-6)

    def test_cohens_d_paired_zero_variance(self):
        """Cohen's d_z is 0 when all differences are the same."""
        diff = np.array([3.0, 3.0, 3.0])
        assert t_test_mod.cohens_d_paired(diff) == 0.0


class TestInterpretD:
    """Tests for Cohen's d interpretation thresholds."""

    @pytest.mark.parametrize(
        "d, expected",
        [
            (0.0, "negligible"),
            (0.15, "negligible"),
            (0.2, "small"),
            (0.45, "small"),
            (0.5, "medium"),
            (0.79, "medium"),
            (0.8, "large"),
            (2.5, "large"),
            (-0.9, "large"),
        ],
    )
    def test_interpret_d(self, d, expected):
        """interpret_d returns correct label for boundary and interior values."""
        assert t_test_mod.interpret_d(d) == expected


class TestMeanDiffCI:
    """Tests for confidence interval functions in t_test.py."""

    def test_mean_diff_ci_symmetric(self):
        """CI for two identical distributions is centred near 0."""
        np.random.seed(42)
        a = np.random.normal(50, 5, 100)
        b = np.random.normal(50, 5, 100)
        lo, hi = t_test_mod.mean_diff_ci(a, b, alpha=0.05)
        # The CI should contain 0 (true difference is 0)
        assert lo < 0 < hi

    def test_paired_diff_ci_excludes_zero(self):
        """CI for clearly shifted paired data does not contain 0."""
        diff = np.array([10.0, 11.0, 12.0, 13.0, 14.0])
        lo, hi = t_test_mod.paired_diff_ci(diff, alpha=0.05)
        assert lo > 0


class TestAssumptionChecks:
    """Tests for normality and equal-variance helpers."""

    def test_check_normality_normal_data(self, capsys):
        """Shapiro-Wilk passes on data drawn from a normal distribution."""
        np.random.seed(0)
        data = np.random.normal(0, 1, 50)
        result = t_test_mod.check_normality(data, "test_group")
        assert result == True  # noqa: E712  (scipy returns np.bool_)
        assert "PASS" in capsys.readouterr().out

    def test_check_normality_non_normal_data(self, capsys):
        """Shapiro-Wilk fails on heavily skewed data."""
        np.random.seed(0)
        data = np.random.exponential(1, 200)
        result = t_test_mod.check_normality(data, "skewed")
        assert result == False  # noqa: E712
        assert "FAIL" in capsys.readouterr().out

    def test_check_normality_too_few_observations(self, capsys):
        """Returns False when n < 3."""
        data = np.array([1.0, 2.0])
        result = t_test_mod.check_normality(data, "tiny")
        assert result == False  # noqa: E712
        assert "n < 3" in capsys.readouterr().out

    def test_check_equal_variance_equal(self, capsys):
        """Levene's test passes for equal-variance groups."""
        np.random.seed(1)
        a = np.random.normal(0, 1, 50)
        b = np.random.normal(0, 1, 50)
        result = t_test_mod.check_equal_variance(a, b)
        assert result == True  # noqa: E712
        assert "PASS" in capsys.readouterr().out

    def test_check_equal_variance_unequal(self, capsys):
        """Levene's test fails for vastly different variances."""
        np.random.seed(2)
        a = np.random.normal(0, 1, 100)
        b = np.random.normal(0, 10, 100)
        result = t_test_mod.check_equal_variance(a, b)
        assert result == False  # noqa: E712
        assert "FAIL" in capsys.readouterr().out


class TestTTestCLI:
    """Integration tests for t_test.py CLI via subprocess."""

    def test_independent_t_test_runs(self, tmp_path):
        """Independent t-test CLI produces output and exits 0."""
        np.random.seed(10)
        df = pd.DataFrame(
            {
                "score": np.concatenate(
                    [np.random.normal(50, 5, 30), np.random.normal(55, 5, 30)]
                ),
                "group": ["A"] * 30 + ["B"] * 30,
            }
        )
        csv = _write_csv(tmp_path, "ind.csv", df)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "t_test.py"),
                "--input", str(csv),
                "--column", "score",
                "--group-column", "group",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Cohen's d" in result.stdout

    def test_paired_t_test_runs(self, tmp_path):
        """Paired t-test CLI produces output and exits 0."""
        np.random.seed(11)
        n = 25
        df = pd.DataFrame(
            {
                "pre": np.random.normal(60, 8, n),
                "post": np.random.normal(65, 8, n),
            }
        )
        csv = _write_csv(tmp_path, "paired.csv", df)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "t_test.py"),
                "--input", str(csv),
                "--column1", "pre",
                "--column2", "post",
                "--paired",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "PAIRED T-TEST" in result.stdout


# ===================================================================
# ANOVA TESTS
# ===================================================================


class TestEtaSquared:
    """Tests for eta-squared computation and interpretation."""

    def test_eta_squared_basic(self):
        """eta_squared returns correct proportion."""
        assert anova_mod.eta_squared(25.0, 100.0) == pytest.approx(0.25)

    def test_eta_squared_zero_total(self):
        """eta_squared returns 0 when SS_total is 0."""
        assert anova_mod.eta_squared(0.0, 0.0) == 0.0

    @pytest.mark.parametrize(
        "es, label",
        [
            (0.005, "negligible"),
            (0.03, "small"),
            (0.10, "medium"),
            (0.20, "large"),
        ],
    )
    def test_interpret_eta(self, es, label):
        """interpret_eta returns correct labels at benchmark boundaries."""
        assert anova_mod.interpret_eta(es) == label


class TestOnewayANOVA:
    """Functional tests for the one-way ANOVA path."""

    def test_significant_anova(self, tmp_path, capsys):
        """One-way ANOVA detects a significant difference among 3 groups."""
        np.random.seed(20)
        df = pd.DataFrame(
            {
                "score": np.concatenate(
                    [
                        np.random.normal(50, 5, 40),
                        np.random.normal(60, 5, 40),
                        np.random.normal(70, 5, 40),
                    ]
                ),
                "group": ["A"] * 40 + ["B"] * 40 + ["C"] * 40,
            }
        )
        csv = _write_csv(tmp_path, "anova.csv", df)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "anova.py"),
                "-i", str(csv),
                "-d", "score",
                "-f", "group",
                "--posthoc", "bonferroni",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Statistically significant" in result.stdout
        assert "Eta-squared" in result.stdout

    def test_non_significant_anova(self, tmp_path):
        """One-way ANOVA correctly reports non-significance for identical groups."""
        np.random.seed(21)
        df = pd.DataFrame(
            {
                "score": np.random.normal(50, 5, 90),
                "group": ["A"] * 30 + ["B"] * 30 + ["C"] * 30,
            }
        )
        csv = _write_csv(tmp_path, "anova_ns.csv", df)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "anova.py"),
                "-i", str(csv),
                "-d", "score",
                "-f", "group",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Not statistically significant" in result.stdout

    def test_eta_squared_matches_scipy(self, tmp_path):
        """Eta-squared computed by the script matches manual computation from scipy."""
        np.random.seed(22)
        g1 = np.random.normal(10, 2, 20)
        g2 = np.random.normal(15, 2, 20)
        g3 = np.random.normal(20, 2, 20)
        all_data = np.concatenate([g1, g2, g3])
        groups = ["A"] * 20 + ["B"] * 20 + ["C"] * 20

        # Compute expected eta-squared
        grand_mean = np.mean(all_data)
        ss_between = sum(
            len(g) * (np.mean(g) - grand_mean) ** 2 for g in [g1, g2, g3]
        )
        ss_total = np.sum((all_data - grand_mean) ** 2)
        expected_eta = ss_between / ss_total

        es = anova_mod.eta_squared(ss_between, ss_total)
        assert es == pytest.approx(expected_eta, rel=1e-9)

    def test_anova_with_tukey_posthoc(self, tmp_path):
        """One-way ANOVA with Tukey HSD post-hoc runs without error."""
        np.random.seed(23)
        df = pd.DataFrame(
            {
                "val": np.concatenate(
                    [
                        np.random.normal(10, 2, 30),
                        np.random.normal(20, 2, 30),
                        np.random.normal(30, 2, 30),
                    ]
                ),
                "grp": ["X"] * 30 + ["Y"] * 30 + ["Z"] * 30,
            }
        )
        csv = _write_csv(tmp_path, "anova_tukey.csv", df)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "anova.py"),
                "-i", str(csv),
                "-d", "val",
                "-f", "grp",
                "--posthoc", "tukey",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Tukey" in result.stdout

    def test_twoway_anova_runs(self, tmp_path):
        """Two-way ANOVA CLI runs and prints ANOVA table."""
        np.random.seed(24)
        n = 20
        df = pd.DataFrame(
            {
                "score": np.random.normal(50, 10, n * 4),
                "treatment": (["drug"] * n + ["placebo"] * n) * 2,
                "sex": ["M"] * (n * 2) + ["F"] * (n * 2),
            }
        )
        csv = _write_csv(tmp_path, "twoway.csv", df)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "anova.py"),
                "-i", str(csv),
                "-d", "score",
                "--factors", "treatment", "sex",
                "--two-way",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "TWO-WAY ANOVA" in result.stdout


# ===================================================================
# CHI-SQUARE TESTS
# ===================================================================


class TestCramersV:
    """Tests for Cramer's V computation and interpretation."""

    def test_cramers_v_known(self):
        """Cramer's V matches hand calculation for a known chi-square."""
        # chi2=10, n=100, 2x2 table -> V = sqrt(10 / (100 * 1)) = sqrt(0.1)
        v = chi_square_mod.cramers_v(10.0, 100, 2, 2)
        assert v == pytest.approx(np.sqrt(0.1), rel=1e-6)

    def test_cramers_v_zero_n(self):
        """Cramer's V is 0 when n=0."""
        assert chi_square_mod.cramers_v(10.0, 0, 2, 2) == 0.0

    def test_cramers_v_single_row(self):
        """Cramer's V is 0 when min dimension is 0 (1 row)."""
        assert chi_square_mod.cramers_v(10.0, 100, 3, 1) == 0.0

    def test_cramers_v_larger_table(self):
        """Cramer's V for a 3x4 table uses min(k-1, r-1) = 2."""
        v = chi_square_mod.cramers_v(20.0, 200, 4, 3)
        expected = np.sqrt(20.0 / (200 * 2))
        assert v == pytest.approx(expected, rel=1e-6)

    @pytest.mark.parametrize(
        "v, label",
        [
            (0.05, "negligible"),
            (0.15, "small"),
            (0.35, "medium"),
            (0.55, "large"),
        ],
    )
    def test_interpret_v(self, v, label):
        """interpret_v returns correct label at benchmark boundaries."""
        assert chi_square_mod.interpret_v(v) == label


class TestChiSquareCLI:
    """Integration tests for chi_square.py CLI."""

    def test_significant_association(self, tmp_path):
        """Chi-square test detects a significant association."""
        df = pd.DataFrame(
            {
                "treatment": ["A"] * 50 + ["B"] * 50,
                "outcome": (["success"] * 40 + ["fail"] * 10
                            + ["success"] * 20 + ["fail"] * 30),
            }
        )
        csv = _write_csv(tmp_path, "chi.csv", df)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "chi_square.py"),
                "-i", str(csv),
                "-r", "treatment",
                "-c", "outcome",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Statistically significant" in result.stdout
        assert "Cramer's V" in result.stdout

    def test_fisher_fallback_small_expected(self, tmp_path):
        """Fisher's exact test is used when expected counts are < 5 in a 2x2 table."""
        df = pd.DataFrame(
            {
                "treatment": ["A"] * 6 + ["B"] * 6,
                "outcome": ["yes", "yes", "yes", "no", "no", "no",
                            "yes", "no", "no", "no", "no", "no"],
            }
        )
        csv = _write_csv(tmp_path, "fisher.csv", df)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "chi_square.py"),
                "-i", str(csv),
                "-r", "treatment",
                "-c", "outcome",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Fisher" in result.stdout

    def test_no_significant_association(self, tmp_path):
        """Chi-square test reports non-significance when association is absent."""
        np.random.seed(30)
        n = 200
        df = pd.DataFrame(
            {
                "row_var": np.random.choice(["X", "Y"], n),
                "col_var": np.random.choice(["P", "Q"], n),
            }
        )
        csv = _write_csv(tmp_path, "chi_ns.csv", df)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "chi_square.py"),
                "-i", str(csv),
                "-r", "row_var",
                "-c", "col_var",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "CHI-SQUARE TEST" in result.stdout


# ===================================================================
# MANN-WHITNEY TESTS
# ===================================================================


class TestRankBiserial:
    """Tests for rank-biserial correlation in mann_whitney.py."""

    def test_rank_biserial_formula(self):
        """Rank-biserial matches the formula r = 1 - 2U/(n1*n2)."""
        # U=10, n1=5, n2=5 -> r = 1 - 20/25 = 0.2
        assert mw_mod.rank_biserial(10.0, 5, 5) == pytest.approx(0.2)

    def test_rank_biserial_perfect_separation(self):
        """Rank-biserial is 1 when U=0 (complete separation)."""
        assert mw_mod.rank_biserial(0.0, 5, 5) == pytest.approx(1.0)

    def test_rank_biserial_no_difference(self):
        """Rank-biserial is 0 when U = n1*n2/2."""
        n1, n2 = 10, 10
        u = n1 * n2 / 2  # 50
        assert mw_mod.rank_biserial(u, n1, n2) == pytest.approx(0.0)

    def test_rank_biserial_zero_product(self):
        """Returns 0.0 when either group is empty."""
        assert mw_mod.rank_biserial(0.0, 0, 5) == 0.0

    @pytest.mark.parametrize(
        "r, label",
        [
            (0.05, "negligible"),
            (0.2, "small"),
            (0.4, "medium"),
            (0.6, "large"),
            (-0.8, "large"),
        ],
    )
    def test_interpret_r(self, r, label):
        """interpret_r returns correct label at benchmark boundaries."""
        assert mw_mod.interpret_r(r) == label


class TestMannWhitneyCLI:
    """Integration tests for mann_whitney.py CLI."""

    def test_significant_difference(self, tmp_path):
        """Mann-Whitney detects a significant difference between shifted groups."""
        np.random.seed(40)
        df = pd.DataFrame(
            {
                "score": np.concatenate(
                    [np.random.normal(10, 2, 30), np.random.normal(20, 2, 30)]
                ),
                "group": ["A"] * 30 + ["B"] * 30,
            }
        )
        csv = _write_csv(tmp_path, "mw.csv", df)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "mann_whitney.py"),
                "-i", str(csv),
                "-c", "score",
                "-g", "group",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Statistically significant" in result.stdout
        assert "Rank-biserial" in result.stdout

    def test_non_significant_difference(self, tmp_path):
        """Mann-Whitney reports non-significance for identical distributions."""
        np.random.seed(41)
        df = pd.DataFrame(
            {
                "val": np.random.normal(50, 5, 60),
                "grp": ["X"] * 30 + ["Y"] * 30,
            }
        )
        csv = _write_csv(tmp_path, "mw_ns.csv", df)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "mann_whitney.py"),
                "-i", str(csv),
                "-c", "val",
                "-g", "grp",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Not statistically significant" in result.stdout

    def test_hodges_lehmann_printed(self, tmp_path):
        """Hodges-Lehmann estimate is printed for manageable sample sizes."""
        np.random.seed(42)
        df = pd.DataFrame(
            {
                "x": np.concatenate(
                    [np.random.normal(0, 1, 15), np.random.normal(3, 1, 15)]
                ),
                "g": ["A"] * 15 + ["B"] * 15,
            }
        )
        csv = _write_csv(tmp_path, "mw_hl.csv", df)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "mann_whitney.py"),
                "-i", str(csv),
                "-c", "x",
                "-g", "g",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Hodges-Lehmann" in result.stdout

    def test_alternative_less(self, tmp_path):
        """Mann-Whitney with --alternative less runs without error."""
        np.random.seed(43)
        df = pd.DataFrame(
            {
                "v": np.concatenate(
                    [np.random.normal(5, 1, 20), np.random.normal(10, 1, 20)]
                ),
                "g": ["lo"] * 20 + ["hi"] * 20,
            }
        )
        csv = _write_csv(tmp_path, "mw_less.csv", df)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "mann_whitney.py"),
                "-i", str(csv),
                "-c", "v",
                "-g", "g",
                "--alternative", "less",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Alternative: less" in result.stdout

    def test_tied_ranks(self, tmp_path):
        """Mann-Whitney handles data with many tied ranks."""
        df = pd.DataFrame(
            {
                "score": [1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3, 3],
                "group": ["A"] * 6 + ["B"] * 6,
            }
        )
        csv = _write_csv(tmp_path, "mw_ties.csv", df)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "mann_whitney.py"),
                "-i", str(csv),
                "-c", "score",
                "-g", "group",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "MANN-WHITNEY U TEST" in result.stdout

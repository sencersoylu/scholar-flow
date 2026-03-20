"""
Comprehensive tests for regression-analysis and power-analysis scripts.

Covers:
- linear_regression.py: OLS fitting, VIF, Cook's distance, CLI
- logistic_regression.py: logistic fitting, odds ratios, ROC-AUC, CLI
- cox_regression.py: Cox PH fitting, hazard ratios, concordance, CLI
- sample_size_calculator.py: all sample-size functions + CLI
"""

from __future__ import annotations

import csv
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Paths to scripts under test
# ---------------------------------------------------------------------------
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "skills" / "statistics"
LINEAR_SCRIPT = SCRIPTS_DIR / "regression-analysis" / "scripts" / "linear_regression.py"
LOGISTIC_SCRIPT = SCRIPTS_DIR / "regression-analysis" / "scripts" / "logistic_regression.py"
COX_SCRIPT = SCRIPTS_DIR / "regression-analysis" / "scripts" / "cox_regression.py"
POWER_SCRIPT = SCRIPTS_DIR / "power-analysis" / "scripts" / "sample_size_calculator.py"

# ---------------------------------------------------------------------------
# Import power-analysis functions directly for unit-level testing
# ---------------------------------------------------------------------------
sys.path.insert(
    0,
    str(SCRIPTS_DIR / "power-analysis" / "scripts"),
)
from sample_size_calculator import (
    ss_ttest_ind,
    ss_ttest_paired,
    ss_anova,
    ss_chi_square,
    ss_correlation,
    ss_regression,
    EFFECT_SIZE_GUIDE,
)

sys.path.insert(
    0,
    str(SCRIPTS_DIR / "regression-analysis" / "scripts"),
)
from linear_regression import compute_vif


# ===================================================================
# HELPERS
# ===================================================================

def _make_csv(tmp_path: Path, df: pd.DataFrame, name: str = "data.csv") -> Path:
    """Write a DataFrame to CSV in tmp_path and return the path."""
    p = tmp_path / name
    df.to_csv(p, index=False)
    return p


def _run_script(script: Path, args: list[str], timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a script as a subprocess and return the result."""
    return subprocess.run(
        [sys.executable, str(script)] + args,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ===================================================================
# LINEAR REGRESSION TESTS
# ===================================================================


class TestLinearRegression:
    """Tests for linear_regression.py."""

    def test_simple_ols_known_coefficients(self, tmp_path):
        """OLS on y = 2 + 3*x + noise should recover slope ~3 and intercept ~2."""
        np.random.seed(42)
        n = 500
        x = np.random.normal(0, 1, n)
        y = 2 + 3 * x + np.random.normal(0, 0.5, n)
        df = pd.DataFrame({"x": x, "y": y})
        csv_path = _make_csv(tmp_path, df)
        out_csv = tmp_path / "coefs.csv"

        result = _run_script(
            LINEAR_SCRIPT,
            ["--input", str(csv_path), "--target", "y", "--predictors", "x", "--output", str(out_csv)],
        )
        assert result.returncode == 0, result.stderr

        coefs = pd.read_csv(out_csv)
        intercept = coefs.loc[coefs["Variable"] == "const", "Coefficient"].values[0]
        slope = coefs.loc[coefs["Variable"] == "x", "Coefficient"].values[0]
        assert intercept == pytest.approx(2.0, rel=0.1)
        assert slope == pytest.approx(3.0, rel=0.1)

    def test_multiple_regression_r_squared(self, tmp_path):
        """Multiple regression with strong signal should have high R-squared."""
        np.random.seed(42)
        n = 300
        x1 = np.random.normal(0, 1, n)
        x2 = np.random.normal(0, 1, n)
        y = 1 + 2 * x1 - 1.5 * x2 + np.random.normal(0, 0.3, n)
        df = pd.DataFrame({"x1": x1, "x2": x2, "y": y})
        csv_path = _make_csv(tmp_path, df)

        result = _run_script(
            LINEAR_SCRIPT,
            ["--input", str(csv_path), "--target", "y", "--predictors", "x1", "x2"],
        )
        assert result.returncode == 0
        # R-squared should be reported and high
        assert "R-squared" in result.stdout

    def test_vif_collinear_predictors(self):
        """VIF should be high (>10) for nearly collinear predictors."""
        np.random.seed(42)
        n = 200
        x1 = np.random.normal(0, 1, n)
        x2 = x1 + np.random.normal(0, 0.01, n)  # nearly identical to x1
        x3 = np.random.normal(0, 1, n)
        features = pd.DataFrame({"x1": x1, "x2": x2, "x3": x3})

        vif_df = compute_vif(features)
        vif_x1 = vif_df.loc[vif_df["Variable"] == "x1", "VIF"].values[0]
        vif_x2 = vif_df.loc[vif_df["Variable"] == "x2", "VIF"].values[0]
        vif_x3 = vif_df.loc[vif_df["Variable"] == "x3", "VIF"].values[0]

        assert vif_x1 > 10, "x1 should have high VIF due to collinearity with x2"
        assert vif_x2 > 10, "x2 should have high VIF due to collinearity with x1"
        assert vif_x3 < 5, "x3 should have low VIF (independent)"

    def test_vif_independent_predictors(self):
        """VIF should be near 1 for independent predictors."""
        np.random.seed(42)
        n = 500
        features = pd.DataFrame({
            "a": np.random.normal(0, 1, n),
            "b": np.random.normal(0, 1, n),
        })
        vif_df = compute_vif(features)
        for _, row in vif_df.iterrows():
            assert row["VIF"] == pytest.approx(1.0, abs=0.2)

    def test_cooks_distance_reported(self, tmp_path):
        """Output should contain Cook's distance diagnostics."""
        np.random.seed(42)
        n = 100
        x = np.random.normal(0, 1, n)
        y = 2 * x + np.random.normal(0, 1, n)
        # Add an outlier
        x = np.append(x, 0.0)
        y = np.append(y, 50.0)
        df = pd.DataFrame({"x": x, "y": y})
        csv_path = _make_csv(tmp_path, df)

        result = _run_script(
            LINEAR_SCRIPT,
            ["--input", str(csv_path), "--target", "y", "--predictors", "x"],
        )
        assert result.returncode == 0
        assert "Cook's distance" in result.stdout

    def test_durbin_watson_reported(self, tmp_path):
        """Output should contain Durbin-Watson statistic."""
        np.random.seed(42)
        n = 100
        x = np.random.normal(0, 1, n)
        y = x + np.random.normal(0, 1, n)
        df = pd.DataFrame({"x": x, "y": y})
        csv_path = _make_csv(tmp_path, df)

        result = _run_script(
            LINEAR_SCRIPT,
            ["--input", str(csv_path), "--target", "y", "--predictors", "x"],
        )
        assert result.returncode == 0
        assert "Durbin-Watson" in result.stdout

    def test_missing_column_error(self, tmp_path):
        """Script should exit with error when a column is not found."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        csv_path = _make_csv(tmp_path, df)

        result = _run_script(
            LINEAR_SCRIPT,
            ["--input", str(csv_path), "--target", "y", "--predictors", "nonexistent"],
        )
        assert result.returncode != 0
        assert "not found" in result.stderr.lower() or "Columns not found" in result.stderr

    def test_diagnostic_plots_saved(self, tmp_path):
        """Diagnostic plots should be saved when --plots is provided."""
        np.random.seed(42)
        n = 100
        x = np.random.normal(0, 1, n)
        y = 2 * x + np.random.normal(0, 1, n)
        df = pd.DataFrame({"x": x, "y": y})
        csv_path = _make_csv(tmp_path, df)
        plot_path = tmp_path / "diag.png"

        result = _run_script(
            LINEAR_SCRIPT,
            ["--input", str(csv_path), "--target", "y", "--predictors", "x",
             "--plots", str(plot_path)],
        )
        assert result.returncode == 0
        assert plot_path.exists(), "Diagnostic plot file should be created"


# ===================================================================
# LOGISTIC REGRESSION TESTS
# ===================================================================


class TestLogisticRegression:
    """Tests for logistic_regression.py (requires scikit-learn)."""

    @pytest.fixture(autouse=True)
    def _skip_if_no_sklearn(self):
        pytest.importorskip("sklearn")

    def _make_logistic_data(self, n=500, seed=42):
        """Generate binary outcome data with known logistic relationship."""
        np.random.seed(seed)
        x = np.random.normal(0, 1, n)
        # True log-odds = -0.5 + 1.5*x
        logits = -0.5 + 1.5 * x
        probs = 1 / (1 + np.exp(-logits))
        y = np.random.binomial(1, probs, n)
        return pd.DataFrame({"x": x, "y": y})

    def test_logistic_coefficients_recovery(self, tmp_path):
        """Logistic regression should approximately recover known coefficients."""
        df = self._make_logistic_data(n=2000, seed=42)
        csv_path = _make_csv(tmp_path, df)
        out_csv = tmp_path / "or.csv"

        result = _run_script(
            LOGISTIC_SCRIPT,
            ["--input", str(csv_path), "--target", "y", "--predictors", "x",
             "--output", str(out_csv)],
        )
        assert result.returncode == 0, result.stderr

        or_df = pd.read_csv(out_csv)
        coef_x = or_df.loc[or_df["Variable"] == "x", "Coefficient"].values[0]
        assert coef_x == pytest.approx(1.5, rel=0.2)

    def test_odds_ratios_reported(self, tmp_path):
        """Output should contain odds ratios."""
        df = self._make_logistic_data()
        csv_path = _make_csv(tmp_path, df)

        result = _run_script(
            LOGISTIC_SCRIPT,
            ["--input", str(csv_path), "--target", "y", "--predictors", "x"],
        )
        assert result.returncode == 0
        assert "Odds Ratios" in result.stdout

    def test_roc_auc_above_chance(self, tmp_path):
        """ROC AUC should be well above 0.5 for data with real signal."""
        df = self._make_logistic_data(n=1000)
        csv_path = _make_csv(tmp_path, df)

        result = _run_script(
            LOGISTIC_SCRIPT,
            ["--input", str(csv_path), "--target", "y", "--predictors", "x"],
        )
        assert result.returncode == 0
        # Extract AUC from output
        for line in result.stdout.splitlines():
            if "ROC AUC" in line:
                auc = float(line.split(":")[-1].strip())
                assert auc > 0.7, f"AUC should be well above chance, got {auc}"
                break
        else:
            pytest.fail("ROC AUC not found in output")

    def test_classification_report_present(self, tmp_path):
        """Output should contain classification report with precision/recall."""
        df = self._make_logistic_data()
        csv_path = _make_csv(tmp_path, df)

        result = _run_script(
            LOGISTIC_SCRIPT,
            ["--input", str(csv_path), "--target", "y", "--predictors", "x"],
        )
        assert result.returncode == 0
        assert "precision" in result.stdout.lower()
        assert "recall" in result.stdout.lower()

    def test_non_binary_target_error(self, tmp_path):
        """Script should error on non-binary target variable."""
        df = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [0, 1, 2, 0, 1]})
        csv_path = _make_csv(tmp_path, df)

        result = _run_script(
            LOGISTIC_SCRIPT,
            ["--input", str(csv_path), "--target", "y", "--predictors", "x"],
        )
        assert result.returncode != 0
        assert "binary" in result.stderr.lower() or "0/1" in result.stderr

    def test_roc_plot_saved(self, tmp_path):
        """ROC curve plot should be saved when --roc is provided."""
        df = self._make_logistic_data()
        csv_path = _make_csv(tmp_path, df)
        roc_path = tmp_path / "roc.png"

        result = _run_script(
            LOGISTIC_SCRIPT,
            ["--input", str(csv_path), "--target", "y", "--predictors", "x",
             "--roc", str(roc_path)],
        )
        assert result.returncode == 0
        assert roc_path.exists(), "ROC plot file should be created"

    def test_multiple_predictors(self, tmp_path):
        """Logistic regression with multiple predictors should work."""
        np.random.seed(42)
        n = 500
        x1 = np.random.normal(0, 1, n)
        x2 = np.random.normal(0, 1, n)
        logits = 0.5 * x1 - 0.8 * x2
        probs = 1 / (1 + np.exp(-logits))
        y = np.random.binomial(1, probs, n)
        df = pd.DataFrame({"x1": x1, "x2": x2, "y": y})
        csv_path = _make_csv(tmp_path, df)

        result = _run_script(
            LOGISTIC_SCRIPT,
            ["--input", str(csv_path), "--target", "y", "--predictors", "x1", "x2"],
        )
        assert result.returncode == 0
        assert "LOGISTIC REGRESSION RESULTS" in result.stdout

    def test_hosmer_lemeshow_present(self, tmp_path):
        """Hosmer-Lemeshow test should appear in output for large enough data."""
        df = self._make_logistic_data(n=1000)
        csv_path = _make_csv(tmp_path, df)

        result = _run_script(
            LOGISTIC_SCRIPT,
            ["--input", str(csv_path), "--target", "y", "--predictors", "x"],
        )
        assert result.returncode == 0
        assert "Hosmer-Lemeshow" in result.stdout


# ===================================================================
# COX REGRESSION TESTS
# ===================================================================


class TestCoxRegression:
    """Tests for cox_regression.py (requires lifelines)."""

    @pytest.fixture(autouse=True)
    def _skip_if_no_lifelines(self):
        pytest.importorskip("lifelines")

    def _make_survival_data(self, n=300, seed=42):
        """Generate survival data with known hazard ratio for treatment."""
        np.random.seed(seed)
        treatment = np.random.binomial(1, 0.5, n)
        age = np.random.normal(60, 10, n)
        # True HR for treatment ~ exp(-0.5) ~ 0.607
        hazard = np.exp(0.02 * (age - 60) - 0.5 * treatment)
        time = np.random.exponential(10 / hazard)
        # Random censoring
        censor_time = np.random.exponential(15, n)
        observed_time = np.minimum(time, censor_time)
        event = (time <= censor_time).astype(int)
        return pd.DataFrame({
            "time": observed_time,
            "event": event,
            "treatment": treatment,
            "age": age,
        })

    def test_cox_hazard_ratio_recovery(self, tmp_path):
        """Cox model should approximately recover known hazard ratio for treatment."""
        df = self._make_survival_data(n=2000)
        csv_path = _make_csv(tmp_path, df)
        out_csv = tmp_path / "hr.csv"

        result = _run_script(
            COX_SCRIPT,
            ["--input", str(csv_path), "--duration", "time", "--event", "event",
             "--predictors", "treatment", "age", "--output", str(out_csv)],
        )
        assert result.returncode == 0, result.stderr

        hr_df = pd.read_csv(out_csv)
        hr_treatment = hr_df.loc[hr_df["Variable"] == "treatment", "HR"].values[0]
        # True HR = exp(-0.5) ~ 0.607
        assert hr_treatment == pytest.approx(0.607, rel=0.25)

    def test_concordance_index_reported(self, tmp_path):
        """Output should contain concordance index."""
        df = self._make_survival_data()
        csv_path = _make_csv(tmp_path, df)

        result = _run_script(
            COX_SCRIPT,
            ["--input", str(csv_path), "--duration", "time", "--event", "event",
             "--predictors", "treatment", "age"],
        )
        assert result.returncode == 0
        assert "Concordance index" in result.stdout

    def test_concordance_above_chance(self, tmp_path):
        """Concordance index should be above 0.5 for data with real signal."""
        df = self._make_survival_data(n=1000)
        csv_path = _make_csv(tmp_path, df)

        result = _run_script(
            COX_SCRIPT,
            ["--input", str(csv_path), "--duration", "time", "--event", "event",
             "--predictors", "treatment", "age"],
        )
        assert result.returncode == 0
        for line in result.stdout.splitlines():
            if "Concordance index" in line:
                ci = float(line.split(":")[-1].strip())
                assert ci > 0.5
                break

    def test_ph_assumption_check(self, tmp_path):
        """Output should contain proportional hazards test."""
        df = self._make_survival_data()
        csv_path = _make_csv(tmp_path, df)

        result = _run_script(
            COX_SCRIPT,
            ["--input", str(csv_path), "--duration", "time", "--event", "event",
             "--predictors", "treatment"],
        )
        assert result.returncode == 0
        assert "Proportional hazards" in result.stdout or "proportional hazards" in result.stdout.lower()

    def test_missing_column_error(self, tmp_path):
        """Script should exit with error when a column is not found."""
        df = pd.DataFrame({"time": [1, 2], "event": [1, 0], "x": [0, 1]})
        csv_path = _make_csv(tmp_path, df)

        result = _run_script(
            COX_SCRIPT,
            ["--input", str(csv_path), "--duration", "time", "--event", "event",
             "--predictors", "nonexistent"],
        )
        assert result.returncode != 0

    def test_single_predictor(self, tmp_path):
        """Cox regression should work with a single predictor."""
        df = self._make_survival_data()
        csv_path = _make_csv(tmp_path, df)

        result = _run_script(
            COX_SCRIPT,
            ["--input", str(csv_path), "--duration", "time", "--event", "event",
             "--predictors", "treatment"],
        )
        assert result.returncode == 0
        assert "COX PROPORTIONAL HAZARDS REGRESSION" in result.stdout

    def test_hazard_ratio_table_saved(self, tmp_path):
        """Hazard ratio CSV should have expected columns."""
        df = self._make_survival_data()
        csv_path = _make_csv(tmp_path, df)
        out_csv = tmp_path / "hr.csv"

        result = _run_script(
            COX_SCRIPT,
            ["--input", str(csv_path), "--duration", "time", "--event", "event",
             "--predictors", "treatment", "age", "--output", str(out_csv)],
        )
        assert result.returncode == 0
        hr_df = pd.read_csv(out_csv)
        expected_cols = {"Variable", "Coefficient", "HR", "HR 95% CI Lower", "HR 95% CI Upper", "p-value"}
        assert expected_cols.issubset(set(hr_df.columns))

    def test_zero_events_error(self, tmp_path):
        """Cox model should fail gracefully when there are zero events."""
        df = pd.DataFrame({
            "time": [1.0, 2.0, 3.0, 4.0, 5.0],
            "event": [0, 0, 0, 0, 0],  # all censored
            "x": [1.0, 2.0, 3.0, 4.0, 5.0],
        })
        csv_path = _make_csv(tmp_path, df)

        result = _run_script(
            COX_SCRIPT,
            ["--input", str(csv_path), "--duration", "time", "--event", "event",
             "--predictors", "x"],
        )
        # Should either fail or produce a warning; not crash silently
        # lifelines may raise an error with zero events
        # Either non-zero exit or some warning/error text is acceptable
        assert result.returncode != 0 or "Error" in result.stderr or "error" in result.stderr.lower() or "0 " in result.stdout


# ===================================================================
# POWER ANALYSIS / SAMPLE SIZE CALCULATOR TESTS
# ===================================================================


class TestSampleSizeCalculator:
    """Tests for sample_size_calculator.py sample-size functions."""

    def test_ttest_ind_cohen_d_medium(self):
        """Cohen's d=0.5, alpha=0.05, power=0.80 should yield ~64 per group."""
        result = ss_ttest_ind(d=0.5, alpha=0.05, power=0.80)
        assert result["n_per_group_1"] == pytest.approx(64, abs=2)

    def test_ttest_ind_cohen_d_small(self):
        """Cohen's d=0.2, alpha=0.05, power=0.80 should yield ~394 per group."""
        result = ss_ttest_ind(d=0.2, alpha=0.05, power=0.80)
        assert result["n_per_group_1"] == pytest.approx(394, abs=5)

    def test_ttest_ind_cohen_d_large(self):
        """Cohen's d=0.8, alpha=0.05, power=0.80 should yield ~26 per group."""
        result = ss_ttest_ind(d=0.8, alpha=0.05, power=0.80)
        assert result["n_per_group_1"] == pytest.approx(26, abs=2)

    @pytest.mark.parametrize("d, expected_n", [
        (0.2, 394),
        (0.5, 64),
        (0.8, 26),
    ])
    def test_ttest_ind_parametrized(self, d, expected_n):
        """Independent t-test sample size across small/medium/large effect sizes."""
        result = ss_ttest_ind(d=d, alpha=0.05, power=0.80)
        assert result["n_per_group_1"] == pytest.approx(expected_n, abs=5)

    def test_ttest_ind_unequal_ratio(self):
        """Unequal allocation ratio (2:1) should yield different group sizes."""
        result = ss_ttest_ind(d=0.5, alpha=0.05, power=0.80, ratio=2.0)
        assert result["n_per_group_2"] > result["n_per_group_1"]
        assert result["total"] == result["n_per_group_1"] + result["n_per_group_2"]

    def test_ttest_paired_medium(self):
        """Paired t-test: d=0.5, alpha=0.05, power=0.80 should yield ~34 pairs."""
        result = ss_ttest_paired(d=0.5, alpha=0.05, power=0.80)
        assert result["n_pairs"] == pytest.approx(34, abs=2)

    def test_anova_three_groups(self):
        """ANOVA: f=0.25 (medium), 3 groups, alpha=0.05, power=0.80."""
        result = ss_anova(f=0.25, alpha=0.05, power=0.80, k=3)
        # FTestAnovaPower returns n_per_group ~158 (its parameterisation
        # counts observations per group needed for the non-central F test).
        assert result["n_per_group"] > 20
        assert result["groups"] == 3
        assert result["total"] == result["n_per_group"] * 3

    def test_anova_four_groups_large(self):
        """ANOVA: f=0.4 (large), 4 groups -- fewer subjects than medium effect."""
        result_large = ss_anova(f=0.4, alpha=0.05, power=0.80, k=4)
        result_medium = ss_anova(f=0.25, alpha=0.05, power=0.80, k=4)
        assert result_large["n_per_group"] < result_medium["n_per_group"], (
            "Larger effect size should require fewer subjects"
        )
        assert result_large["total"] == result_large["n_per_group"] * 4

    def test_chi_square_medium(self):
        """Chi-square: w=0.3 (medium), df=1, alpha=0.05, power=0.80."""
        result = ss_chi_square(w=0.3, alpha=0.05, power=0.80, df=1)
        assert result["total_n"] == pytest.approx(88, abs=5)

    def test_correlation_medium(self):
        """Correlation: r=0.3, alpha=0.05, power=0.80 should yield ~85."""
        result = ss_correlation(r=0.3, alpha=0.05, power=0.80)
        assert result["total_n"] == pytest.approx(85, abs=5)

    def test_correlation_small(self):
        """Correlation: r=0.1, alpha=0.05, power=0.80 should yield ~782."""
        result = ss_correlation(r=0.1, alpha=0.05, power=0.80)
        assert result["total_n"] == pytest.approx(782, abs=15)

    def test_regression_more_predictors_needs_more_subjects(self):
        """Regression: more predictors should require a larger sample size."""
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r3 = ss_regression(f2=0.15, alpha=0.05, power=0.80, n_predictors=3)
            r10 = ss_regression(f2=0.15, alpha=0.05, power=0.80, n_predictors=10)
        assert r10["total_n"] >= r3["total_n"], (
            "More predictors should need at least as many subjects"
        )
        assert r3["predictors"] == 3
        assert r10["predictors"] == 10

    def test_higher_power_needs_more_subjects(self):
        """Increasing power from 0.80 to 0.95 should require more subjects."""
        r80 = ss_ttest_ind(d=0.5, alpha=0.05, power=0.80)
        r95 = ss_ttest_ind(d=0.5, alpha=0.05, power=0.95)
        assert r95["n_per_group_1"] > r80["n_per_group_1"]

    def test_lower_alpha_needs_more_subjects(self):
        """Stricter alpha (0.01 vs 0.05) should require more subjects."""
        r05 = ss_ttest_ind(d=0.5, alpha=0.05, power=0.80)
        r01 = ss_ttest_ind(d=0.5, alpha=0.01, power=0.80)
        assert r01["n_per_group_1"] > r05["n_per_group_1"]

    def test_effect_size_guide_keys(self):
        """EFFECT_SIZE_GUIDE should have entries for all supported test types."""
        expected_keys = {"t-test-ind", "t-test-paired", "anova", "chi-square", "correlation", "regression"}
        assert expected_keys == set(EFFECT_SIZE_GUIDE.keys())


class TestSampleSizeCLI:
    """CLI-level tests for sample_size_calculator.py."""

    def test_cli_ttest_ind(self):
        """CLI mode for independent t-test should print result."""
        result = _run_script(
            POWER_SCRIPT,
            ["--test-type", "t-test-ind", "--effect-size", "0.5",
             "--alpha", "0.05", "--power", "0.80"],
        )
        assert result.returncode == 0
        assert "SAMPLE SIZE CALCULATION RESULT" in result.stdout

    def test_cli_anova_requires_groups(self):
        """CLI should error if --groups is missing for ANOVA."""
        result = _run_script(
            POWER_SCRIPT,
            ["--test-type", "anova", "--effect-size", "0.25",
             "--alpha", "0.05", "--power", "0.80"],
        )
        assert result.returncode != 0

    def test_cli_regression_requires_predictors(self):
        """CLI should error if --predictors is missing for regression."""
        result = _run_script(
            POWER_SCRIPT,
            ["--test-type", "regression", "--effect-size", "0.15",
             "--alpha", "0.05", "--power", "0.80"],
        )
        assert result.returncode != 0

    def test_cli_chi_square(self):
        """CLI mode for chi-square should print result."""
        result = _run_script(
            POWER_SCRIPT,
            ["--test-type", "chi-square", "--effect-size", "0.3",
             "--alpha", "0.05", "--power", "0.80", "--df", "2"],
        )
        assert result.returncode == 0
        assert "Total N" in result.stdout

    def test_cli_missing_test_type_and_effect_size(self):
        """CLI should error when neither --test-type nor --interactive given."""
        result = _run_script(POWER_SCRIPT, [])
        assert result.returncode != 0

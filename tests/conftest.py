"""Shared fixtures for descriptive-statistics tests."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def normal_csv(tmp_path):
    """CSV with a normally distributed column (n=200), plus a group column."""
    rng = np.random.default_rng(42)
    n = 200
    df = pd.DataFrame(
        {
            "age": rng.normal(50, 10, n),
            "bmi": rng.normal(25, 4, n),
            "group": rng.choice(["A", "B"], n),
            "sex": rng.choice(["M", "F"], n),
        }
    )
    path = tmp_path / "normal.csv"
    df.to_csv(path, index=False)
    return path


@pytest.fixture
def skewed_csv(tmp_path):
    """CSV with a right-skewed column."""
    rng = np.random.default_rng(7)
    n = 150
    df = pd.DataFrame(
        {
            "income": rng.lognormal(10, 1, n),
            "group": rng.choice(["ctrl", "treat"], n),
        }
    )
    path = tmp_path / "skewed.csv"
    df.to_csv(path, index=False)
    return path


@pytest.fixture
def small_csv(tmp_path):
    """CSV with only 5 rows for edge-case testing."""
    df = pd.DataFrame({"val": [1.0, 2.0, 3.0, 4.0, 5.0], "group": ["A", "B", "A", "B", "A"]})
    path = tmp_path / "small.csv"
    df.to_csv(path, index=False)
    return path


@pytest.fixture
def all_nan_csv(tmp_path):
    """CSV where the target column is entirely NaN."""
    df = pd.DataFrame({"x": [np.nan, np.nan, np.nan], "group": ["A", "B", "A"]})
    path = tmp_path / "allnan.csv"
    df.to_csv(path, index=False)
    return path


@pytest.fixture
def constant_csv(tmp_path):
    """CSV where the target column has zero variance."""
    df = pd.DataFrame({"val": [7.0] * 30, "group": ["A"] * 15 + ["B"] * 15})
    path = tmp_path / "constant.csv"
    df.to_csv(path, index=False)
    return path


@pytest.fixture
def mixed_csv(tmp_path):
    """CSV with numeric and non-numeric columns, some missing values."""
    rng = np.random.default_rng(99)
    n = 100
    age = rng.normal(45, 12, n).tolist()
    # inject some NaNs
    age[5] = np.nan
    age[20] = np.nan
    age[50] = np.nan
    df = pd.DataFrame(
        {
            "age": age,
            "name": [f"person_{i}" for i in range(n)],
            "score": rng.integers(0, 100, n).astype(float),
            "group": rng.choice(["treatment", "control"], n),
            "smoking": rng.choice(["yes", "no"], n),
        }
    )
    path = tmp_path / "mixed.csv"
    df.to_csv(path, index=False)
    return path

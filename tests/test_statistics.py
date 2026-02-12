"""Tests for statistical testing module."""

import os
import sys
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.statistics import (
    z_test, cohens_h, interpret_effect_size,
    power_analysis, bayesian_ab_test, bonferroni_correction,
)


class TestZTest:
    def test_returns_dict(self):
        df = pd.DataFrame({
            "group": ["control"] * 1000 + ["treatment"] * 1000,
            "converted": [1]*120 + [0]*880 + [1]*130 + [0]*870,
        })
        result = z_test(df)
        assert isinstance(result, dict)
        assert "z_statistic" in result
        assert "p_value" in result
        assert "ci_95_lower" in result

    def test_identical_groups(self):
        df = pd.DataFrame({
            "group": ["control"] * 500 + ["treatment"] * 500,
            "converted": [1]*60 + [0]*440 + [1]*60 + [0]*440,
        })
        result = z_test(df)
        assert abs(result["absolute_diff"]) < 0.01
        assert result["p_value"] > 0.5


class TestCohensH:
    def test_identical_proportions(self):
        assert cohens_h(0.5, 0.5) == 0.0

    def test_positive_when_p1_greater(self):
        assert cohens_h(0.6, 0.4) > 0

    def test_negligible_effect(self):
        assert interpret_effect_size(0.05) == "Negligible"

    def test_large_effect(self):
        assert interpret_effect_size(0.9) == "Large"


class TestPowerAnalysis:
    def test_required_sample_size(self):
        result = power_analysis(baseline_rate=0.12, mde=0.01)
        assert "required_n_per_group" in result
        assert result["required_n_per_group"] > 0

    def test_detectable_mde(self):
        result = power_analysis(baseline_rate=0.12, n_per_group=145000)
        assert "detectable_mde" in result
        assert result["detectable_mde"] > 0

    def test_larger_sample_needs_smaller_mde(self):
        r1 = power_analysis(baseline_rate=0.12, n_per_group=10000)
        r2 = power_analysis(baseline_rate=0.12, n_per_group=100000)
        assert r2["detectable_mde"] < r1["detectable_mde"]


class TestBayesian:
    def test_returns_probabilities(self):
        result = bayesian_ab_test(1000, 120, 1000, 130)
        assert 0 <= result["prob_treatment_better"] <= 1
        assert abs(result["prob_treatment_better"] + result["prob_control_better"] - 1.0) < 0.01

    def test_clear_winner(self):
        result = bayesian_ab_test(1000, 100, 1000, 200)
        assert result["prob_treatment_better"] > 0.99


class TestBonferroni:
    def test_adjusts_alpha(self):
        result = bonferroni_correction([0.01, 0.03, 0.04], alpha=0.05)
        assert result["adjusted_alpha"] < 0.05
        assert result["n_tests"] == 3

    def test_significance_changes(self):
        result = bonferroni_correction([0.02, 0.03], alpha=0.05)
        # With 2 tests, adjusted alpha = 0.025
        assert result["results"][0]["significant"]  # 0.02 < 0.025
        assert not result["results"][1]["significant"]  # 0.03 > 0.025

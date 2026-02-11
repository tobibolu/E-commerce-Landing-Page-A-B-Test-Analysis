from __future__ import annotations

from dataclasses import dataclass
from math import asin, sqrt

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, norm
from statsmodels.stats.proportion import proportions_ztest


@dataclass
class ABResult:
    control_rate: float
    treatment_rate: float
    absolute_lift: float
    relative_lift: float
    z_statistic: float
    p_value: float
    ci_low: float
    ci_high: float
    cohens_h: float


def srm_check(df: pd.DataFrame, expected_split: tuple[float, float] = (0.5, 0.5)) -> dict[str, float]:
    """Sample ratio mismatch chi-square test for assignment parity."""
    counts = df["group"].value_counts()
    observed = np.array([counts.get("control", 0), counts.get("treatment", 0)])
    total = observed.sum()
    expected = np.array([expected_split[0] * total, expected_split[1] * total])
    chi2, p_value = chi2_contingency([observed, expected])[:2]
    return {
        "control_count": int(observed[0]),
        "treatment_count": int(observed[1]),
        "chi2": float(chi2),
        "p_value": float(p_value),
    }


def run_ab_test(df: pd.DataFrame, alpha: float = 0.05, alternative: str = "two-sided") -> ABResult:
    """Two-proportion z-test with confidence interval and effect size."""
    control = df[df["group"] == "control"]["converted"]
    treatment = df[df["group"] == "treatment"]["converted"]

    n1, n2 = len(control), len(treatment)
    x1, x2 = int(control.sum()), int(treatment.sum())
    p1, p2 = x1 / n1, x2 / n2

    z_stat, p_val = proportions_ztest([x2, x1], [n2, n1], alternative=alternative)

    diff = p2 - p1
    se = sqrt((p1 * (1 - p1) / n1) + (p2 * (1 - p2) / n2))
    z_critical = norm.ppf(1 - alpha / 2)
    ci_low = diff - z_critical * se
    ci_high = diff + z_critical * se

    cohens_h = 2 * (asin(sqrt(p2)) - asin(sqrt(p1)))

    return ABResult(
        control_rate=p1,
        treatment_rate=p2,
        absolute_lift=diff,
        relative_lift=diff / p1,
        z_statistic=float(z_stat),
        p_value=float(p_val),
        ci_low=float(ci_low),
        ci_high=float(ci_high),
        cohens_h=float(cohens_h),
    )


def holm_correction(p_values: list[float]) -> list[float]:
    """Holm-Bonferroni adjusted p-values."""
    order = np.argsort(p_values)
    adjusted = np.empty(len(p_values), dtype=float)
    for rank, idx in enumerate(order):
        adjusted[idx] = min((len(p_values) - rank) * p_values[idx], 1.0)
    return adjusted.tolist()


def mde_sample_size(baseline_rate: float, mde: float, alpha: float = 0.05, power: float = 0.8) -> int:
    """Approximate sample size per variant for two-proportion test."""
    z_alpha = norm.ppf(1 - alpha / 2)
    z_beta = norm.ppf(power)
    p1 = baseline_rate
    p2 = baseline_rate + mde
    pooled_var = p1 * (1 - p1) + p2 * (1 - p2)
    n = ((z_alpha + z_beta) ** 2 * pooled_var) / (mde**2)
    return int(np.ceil(n))

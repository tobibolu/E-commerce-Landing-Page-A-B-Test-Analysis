"""Statistical testing module for A/B test analysis.

Implements frequentist Z-test, power analysis, Bayesian analysis,
and multiple testing correction.
"""

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm


def z_test(df: pd.DataFrame, group_col: str = "group",
           conv_col: str = "converted",
           control: str = "control",
           treatment: str = "treatment") -> dict:
    """Perform a two-proportion Z-test between control and treatment.

    Returns:
        Dictionary with z_statistic, p_value, control_conv, treatment_conv,
        conv_diff, relative_diff, confidence_interval.
    """
    ctrl = df[df[group_col] == control]
    treat = df[df[group_col] == treatment]

    n_ctrl, n_treat = len(ctrl), len(treat)
    x_ctrl = ctrl[conv_col].sum()
    x_treat = treat[conv_col].sum()

    z_stat, p_val = sm.stats.proportions_ztest([x_treat, x_ctrl], [n_treat, n_ctrl])

    p_ctrl = x_ctrl / n_ctrl
    p_treat = x_treat / n_treat
    diff = p_treat - p_ctrl

    # Confidence interval for the difference
    se = np.sqrt(p_ctrl * (1 - p_ctrl) / n_ctrl + p_treat * (1 - p_treat) / n_treat)
    ci_lower = diff - 1.96 * se
    ci_upper = diff + 1.96 * se

    return {
        "z_statistic": round(z_stat, 4),
        "p_value": round(p_val, 4),
        "control_conv": round(p_ctrl, 6),
        "treatment_conv": round(p_treat, 6),
        "absolute_diff": round(diff, 6),
        "relative_diff_pct": round(diff / p_ctrl * 100, 4) if p_ctrl > 0 else 0.0,
        "ci_95_lower": round(ci_lower, 6),
        "ci_95_upper": round(ci_upper, 6),
    }


def cohens_h(p1: float, p2: float) -> float:
    """Calculate Cohen's h effect size for two proportions."""
    return round(2 * (np.arcsin(np.sqrt(p1)) - np.arcsin(np.sqrt(p2))), 4)


def interpret_effect_size(h: float) -> str:
    """Interpret Cohen's h value."""
    h_abs = abs(h)
    if h_abs < 0.2:
        return "Negligible"
    elif h_abs < 0.5:
        return "Small"
    elif h_abs < 0.8:
        return "Medium"
    return "Large"


def power_analysis(baseline_rate: float, mde: float = None,
                   alpha: float = 0.05, power: float = 0.80,
                   n_per_group: int = None) -> dict:
    """Perform statistical power analysis for two-proportion test.

    If mde is given, calculates required sample size.
    If n_per_group is given, calculates the minimum detectable effect.

    Args:
        baseline_rate: Baseline conversion rate (e.g., 0.12).
        mde: Minimum detectable effect (absolute, e.g., 0.01 for +1%).
        alpha: Significance level.
        power: Desired power (1 - beta).
        n_per_group: Sample size per group (if computing MDE).

    Returns:
        Dictionary with power analysis results.
    """
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)

    results = {"baseline_rate": baseline_rate, "alpha": alpha, "power": power}

    if mde is not None:
        # Required sample size for given MDE
        p1 = baseline_rate
        p2 = baseline_rate + mde
        p_avg = (p1 + p2) / 2
        se_null = np.sqrt(2 * p_avg * (1 - p_avg))
        se_alt = np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
        n_required = ((z_alpha * se_null + z_beta * se_alt) / mde) ** 2
        results["mde"] = mde
        results["required_n_per_group"] = int(np.ceil(n_required))
        results["required_n_total"] = int(np.ceil(n_required)) * 2

    if n_per_group is not None:
        # MDE for given sample size (numerical approximation)
        results["n_per_group"] = n_per_group
        # Binary search for MDE
        lo, hi = 0.0001, 0.10
        for _ in range(100):
            mid = (lo + hi) / 2
            p2 = baseline_rate + mid
            p_avg = (baseline_rate + p2) / 2
            se_null = np.sqrt(2 * p_avg * (1 - p_avg))
            se_alt = np.sqrt(baseline_rate * (1 - baseline_rate) + p2 * (1 - p2))
            n_needed = ((z_alpha * se_null + z_beta * se_alt) / mid) ** 2
            if n_needed > n_per_group:
                lo = mid
            else:
                hi = mid
        results["detectable_mde"] = round(mid, 6)
        results["detectable_mde_pct"] = round(mid / baseline_rate * 100, 2)

    return results


def bayesian_ab_test(n_ctrl: int, conv_ctrl: int,
                     n_treat: int, conv_treat: int,
                     n_samples: int = 100_000,
                     prior_alpha: float = 1.0,
                     prior_beta: float = 1.0,
                     seed: int = 42) -> dict:
    """Bayesian A/B test using Beta-Binomial conjugate model.

    Uses uninformative Beta(1,1) prior by default.

    Returns:
        Dictionary with posterior statistics and probability that
        treatment beats control.
    """
    rng = np.random.RandomState(seed)

    # Posterior distributions: Beta(alpha + successes, beta + failures)
    post_ctrl = rng.beta(
        prior_alpha + conv_ctrl,
        prior_beta + n_ctrl - conv_ctrl,
        n_samples,
    )
    post_treat = rng.beta(
        prior_alpha + conv_treat,
        prior_beta + n_treat - conv_treat,
        n_samples,
    )

    diff = post_treat - post_ctrl
    prob_treat_better = (diff > 0).mean()

    # Expected loss: if we choose treatment but it's worse, how much do we lose?
    expected_loss_treat = np.maximum(post_ctrl - post_treat, 0).mean()
    expected_loss_ctrl = np.maximum(post_treat - post_ctrl, 0).mean()

    return {
        "prob_treatment_better": round(prob_treat_better, 4),
        "prob_control_better": round(1 - prob_treat_better, 4),
        "expected_diff_mean": round(diff.mean(), 6),
        "expected_diff_ci_2.5": round(np.percentile(diff, 2.5), 6),
        "expected_diff_ci_97.5": round(np.percentile(diff, 97.5), 6),
        "expected_loss_if_choose_treatment": round(expected_loss_treat, 6),
        "expected_loss_if_choose_control": round(expected_loss_ctrl, 6),
        "control_posterior_mean": round(post_ctrl.mean(), 6),
        "treatment_posterior_mean": round(post_treat.mean(), 6),
        "posterior_ctrl_samples": post_ctrl,
        "posterior_treat_samples": post_treat,
    }


def bonferroni_correction(p_values: list[float], alpha: float = 0.05) -> dict:
    """Apply Bonferroni correction for multiple comparisons.

    Returns:
        Dictionary with adjusted alpha and which tests remain significant.
    """
    n_tests = len(p_values)
    adjusted_alpha = alpha / n_tests
    return {
        "original_alpha": alpha,
        "n_tests": n_tests,
        "adjusted_alpha": round(adjusted_alpha, 6),
        "results": [
            {"p_value": round(p, 4), "significant": p < adjusted_alpha}
            for p in p_values
        ],
    }


def segment_analysis(df: pd.DataFrame, segment_col: str,
                     conv_col: str = "converted",
                     group_col: str = "group") -> pd.DataFrame:
    """Run Z-test for each segment and apply Bonferroni correction.

    Returns:
        DataFrame with per-segment test results and corrected significance.
    """
    segments = df[segment_col].unique()
    results = []
    p_values = []

    for seg in sorted(segments):
        seg_df = df[df[segment_col] == seg]
        test = z_test(seg_df, group_col=group_col, conv_col=conv_col)
        test["segment"] = seg
        test["n_total"] = len(seg_df)
        results.append(test)
        p_values.append(test["p_value"])

    correction = bonferroni_correction(p_values)
    adj_alpha = correction["adjusted_alpha"]

    results_df = pd.DataFrame(results)
    results_df["bonferroni_significant"] = results_df["p_value"] < adj_alpha
    results_df["adjusted_alpha"] = adj_alpha

    return results_df

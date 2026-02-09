"""Visualization utilities for A/B test analysis."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_conversion_rates(df: pd.DataFrame) -> None:
    """Plot overall conversion rates by group and by country."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    sns.barplot(x="group", y="converted", data=df, ci=95, ax=ax1)
    ax1.set_title("Overall Conversion Rates by Group")
    ax1.set_ylabel("Conversion Rate")

    sns.barplot(x="country", y="converted", hue="group", data=df, ax=ax2)
    ax2.set_title("Conversion Rates by Country")
    ax2.set_ylabel("Conversion Rate")

    plt.tight_layout()
    plt.show()


def plot_power_curve(baseline_rate: float, n_per_group: int,
                     alpha: float = 0.05) -> None:
    """Plot power curve showing detectable effect sizes at various power levels."""
    from scipy import stats

    z_alpha = stats.norm.ppf(1 - alpha / 2)
    powers = np.linspace(0.5, 0.99, 50)
    mdes = []

    for pwr in powers:
        z_beta = stats.norm.ppf(pwr)
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
        mdes.append(mid * 100)

    plt.figure(figsize=(10, 5))
    plt.plot(powers * 100, mdes, "b-", lw=2)
    plt.axhline(y=1.0, color="r", linestyle="--", alpha=0.5, label="1% MDE")
    plt.axvline(x=80, color="g", linestyle="--", alpha=0.5, label="80% power")
    plt.xlabel("Statistical Power (%)")
    plt.ylabel("Minimum Detectable Effect (%)")
    plt.title(f"Power Curve (n={n_per_group:,} per group, baseline={baseline_rate:.1%})")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()


def plot_bayesian_posteriors(posterior_ctrl: np.ndarray,
                             posterior_treat: np.ndarray) -> None:
    """Plot posterior distributions from Bayesian A/B test."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.hist(posterior_ctrl, bins=100, alpha=0.6, label="Control", density=True)
    ax1.hist(posterior_treat, bins=100, alpha=0.6, label="Treatment", density=True)
    ax1.set_xlabel("Conversion Rate")
    ax1.set_ylabel("Density")
    ax1.set_title("Posterior Distributions")
    ax1.legend()

    diff = posterior_treat - posterior_ctrl
    ax2.hist(diff, bins=100, alpha=0.7, color="purple", density=True)
    ax2.axvline(x=0, color="red", linestyle="--", lw=2)
    pct_positive = (diff > 0).mean() * 100
    ax2.set_xlabel("Treatment - Control")
    ax2.set_ylabel("Density")
    ax2.set_title(f"Posterior Difference (P(treat > ctrl) = {pct_positive:.1f}%)")

    plt.tight_layout()
    plt.show()


def plot_segment_results(segment_df: pd.DataFrame) -> None:
    """Plot conversion rates and significance by segment."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    segments = segment_df["segment"].unique()
    x = np.arange(len(segments))
    width = 0.35

    ctrl_rates = segment_df[segment_df.index % 1 == 0]["control_conv"].values if "control_conv" in segment_df.columns else []

    ax1.bar(x - width/2, segment_df["control_conv"] * 100, width, label="Control")
    ax1.bar(x + width/2, segment_df["treatment_conv"] * 100, width, label="Treatment")
    ax1.set_xticks(x)
    ax1.set_xticklabels(segment_df["segment"])
    ax1.set_ylabel("Conversion Rate (%)")
    ax1.set_title("Conversion Rates by Segment")
    ax1.legend()

    colors = ["red" if not sig else "green" for sig in segment_df["bonferroni_significant"]]
    ax2.barh(segment_df["segment"], segment_df["p_value"], color=colors)
    ax2.axvline(x=segment_df["adjusted_alpha"].iloc[0], color="black", linestyle="--",
                label=f"Bonferroni α = {segment_df['adjusted_alpha'].iloc[0]:.4f}")
    ax2.set_xlabel("P-value")
    ax2.set_title("Statistical Significance by Segment")
    ax2.legend()

    plt.tight_layout()
    plt.show()


def plot_daily_conversion_trend(daily_df: pd.DataFrame) -> None:
    """Plot daily conversion rates over time."""
    plt.figure(figsize=(12, 5))
    for group in daily_df["group"].unique():
        gdf = daily_df[daily_df["group"] == group]
        plt.plot(gdf["test_date"], gdf["conversion_rate"], marker="o",
                 markersize=3, label=group)

    plt.xlabel("Date")
    plt.ylabel("Conversion Rate (%)")
    plt.title("Daily Conversion Rate Trend")
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

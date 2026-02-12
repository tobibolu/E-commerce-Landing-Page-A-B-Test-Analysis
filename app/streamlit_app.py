"""Interactive A/B Test Analysis Dashboard.

Run with: streamlit run app/streamlit_app.py
"""

import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data_loader import load_ab_data, load_countries, clean_ab_data
from src.statistics import z_test, cohens_h, interpret_effect_size, power_analysis, bayesian_ab_test

st.set_page_config(page_title="A/B Test Dashboard", page_icon="📊", layout="wide")


@st.cache_data
def load_data():
    raw = load_ab_data()
    countries = load_countries()
    clean = clean_ab_data(raw, countries)
    return clean


def main():
    st.title("📊 E-commerce A/B Test Dashboard")
    st.markdown("Interactive analysis of the landing page experiment.")

    df = load_data()

    # Sidebar metrics
    st.sidebar.header("Experiment Summary")
    st.sidebar.metric("Total Users", f"{len(df):,}")
    st.sidebar.metric("Control Group", f"{len(df[df['group']=='control']):,}")
    st.sidebar.metric("Treatment Group", f"{len(df[df['group']=='treatment']):,}")

    tab1, tab2, tab3 = st.tabs(["📈 Frequentist", "🎲 Bayesian", "⚡ Power Analysis"])

    with tab1:
        st.subheader("Z-Test Results")
        results = z_test(df)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Control Rate", f"{results['control_conv']:.4%}")
        col2.metric("Treatment Rate", f"{results['treatment_conv']:.4%}")
        col3.metric("P-value", f"{results['p_value']:.4f}")
        col4.metric("Significant?", "No" if results["p_value"] > 0.05 else "Yes")

        h = cohens_h(results["treatment_conv"], results["control_conv"])
        st.write(f"**Effect size (Cohen's h):** {h} ({interpret_effect_size(h)})")
        st.write(f"**95% CI for difference:** [{results['ci_95_lower']:.4%}, {results['ci_95_upper']:.4%}]")

        # Country breakdown
        st.subheader("By Country")
        from src.statistics import segment_analysis
        seg = segment_analysis(df, "country")
        st.dataframe(seg[["segment", "control_conv", "treatment_conv", "p_value", "bonferroni_significant"]])

    with tab2:
        st.subheader("Bayesian A/B Test")
        n_ctrl = len(df[df["group"] == "control"])
        conv_ctrl = df[df["group"] == "control"]["converted"].sum()
        n_treat = len(df[df["group"] == "treatment"])
        conv_treat = df[df["group"] == "treatment"]["converted"].sum()

        bayes = bayesian_ab_test(n_ctrl, conv_ctrl, n_treat, conv_treat)

        col1, col2 = st.columns(2)
        col1.metric("P(Treatment Better)", f"{bayes['prob_treatment_better']:.1%}")
        col2.metric("P(Control Better)", f"{bayes['prob_control_better']:.1%}")

        st.write(f"**Expected difference:** {bayes['expected_diff_mean']:.4%}")
        st.write(f"**95% Credible Interval:** [{bayes['expected_diff_ci_2.5']:.4%}, {bayes['expected_diff_ci_97.5']:.4%}]")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        ax1.hist(bayes["posterior_ctrl_samples"], bins=100, alpha=0.6, label="Control", density=True)
        ax1.hist(bayes["posterior_treat_samples"], bins=100, alpha=0.6, label="Treatment", density=True)
        ax1.set_title("Posterior Distributions")
        ax1.legend()

        diff = bayes["posterior_treat_samples"] - bayes["posterior_ctrl_samples"]
        ax2.hist(diff, bins=100, alpha=0.7, color="purple", density=True)
        ax2.axvline(x=0, color="red", linestyle="--")
        ax2.set_title("Difference Distribution")
        plt.tight_layout()
        st.pyplot(fig)

    with tab3:
        st.subheader("Statistical Power Analysis")
        baseline = results["control_conv"]

        mde_input = st.slider("Minimum Detectable Effect (%)", 0.1, 5.0, 1.0, 0.1)
        pa = power_analysis(baseline_rate=baseline, mde=mde_input/100)
        st.write(f"**Required sample size per group:** {pa['required_n_per_group']:,}")
        st.write(f"**Total required:** {pa['required_n_total']:,}")

        n_per_group = len(df[df["group"] == "control"])
        pa_actual = power_analysis(baseline_rate=baseline, n_per_group=n_per_group)
        st.write(f"\n**With actual sample size ({n_per_group:,} per group):**")
        st.write(f"- Minimum Detectable Effect: {pa_actual['detectable_mde']:.4%} ({pa_actual['detectable_mde_pct']:.2f}% relative)")


if __name__ == "__main__":
    main()

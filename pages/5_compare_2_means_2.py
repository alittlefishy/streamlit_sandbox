import streamlit as st
import numpy as np
from statsmodels.stats.power import TTestIndPower

st.set_page_config(page_title="Sample Size Calculator", layout="centered")
st.title("📊 Sample Size Calculator for Comparing Two Independent Means")

# --- TEST SETTINGS ---
with st.expander("🔬 Study Design", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        test_type = st.selectbox(
            "Test Type", ["Equality", "Superiority", "Non-Inferiority", "Equivalence"],
            help="Choose the hypothesis framework for your comparison."
        )
    with col2:
        tail = st.radio("Test Sidedness", ["Two-sided", "One-sided"],
                        help="Two-sided tests detect any difference. One-sided tests detect effects in one direction.")
        alternative = "two-sided" if tail == "Two-sided" else "larger"

    if test_type in ["Superiority", "Non-Inferiority", "Equivalence"]:
        margin = st.number_input("Margin (Δ)", min_value=0.0, value=0.5, step=0.1,
                                 help="The smallest meaningful difference to detect or rule out.")
    else:
        margin = 0.0

# --- EFFECT SIZE INPUTS ---
with st.expander("📥 Inputs: Effect Size & Variability", expanded=True):
    input_mode = st.radio("Input Method", ["Expected Means", "Expected Difference"])
    if input_mode == "Expected Means":
        col1, col2 = st.columns(2)
        with col1:
            mean1 = st.number_input("Mean of Group 1", value=1.0)
        with col2:
            mean2 = st.number_input("Mean of Group 2", value=0.0)
        mean_diff = mean1 - mean2
    else:
        mean_diff = st.number_input("Expected Difference Between Means", value=1.0)
        mean1, mean2 = mean_diff, 0  # for consistent logic later

    sd_mode = st.radio("Standard Deviation Type", ["Pooled SD", "Separate SDs"])
    if sd_mode == "Pooled SD":
        std_dev = st.number_input("Pooled Standard Deviation", min_value=0.01, value=1.0)
    else:
        col1, col2 = st.columns(2)
        with col1:
            std1 = st.number_input("SD of Group 1", min_value=0.01, value=1.0)
        with col2:
            std2 = st.number_input("SD of Group 2", min_value=0.01, value=1.0)
        std_dev = np.sqrt((std1**2 + std2**2) / 2)

# --- STATISTICAL SETTINGS ---
with st.expander("⚙️ Alpha, Power & Sample Size Ratio", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        alpha = st.number_input("Significance Level (α)", min_value=0.0001, max_value=0.2, value=0.05, step=0.005)
    with col2:
        power = st.number_input("Power (1 - β)", min_value=0.5, max_value=0.99, value=0.8, step=0.01)

    ratio = st.number_input("Group 2 / Group 1 Sample Size Ratio", min_value=0.1, max_value=10.0, value=1.0, step=0.1)

# --- CALCULATE EFFECT SIZE ---

if test_type == "Superiority":
    adjusted_effect = (mean1 - mean2 - margin) / std_dev
elif test_type == "Non-Inferiority":
    adjusted_effect = (mean1 - mean2 + margin) / std_dev
elif test_type == "Equivalence":
    effect_lo = (mean_diff + margin) / std_dev
    effect_hi = (mean_diff - margin) / std_dev
else:
    adjusted_effect = abs(mean_diff) / std_dev

# --- CALCULATE SAMPLE SIZE ---
st.markdown("---")
st.subheader("📐 Required Sample Size")

try:
    analysis = TTestIndPower()

    if test_type == "Equivalence":
        # Manual TOST: two one-sided tests
        if effect_lo <= 0 or effect_hi >= 0:
            st.warning("Effect size is not within equivalence margins. Please revise your inputs.")
        else:
            n_lo = analysis.solve_power(effect_size=effect_lo, alpha=alpha, power=power, ratio=ratio, alternative="larger")
            n_hi = analysis.solve_power(effect_size=effect_hi, alpha=alpha, power=power, ratio=ratio, alternative="smaller")
            n_equiv = max(n_lo, n_hi)
            n2_equiv = n_equiv * ratio
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Group 1", f"{int(np.ceil(n_equiv))} participants")
            with col2:
                st.metric("Group 2", f"{int(np.ceil(n2_equiv))} participants")
    else:
        if adjusted_effect <= 0:
            st.warning("Adjusted effect size must be > 0. Please revise your inputs.")
        else:
            n1 = analysis.solve_power(
                effect_size=adjusted_effect,
                alpha=alpha,
                power=power,
                ratio=ratio,
                alternative=alternative
            )
            n2 = n1 * ratio
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Group 1", f"{int(np.ceil(n1))} participants")
            with col2:
                st.metric("Group 2", f"{int(np.ceil(n2))} participants")

except Exception as e:
    st.error(f"⚠️ Error: {e}")

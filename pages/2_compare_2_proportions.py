import streamlit as st
import numpy as np
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

st.set_page_config(page_title="Sample Size Calculator", layout="centered")
st.title("📊 Sample Size Calculator for Comparing Two Independent Proportions")

# --- TEST SETTINGS ---
with st.expander("🔬 Study Design", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        test_type = st.selectbox(
            "Test Type", ["Equality", "Superiority", "Non-Inferiority"],
            help="Choose the hypothesis framework for your comparison."
        )
    with col2:
        tail = st.radio("Test Sidedness", ["Two-sided", "One-sided"],
                        help="Two-sided tests detect any difference. One-sided tests detect effects in one direction.")
        alternative = "two-sided" if tail == "Two-sided" else "larger"

    if test_type in ["Superiority", "Non-Inferiority"]:
        margin = st.number_input("Margin (Δ)", min_value=0.0, value=0.05, step=0.01,
                                 help="The smallest meaningful difference to detect or rule out.")
    else:
        margin = 0.0

# --- EFFECT SIZE INPUTS ---
with st.expander("📥 Inputs: Proportions", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        prop1 = st.number_input("Proportion in Group 1", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
    with col2:
        prop2 = st.number_input("Proportion in Group 2", min_value=0.0, max_value=1.0, value=0.4, step=0.01)

    # Adjust for hypothesis
    if test_type == "Superiority":
        effect_size = proportion_effectsize(prop1, prop2 - margin)
    elif test_type == "Non-Inferiority":
        effect_size = proportion_effectsize(prop1, prop2 + margin)
    else:
        effect_size = proportion_effectsize(prop1, prop2)

# --- STATISTICAL SETTINGS ---
with st.expander("⚙️ Alpha, Power & Sample Size Ratio", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        alpha = st.number_input("Significance Level (α)", min_value=0.0001, max_value=0.2, value=0.05, step=0.005)
    with col2:
        power = st.number_input("Power (1 - β)", min_value=0.5, max_value=0.99, value=0.8, step=0.01)

    ratio = st.number_input("Group 2 / Group 1 Sample Size Ratio", min_value=0.1, max_value=10.0, value=1.0, step=0.1)

# --- CALCULATE SAMPLE SIZE ---
st.markdown("---")
st.subheader("📐 Required Sample Size")

try:
    if effect_size <= 0:
        st.warning("Effect size must be > 0. Please revise your inputs.")
    else:
        analysis = NormalIndPower()
        n1 = analysis.solve_power(
            effect_size=effect_size,
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

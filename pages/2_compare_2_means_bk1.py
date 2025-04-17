import streamlit as st
from statsmodels.stats.power import TTestIndPower
import numpy as np

st.set_page_config(page_title="Sample Size Calculator", layout="centered")

st.title("📊 Sample Size Calculator for Two Independent Means")

# Select test type
test_type = st.selectbox(
    "Select Test Type:",
    ["Equality", "Superiority", "Non-Inferiority", "Equivalence"]
)

# Tail selection
tail = st.radio("Tail of the Test", ["Two-sided", "One-sided"])
alternative = "two-sided" if tail == "Two-sided" else "larger"

# Input mode
input_mode = st.radio("Input Effect As:", ["Expected Means", "Expected Difference"])

# SD input type
sd_mode = st.radio("Standard Deviation Type", ["Pooled SD", "Separate SDs"])

# Group size ratio
ratio = st.number_input("Group 2 / Group 1 Sample Size Ratio", min_value=0.1, max_value=10.0, value=1.0, step=0.1)

# Collect basic inputs
alpha = st.number_input("Significance Level (α)", min_value=0.0001, max_value=0.2, value=0.05, step=0.005)
power = st.number_input("Power (1 - β)", min_value=0.5, max_value=0.99, value=0.8, step=0.01)

if input_mode == "Expected Means":
    mean1 = st.number_input("Mean of Group 1", value=1.0)
    mean2 = st.number_input("Mean of Group 2", value=0.0)
    mean_diff = abs(mean1 - mean2)
else:
    mean_diff = st.number_input("Expected Difference Between Means", value=1.0)

# SD input
if sd_mode == "Pooled SD":
    std_dev = st.number_input("Pooled Standard Deviation (σ)", min_value=0.01, value=1.0)
else:
    std1 = st.number_input("Standard Deviation for Group 1", min_value=0.01, value=1.0)
    std2 = st.number_input("Standard Deviation for Group 2", min_value=0.01, value=1.0)
    std_dev = np.sqrt((std1**2 + std2**2) / 2)

# Margin input for non-inferiority/superiority/equivalence
if test_type in ["Superiority", "Non-Inferiority", "Equivalence"]:
    margin = st.number_input("Margin (Δ)", min_value=0.0, value=0.5, step=0.1)
else:
    margin = 0.0

# Effect size calculation
if test_type in ["Superiority", "Non-Inferiority"]:
    adjusted_effect = (mean_diff - margin) / std_dev
elif test_type == "Equivalence":
    equivalence_margin = margin / std_dev
else:  # Equality
    adjusted_effect = mean_diff / std_dev

# Sample size calculation
if test_type != "Equivalence":
    if adjusted_effect <= 0:
        st.warning("The adjusted effect size is non-positive. Please check your inputs.")
    else:
        try:
            analysis = TTestIndPower()
            sample_size_group1 = analysis.solve_power(
                effect_size=adjusted_effect,
                alpha=alpha,
                power=power,
                ratio=ratio,
                alternative=alternative
            )
            sample_size_group2 = sample_size_group1 * ratio

            st.success(f"Required sample size:")
            st.markdown(f"- **Group 1:** {int(np.ceil(sample_size_group1))}")
            st.markdown(f"- **Group 2:** {int(np.ceil(sample_size_group2))}")
        except Exception as e:
            st.error(f"Error in calculation: {e}")
else:
    # Equivalence test via two one-sided tests (TOST)
    try:
        analysis = TTestIndPower()
        n1_low = analysis.solve_power(
            effect_size=equivalence_margin,
            alpha=alpha,
            power=power,
            alternative="larger",  # test for diff > -margin
            ratio=ratio
        )
        n1_high = analysis.solve_power(
            effect_size=equivalence_margin,
            alpha=alpha,
            power=power,
            alternative="smaller",  # test for diff < +margin
            ratio=ratio
        )
        n_equiv = max(n1_low, n1_high)
        st.success("Required sample size for equivalence (TOST):")
        st.markdown(f"- **Group 1:** {int(np.ceil(n_equiv))}")
        st.markdown(f"- **Group 2:** {int(np.ceil(n_equiv * ratio))}")
    except Exception as e:
        st.error(f"Error in equivalence calculation: {e}")
        st.success("Required sample size for equivalence:")
        st.markdown(f"- **Group 1:** {int(np.ceil(n_equiv))}")
        st.markdown(f"- **Group 2:** {int(np.ceil(n_equiv * ratio))}")
    except Exception as e:
        st.error(f"Error in equivalence calculation: {e}")

import streamlit as st

st.title("Fisher App")

st.write("""
Welcome to the Sample Size Calculators app! This application provides tools to help you determine the appropriate sample sizes for your research studies. 
You can use the calculators to input your parameters and obtain the necessary sample sizes based on your study design.

### Available Calculators
""")

st.page_link("pages/1_compare_2_means.py", label="📊 Compare 2 Independent Means")
st.page_link("pages/2_compare_2_proportions.py", label="🍕 Compare 2 Independent Proportions")

st.write("""
Please select a calculator from the list above to get started.
""")
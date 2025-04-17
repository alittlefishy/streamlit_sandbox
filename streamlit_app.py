import streamlit as st

st.title('🍡 Data Dango')

st.write('Hello world!')

x = st.text_input("Movie", "Star Wars")

if st.button("Click Me"):
    st.write(f"Your favorite movie is `{x}`")
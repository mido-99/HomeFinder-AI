import streamlit as st

st.set_page_config(
    page_title="Analyze Page",
    page_icon="📊",
)

st.title("📊 Analyze Page")

st.markdown(
    """
    This page is dedicated to data analysis and visualization.
    You could load datasets, display charts, or run models here.
    """
)

# Example Data Input/Display
data_source = st.selectbox(
    "Select data source:",
    ("Sales Data", "User Logs", "Financial Metrics")
)

st.info(f"Preparing to analyze: **{data_source}**")

st.bar_chart({"A": 100, "B": 85, "C": 120})
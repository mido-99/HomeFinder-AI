import streamlit as st

# Set page config for a cleaner look
st.set_page_config(
    page_title="Minimal Multi-Page App",
    page_icon="🏠",
)

st.title("🏠 Welcome to the Minimal Streamlit App")
st.markdown(
    """
    This is the **Home Page**.

    Use the navigation sidebar on the left to switch between the
    'Search' and 'Analyze' pages. Streamlit automatically detects
    Python files placed in the `pages/` directory and creates the
    sidebar navigation for you!

    ### To run this app:
    1. Save these files (`streamlit_app.py`, `pages/search.py`, `pages/analyze.py`)
    2. Ensure `search.py` and `analyze.py` are inside a folder named `pages/`.
    3. Run: `streamlit run streamlit_app.py`
    """
)

# Optional: Add a separator
st.sidebar.success("Select a page above.")
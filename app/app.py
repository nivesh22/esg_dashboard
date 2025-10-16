import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from src import data_loader, layout, utils

# Page configuration with custom theme and favicon
st.set_page_config(
    page_title="ESG Company Score Explorer",
    page_icon="assets/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

def add_disclaimer():
    """Add professional disclaimer and author information."""
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            """
            <div style='background-color: rgba(255, 255, 255, 0.1); padding: 1rem; border-radius: 0.5rem;'>
                <p style='font-size: 0.8rem; color: #B0BEC5;'>
                    <b>About this Dashboard</b><br>
                    Created by <a href="https://github.com/niveshke" style="color: #00C853;">Nivesh</a> 
                    to showcase data visualization and analytics capabilities. 
                    This is a demonstration project and should not be used for investment decisions.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

def main():
    """Main application entry point."""
    # Custom CSS for professional styling
    st.markdown(
        """
        <style>
        .main {
            background-color: #0A1929;
        }
        .stTitle {
            font-size: 2.5rem !important;
            font-weight: 600 !important;
            color: #F8F9FA !important;
        }
        .stSubheader {
            color: #B0BEC5 !important;
        }
        .plot-container {
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 1rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("ESG Company Score Explorer")
    st.caption(
        """
        Compare Environmental, Social, and Governance performance across companies and sectors. 
        Interactive analysis of ESG metrics normalized to 0–100 scale.
        """
    )

    # sidebar and data
    cfg = layout.sidebar_controls()
    df = data_loader.load_dataset()

    if df is None or df.empty:
        st.warning("No data available for the selected dataset. Use `make dummy-data` to generate demo data or upload a CSV.")
        return

    df = data_loader.preprocess(df)

    layout.render_tabs(df, cfg)


if __name__ == "__main__":
    main()

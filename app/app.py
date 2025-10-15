import streamlit as st
from src import data_loader, layout, utils


st.set_page_config(page_title="ESG Company Score Explorer", layout="wide")


def main():
    st.title("ESG Company Score Explorer")
    st.caption("Compare Environmental, Social, and Governance performance across companies and sectors. Data normalized to 0–100.")

    # sidebar and data
    cfg = layout.sidebar_controls()
    df = data_loader.load_dataset(cfg)

    if df is None or df.empty:
        st.warning("No data available for the selected dataset. Use `make dummy-data` to generate demo data or upload a CSV.")
        return

    df = data_loader.preprocess(df)

    layout.render_tabs(df, cfg)


if __name__ == "__main__":
    main()

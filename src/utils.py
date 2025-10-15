"""Utility helpers for the ESG dashboard."""
from __future__ import annotations

from typing import Optional

import pandas as pd
import streamlit as st


def download_button_csv(df: pd.DataFrame, label: str = "Download CSV"):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(label, data=csv, file_name="esg_filtered.csv", mime="text/csv")


def small_methodology():
    st.markdown(
        """
        ### Methodology

        - ESG_total is the mean of E, S, and G unless a provider total is available.
        - Scores are normalized to 0–100.
        - market_cap_usd is in billions (USD).
        - This dashboard is a demo and not investment advice.
        """
    )

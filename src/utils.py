"""Utility helpers for the ESG dashboard."""
from __future__ import annotations

from typing import Optional

import pandas as pd
import streamlit as st


def download_button_csv(df: pd.DataFrame, label: str = "Download CSV", key: Optional[str] = None):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(label, data=csv, file_name="esg_filtered.csv", mime="text/csv", key=key or "download_csv")


def small_methodology():
    st.markdown(
        """
        ### About the Data & Methodology

        #### Data Sources
        - **Demo Data**: The current view shows synthetic data for demonstration purposes.
        - **Real ESG Data** can be obtained from:
            - [Refinitiv ESG](https://www.refinitiv.com/en/sustainable-finance/esg-scores)
            - [MSCI ESG Ratings](https://www.msci.com/our-solutions/esg-investing/esg-ratings)
            - [Sustainalytics ESG Risk Ratings](https://www.sustainalytics.com/esg-ratings)
            - [S&P Global ESG Scores](https://www.spglobal.com/esg/scores/)
        
        #### Scoring Methodology
        - ESG scores are normalized to 0-100 scale for consistency
        - ESG_total is calculated as the mean of E, S, and G pillars
        - Market capitalization is in billions USD
        - Regional and sector classifications follow industry standards
        
        #### Data Processing
        - Raw ESG scores are cleaned and standardized
        - Missing values are handled using industry best practices
        - Outliers are identified and validated
        - Regular updates ensure data relevancy

        #### Important Notes
        - This dashboard uses synthetic data for demonstration
        - Real ESG analysis requires premium data subscriptions
        - Not intended for investment decisions
        - Methodology may vary between data providers
        """
    )

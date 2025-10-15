import pandas as pd
import streamlit as st
from pathlib import Path

@st.cache_data
def load_data(file_path: str | Path) -> pd.DataFrame:
    """
    Load ESG data from CSV file with caching.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        pd.DataFrame: Loaded and validated ESG data
    """
    try:
        df = pd.read_csv(file_path)
        required_columns = [
            'company', 'ticker', 'sector', 'region', 'country',
            'year', 'E', 'S', 'G', 'ESG_total', 'market_cap_usd'
        ]
        
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
            
        return df
        
    except FileNotFoundError:
        st.error(f"Data file not found: {file_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent))

import streamlit as st
from utils.data_loader import load_data

def main():
    st.title("ESG Company Score Explorer")
    
    # Test data loading
    data_path = Path(__file__).parent / "data" / "esg_scores.csv"
    print(f"Loading data from {data_path}")
    if data_path.exists():
        data = load_data(data_path)
        if not data.empty:
            st.write("Data loaded successfully!")
            st.dataframe(data.head())
    else:
        st.error(f"Data file not found at {data_path}")

if __name__ == "__main__":
    main()
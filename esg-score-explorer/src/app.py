from streamlit import st
import pandas as pd
from utils.data_loader import load_data
from utils.layout import create_sidebar, create_tabs

def main():
    st.title("ESG Company Score Explorer")
    
    # Load data
    data = load_data()

    # Create sidebar for filters
    create_sidebar(data)

    # Create tabs for different views
    create_tabs(data)

if __name__ == "__main__":
    main()
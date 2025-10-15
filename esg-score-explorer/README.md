# ESG Company Score Explorer

## Overview
The ESG Company Score Explorer is a Streamlit application designed to help users explore and analyze Environmental, Social, and Governance (ESG) scores of various companies. The application provides interactive visualizations and insights into ESG performance, allowing users to compare companies, explore sector trends, and understand the methodology behind the scoring.

## Features
- Interactive dashboard with sidebar filters and tabs
- Visualizations including histograms, box plots, scatter plots, and radar charts
- Data loading and processing capabilities
- Comparison of ESG scores across different companies and sectors
- Methodology explanation for ESG scoring

## Quickstart Instructions
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd esg-score-explorer
   ```

2. **Set up a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Kaggle API credentials:**
   - Rename `.env.sample` to `.env` and fill in your Kaggle username and key.

5. **Run the Streamlit application:**
   ```bash
   streamlit run src/app.py
   ```

## Deployment
To deploy the application, you can use platforms like Streamlit Sharing, Heroku, or any cloud service that supports Python applications. Ensure that all dependencies are included in the `requirements.txt` file and that environment variables are set appropriately.

## Data Model
The application utilizes ESG scores stored in CSV format. The data includes various metrics for each company, such as:
- ESG Score
- Market Capitalization
- Sector
- Year

The data is processed and visualized using libraries like Pandas, Plotly, and Altair to provide meaningful insights.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.
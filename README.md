# ESG Company Score Explorer

Lightweight Streamlit dashboard to explore Environmental, Social, and Governance (ESG) scores across companies and sectors. Built as a demo/portfolio app.

Features
- Interactive filters (year, sector, region, country, score ranges, market cap)
- Overview, Compare, Sector deep-dive, and Methodology tabs
- Plotly visualizations: histogram, box, scatter, choropleth, radar, treemap
- CLI scripts to generate demo data, fetch Kaggle datasets, and enrich market caps via yfinance

Quickstart

1. Create virtualenv and install:
```
make setup
```
2. Generate demo data:
```
make dummy-data
```
3. Run app:
```
make run
```

Deploy
- On Streamlit Community Cloud, set the main file to `app/app.py`.
- If using Kaggle fetch in the cloud, add `KAGGLE_USERNAME` and `KAGGLE_KEY` to secrets.

Data model

Required columns and semantics:

- `company` (string) — canonical company name
- `ticker` (string) — stock ticker
- `sector` (string) — GICS-like sector
- `region` (string) — region bucket
- `country` (string) — full country name
- `year` (int)
- `E`, `S`, `G` (float 0–100) — pillar scores
- `ESG_total` (float 0–100) — mean(E,S,G) if missing
- `market_cap_usd` (float, billions)

Optional sub-pillars included in demo:

- `E_emissions`, `E_energy`, `S_diversity`, `G_board`

Folder structure

```
esg-dashboard/
├── app/
│   └── app.py
├── src/
│   ├── data_loader.py
│   ├── charts.py
│   ├── layout.py
│   └── utils.py
├── scripts/
│   ├── generate_dummy_data.py
│   ├── fetch_kaggle_esg.py
│   └── enrich_market_cap_yf.py
├── data/
│   ├── raw/
│   └── processed/
├── .streamlit/
│   └── config.toml
├── requirements.txt
├── Makefile
└── README.md
```

Notes
- Kaggle API requires credentials in environment variables or `.kaggle/kaggle.json`.
- yfinance may not have data for synthetic tickers; use real tickers for enrichment.
- This is a demo app and not investment advice.
# esg_dashboard
# 🌍 ESG Score Explorer

**Live Dashboard:** [https://esgdash.streamlit.app/](https://esgdash.streamlit.app/)

---

## Overview

**ESG Score Explorer** is an interactive Streamlit dashboard built to analyze **Environmental, Social, and Governance (ESG)** performance across companies and industries.  
It provides intuitive visualizations to help investors, analysts, and researchers understand sustainability trends and their relationship with financial indicators.

This app currently uses **sample ESG data** for demonstration purposes.  
However, actual ESG datasets can be obtained through:
- **Financial data APIs** such as [Yahoo Finance](https://pypi.org/project/yfinance/), Refinitiv, or Bloomberg ESG datasets  
- **Public ESG databases** (e.g., MSCI, Sustainalytics, or CDP)  
- **Company sustainability reports** published annually  

---

## 🔍 Key Metrics & Visualizations

### 🧭 Company-Level ESG Breakdown
Each company is scored across the three ESG pillars:
- **Environmental (E):** Emissions, energy use, renewables, and resource efficiency  
- **Social (S):** Employee welfare, diversity, labor standards, community involvement  
- **Governance (G):** Board independence, transparency, compliance, and ethics  

Visuals:
- **Bar charts** showing ESG sub-score distributions  
- **Radar plots** comparing company ESG profiles against industry benchmarks  

---

### 📊 Sector & Industry Comparison
Analyze how ESG performance varies across industries or geographies.

Visuals:
- **Grouped bar and box plots** show sector-wise ESG score distributions  
- **Trend lines** to track score changes over time  
- **Heatmaps** highlighting top and bottom-performing sectors  

Interpretation:
- Taller bars → stronger performance on that ESG pillar  
- Narrower score spread → consistent sector-level performance  
- Darker color gradients → higher ESG intensity or positive trend  

---

### 💹 ESG vs Financial Performance
Explore the relationship between ESG scores and stock market behavior.

Visuals:
- **Scatter plots** correlating ESG scores with stock returns  
- **Line charts** overlaying ESG trends with price movements (via `yfinance`)  

Interpretation:
- Upward-sloping scatter → higher ESG scores linked to better performance  
- Divergence between price and ESG trend → potential valuation misalignment  

---

### 📈 Summary Dashboard
An aggregated panel displaying:
- Average ESG score  
- ESG rank within the sector  
- Year-over-year ESG changes  
- Company comparison tables  

---

## ⚙️ Setup Instructions

You can run the app locally in just a few steps.

### 1. Clone the Repository
```bash
git clone https://github.com/nivesh22/esg_dashboard.git
cd esg_dashboard


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
```
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
├── data/
│   ├── raw/
│   └── processed/
├── .streamlit/
│   └── config.toml
├── requirements.txt
└── README.md
```

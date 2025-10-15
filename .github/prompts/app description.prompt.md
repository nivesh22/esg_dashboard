---
mode: agent
---


Modify the current repo to have a production-quality, portfolio-ready **Streamlit ESG Company Score Explorer** that I can finish and deploy within 3 hours. Build everything end-to-end as specified below.

### 1) Tech Stack & Standards

* **Language:** Python 3.11+
* **UI:** Streamlit (wide layout, light/dark theme friendly)
* **Viz:** Plotly Express (+ basic Graph Objects where needed), Altair optional
* **Data:** CSV inputs; optional Kaggle fetch; optional `yfinance` enrichment
* **Config:** `.env` for secrets (Kaggle), Streamlit `config.toml` for theme
* **Style:** PEP 8; small, composable functions; inline docstrings
* **Caching:** Streamlit `@st.cache_data` where appropriate
* **Logging:** Minimal console logging for scripts; user-friendly errors in app

### 2) Repository & File/Folder Structure

Create exactly this structure (populate all files as described):

```
esg-dashboard/
├── app/
│   └── app.py                     # Streamlit entrypoint; imports from src/*
├── src/
│   ├── data_loader.py             # load/validate/normalize/filter/rank helpers
│   ├── charts.py                  # plot factories (hist, box, scatter, map, radar, bars, treemap)
│   ├── layout.py                  # sidebar + tabs (Overview, Compare, Sector, Methodology)
│   └── utils.py                   # shared helpers (e.g., caching, text blocks)
├── scripts/
│   ├── generate_dummy_data.py     # CLI: create demo dataset with specified schema
│   ├── fetch_kaggle_esg.py        # CLI: download a public ESG CSV via Kaggle API
│   └── enrich_market_cap_yf.py    # CLI: fetch market caps for tickers via yfinance
├── data/
│   ├── raw/                       # raw pulled files (e.g., kaggle_esg.csv)
│   └── processed/                 # cleaned/merged CSV (e.g., esg_demo.csv, esg_demo_enriched.csv)
├── .streamlit/
│   └── config.toml                # theme (brand colors, readable dark mode)
├── requirements.txt               # all Python deps with sensible pins/ranges
├── Makefile                       # developer commands (dummy-data, fetch-kaggle, enrich-yf, run)
├── README.md                      # project overview, quickstart, deploy steps, data model
├── .env.sample                    # KAGGLE_USERNAME, KAGGLE_KEY placeholders
└── .gitignore                     # ignore venv, .env, __pycache__, etc.
```

### 3) Data Model (Exact Columns & Semantics)

All data used by the dashboard must conform to this schema (create and validate):

**Required columns**

* `company` (string) — canonical company name
* `ticker` (string) — stock ticker (synthetic for dummy data is fine)
* `sector` (string) — GICS-like sector (see allowed set below)
* `region` (string) — one of: `North America`, `Europe`, `Asia-Pacific`, `Latin America`, `Middle East & Africa`
* `country` (string) — full country name (e.g., “United States”)
* `year` (int) — e.g., 2018–2024
* `E` (float, 0–100) — environmental score
* `S` (float, 0–100) — social score
* `G` (float, 0–100) — governance score
* `ESG_total` (float, 0–100) — if missing, compute as mean(E, S, G)
* `market_cap_usd` (float, **billions**)

**Optional sub-pillars (include in dummy data)**

* `E_emissions`, `E_energy`, `S_diversity`, `G_board` (floats, 0–100)

**Allowed sectors**
`Communication Services`, `Consumer Discretionary`, `Consumer Staples`, `Energy`, `Financials`, `Health Care`, `Industrials`, `Information Technology`, `Materials`, `Real Estate`, `Utilities`.

**Derived columns in app**

* `iso3` — ISO-3 code from `country` (for map)
* `rank_overall` — rank by `ESG_total` (desc)
* `quartile` — 1–4 by `ESG_total`
* Optional: z-scores as needed for advanced toggles

### 4) Dummy Data Generator (CLI spec; do not hardcode paths)

Implement `scripts/generate_dummy_data.py` with a CLI:

* Args: `--rows` (default 350), `--year` (default 2021), `--out` (default `data/processed/esg_demo.csv`)
* Generates realistic values:

  * Mix of regions/countries per region, sector-biased distributions for E/S/G
  * `ESG_total` = mean(E,S,G) rounded to 2 decimals
  * `market_cap_usd` ~ log-normal-ish billions; round to 2 decimals
  * Include sub-pillars above with slight noise around their parent pillar
* Print summary on completion; create directories if missing
* Ensure columns are exactly as per schema and values clipped to 0–100

### 5) Kaggle Fetch (Optional but implemented)

Implement `scripts/fetch_kaggle_esg.py` (CLI):

* Args:

  * `--dataset` (default: `therohk/global-esg-scores-2021`),
  * `--file` (default: a plausible CSV inside that dataset),
  * `--out` (default: `data/raw/kaggle_esg.csv`)
* Use Kaggle API; require `KAGGLE_USERNAME` + `KAGGLE_KEY` via env or `.env`
* Download + extract the CSV; save to `--out`
* Print row count; errors should be clear (e.g., missing CLI, bad creds, file not found)

### 6) Market Cap Enrichment via yfinance (Optional but implemented)

Implement `scripts/enrich_market_cap_yf.py` (CLI):

* Args: `--infile` and `--out`
* For unique `ticker` values, query `yfinance` and update `market_cap_usd` (convert to **billions**) where available; leave existing values otherwise
* Be resilient to missing/invalid tickers and rate limits; print how many updated

### 7) Streamlit App Behavior & Layout

**Top of page**

* Title: “ESG Company Score Explorer”
* Subtitle/caption: “Compare Environmental, Social, and Governance performance across companies and sectors. Data normalized to 0–100.”

**Dataset switcher (in sidebar)**

* Options: `Demo (dummy data)` / `From file (CSV)` / `Kaggle ESG (raw)`
* For “Demo”, expect `data/processed/esg_demo.csv` (show friendly warning with how to generate if missing)
* For “From file”, display file uploader
* For “Kaggle ESG (raw)”, expect `data/raw/kaggle_esg.csv` (show friendly warning explaining the `make fetch-kaggle` command if missing)

**Sidebar Filters (all charts react)**

* Year: selectbox (default latest year present)
* Sector: multiselect (default all)
* Region: multiselect (default all)
* Country: multiselect (dependent on Region; default none = all in selection)
* Sliders: E, S, G, ESG_total (0–100, default 0–100)
* Market cap (billions): min–max slider (default min=0, max=dataset max)
* Checkbox: “Only complete rows” (default on)
* Company search text input + multiselect “Compare companies (up to 5)”
* “Advanced” expander: toggles for scatter log-y (default on), trendline (default on)

**Tabs**

1. **Overview**

   * KPI row: Avg ESG, Median ESG, Coverage (N companies), Top Company (name + score)
   * Histogram: ESG_total distribution (bin ~20)
   * Box/Violin by sector: ESG_total spread
   * Bubble scatter: ESG_total (x) vs market_cap_usd (y, log toggle), color by sector, size ~ sqrt(market cap), hover shows key fields; optional OLS trendline
   * Choropleth map: avg ESG_total by country (iso3)
   * Data table: current filtered rows, sortable; download button to CSV
   * Empty-state warnings if filters eliminate all rows

2. **Compare Companies**

   * If none selected: friendly info message
   * Profile cards across selected: company, ticker, sector/region/country, ESG_total metric, and progress bars for E/S/G
   * Radar/spider chart (E, S, G axes) for up to 5 companies
   * Grouped bars (E/S/G by company)
   * Optional: sub-pillar heatmap if columns available

3. **Sector Deep Dive**

   * Selectbox “Focus sector” (defaults to first available)
   * Strip/box plot for ESG_total within sector, color by quartile, hover company names
   * Two tables side-by-side: Top 10 and Bottom 10 by ESG_total in the sector (with E/S/G and market_cap_usd)
   * Treemap: path [sector, company], values market_cap_usd, color by ESG_total

4. **Methodology & Download**

   * Narrative on sources (dummy/Kaggle), normalization, scoring (ESG_total=mean where missing), and caveats (provider differences)
   * Download buttons: filtered data, sector summary if produced
   * Snippet showing `requirements.txt` set and how to deploy
   * This app is for demo/portfolio only, not investment advice

### 8) Requirements & Config

* `requirements.txt` must include: streamlit, pandas, numpy, plotly, altair, yfinance, python-dotenv, pycountry, kaggle, requests, beautifulsoup4, statsmodels (for trendline)
* `.streamlit/config.toml`: tasteful theme (accessible in dark mode)
* `.env.sample`: `KAGGLE_USERNAME`, `KAGGLE_KEY` placeholders
* `.gitignore`: ignore `.venv`, `.env`, `__pycache__`, `.DS_Store`, `.pytest_cache`, `.streamlit/secrets.toml`

### 9) Makefile Targets (exact names & behavior)

* `setup` — install from `requirements.txt`
* `dummy-data` — run dummy generator with defaults to produce `data/processed/esg_demo.csv`
* `fetch-kaggle` — download default Kaggle dataset to `data/raw/kaggle_esg.csv`
* `enrich-yf` — read processed CSV, update market caps using yfinance, write `data/processed/esg_demo_enriched.csv`
* `run` — run Streamlit app (`app/app.py`)

### 10) README.md (sections & content to include)

* Project name + short description
* Feature list (filters, tabs, charts)
* Quickstart (Make commands)
* Deploy to Streamlit Community Cloud (repo → pick `app/app.py`; add secrets if using Kaggle)
* Data model table (all columns with short descriptions)
* Folder structure (tree)
* Notes: Kaggle API setup, yfinance caveats, portfolio disclaimer

### 11) Acceptance Criteria / Smoke Tests

* After `make dummy-data` and `make run`, the app loads, charts render, filters work, and the map colors countries without error
* Histogram, sector boxplot, scatter (with log toggle), and map all use filtered data
* Compare tab shows radar and grouped bars for selected companies
* Sector tab shows top/bottom 10 tables and a treemap
* `make fetch-kaggle` saves a CSV; app can load it from “Kaggle ESG (raw)”
* `make enrich-yf` updates at least some `market_cap_usd` values when valid tickers exist
* No uncaught exceptions; empty states display friendly messages
* Lint for obvious style issues; type hints on main functions preferred

### 12) Developer Experience & Handoff

* Add concise inline comments where logic might be non-obvious
* Keep functions small and testable
* Ensure all paths are relative to repo root and created as needed
* Provide helpful terminal output for all scripts (rows written, path used)

**Deliverables:**
Generate all files, fully implemented per the above. Do not include placeholder “TODO”s. Ensure I can run:

1. `make dummy-data`
2. `make run`
   …and immediately see the working dashboard.

---


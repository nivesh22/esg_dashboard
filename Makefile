PY=python3

.PHONY: setup dummy-data fetch-kaggle enrich-yf run

setup:
	pip install -r requirements.txt

dummy-data:
	$(PY) scripts/generate_dummy_data.py --rows 350 --year 2021 --out data/processed/esg_demo.csv

fetch-kaggle:
	$(PY) scripts/fetch_kaggle_esg.py --dataset therohk/global-esg-scores-2021 --out data/raw/kaggle_esg.csv

enrich-yf:
	$(PY) scripts/enrich_market_cap_yf.py --infile data/processed/esg_demo.csv --out data/processed/esg_demo_enriched.csv

run:
	streamlit run app/app.py

"""Enrich market_cap_usd using yfinance for tickers in a CSV file.

Converts market cap to billions USD and writes an output CSV.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import time

import pandas as pd
import yfinance as yf


def main():
    parser = argparse.ArgumentParser(description="Enrich market caps via yfinance")
    parser.add_argument("--infile", default="data/processed/esg_demo.csv")
    parser.add_argument("--out", default="data/processed/esg_demo_enriched.csv")
    args = parser.parse_args()

    infile = Path(args.infile)
    if not infile.exists():
        print(f"Input file not found: {infile}")
        return

    df = pd.read_csv(infile)
    tickers = df["ticker"].dropna().unique().tolist()
    updated = 0

    for t in tickers:
        try:
            obj = yf.Ticker(t)
            info = obj.info
            mcap = info.get("marketCap")
            if mcap:
                # convert to billions
                mcap_bill = round(mcap / 1e9, 2)
                df.loc[df["ticker"] == t, "market_cap_usd"] = mcap_bill
                updated += 1
        except Exception:
            # skip invalid tickers
            continue
        time.sleep(0.1)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote enriched file to {out}. Updated {updated} tickers.")


if __name__ == "__main__":
    main()

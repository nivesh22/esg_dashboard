"""CLI to generate realistic dummy ESG dataset."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import random
import numpy as np
import pandas as pd

SECTORS = [
    "Communication Services",
    "Consumer Discretionary",
    "Consumer Staples",
    "Energy",
    "Financials",
    "Health Care",
    "Industrials",
    "Information Technology",
    "Materials",
    "Real Estate",
    "Utilities",
]

REGIONS = {
    "North America": ["United States", "Canada", "Mexico"],
    "Europe": ["United Kingdom", "Germany", "France", "Netherlands", "Sweden"],
    "Asia-Pacific": ["Japan", "Australia", "China", "India", "Singapore"],
    "Latin America": ["Brazil", "Argentina", "Chile"],
    "Middle East & Africa": ["South Africa", "United Arab Emirates", "Saudi Arabia"],
}


def _sector_score_base(sector: str):
    # sector-biased means: Energy lower E, InfoTech higher E, Financials lower E
    base = {
        "Energy": (40, 50, 55),
        "Information Technology": (65, 60, 60),
        "Health Care": (60, 65, 60),
        "Financials": (50, 55, 50),
    }
    return base.get(sector, (55, 55, 55))


def generate(rows=350, year=2021):
    rows = int(rows)
    data = []
    for i in range(rows):
        sector = random.choice(SECTORS)
        region = random.choice(list(REGIONS.keys()))
        country = random.choice(REGIONS[region])
        company = f"Company {i+1} {sector.split()[0]}"
        ticker = f"C{i+1:03d}"

        e_base, s_base, g_base = _sector_score_base(sector)
        E = np.clip(np.random.normal(e_base, 12), 0, 100)
        S = np.clip(np.random.normal(s_base, 12), 0, 100)
        G = np.clip(np.random.normal(g_base, 10), 0, 100)

        E_emissions = np.clip(E + np.random.normal(0, 5), 0, 100)
        E_energy = np.clip(E + np.random.normal(0, 5), 0, 100)
        S_diversity = np.clip(S + np.random.normal(0, 5), 0, 100)
        G_board = np.clip(G + np.random.normal(0, 5), 0, 100)

        ESG_total = round(float(np.mean([E, S, G])), 2)

        # market cap log-normal in billions
        market_cap_usd = round(float(np.random.lognormal(mean=1.5, sigma=1.2)), 2)

        data.append(
            {
                "company": company,
                "ticker": ticker,
                "sector": sector,
                "region": region,
                "country": country,
                "year": int(year),
                "E": round(float(E), 2),
                "S": round(float(S), 2),
                "G": round(float(G), 2),
                "ESG_total": ESG_total,
                "market_cap_usd": market_cap_usd,
                "E_emissions": round(float(E_emissions), 2),
                "E_energy": round(float(E_energy), 2),
                "S_diversity": round(float(S_diversity), 2),
                "G_board": round(float(G_board), 2),
            }
        )

    df = pd.DataFrame(data)
    # Ensure column order
    cols = [
        "company",
        "ticker",
        "sector",
        "region",
        "country",
        "year",
        "E",
        "S",
        "G",
        "ESG_total",
        "market_cap_usd",
        "E_emissions",
        "E_energy",
        "S_diversity",
        "G_board",
    ]
    df = df[cols]
    return df


def main():
    parser = argparse.ArgumentParser(description="Generate dummy ESG CSV")
    parser.add_argument("--rows", type=int, default=350)
    parser.add_argument("--year", type=int, default=2021)
    parser.add_argument("--out", type=str, default="data/processed/esg_demo.csv")
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    df = generate(rows=args.rows, year=args.year)
    df.to_csv(out_path, index=False)

    print(f"Wrote {len(df)} rows to {out_path}")


if __name__ == "__main__":
    main()

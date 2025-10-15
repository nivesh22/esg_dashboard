"""Data loading and preprocessing helpers for the ESG dashboard.

Implements: load_dataset, preprocess, validate_schema, compute_derived
"""
from __future__ import annotations

import os
from typing import Optional, Dict

import pandas as pd
import numpy as np
import pycountry
import streamlit as st

REQUIRED_COLS = [
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
]

OPTIONAL_SUB = ["E_emissions", "E_energy", "S_diversity", "G_board"]

ALLOWED_SECTORS = [
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


@st.cache_data
def load_dataset(cfg: Dict) -> Optional[pd.DataFrame]:
    """Load dataset based on sidebar config.

    cfg: dict with keys dataset (Demo/From file/Kaggle) and file uploader path
    """
    dataset = cfg.get("dataset")
    if dataset == "Demo (dummy data)":
        path = os.path.join("data", "processed", "esg_demo.csv")
        if not os.path.exists(path):
            st.warning(f"Demo data not found at {path}. Run `make dummy-data` to generate it.")
            return pd.DataFrame()
        df = pd.read_csv(path)
        return df

    if dataset == "Kaggle ESG (raw)":
        path = os.path.join("data", "raw", "kaggle_esg.csv")
        if not os.path.exists(path):
            st.warning(f"Kaggle raw file not found at {path}. Run `make fetch-kaggle` to download it.")
            return pd.DataFrame()
        return pd.read_csv(path)

    # From file
    upload = cfg.get("upload")
    if upload is not None:
        try:
            return pd.read_csv(upload)
        except Exception as e:
            st.error(f"Failed to read uploaded file: {e}")
            return pd.DataFrame()

    return pd.DataFrame()


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize and validate DataFrame to the canonical schema.

    Adds iso3, rank_overall, quartile, fills ESG_total, casts types.
    """
    if df is None or df.empty:
        return df

    # Ensure required columns exist; if ESG_total missing, compute
    for col in ["E", "S", "G"]:
        if col not in df.columns:
            df[col] = np.nan

    if "ESG_total" not in df.columns or df["ESG_total"].isnull().all():
        df["ESG_total"] = df[["E", "S", "G"]].mean(axis=1)

    # Clip scores
    for col in ["E", "S", "G", "ESG_total"] + OPTIONAL_SUB:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").clip(0, 100)

    # market cap to float
    if "market_cap_usd" in df.columns:
        df["market_cap_usd"] = pd.to_numeric(df["market_cap_usd"], errors="coerce")
    else:
        df["market_cap_usd"] = np.nan

    # year cast
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype(pd.Int64Dtype())

    # iso3 mapping
    df["iso3"] = df["country"].apply(lambda c: country_to_iso3(c))

    # rank and quartile
    df["rank_overall"] = df["ESG_total"].rank(method="min", ascending=False)
    df["quartile"] = pd.qcut(df["ESG_total"].fillna(-1), q=4, labels=[1, 2, 3, 4])

    return df


def country_to_iso3(name: str) -> Optional[str]:
    try:
        if not isinstance(name, str) or not name.strip():
            return None
        c = pycountry.countries.lookup(name)
        return c.alpha_3
    except Exception:
        return None

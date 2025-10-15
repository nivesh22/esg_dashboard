"""Layout builders for Streamlit app: sidebar controls and tab rendering."""
from __future__ import annotations

from typing import Dict, List, Optional

import streamlit as st
import pandas as pd

from . import charts, utils


def sidebar_controls() -> Dict:
    st.sidebar.header("Dataset & Filters")
    dataset = st.sidebar.selectbox("Dataset", ["Demo (dummy data)", "From file (CSV)", "Kaggle ESG (raw)"])

    upload = None
    if dataset == "From file (CSV)":
        upload = st.sidebar.file_uploader("Upload CSV file", type=["csv"])

    st.sidebar.markdown("---")
    year = st.sidebar.selectbox("Year", options=[2024, 2023, 2022, 2021, 2020], index=0)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Advanced")
    log_y = st.sidebar.checkbox("Scatter: log y-axis (market cap)", value=True)
    trendline = st.sidebar.checkbox("Scatter: show trendline", value=True)

    cfg = {"dataset": dataset, "upload": upload, "year": year, "log_y": log_y, "trendline": trendline}
    return cfg


def render_tabs(df: pd.DataFrame, cfg: Dict):
    tabs = st.tabs(["Overview", "Compare", "Sector", "Methodology & Download"])

    with tabs[0]:
        render_overview(df, cfg)

    with tabs[1]:
        render_compare(df, cfg)

    with tabs[2]:
        render_sector(df, cfg)

    with tabs[3]:
        render_methodology(df, cfg)


def _filter_panel(df: pd.DataFrame) -> pd.DataFrame:
    # Basic filters inline for now
    st.sidebar.subheader("Filters")
    years = sorted(df["year"].dropna().unique().tolist())
    year = st.sidebar.selectbox("Year", options=years, index=len(years) - 1 if years else 0)

    sectors = sorted(df["sector"].dropna().unique().tolist())
    sel_sectors = st.sidebar.multiselect("Sector", options=sectors, default=sectors)

    regions = sorted(df["region"].dropna().unique().tolist())
    sel_regions = st.sidebar.multiselect("Region", options=regions, default=regions)

    # dependent country
    countries = sorted(df[df["region"].isin(sel_regions)]["country"].dropna().unique().tolist())
    sel_countries = st.sidebar.multiselect("Country", options=countries, default=None)

    e_min, e_max = st.sidebar.slider("E range", 0.0, 100.0, (0.0, 100.0))
    s_min, s_max = st.sidebar.slider("S range", 0.0, 100.0, (0.0, 100.0))
    g_min, g_max = st.sidebar.slider("G range", 0.0, 100.0, (0.0, 100.0))
    esg_min, esg_max = st.sidebar.slider("ESG_total range", 0.0, 100.0, (0.0, 100.0))

    mc_min, mc_max = st.sidebar.slider("Market cap (billions)", 0.0, float(df["market_cap_usd"].max() or 0.0), (0.0, float(df["market_cap_usd"].max() or 0.0)))

    only_complete = st.sidebar.checkbox("Only complete rows", value=True)

    company_search = st.sidebar.text_input("Company search")
    compare_companies = st.sidebar.multiselect("Compare companies (up to 5)", options=sorted(df["company"].dropna().unique().tolist()), max_selections=5)

    # Apply filters
    d = df.copy()
    if years:
        d = d[d["year"] == year]
    if sel_sectors:
        d = d[d["sector"].isin(sel_sectors)]
    if sel_regions:
        d = d[d["region"].isin(sel_regions)]
    if sel_countries:
        d = d[d["country"].isin(sel_countries)]

    d = d[(d["E"] >= e_min) & (d["E"] <= e_max) & (d["S"] >= s_min) & (d["S"] <= s_max) & (d["G"] >= g_min) & (d["G"] <= g_max) & (d["ESG_total"] >= esg_min) & (d["ESG_total"] <= esg_max)]

    d = d[(d["market_cap_usd"] >= mc_min) & (d["market_cap_usd"] <= mc_max)]

    if only_complete:
        d = d.dropna(subset=["E", "S", "G", "ESG_total", "market_cap_usd"])

    if company_search:
        d = d[d["company"].str.contains(company_search, case=False, na=False)]

    return d


def render_overview(df: pd.DataFrame, cfg: Dict):
    d = _filter_panel(df)

    if d.empty:
        st.warning("No rows match the selected filters. Try relaxing filters.")
        return

    # KPI row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Average ESG", f"{d['ESG_total'].mean():.2f}")
    col2.metric("Median ESG", f"{d['ESG_total'].median():.2f}")
    col3.metric("Coverage (companies)", f"{d['company'].nunique()}")
    top = d.sort_values("ESG_total", ascending=False).iloc[0]
    col4.metric("Top company", f"{top['company']} ({top['ESG_total']:.2f})")

    st.plotly_chart(charts.hist_esg(d), use_container_width=True)
    st.plotly_chart(charts.box_by_sector(d), use_container_width=True)
    st.plotly_chart(charts.scatter_esg_vs_market(d, log_y=cfg.get('log_y', True), trendline=cfg.get('trendline', True)), use_container_width=True)

    st.plotly_chart(charts.choropleth_country(d), use_container_width=True)

    st.dataframe(d.reset_index(drop=True))
    utils.download_button_csv(d)


def render_compare(df: pd.DataFrame, cfg: Dict):
    d = _filter_panel(df)
    companies = st.sidebar.multiselect("Compare companies (main tab)", options=sorted(df["company"].dropna().unique().tolist()), default=None)

    if not companies:
        st.info("Select companies from the sidebar to compare (up to 5).")
        return

    rows = d[d["company"].isin(companies)]
    if rows.empty:
        st.warning("No selected companies match current filters.")
        return

    # Profile cards
    cols = st.columns(len(companies))
    for i, comp in enumerate(companies):
        r = rows[rows["company"] == comp].iloc[0]
        with cols[i]:
            st.subheader(r["company"])
            st.write(f"Ticker: {r.get('ticker', '')}")
            st.write(f"Sector: {r.get('sector', '')}")
            st.write(f"Region/Country: {r.get('region', '')} / {r.get('country', '')}")
            st.progress(int(r.get("ESG_total", 0)))

    st.plotly_chart(charts.radar_companies(d, companies), use_container_width=True)
    st.plotly_chart(charts.grouped_bars_esg(d, companies), use_container_width=True)


def render_sector(df: pd.DataFrame, cfg: Dict):
    d = _filter_panel(df)
    sectors = sorted(d["sector"].dropna().unique().tolist())
    if not sectors:
        st.warning("No sectors available in filtered data.")
        return
    focus = st.selectbox("Focus sector", options=sectors, index=0)

    # strip/box within sector
    s = d[d["sector"] == focus]
    st.plotly_chart(charts.box_by_sector(s), use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.write("Top 10 by ESG_total")
        st.dataframe(s.sort_values("ESG_total", ascending=False).head(10))
    with right:
        st.write("Bottom 10 by ESG_total")
        st.dataframe(s.sort_values("ESG_total", ascending=True).head(10))

    st.plotly_chart(charts.treemap_sector(s, focus), use_container_width=True)


def render_methodology(df: pd.DataFrame, cfg: Dict):
    utils.small_methodology()
    st.markdown("---")
    st.write("Download current filtered dataset:")
    d = _filter_panel(df)
    if not d.empty:
        utils.download_button_csv(d)
    st.markdown("This app is for demo/portfolio use only and not investment advice.")

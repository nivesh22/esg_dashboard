# layout.py
from __future__ import annotations
from typing import Dict
from contextlib import contextmanager

import streamlit as st
import pandas as pd

# Dashboard styling with title bar
st.markdown("""
<style>
    /* Title bar */
    .title-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        background: linear-gradient(90deg, rgba(9,9,21,0.99) 0%, rgba(22,28,47,0.99) 100%);
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding: 0.5rem 1rem;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }
    
    .title-bar-content {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .logo-wrapper {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .logo {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #00BCD4, #4CAF50);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
        font-size: 16px;
    }
    
    .title-text {
        color: #F8F9FA;
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0;
        padding: 0;
        line-height: 1;
    }
    
    .subtitle-text {
        color: #B0BEC5;
        font-size: 0.875rem;
        margin: 4px 0 0 0;
        padding: 0;
        line-height: 1;
    }
    
    .title-bar-right {
        margin-left: auto;
        display: flex;
        align-items: center;
        gap: 1rem;
        color: #B0BEC5;
        font-size: 0.875rem;
    }

    /* Base styles */
    .block-container { padding-top: 4rem !important; }
    .sect-title { margin: 0 0 6px 0; font-size: 1.6rem; font-weight: 800; letter-spacing: -0.01em; }
    .sect-desc  { margin: 0 0 12px 0; opacity: 0.85; }
    [data-testid="stHorizontalBlock"] { gap: 1rem !important; }
  [data-testid="stHorizontalBlock"] > div { flex: 1; }
</style>
""", unsafe_allow_html=True)

from . import charts, utils  # your modules

def draw_sidebar_filters(df: pd.DataFrame) -> None:
    """Render sidebar controls ONCE and store selections in st.session_state."""
    st.sidebar.header("Filters")

    years = sorted(df["year"].dropna().unique().tolist())
    st.sidebar.selectbox("Year", options=years or [None],
                         index=(len(years)-1 if years else 0), key="flt_year")

    sectors = sorted(df["sector"].dropna().unique().tolist())
    st.sidebar.multiselect("Sector", options=sectors, default=sectors, key="flt_sectors")

    regions = sorted(df["region"].dropna().unique().tolist())
    st.sidebar.multiselect("Region", options=regions, default=regions, key="flt_regions")

    # Countries depend on selected regions (use current state if exists)
    sel_regions = st.session_state.get("flt_regions", regions)
    countries = sorted(df[df["region"].isin(sel_regions)]["country"].dropna().unique().tolist())
    st.sidebar.multiselect("Country", options=countries, key="flt_countries")

    st.sidebar.markdown("---")
    st.sidebar.slider("Environmental (E) Score", 0.0, 100.0, (0.0, 100.0), key="flt_e")
    st.sidebar.slider("Social (S) Score",       0.0, 100.0, (0.0, 100.0), key="flt_s")
    st.sidebar.slider("Governance (G) Score",   0.0, 100.0, (0.0, 100.0), key="flt_g")
    st.sidebar.slider("Total ESG Score",        0.0, 100.0, (0.0, 100.0), key="flt_esg")

    st.sidebar.markdown("---")
    max_mc = float((df["market_cap_usd"].max() or 0.0))
    st.sidebar.slider("Market Cap (Billions USD)", 0.0, max_mc, (0.0, max_mc), key="flt_mc")

    st.sidebar.checkbox("Show only rows with complete data", value=True, key="flt_complete")
    st.sidebar.text_input("Search companies", key="flt_search")


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Read filter values from session_state and return the filtered frame."""
    d = df.copy()

    year = st.session_state.get("flt_year", None)
    if year is not None:
        d = d[d["year"] == year]

    sectors = st.session_state.get("flt_sectors", None)
    if sectors:
        d = d[d["sector"].isin(sectors)]

    regions = st.session_state.get("flt_regions", None)
    if regions:
        d = d[d["region"].isin(regions)]

    countries = st.session_state.get("flt_countries", None)
    if countries:
        d = d[d["country"].isin(countries)]

    e_min, e_max   = st.session_state.get("flt_e",   (0.0, 100.0))
    s_min, s_max   = st.session_state.get("flt_s",   (0.0, 100.0))
    g_min, g_max   = st.session_state.get("flt_g",   (0.0, 100.0))
    esg_min, esg_max = st.session_state.get("flt_esg", (0.0, 100.0))
    mc_min, mc_max = st.session_state.get("flt_mc",  (0.0, float(d["market_cap_usd"].max() or 0.0)))

    d = d[(d["E"].between(e_min, e_max)) &
          (d["S"].between(s_min, s_max)) &
          (d["G"].between(g_min, g_max)) &
          (d["ESG_total"].between(esg_min, esg_max)) &
          (d["market_cap_usd"].between(mc_min, mc_max))]

    if st.session_state.get("flt_complete", True):
        d = d.dropna(subset=["E", "S", "G", "ESG_total", "market_cap_usd"])

    search = st.session_state.get("flt_search", "")
    if search:
        d = d[d["company"].str.contains(search, case=False, na=False)]

    return d


@contextmanager
def section(title: str, description: str = ""):
    """
    Guaranteed-nested section: title, description, and all children render
    inside the same bordered Streamlit container. No HTML open/close tags.
    """
    c = st.container(border=True)  # requires Streamlit >= 1.30
    with c:
        st.markdown(f"<div class='sect-title'>{title}</div>", unsafe_allow_html=True)
        if description:
            st.markdown(f"<div class='sect-desc'>{description}</div>", unsafe_allow_html=True)
        yield  # children live *inside* this bordered container


def sidebar_controls() -> Dict:
    st.sidebar.header("Filters")
    year = st.sidebar.selectbox("Year", options=[2024, 2023, 2022, 2021, 2020], index=0, key="year_select_main")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Advanced")
    log_y = st.sidebar.checkbox("Scatter: log y-axis (market cap)", value=True, key="log_y_check")
    trendline = st.sidebar.checkbox("Scatter: show trendline", value=True, key="trendline_check")

    return {"year": year, "log_y": log_y, "trendline": trendline}


def render_tabs(df: pd.DataFrame, cfg: Dict):
    # Draw header
    
    # Draw sidebar filters ONCE (global)
    draw_sidebar_filters(df)

    # Real tabs in the main area
    t1, t2, t3, t4 = st.tabs(["Overview", "Compare", "Sector", "Methodology & Download"])
    with t1: render_overview(df, cfg)      # each tab will call apply_filters()
    with t2: render_compare(df, cfg)
    with t3: render_sector(df, cfg)
    with t4: render_methodology(df)




def _filter_panel(
    df: pd.DataFrame,
    tab_id: str = "overview",
    *,
    show_sector: bool = True,
    show_region: bool = True,
    show_country: bool = True
) -> pd.DataFrame:
    st.sidebar.subheader("Filters")

    years = sorted(df["year"].dropna().unique().tolist())
    year = st.sidebar.selectbox("Year", options=years or [None],
                                index=(len(years)-1 if years else 0),
                                key=f"year_{tab_id}")

    # --- Sector / Region / Country controls (toggleable) ---
    sectors_all = sorted(df["sector"].dropna().unique().tolist())
    if show_sector:
        sel_sectors = st.sidebar.multiselect("Sector", options=sectors_all, default=sectors_all,
                                             key=f"sector_{tab_id}")
    else:
        sel_sectors = sectors_all  # use all sectors when control hidden

    regions_all = sorted(df["region"].dropna().unique().tolist())
    if show_region:
        sel_regions = st.sidebar.multiselect("Region", options=regions_all, default=regions_all,
                                             key=f"region_{tab_id}")
    else:
        sel_regions = regions_all

    countries_all = sorted(df[df["region"].isin(sel_regions)]["country"].dropna().unique().tolist())
    if show_country:
        sel_countries = st.sidebar.multiselect("Country", options=countries_all,
                                               key=f"country_{tab_id}")
    else:
        sel_countries = None

    st.sidebar.markdown("---")
    e_min, e_max = st.sidebar.slider("Environmental (E) Score", 0.0, 100.0, (0.0, 100.0), key=f"e_{tab_id}")
    s_min, s_max = st.sidebar.slider("Social (S) Score", 0.0, 100.0, (0.0, 100.0), key=f"s_{tab_id}")
    g_min, g_max = st.sidebar.slider("Governance (G) Score", 0.0, 100.0, (0.0, 100.0), key=f"g_{tab_id}")
    esg_min, esg_max = st.sidebar.slider("Total ESG Score", 0.0, 100.0, (0.0, 100.0), key=f"esg_{tab_id}")

    st.sidebar.markdown("---")
    max_mc = float((df["market_cap_usd"].max() or 0.0))
    mc_min, mc_max = st.sidebar.slider("Market Cap (Billions USD)", 0.0, max_mc, (0.0, max_mc), key=f"mc_{tab_id}")

    only_complete = st.sidebar.checkbox("Show only rows with complete data", value=True, key=f"complete_{tab_id}")
    company_search = st.sidebar.text_input("Search companies", key=f"search_{tab_id}")

    # ---- Apply filters ----
    d = df.copy()
    if years: d = d[d["year"] == year]
    if sel_sectors: d = d[d["sector"].isin(sel_sectors)]
    if sel_regions: d = d[d["region"].isin(sel_regions)]
    if sel_countries: d = d[d["country"].isin(sel_countries)]

    d = d[(d["E"].between(e_min, e_max)) &
          (d["S"].between(s_min, s_max)) &
          (d["G"].between(g_min, g_max)) &
          (d["ESG_total"].between(esg_min, esg_max)) &
          (d["market_cap_usd"].between(mc_min, mc_max))]

    if only_complete:
        d = d.dropna(subset=["E", "S", "G", "ESG_total", "market_cap_usd"])

    if company_search:
        d = d[d["company"].str.contains(company_search, case=False, na=False)]

    return d


def render_overview(df: pd.DataFrame, cfg: Dict):
    d = apply_filters(df)
    if d.empty:
        st.warning("No rows match the selected filters. Try relaxing filters.")
        return

    with section("Key Performance Indicators"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Average ESG", f"{d['ESG_total'].mean():.2f}")
        c2.metric("Median ESG",  f"{d['ESG_total'].median():.2f}")
        c3.metric("Coverage (companies)", f"{d['company'].nunique()}")
        top = d.sort_values("ESG_total", ascending=False).iloc[0]
        c4.metric("Top company", f"{top['company']} ({top['ESG_total']:.2f})")

    with section("Score Distribution",
                 "Analyze the distribution of ESG scores across companies to understand overall sustainability performance patterns."):
        st.plotly_chart(charts.hist_esg(d), use_container_width=True)

    with section("Sector Performance", "Compare ESG performance across sectors using box plots to identify sector-specific trends."):
        st.plotly_chart(charts.box_by_sector(d), use_container_width=True)

    with section("Size vs Performance", "Relationship between market capitalization and ESG performance."):
        st.plotly_chart(charts.scatter_esg_vs_market(d, log_y=cfg.get("log_y", True), trendline=cfg.get("trendline", True)),
                        use_container_width=True)

    with section("Geographic Distribution", "Average ESG by country."):
        st.plotly_chart(charts.choropleth_country(d), use_container_width=True)

    with section("Detailed Data", "Access and download the complete dataset with all ESG metrics and company information."):
        st.dataframe(d.reset_index(drop=True))
        utils.download_button_csv(d, key="overview_download")


def render_compare(df: pd.DataFrame, cfg: Dict):
    d = apply_filters(df)
    
    with section("Company Selection", "Select companies to compare their ESG performance."):
        companies = st.sidebar.multiselect(
            "Compare companies",
            options=sorted(df["company"].dropna().unique().tolist()),
            max_selections=5, 
            key="companies_compare_main"
        )
        if not companies:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.info("Select companies from the sidebar to compare (up to 5).")
                if st.button("📋 Select Companies", use_container_width=True):
                    # Use JavaScript to focus the companies filter
                    js = f'''
                        <script>
                            window.parent.document.querySelector('input[aria-label*="Compare companies"]').focus();
                        </script>
                        '''
                    st.components.v1.html(js, height=0)
            return

        rows = d[d["company"].isin(companies)]
        if rows.empty:
            st.warning("No selected companies match current filters.")
            return

    with section("Company Profiles", "Key information and overall ESG scores for selected companies."):
        cols = st.columns(len(companies))
        for i, comp in enumerate(companies):
            r = rows[rows["company"] == comp].iloc[0]
            with cols[i]:
                st.subheader(r["company"])
                st.write(f"Ticker: {r.get('ticker','')}")
                st.write(f"Sector: {r.get('sector','')}")
                st.write(f"Region/Country: {r.get('region','')} / {r.get('country','')}")
                st.progress(int(r.get("ESG_total", 0)))

    with section("ESG Score Breakdown", "Detailed comparison of Environmental, Social, and Governance scores."):
        st.plotly_chart(charts.radar_companies(d, companies), use_container_width=True)

    with section("Pillar Comparison", "Side-by-side comparison of E, S, G scores for selected companies."):
        st.plotly_chart(charts.grouped_bars_esg(d, companies), use_container_width=True)


def render_sector(df: pd.DataFrame, cfg: Dict):
    d = apply_filters(df)

    with section("Sector Controls", "Pick a sector to analyze."):
        sectors = sorted(d["sector"].dropna().unique().tolist())
        if not sectors:
            st.warning("No sectors available in filtered data.")
            return
        focus = st.selectbox("Focus sector", options=sectors, index=0, key="sector_focus")

    s = d[d["sector"] == focus]

    with section("Distribution within Sector", "Box plot of ESG scores for companies in the selected sector."):
        st.plotly_chart(charts.box_by_sector(s), use_container_width=True)

    with section("Top 10 by ESG Total"):
        st.dataframe(s.sort_values("ESG_total", ascending=False).head(10).reset_index(drop=True))

    with section("Bottom 10 by ESG Total"):
        st.dataframe(s.sort_values("ESG_total", ascending=True).head(10).reset_index(drop=True))

    with section("Sector Composition Treemap"):
        st.plotly_chart(charts.treemap_sector(s, focus), use_container_width=True)


def render_methodology(df: pd.DataFrame):
    """Render the data & methodology section with download options."""
    d = apply_filters(df)
    
    with section("Data Access & Downloads", "Download the filtered dataset and understand data sources."):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
                ### Understanding the Data
                
                This dashboard currently displays **synthetic demo data** to showcase the analytical 
                capabilities. For real ESG analysis, you would need to obtain data from professional 
                ESG data providers.

                #### How to Get Real ESG Data
                1. **Commercial Data Providers**:
                   - Refinitiv ESG (formerly ASSET4)
                   - MSCI ESG Research
                   - Sustainalytics
                   - S&P Global ESG Scores
                
                2. **Alternative Sources**:
                   - Company Sustainability Reports
                   - CDP (Carbon Disclosure Project)
                   - GRI (Global Reporting Initiative)
                   - Annual Financial Reports
            """)
        
        with col2:
            st.markdown("""
                ### Download Options
                """)
            if not d.empty:
                utils.download_button_csv(
                    d, 
                    "📥 Download Filtered Data (CSV)", 
                    "methodology_download"
                )
                st.markdown("""
                    #### File Contents
                    - Company details
                    - ESG scores & subscores
                    - Market data
                    - Regional information
                    
                    *Note: This is demo data for 
                    illustration purposes only*
                """)
    
    with section("Methodology & Data Sources", "Understanding the data processing and scoring methodology."):
        utils.small_methodology()
        st.caption("This app is for demonstration and portfolio purposes only and should not be used for investment decisions.")

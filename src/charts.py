"""Plot factories for the ESG dashboard using Plotly Express."""
from __future__ import annotations

from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def hist_esg(df: pd.DataFrame, bins: int = 20):
    fig = px.histogram(df, x="ESG_total", nbins=bins, title="ESG_total distribution")
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
    return fig


def box_by_sector(df: pd.DataFrame):
    fig = px.box(df, x="sector", y="ESG_total", points="suspected", title="ESG by Sector")
    fig.update_layout(xaxis_tickangle=-45, margin=dict(t=30))
    return fig


def scatter_esg_vs_market(df: pd.DataFrame, log_y: bool = True, trendline: bool = True):
    # size ~ sqrt market cap for stability
    size = None
    if "market_cap_usd" in df.columns:
        size = df["market_cap_usd"].apply(lambda v: max(1, (v or 0) ** 0.5))

    fig = px.scatter(
        df,
        x="ESG_total",
        y="market_cap_usd",
        color="sector",
        size=size,
        hover_data=["company", "ticker", "region", "country", "E", "S", "G"],
        title="ESG vs Market Cap",
        trendline="ols" if trendline else None,
    )
    if log_y:
        fig.update_yaxes(type="log")
    fig.update_layout(margin=dict(t=30))
    return fig


def choropleth_country(df: pd.DataFrame):
    agg = df.groupby("iso3", dropna=True)["ESG_total"].mean().reset_index()
    agg = agg.dropna(subset=["iso3"])  # drop rows without iso3
    fig = px.choropleth(agg, locations="iso3", color="ESG_total", color_continuous_scale="Viridis", title="Average ESG by Country")
    fig.update_layout(margin=dict(t=30))
    return fig


def radar_companies(df: pd.DataFrame, companies: list[str]):
    rows = df[df["company"].isin(companies)]
    categories = ["E", "S", "G"]
    fig = go.Figure()
    for _, r in rows.iterrows():
        values = [r.get(c, 0) or 0 for c in categories]
        fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill="toself", name=r["company"]))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 100])), showlegend=True, title="E/S/G Radar")
    return fig


def grouped_bars_esg(df: pd.DataFrame, companies: list[str]):
    rows = df[df["company"].isin(companies)]
    melted = rows.melt(id_vars=["company"], value_vars=["E", "S", "G"], var_name="pillar", value_name="score")
    fig = px.bar(melted, x="company", y="score", color="pillar", barmode="group", title="E/S/G by Company")
    return fig


def treemap_sector(df: pd.DataFrame, focus_sector: Optional[str] = None):
    d = df if focus_sector is None else df[df["sector"] == focus_sector]
    fig = px.treemap(d, path=["sector", "company"], values="market_cap_usd", color="ESG_total", title="Market Cap Treemap by Sector")
    return fig

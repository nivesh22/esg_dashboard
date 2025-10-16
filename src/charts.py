"""Plot factories for the ESG dashboard using Plotly.

All charts follow a consistent theme, are interactive by default, and are
designed to blend with the Streamlit app (transparent backgrounds, no titles).
The color system is coherent across visuals and draws from an ESG palette.

Ruff compliance:
- typed functions
- concise, informative docstrings
- no unused imports
"""

from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# --------------------------------------------------------------------------- #
#                                COLOR SYSTEM                                 #
# --------------------------------------------------------------------------- #

# Pillar/categorical colors (consistent across all charts)
COLORS: dict[str, str] = {
    "E": "#16a34a",  # green 600
    "S": "#2563eb",  # blue 600
    "G": "#f59e0b",  # amber 500
    "TOTAL": "#0e7490",  # cyan 700 (overall/ESG_total)
}

# Continuous scale (low -> high) derived from the same hue family for coherence
CONTINUOUS_SCALE: list[str] = [
    "#e6f6f8",
    "#c6eaf0",
    "#a4dce7",
    "#7fcddc",
    "#55bbcE",
    "#2eaac1",
    "#0e7490",
]

# Neutral greys for strokes/borders on dark or light backgrounds
BORDER_COLOR = "rgba(255,255,255,0.28)"
GRID_COLOR = "rgba(128,128,128,0.12)"


# --------------------------------------------------------------------------- #
#                             LAYOUT / STYLING                                #
# --------------------------------------------------------------------------- #

def _apply_common_styling(fig: go.Figure) -> go.Figure:
    """Apply a unified, theme-friendly style with no titles.

    - Transparent backgrounds (blend with Streamlit theme)
    - No figure titles (sections handle headings)
    - Outside ticks, light grid, compact margins
    - Legend moved up and out of the way
    """
    # Base layout (no chart titles)
    fig.update_layout(
        title=None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=24, r=16, t=8, b=24),
        font=dict(family="Inter, Segoe UI, Arial, sans-serif", size=13),
        legend=dict(
            title_text="",              # prevent 'undefined' legend title
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            itemclick="toggleothers",
            itemdoubleclick="toggle",
        ),
        dragmode="pan",
        # Some px figures stash title in layout.title.text; make it explicitly empty
        title_text="",
    )

    # Axes: no titles, light grid
    fig.update_xaxes(
        showgrid=True,
        gridwidth=0.5,
        gridcolor=GRID_COLOR,
        ticks="outside",
        zeroline=False,
        linecolor=BORDER_COLOR,
        mirror=False,
        title_text="",               # prevent 'undefined' axis titles
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=0.5,
        gridcolor=GRID_COLOR,
        ticks="outside",
        zeroline=False,
        linecolor=BORDER_COLOR,
        mirror=False,
        title_text="",               # prevent 'undefined' axis titles
    )

    # Colorbar (for choropleth/treemap): no title
    if hasattr(fig.layout, "coloraxis") and getattr(fig.layout.coloraxis, "colorbar", None):
        fig.update_layout(coloraxis_colorbar=dict(title=None))

    # Strip any auto-added empty/undefined annotations (px sometimes creates one for titles)
    anns = []
    if fig.layout.annotations:
        for ann in fig.layout.annotations:
            txt = (getattr(ann, "text", "") or "").strip().lower()
            if txt in ("", "undefined", "none"):
                continue
            anns.append(ann)
        fig.update_layout(annotations=anns)

    return fig



def _fmt_num(val: float | int | None, digits: int = 1) -> str:
    """Return a safe formatted number string for hover labels."""
    if val is None:
        return "–"
    try:
        return f"{float(val):.{digits}f}"
    except Exception:
        return "–"


# --------------------------------------------------------------------------- #
#                                   CHARTS                                    #
# --------------------------------------------------------------------------- #

def hist_esg(df: pd.DataFrame, bins: int = 20) -> go.Figure:
    """Histogram of ESG total scores.

    Args:
        df: DataFrame with an 'ESG_total' column in [0, 100].
        bins: Number of histogram bins.

    Returns:
        A Plotly Figure.
    """
    fig = px.histogram(
        df,
        x="ESG_total",
        nbins=bins,
        color_discrete_sequence=[COLORS["TOTAL"]],
        opacity=0.95,
    )
    # Interactive/visual polish
    fig.update_traces(
        hovertemplate="Avg ESG Bin Center: %{x:.1f}<br>Count: %{y}<extra></extra>",
        marker_line=dict(width=0.5, color=BORDER_COLOR),
    )
    fig.update_layout(bargap=0.08)
    # Y axis label is self-explanatory; keep axes unlabeled for a clean look
    return _apply_common_styling(fig)


def box_by_sector(df: pd.DataFrame) -> go.Figure:
    """Box plot of ESG totals by sector.

    Args:
        df: DataFrame with 'sector' and 'ESG_total' columns.

    Returns:
        A Plotly Figure.
    """
    fig = px.box(
        df,
        x="sector",
        y="ESG_total",
        points="outliers",
        color_discrete_sequence=[COLORS["TOTAL"]],
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>ESG: %{y:.1f}<extra></extra>",
        marker=dict(opacity=0.5),
    )
    fig.update_layout(showlegend=False)
    fig.update_xaxes(tickangle=-30)
    return _apply_common_styling(fig)


def scatter_esg_vs_market(
    df: pd.DataFrame, *, log_y: bool = True, trendline: bool = True
) -> go.Figure:
    """Scatter of ESG_total vs. market_cap_usd with optional trendline.

    Args:
        df: DataFrame with 'ESG_total' and 'market_cap_usd' columns.
        log_y: Whether to use a log scale for market cap.
        trendline: Whether to add an OLS trendline.

    Returns:
        A Plotly Figure.
    """
    # Use sector as color to aid scanability, but keep palette subdued.
    # (Plotly will auto-assign a categorical cycle; that’s OK for sectors.)
    fig = px.scatter(
        df,
        x="ESG_total",
        y="market_cap_usd",
        color="sector",
        size="market_cap_usd",
        size_max=28,
        hover_data={
            "company": True,
            "ticker": True,
            "region": True,
            "country": True,
            "E": ":.1f",
            "S": ":.1f",
            "G": ":.1f",
            "ESG_total": ":.1f",
            "market_cap_usd": ":.1f",
        },
        trendline="ols" if trendline else None,
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
            "ESG: %{customdata[4]:.1f} | "
            "E: %{customdata[2]:.1f} • S: %{customdata[3]:.1f} • G: %{customdata[5]:.1f}<br>"
            "Mkt Cap: %{y:.1f} B<br>"
            "<extra></extra>"
        ),
        marker=dict(line=dict(width=0.5, color=BORDER_COLOR)),
    )
    if log_y:
        fig.update_yaxes(type="log")
    # Slight padding so points/labels never clip
    fig.update_xaxes(range=[-2, 102])
    return _apply_common_styling(fig)


def choropleth_country(df: pd.DataFrame) -> go.Figure:
    """World choropleth of mean ESG_total aggregated by ISO3.

    Args:
        df: DataFrame with 'iso3' and 'ESG_total' columns.

    Returns:
        A Plotly Figure.
    """
    if "iso3" not in df.columns or "ESG_total" not in df.columns:
        raise ValueError("Expected 'iso3' and 'ESG_total' columns.")

    agg = (
        df.groupby("iso3", dropna=True)["ESG_total"]
          .mean()
          .reset_index()
          .dropna(subset=["iso3"])
    )

    # Cohesive, dark-friendly teal scale (low -> high)
    scale = ["#0b2e35", "#0f4650", "#13606b", "#177a86", "#1994a2", "#1aafbe", "#1ac8d9"]

    fig = px.choropleth(
        agg,
        locations="iso3",
        color="ESG_total",
        color_continuous_scale=scale,
        range_color=[0, 100],
        projection="natural earth",
    )

    # Crisp borders so countries pop on dark backgrounds
    fig.update_traces(
        hovertemplate="<b>%{location}</b><br>Avg ESG: %{z:.2f}<extra></extra>",
        marker_line_color="rgba(255,255,255,0.55)",
        marker_line_width=0.7,
    )

    # Dark map styling that blends with the dashboard
    fig.update_geos(
        projection_type="natural earth",
        showcountries=True,
        countrycolor="rgba(255,255,255,0.35)",
        countrywidth=0.6,
        showcoastlines=True,
        coastlinecolor="rgba(255,255,255,0.18)",
        coastlinewidth=0.6,
        showland=True,
        landcolor="rgba(20,27,38,0.85)",      # subtle slate land tint
        showocean=True,
        oceancolor="rgba(5,12,22,0.95)",      # deep navy ocean
        showlakes=True,
        lakecolor="rgba(5,12,22,0.95)",
        showframe=False,
        fitbounds="locations",
        bgcolor="rgba(0,0,0,0)",
    )

    # Remove titles and use dark-friendly colorbar
    fig.update_layout(
        title=None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=8, t=8, b=8),
        coloraxis_colorbar=dict(
            title=None,
            ticks="outside",
            tickformat=".0f",
            len=0.8,
            thickness=10,
            outlinewidth=0,
            bgcolor="rgba(0,0,0,0)",
        ),
        font=dict(size=13),
    )

    return fig


def radar_companies(df: pd.DataFrame, companies: list[str]) -> go.Figure:
    """Radar chart comparing E, S, G for selected companies.

    Args:
        df: DataFrame with pillar columns 'E', 'S', 'G'.
        companies: Company names to compare (ideally <= 5).

    Returns:
        A Plotly Figure.
    """
    rows = df[df["company"].isin(companies)].copy()
    categories: list[str] = ["E", "S", "G"]

    # Build traces
    fig = go.Figure()
    palette: list[str] = [
        "#60a5fa",  # blue 400
        "#34d399",  # emerald 400
        "#fbbf24",  # amber 400
        "#a78bfa",  # violet 400
        "#f87171",  # red 400
    ]

    for i, (_, r) in enumerate(rows.iterrows()):
        vals = [float(r.get("E", 0) or 0), float(r.get("S", 0) or 0), float(r.get("G", 0) or 0)]
        color = palette[i % len(palette)]
        fig.add_trace(
            go.Scatterpolar(
                r=vals + [vals[0]],
                theta=categories + [categories[0]],
                fill="toself",
                name=str(r.get("company", f"Series {i+1}")),
                line=dict(color=color, width=2),
                fillcolor=color.replace(")", ",0.18)").replace("rgb", "rgba") if color.startswith("rgb")
                else color + "99",  # simple alpha for hex
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "E: %{r[0]:.1f} • S: %{r[1]:.1f} • G: %{r[2]:.1f}<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                range=[0, 100],
                showline=True,
                linecolor=BORDER_COLOR,
                gridcolor=GRID_COLOR,
                ticksuffix="",
            ),
            angularaxis=dict(
                showline=True,
                linecolor=GRID_COLOR,
                gridcolor=GRID_COLOR,
            ),
        ),
        showlegend=True,
        margin=dict(l=8, r=8, t=8, b=8),
    )
    return _apply_common_styling(fig)


def grouped_bars_esg(df: pd.DataFrame, companies: list[str]) -> go.Figure:
    """Grouped bars of E, S, G for selected companies.

    Args:
        df: DataFrame with 'company', 'E', 'S', 'G' columns.
        companies: Company names to include.

    Returns:
        A Plotly Figure.
    """
    rows = df[df["company"].isin(companies)].copy()

    def _bar(name: str, field: str, color: str) -> go.Bar:
        return go.Bar(
            name=name,
            x=rows["company"],
            y=rows[field],
            marker_color=color,
            marker_line=dict(color=BORDER_COLOR, width=0.6),
            hovertemplate=f"{name}: %{{y:.1f}}<extra></extra>",
        )

    fig = go.Figure()
    fig.add_trace(_bar("Environmental", "E", COLORS["E"]))
    fig.add_trace(_bar("Social", "S", COLORS["S"]))
    fig.add_trace(_bar("Governance", "G", COLORS["G"]))

    fig.update_layout(
        barmode="group",
        bargap=0.18,
        bargroupgap=0.08,
        yaxis=dict(range=[0, 100]),
        legend_traceorder="reversed",
    )
    fig.update_xaxes(tickangle=-15)
    return _apply_common_styling(fig)


def treemap_sector(df: pd.DataFrame, focus_sector: Optional[str] = None) -> go.Figure:
    """Treemap of market cap sized tiles, colored by ESG_total.

    Args:
        df: DataFrame with 'sector', 'company', 'market_cap_usd', 'ESG_total'.
        focus_sector: If provided, filter to a single sector.

    Returns:
        A Plotly Figure.
    """
    data = df if focus_sector is None else df[df["sector"] == focus_sector]

    fig = px.treemap(
        data,
        path=["sector", "company"],
        values="market_cap_usd",
        color="ESG_total",
        color_continuous_scale=CONTINUOUS_SCALE,
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Market Cap: %{value:,.1f} B<br>"
            "ESG: %{color:.1f}<extra></extra>"
        ),
        marker=dict(line=dict(color=BORDER_COLOR, width=0.6)),
    )
    return _apply_common_styling(fig)

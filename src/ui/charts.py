"""
src/ui/charts.py
All Plotly figure builders for the GeoOps dashboard.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Shared theme ──────────────────────────────────────────────────────────────

_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#7a8ba8", size=12),
    title_font=dict(family="Space Grotesk, sans-serif", color="#e8edf5", size=15),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
    colorway=["#00d4b4", "#6366f1", "#f59e0b", "#f87171", "#34d399", "#a78bfa"],
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#7a8ba8")),
    margin=dict(l=16, r=16, t=40, b=16),
)

_TEAL_SCALE = [[0, "#1e3a2f"], [1, "#00d4b4"]]
_AMBER_SCALE = [[0, "#1e2a40"], [1, "#f59e0b"]]
_RISK_COLORS  = ["#34d399", "#fbbf24", "#f59e0b", "#f87171"]


def _theme(fig: go.Figure) -> go.Figure:
    fig.update_layout(**_LAYOUT)
    return fig


# ── Issue / QA charts ─────────────────────────────────────────────────────────

def severity_donut(severity_counts: dict) -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=list(severity_counts.keys()),
        values=list(severity_counts.values()),
        hole=0.55,
        marker=dict(
            colors=["#f87171", "#f59e0b", "#fbbf24", "#34d399", "#00d4b4"],
            line=dict(color="#07090f", width=2),
        ),
        textfont=dict(color="#e8edf5"),
    ))
    fig.update_layout(title_text="Severity Distribution", **_LAYOUT)
    return fig


def category_bar(category_counts: dict) -> go.Figure:
    df = (
        pd.DataFrame({"Category": list(category_counts.keys()), "Count": list(category_counts.values())})
        .sort_values("Count", ascending=True)
        .tail(12)
    )
    fig = px.bar(
        df, x="Count", y="Category", orientation="h",
        title="Top Issue Categories",
        color="Count", color_continuous_scale=_TEAL_SCALE,
    )
    fig.update_coloraxes(showscale=False)
    return _theme(fig)


# ── Risk / utility charts ─────────────────────────────────────────────────────

def priority_bar(priority_counts: pd.Series) -> go.Figure:
    df = priority_counts.reset_index()
    df.columns = ["Priority", "Count"]
    fig = px.bar(
        df, x="Priority", y="Count",
        title="Maintenance Priority Distribution",
        color="Count", color_continuous_scale=_TEAL_SCALE,
    )
    fig.update_coloraxes(showscale=False)
    return _theme(fig)


def risk_histogram(risk_scores: pd.Series) -> go.Figure:
    fig = px.histogram(
        risk_scores, nbins=20,
        title="Risk Score Distribution",
        color_discrete_sequence=["#00d4b4"],
    )
    return _theme(fig)


def risk_scatter(df: pd.DataFrame) -> go.Figure:
    """Scatter of risk score vs install year, sized by condition severity."""
    fig = px.scatter(
        df, x="install_year", y="utility_risk_score",
        color="maintenance_priority",
        title="Risk Score vs Install Year",
        color_discrete_map={
            "Critical Priority": "#f87171",
            "High Priority":     "#f59e0b",
            "Medium Priority":   "#fbbf24",
            "Low Priority":      "#34d399",
            "Routine":           "#00d4b4",
        },
        hover_data=["asset_id"] if "asset_id" in df.columns else None,
    )
    return _theme(fig)


# ── Spatial / hotspot charts ──────────────────────────────────────────────────

def zone_risk_bar(hotspots_df: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        hotspots_df, x="pressure_zone", y="avg_risk_score",
        title="Avg Utility Risk by Pressure Zone",
        text="avg_risk_score",
        color="avg_risk_score",
        color_continuous_scale=_AMBER_SCALE,
    )
    fig.update_coloraxes(showscale=False)
    return _theme(fig)


def zone_scatter(hotspots_df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        hotspots_df, x="asset_count", y="avg_risk_score",
        size="critical_priority_count",
        color="pressure_zone",
        title="Zone Risk Concentration",
        color_discrete_sequence=["#00d4b4", "#6366f1", "#f59e0b", "#f87171", "#a78bfa"],
    )
    return _theme(fig)

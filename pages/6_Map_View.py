"""
pages/6_Map_View.py
Interactive asset risk map — Folium marker cluster, colored by risk score.
Requires the pipeline to have run first (session state: geoops_result).
"""

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src.ui.styles import inject_styles
from src.ui.components import section_header, teal_divider, metric_panel

st.set_page_config(
    page_title="GeoOps · Map View",
    page_icon="◉",
    layout="wide",
)
inject_styles()


# ── Risk color helper ─────────────────────────────────────────────────────────

def _risk_color(score: float) -> str:
    if score >= 75:
        return "#f87171"   # red   — critical
    if score >= 55:
        return "#f59e0b"   # amber — high
    if score >= 35:
        return "#fbbf24"   # yellow — medium
    return "#34d399"       # green — low / routine


def _risk_label(score: float) -> str:
    if score >= 75: return "Critical Priority"
    if score >= 55: return "High Priority"
    if score >= 35: return "Medium Priority"
    return "Low / Routine"


# ── Map builder ───────────────────────────────────────────────────────────────

def build_map(merged_df: pd.DataFrame) -> str:
    """Build a Folium map and return its HTML string."""
    try:
        import folium
        from folium.plugins import MarkerCluster
    except ImportError:
        return "<p style='color:#f87171;font-family:Inter,sans-serif;'>Install folium: <code>pip install folium</code></p>"

    lat_col = next((c for c in ["latitude", "lat", "LAT", "y"] if c in merged_df.columns), None)
    lon_col = next((c for c in ["longitude", "lon", "LON", "x"] if c in merged_df.columns), None)

    if lat_col is None or lon_col is None:
        return "<p style='color:#f59e0b;font-family:Inter,sans-serif;'>No latitude/longitude columns found in dataset. Map view requires <code>latitude</code> and <code>longitude</code> fields.</p>"

    valid = merged_df.dropna(subset=[lat_col, lon_col]).copy()
    valid[lat_col] = pd.to_numeric(valid[lat_col], errors="coerce")
    valid[lon_col] = pd.to_numeric(valid[lon_col], errors="coerce")
    valid = valid.dropna(subset=[lat_col, lon_col])

    if valid.empty:
        return "<p style='color:#f59e0b;font-family:Inter,sans-serif;'>No valid coordinates found to plot.</p>"

    center_lat = float(valid[lat_col].mean())
    center_lon = float(valid[lon_col].mean())

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles="CartoDB dark_matter",
        prefer_canvas=True,
    )

    cluster = MarkerCluster(
        options={
            "maxClusterRadius": 40,
            "disableClusteringAtZoom": 16,
        }
    ).add_to(m)

    for _, row in valid.iterrows():
        score     = float(row.get("utility_risk_score", 0))
        asset_id  = str(row.get("asset_id", "—"))
        condition = str(row.get("condition", "—"))
        material  = str(row.get("material", "—"))
        priority  = str(row.get("maintenance_priority", _risk_label(score)))
        action    = str(row.get("recommended_action", "—"))
        color     = _risk_color(score)

        popup_html = f"""
        <div style="font-family:Inter,sans-serif;font-size:13px;min-width:220px;
                    background:#0d1524;color:#c9d1e0;padding:14px;border-radius:8px;">
            <div style="font-weight:700;font-size:15px;color:#e8edf5;margin-bottom:8px;">
                {asset_id}
            </div>
            <div style="color:{color};font-size:20px;font-weight:700;margin-bottom:6px;">
                Risk Score: {score:.0f}
            </div>
            <div style="margin-bottom:4px;"><b>Priority:</b> {priority}</div>
            <div style="margin-bottom:4px;"><b>Condition:</b> {condition}</div>
            <div style="margin-bottom:4px;"><b>Material:</b> {material}</div>
            <div style="margin-top:10px;padding:8px;background:rgba(255,255,255,0.05);
                        border-radius:6px;color:#fbbf24;font-size:12px;">
                ⚑ {action}
            </div>
        </div>
        """

        folium.CircleMarker(
            location=[float(row[lat_col]), float(row[lon_col])],
            radius=6 + score / 20,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.75,
            weight=1.5,
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=f"{asset_id} — Risk: {score:.0f}",
        ).add_to(cluster)

    # Legend
    legend_html = """
    <div style="position:fixed;bottom:30px;right:30px;z-index:9999;
                background:#0d1524;border:1px solid rgba(0,212,180,0.2);
                border-radius:10px;padding:14px 18px;font-family:Inter,sans-serif;
                font-size:12px;color:#c9d1e0;">
        <div style="font-weight:700;margin-bottom:10px;color:#e8edf5;">Risk Score Legend</div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
            <div style="width:12px;height:12px;border-radius:50%;background:#f87171;"></div>
            Critical (≥ 75)
        </div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
            <div style="width:12px;height:12px;border-radius:50%;background:#f59e0b;"></div>
            High (55–74)
        </div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
            <div style="width:12px;height:12px;border-radius:50%;background:#fbbf24;"></div>
            Medium (35–54)
        </div>
        <div style="display:flex;align-items:center;gap:8px;">
            <div style="width:12px;height:12px;border-radius:50%;background:#34d399;"></div>
            Low / Routine (&lt; 35)
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m._repr_html_()


# ── Page ──────────────────────────────────────────────────────────────────────

section_header("SPATIAL RISK VIEW", "Interactive Asset Risk Map",
               "Assets plotted by location and colored by utility risk score. Click any marker for detail.")

if "geoops_result" not in st.session_state or "loaded_df" not in st.session_state:
    st.warning("Run the full assessment first via the **Assessment** page, then return here.")
    st.stop()

result     = st.session_state["geoops_result"]
assets_df  = st.session_state["loaded_df"]
utility_df = pd.read_csv(result["outputs"]["utility_intelligence_csv"])

# Merge risk scores back onto original asset data
merged = assets_df.copy()
merged["utility_risk_score"]  = utility_df["utility_risk_score"].values
merged["maintenance_priority"] = utility_df["maintenance_priority"].values
merged["recommended_action"]   = utility_df["recommended_action"].values

teal_divider()

# Quick summary metrics above the map
c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_panel("Total Assets", f"{len(merged):,}", "plotted on map")
with c2:
    crit = int((utility_df["maintenance_priority"] == "Critical Priority").sum())
    metric_panel("Critical Risk", crit, "red markers", "mp-danger")
with c3:
    high = int((utility_df["maintenance_priority"] == "High Priority").sum())
    metric_panel("High Risk", high, "amber markers", "mp-warning")
with c4:
    lat_col = next((c for c in ["latitude", "lat"] if c in merged.columns), None)
    mappable = int(merged[lat_col].notna().sum()) if lat_col else 0
    metric_panel("Mappable Assets", mappable, "with valid coordinates")

teal_divider()

# Filter controls
with st.expander("Filter by Risk Level", expanded=False):
    selected_priorities = st.multiselect(
        "Show priorities",
        ["Critical Priority", "High Priority", "Medium Priority", "Low Priority", "Routine"],
        default=["Critical Priority", "High Priority", "Medium Priority", "Low Priority", "Routine"],
    )
    if selected_priorities:
        merged = merged[merged["maintenance_priority"].isin(selected_priorities)]

# Render map
map_html = build_map(merged)
components.html(map_html, height=600, scrolling=False)

teal_divider()

# Top 10 riskiest assets table
section_header("HIGHEST RISK ASSETS", "Top 10 by Risk Score")
display_cols = [c for c in [
    "asset_id", "utility_risk_score", "maintenance_priority",
    "condition", "material", "install_year", "pressure_zone",
] if c in merged.columns]
st.dataframe(
    merged.nlargest(10, "utility_risk_score")[display_cols],
    use_container_width=True,
    height=280,
)

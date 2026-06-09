"""
app.py — GeoOps Intelligence Layer
Entry point for the Streamlit dashboard.

Run locally:
    streamlit run app.py

This file is intentionally thin. All logic lives in:
    src/ui/          — styles, components, charts
    src/pipeline/    — analysis orchestration
    src/geoqa/       — data quality checks
    src/intelligence/— explainability + recommendations
    src/risk/        — asset risk scoring
"""

import os
from pathlib import Path

import pandas as pd
import streamlit as st

from src.ui.styles import inject_styles
from src.ui.components import (
    hero_bar, section_header, teal_divider,
    metric_panel, score_panel, explain_panel,
    pipeline_diagram, readiness_badge_html,
)
from src.ui.charts import (
    severity_donut, category_bar,
    priority_bar, risk_histogram,
    zone_risk_bar, zone_scatter,
)

try:
    from src.pipeline.geoops_pipeline import run_geoops_pipeline
    from src.arcgis.feature_layer_loader import load_arcgis_feature_layer
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="GeoOps // Municipal Intelligence",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_styles()

# ── Sample data path ──────────────────────────────────────────────────────────

SAMPLE_DATA_PATH = Path("data/sample_water_mains.csv")


# ── Demo data loader ──────────────────────────────────────────────────────────

def _create_inline_demo() -> pd.DataFrame:
    """Fallback synthetic data if sample CSV is missing."""
    rows = []
    for i in range(1, 501):
        rows.append({
            "asset_id":             f"HYD-{i:05d}" if i % 19 != 0 else "",
            "condition":            ["Good", "Fair", "Poor", "Critical", "", "Broken"][i % 6],
            "install_year":         2035 if i % 41 == 0 else 1945 + (i % 78),
            "last_inspection_date": "" if i % 12 == 0 else "2022-05-01",
            "diameter_in":          999 if i % 37 == 0 else [4, 6, 8, 10, 12, 16][i % 6],
            "pressure_zone":        "" if i % 14 == 0 else f"Zone {chr(65 + (i % 5))}",
            "material":             ["Cast Iron", "PVC", "Ductile Iron", "", "Steel"][i % 5],
            "status":               ["Active", "Inactive", "Active", "Unknown"][i % 4],
            "latitude":             40.62 + (i // 50) * 0.006,
            "longitude":            -89.70 + (i % 50) * 0.004,
        })
    return pd.DataFrame(rows)


# ── Data loader ───────────────────────────────────────────────────────────────

def load_selected_data(data_source: str) -> pd.DataFrame | None:
    if data_source == "Sample Dataset (Water Mains)":
        if SAMPLE_DATA_PATH.exists():
            df = pd.read_csv(SAMPLE_DATA_PATH)
            st.sidebar.success(f"✓ Sample dataset loaded — {len(df):,} assets")
        else:
            df = _create_inline_demo()
            st.sidebar.info("Sample CSV not found — using inline demo data")
        return df

    elif data_source == "Upload CSV":
        uploaded = st.sidebar.file_uploader("Upload municipal asset CSV", type=["csv"])
        if uploaded:
            df = pd.read_csv(uploaded)
            st.sidebar.success(f"✓ Loaded {len(df):,} records")
            return df

    elif data_source == "ArcGIS Feature Layer":
        st.sidebar.markdown(
            '<p style="font-size:12px;color:#4a5568;margin-bottom:8px;">'
            "Paste a public ArcGIS Feature Layer URL.</p>",
            unsafe_allow_html=True,
        )
        layer_url   = st.sidebar.text_area("Layer URL", height=100,
                                            placeholder="https://.../FeatureServer/0")
        max_records = st.sidebar.number_input("Max records", 100, 50000, 5000, 500)

        if st.sidebar.button("Connect Layer", use_container_width=True):
            if not layer_url.strip():
                st.sidebar.error("Enter a valid ArcGIS layer URL.")
            elif not PIPELINE_AVAILABLE:
                st.sidebar.error("ArcGIS loader not available in this environment.")
            else:
                with st.spinner("Connecting to ArcGIS..."):
                    try:
                        df = load_arcgis_feature_layer(layer_url.strip(), max_records=max_records)
                        st.session_state["loaded_arcgis_df"] = df
                        st.sidebar.success(f"✓ {len(df):,} records loaded")
                    except Exception as exc:
                        st.sidebar.error(f"Connection failed: {exc}")

        if "loaded_arcgis_df" in st.session_state:
            return st.session_state["loaded_arcgis_df"]

    return None


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:

    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="padding:16px 0 20px;">
            <div style="font-family:'Space Grotesk',sans-serif;font-size:20px;
                        font-weight:700;color:#e8edf5;letter-spacing:-0.3px;">⬡ GeoOps</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                        color:#00d4b4;letter-spacing:0.15em;margin-top:3px;">
                MUNICIPAL INTELLIGENCE
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section">Data Source</div>', unsafe_allow_html=True)
        data_source = st.radio(
            "",
            ["Sample Dataset (Water Mains)", "Upload CSV", "ArcGIS Feature Layer"],
            label_visibility="collapsed",
        )

        st.markdown('<div class="sidebar-section">Pipeline</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                    color:#374151;line-height:2.2;">
            INTAKE → GEO QA → READINESS<br>→ RISK ENGINE → EXPLAINABILITY<br>
            → RECOMMENDATIONS → EXPORT
        </div>""", unsafe_allow_html=True)

    df = load_selected_data(data_source)

    # Store in session so map page can access it
    if df is not None:
        st.session_state["loaded_df"] = df

    # Hero bar
    hero_bar(
        records=len(df) if df is not None else None,
        fields=len(df.columns) if df is not None else None,
    )

    if df is None:
        st.markdown("""
        <div style="text-align:center;padding:80px 0;">
            <div style="font-family:'Space Grotesk',sans-serif;font-size:18px;
                        color:#374151;margin-bottom:8px;">Select a data source to begin</div>
            <div style="font-size:13px;color:#1f2937;">
                Choose from the sidebar: sample data, CSV upload, or a live ArcGIS Feature Layer.
            </div>
        </div>""", unsafe_allow_html=True)
        return

    # Tab layout
    tabs = st.tabs([
        "⬡  Overview",
        "◈  Assessment",
        "⚑  Issue Intel",
        "⚙  Risk Intel",
        "◉  Spatial Intel",
        "✦  Explainability",
        "⬚  ArcGIS Fit",
        "↓  Exports",
        "◎  Roadmap",
    ])

    safe_df = df.drop(columns=["SHAPE", "geometry", "geom"], errors="ignore")

    # ── Tab 0: Overview ───────────────────────────────────────────────────────
    with tabs[0]:
        section_header("DATASET PROFILE", "Loaded Asset Overview",
                        "Quick snapshot before analysis runs.")
        c1, c2, c3, c4 = st.columns(4)
        with c1: metric_panel("Total Records",  f"{len(df):,}", "Features loaded")
        with c2: metric_panel("Total Fields",   len(df.columns), "Attributes available")
        with c3: metric_panel("Missing Values", f"{int(safe_df.isna().sum().sum()):,}",
                               "Completeness flags", "mp-warning")
        with c4: metric_panel("Duplicate Rows", int(safe_df.duplicated().sum()),
                               "Exact duplicates",
                               "mp-danger" if safe_df.duplicated().sum() > 0 else "mp-accent")
        teal_divider()
        section_header("CAPABILITIES", "What GeoOps Delivers")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""<div class="glass-card">
                <div class="glass-card-title">⬡ GIS Quality Intelligence</div>
                <div class="glass-card-body">Detects missing IDs, invalid attributes, duplicate assets,
                stale inspections, and geometry anomalies across your full feature dataset.</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""<div class="glass-card">
                <div class="glass-card-title">◈ Asset Risk Scoring</div>
                <div class="glass-card-body">Scores every asset 0–100 based on age, condition,
                inspection currency, and data quality — with full per-asset explanation.</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown("""<div class="glass-card">
                <div class="glass-card-title">↓ ArcGIS-Ready Outputs</div>
                <div class="glass-card-body">Exports prioritized review layers, spatial hotspot
                intelligence, and analyst recommendations ready for ArcGIS import.</div>
            </div>""", unsafe_allow_html=True)
        teal_divider()
        section_header("PIPELINE", "Analysis Flow")
        pipeline_diagram([
            "GIS Data In", "GeoQA Engine", "Readiness Score",
            "Risk Engine", "Explainability", "ArcGIS Export",
        ])
        teal_divider()
        section_header("RAW DATA", "Dataset Preview", "First 50 records")
        st.dataframe(df.head(50), use_container_width=True, height=320)

    # ── Tab 1: Assessment ─────────────────────────────────────────────────────
    with tabs[1]:
        section_header("GIS HEALTH", "Full Municipal Assessment",
                        "Run the complete GeoOps pipeline.")
        if not PIPELINE_AVAILABLE:
            st.info("Pipeline modules not found. Connect your src/ package to enable full analysis.")

        run_col, _ = st.columns([2, 3])
        with run_col:
            if st.button("▶  Run Full GeoOps Assessment", type="primary", use_container_width=True):
                if not PIPELINE_AVAILABLE:
                    st.error("Pipeline unavailable — install src/ modules.")
                else:
                    with st.spinner("Running decision intelligence pipeline..."):
                        result = run_geoops_pipeline(df)
                        st.session_state["geoops_result"] = result

        if "geoops_result" not in st.session_state:
            st.markdown('<p style="color:#374151;font-size:14px;margin-top:24px;">'
                        'Assessment results will appear here after running.</p>',
                        unsafe_allow_html=True)
        else:
            result    = st.session_state["geoops_result"]
            readiness = result["readiness_summary"]
            issue_sum = result["issue_summary"]
            teal_divider()
            section_header("SCORES", "Executive Readiness Dashboard")
            c1, c2, c3, c4 = st.columns(4)
            with c1: score_panel("Overall GIS Health",  readiness["overall_gis_health_score"])
            with c2: score_panel("Data Quality",         readiness["data_quality_score"])
            with c3: score_panel("Utility Readiness",    readiness["utility_network_readiness_score"])
            with c4: score_panel("Asset Readiness",      readiness["asset_management_readiness_score"])
            st.markdown(
                f'<p style="margin-top:6px;">Readiness Level &nbsp;'
                f'{readiness_badge_html(readiness["readiness_level"])}</p>',
                unsafe_allow_html=True,
            )
            teal_divider()
            section_header("RECOMMENDATIONS", "Analyst Action Plan")
            for rec in result.get("recommendations", []):
                st.warning(rec)

    # ── Tab 2: Issue Intelligence ─────────────────────────────────────────────
    with tabs[2]:
        section_header("ISSUE INTELLIGENCE", "Flagged Records & Priority Ranking")
        if "geoops_result" not in st.session_state:
            st.warning("Run the assessment first (◈ Assessment tab).")
        else:
            outputs      = st.session_state["geoops_result"]["outputs"]
            issues_df    = pd.read_csv(outputs["issues_csv"])
            priorities_df = pd.read_csv(outputs["priorities_csv"])

            issue_sum = st.session_state["geoops_result"]["issue_summary"]
            c1, c2, c3 = st.columns(3)
            with c1: metric_panel("Total Issues",  issue_sum["total_issues"], "All QA flags")
            with c2: metric_panel("Critical", issue_sum.get("severity_breakdown", {}).get("Critical", 0),
                                  "Immediate action", "mp-danger")
            with c3: metric_panel("High",     issue_sum.get("severity_breakdown", {}).get("High", 0),
                                  "Near-term review", "mp-warning")

            teal_divider()
            left, right = st.columns(2)
            with left:
                sev = issue_sum.get("severity_breakdown", {})
                if sev:
                    st.plotly_chart(severity_donut(sev), use_container_width=True)
            with right:
                cat = issue_sum.get("category_breakdown", {})
                if cat:
                    st.plotly_chart(category_bar(cat), use_container_width=True)

            teal_divider()
            f1, f2 = st.columns(2)
            with f1:
                sel_sev = st.multiselect("Severity", sorted(issues_df["severity"].dropna().unique()),
                                          default=list(issues_df["severity"].dropna().unique()))
            with f2:
                sel_cat = st.multiselect("Category", sorted(issues_df["issue_category"].dropna().unique()),
                                          default=list(issues_df["issue_category"].dropna().unique()))
            filtered = issues_df[
                issues_df["severity"].isin(sel_sev) & issues_df["issue_category"].isin(sel_cat)
            ]
            section_header("FLAGGED RECORDS", f"{len(filtered):,} matching issues")
            st.dataframe(filtered, use_container_width=True, height=340)
            teal_divider()
            section_header("REVIEW PRIORITIES", "Ranked by Risk Score")
            st.dataframe(priorities_df, use_container_width=True, height=320)

    # ── Tab 3: Risk Intelligence ──────────────────────────────────────────────
    with tabs[3]:
        section_header("RISK INTELLIGENCE", "Asset Risk Scoring & Maintenance Prioritization")
        if "geoops_result" not in st.session_state:
            st.warning("Run the assessment first.")
        else:
            udf = pd.read_csv(st.session_state["geoops_result"]["outputs"]["utility_intelligence_csv"])
            c1, c2, c3 = st.columns(3)
            with c1: metric_panel("Peak Risk Score", int(udf["utility_risk_score"].max()),
                                   "Highest asset risk", "mp-danger")
            with c2: metric_panel("Critical Priority",
                                   int((udf["maintenance_priority"] == "Critical Priority").sum()),
                                   "Immediate action needed", "mp-danger")
            with c3: metric_panel("High Priority",
                                   int((udf["maintenance_priority"] == "High Priority").sum()),
                                   "Near-term maintenance", "mp-warning")
            teal_divider()
            left, right = st.columns(2)
            with left:
                st.plotly_chart(priority_bar(udf["maintenance_priority"].value_counts()),
                                use_container_width=True)
            with right:
                st.plotly_chart(risk_histogram(udf["utility_risk_score"]),
                                use_container_width=True)
            teal_divider()
            section_header("TOP RISK ASSETS", "Highest-Scoring Records")
            st.dataframe(udf.head(25), use_container_width=True, height=360)

    # ── Tab 4: Spatial Intelligence ───────────────────────────────────────────
    with tabs[4]:
        section_header("SPATIAL INTELLIGENCE", "Pressure Zone Risk Hotspots")
        if "geoops_result" not in st.session_state:
            st.warning("Run the assessment first.")
        else:
            hp_path = st.session_state["geoops_result"]["outputs"].get("spatial_hotspots_csv")
            if not hp_path or not os.path.exists(hp_path):
                st.info("Dataset does not contain a `pressure_zone` field.")
            else:
                hdf = pd.read_csv(hp_path)
                if hdf.empty:
                    st.info("No hotspot patterns detected.")
                else:
                    left, right = st.columns(2)
                    with left: st.plotly_chart(zone_risk_bar(hdf), use_container_width=True)
                    with right: st.plotly_chart(zone_scatter(hdf), use_container_width=True)
                    teal_divider()
                    st.dataframe(hdf, use_container_width=True, height=280)
                    teal_divider()
                    section_header("HOTSPOT INSIGHTS", "Automated Observations")
                    for insight in st.session_state["geoops_result"].get("hotspot_insights", []):
                        st.warning(insight)

    # ── Tab 5: Explainability ─────────────────────────────────────────────────
    with tabs[5]:
        section_header("EXPLAINABILITY", "Why Was This Asset Flagged?",
                        "Score breakdown and plain-English explanation for the top 10 highest-risk assets.")
        if "geoops_result" not in st.session_state:
            st.warning("Run the assessment first.")
        else:
            explanations = st.session_state["geoops_result"].get("explanations", [])
            if not explanations:
                st.info("No explanations generated. Re-run the assessment.")
            else:
                st.markdown(
                    '<p style="font-size:13px;color:#4a5568;margin-bottom:16px;">'
                    "Each panel shows the exact factors that drove the risk score, "
                    "the point contribution of each factor, and the recommended action.</p>",
                    unsafe_allow_html=True,
                )
                for exp in explanations:
                    explain_panel(exp)

    # ── Tab 6: ArcGIS Fit ─────────────────────────────────────────────────────
    with tabs[6]:
        section_header("ARCGIS INTEGRATION", "How GeoOps Fits Your Existing Workflow")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""<div class="glass-card">
                <div class="glass-card-title">⬚ Without GeoOps</div>
                <div class="glass-card-body">
                ArcGIS Data → Manual Review → Cleanup → Delivery<br><br>
                Time-intensive, inconsistent, no audit trail.
                </div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""<div class="glass-card">
                <div class="glass-card-title">⬡ With GeoOps</div>
                <div class="glass-card-body">
                ArcGIS Feature Layer → GeoOps Intake → GeoQA + Risk Scoring →
                Explainability → Issue Layer Export → Analyst Review in ArcGIS<br><br>
                Automated, scored, explainable, repeatable.
                </div></div>""", unsafe_allow_html=True)
        teal_divider()
        st.markdown("""<div class="glass-card" style="max-width:680px;">
            <div class="glass-card-title">◈ ArcGIS Remains System of Record</div>
            <div class="glass-card-body">
            GeoOps adds a decision intelligence layer around ArcGIS — it never replaces it.
            Features are loaded from Feature Layers, enriched with QA scores and risk rankings,
            then exported back as analyst-ready CSVs and GeoJSON that slot directly into
            your existing ArcGIS workflow without migration or disruption.
            </div></div>""", unsafe_allow_html=True)

    # ── Tab 7: Exports ────────────────────────────────────────────────────────
    with tabs[7]:
        section_header("GENERATED OUTPUTS", "Download Assessment Files")
        if "geoops_result" not in st.session_state:
            st.warning("Run the assessment first.")
        else:
            outputs = st.session_state["geoops_result"]["outputs"]
            for name, path in outputs.items():
                if path and os.path.exists(path):
                    with open(path, "rb") as f:
                        col, _ = st.columns([2, 3])
                        with col:
                            st.download_button(
                                label=f"↓  {name.replace('_', ' ').title()}",
                                data=f,
                                file_name=os.path.basename(path),
                                use_container_width=True,
                            )

    # ── Tab 8: Roadmap ────────────────────────────────────────────────────────
    with tabs[8]:
        section_header("PRODUCT ROADMAP", "Development Phases")
        st.markdown("""
        <div class="roadmap-phase">
            <h4>Phase 1 — Clean MVP &nbsp;<span class="badge badge-success" style="font-size:11px;">Complete</span></h4>
            <ul>
                <li>Data intake: CSV, ArcGIS REST, sample datasets</li>
                <li>GeoQA engine with severity classification (15 checks)</li>
                <li>Asset risk scoring with explainability layer</li>
                <li>Expanded recommendation engine (7 action codes)</li>
                <li>Interactive Folium risk map</li>
                <li>Readiness scoring dashboard</li>
                <li>51 unit tests — all passing</li>
            </ul>
        </div>
        <div class="roadmap-phase roadmap-phase-warning">
            <h4>Phase 2 — GeoAI Enrichment &nbsp;<span class="badge badge-warning" style="font-size:11px;">Planned</span></h4>
            <ul>
                <li>Anomaly detection (Isolation Forest on inspection gaps, spatial outliers)</li>
                <li>GeoOps Copilot — natural language dataset Q&amp;A</li>
                <li>ArcGIS Online authenticated access (OAuth token)</li>
                <li>Scheduled QA runs via config</li>
            </ul>
        </div>
        <div class="roadmap-phase roadmap-phase-info">
            <h4>Phase 3 — Platform Architecture &nbsp;<span class="badge badge-info" style="font-size:11px;">Roadmap</span></h4>
            <ul>
                <li>FastAPI backend + React frontend</li>
                <li>PostgreSQL/PostGIS for persistent asset records</li>
                <li>User roles: Analyst, Manager, Admin</li>
                <li>ArcGIS Webhooks for real-time sync</li>
            </ul>
        </div>
        <div class="roadmap-phase roadmap-phase-dim">
            <h4>Phase 4 — Enterprise Deployment &nbsp;<span class="badge badge-info" style="font-size:11px;">Future</span></h4>
            <ul>
                <li>Multi-tenant SaaS architecture</li>
                <li>AWS/Azure GovCloud for utility clients</li>
                <li>ArcGIS Enterprise compatibility</li>
                <li>REST API for Power BI / Tableau embedding</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

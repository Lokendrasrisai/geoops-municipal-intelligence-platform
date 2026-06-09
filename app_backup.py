import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ── Optional pipeline imports (gracefully handled if missing) ─────────────────
try:
    from src.pipeline.geoops_pipeline import run_geoops_pipeline
    from src.arcgis.feature_layer_loader import load_arcgis_feature_layer
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GeoOps // Municipal Intelligence",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS  — dark command-center aesthetic
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
/* ── Reset & base ──────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #07090f;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% 0%, rgba(0, 212, 180, 0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 100%, rgba(99, 102, 241, 0.06) 0%, transparent 60%);
    background-attachment: fixed;
}

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 2rem; max-width: 1600px; }

/* ── Sidebar ───────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0b0e1a !important;
    border-right: 1px solid rgba(0, 212, 180, 0.12);
}
[data-testid="stSidebar"] * { color: #c9d1e0 !important; }
[data-testid="stSidebar"] .stRadio label {
    padding: 8px 14px;
    border-radius: 8px;
    transition: background 0.2s;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(0, 212, 180, 0.08);
}

/* ── Wordmark / top bar ────────────────────────────────────────────────────── */
.wordmark {
    display: flex;
    align-items: baseline;
    gap: 10px;
    margin-bottom: 4px;
}
.wordmark-main {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 32px;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: #e8edf5;
}
.wordmark-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    color: #00d4b4;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 3px 8px;
    background: rgba(0, 212, 180, 0.1);
    border: 1px solid rgba(0, 212, 180, 0.25);
    border-radius: 4px;
}
.hero-bar {
    padding: 28px 32px;
    border-radius: 16px;
    background: linear-gradient(135deg, #0d1524 0%, #111827 100%);
    border: 1px solid rgba(0, 212, 180, 0.15);
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero-bar::before {
    content: '';
    position: absolute;
    top: -1px; left: -1px; right: -1px;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00d4b4, #6366f1, transparent);
}
.hero-sub {
    font-size: 14px;
    color: #6b7a99;
    margin-top: 8px;
    max-width: 800px;
    line-height: 1.6;
}
.hero-stats {
    display: flex;
    gap: 32px;
    margin-top: 20px;
}
.hero-stat {
    display: flex;
    flex-direction: column;
}
.hero-stat-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 22px;
    font-weight: 500;
    color: #00d4b4;
}
.hero-stat-label {
    font-size: 11px;
    color: #4a5568;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 2px;
}

/* ── Glass cards ───────────────────────────────────────────────────────────── */
.glass-card {
    background: rgba(13, 21, 36, 0.85);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 22px 24px;
    backdrop-filter: blur(12px);
    transition: border-color 0.2s, box-shadow 0.2s;
    height: 100%;
}
.glass-card:hover {
    border-color: rgba(0, 212, 180, 0.2);
    box-shadow: 0 0 24px rgba(0, 212, 180, 0.05);
}
.glass-card-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 13px;
    font-weight: 600;
    color: #00d4b4;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 10px;
}
.glass-card-body {
    font-size: 14px;
    color: #7a8ba8;
    line-height: 1.65;
}

/* ── Metric cards ──────────────────────────────────────────────────────────── */
.metric-panel {
    background: linear-gradient(145deg, #0d1524 0%, #111827 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
    margin-bottom: 14px;
}
.metric-panel::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,212,180,0.3), transparent);
}
.mp-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    color: #4a5568;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 8px;
}
.mp-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 36px;
    font-weight: 700;
    color: #e8edf5;
    line-height: 1;
    margin-bottom: 6px;
    letter-spacing: -1px;
}
.mp-helper {
    font-size: 12px;
    color: #4a5568;
}
.mp-accent { color: #00d4b4; }
.mp-warning { color: #f59e0b; }
.mp-danger  { color: #f87171; }

/* ── Score ring variant ────────────────────────────────────────────────────── */
.score-panel {
    background: linear-gradient(145deg, #0d1524 0%, #111827 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 22px;
    text-align: center;
    margin-bottom: 14px;
    position: relative;
    overflow: hidden;
}
.score-number {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 48px;
    font-weight: 700;
    letter-spacing: -2px;
    line-height: 1;
    margin-bottom: 4px;
}
.score-label {
    font-size: 11px;
    color: #4a5568;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 6px;
}
.score-status {
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.05em;
}

/* ── Badges ────────────────────────────────────────────────────────────────── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.badge-success { background: rgba(0, 212, 180, 0.12); color: #00d4b4; border: 1px solid rgba(0,212,180,0.25); }
.badge-warning { background: rgba(245, 158, 11, 0.12); color: #f59e0b; border: 1px solid rgba(245,158,11,0.25); }
.badge-danger  { background: rgba(248, 113, 113, 0.12); color: #f87171; border: 1px solid rgba(248,113,113,0.25); }
.badge-info    { background: rgba(99, 102, 241, 0.12); color: #818cf8; border: 1px solid rgba(99,102,241,0.25); }

/* ── Flow pipeline ─────────────────────────────────────────────────────────── */
.pipeline-wrap {
    display: flex;
    align-items: center;
    gap: 0;
    flex-wrap: wrap;
    margin: 16px 0;
}
.pipe-node {
    background: rgba(13, 21, 36, 0.9);
    border: 1px solid rgba(0, 212, 180, 0.2);
    border-radius: 8px;
    padding: 10px 18px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 13px;
    font-weight: 600;
    color: #c9d1e0;
    white-space: nowrap;
}
.pipe-arrow {
    color: rgba(0,212,180,0.35);
    font-size: 18px;
    padding: 0 4px;
    flex-shrink: 0;
}

/* ── Section header ────────────────────────────────────────────────────────── */
.section-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #00d4b4;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    margin-bottom: 6px;
}
.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #e8edf5;
    margin-bottom: 4px;
}

/* ── Run button override ───────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #00d4b4 0%, #0891b2 100%) !important;
    color: #07090f !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    height: 3rem !important;
    letter-spacing: 0.02em;
    transition: opacity 0.2s, transform 0.15s !important;
}
.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}

/* ── Tabs override ─────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(13, 21, 36, 0.6);
    border-radius: 10px;
    padding: 4px;
    border: 1px solid rgba(255,255,255,0.06);
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 7px !important;
    color: #6b7a99 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    border: none !important;
    transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(0, 212, 180, 0.12) !important;
    color: #00d4b4 !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-border"] { display: none !important; }
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* ── Data table ────────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.07) !important;
}

/* ── Alerts ────────────────────────────────────────────────────────────────── */
.stSuccess { background: rgba(0,212,180,0.07) !important; border-left-color: #00d4b4 !important; color: #00d4b4 !important; }
.stWarning { background: rgba(245,158,11,0.07) !important; border-left-color: #f59e0b !important; color: #f59e0b !important; }
.stInfo    { background: rgba(99,102,241,0.07) !important; border-left-color: #818cf8 !important; color: #818cf8 !important; }

/* ── Sidebar section label ─────────────────────────────────────────────────── */
.sidebar-section {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: rgba(0,212,180,0.6);
    text-transform: uppercase;
    letter-spacing: 0.2em;
    padding: 14px 0 6px;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin-top: 10px;
}

/* ── Divider ───────────────────────────────────────────────────────────────── */
.teal-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,212,180,0.2), transparent);
    margin: 24px 0;
}

/* ── Roadmap ───────────────────────────────────────────────────────────────── */
.roadmap-phase {
    background: rgba(13, 21, 36, 0.85);
    border: 1px solid rgba(255,255,255,0.07);
    border-left: 3px solid #00d4b4;
    border-radius: 0 12px 12px 0;
    padding: 18px 22px;
    margin-bottom: 14px;
}
.roadmap-phase-warning { border-left-color: #f59e0b; }
.roadmap-phase-info    { border-left-color: #818cf8; }
.roadmap-phase-dim     { border-left-color: #374151; }
.roadmap-phase h4 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 14px;
    font-weight: 700;
    color: #e8edf5;
    margin: 0 0 10px;
}
.roadmap-phase ul {
    margin: 0; padding-left: 18px;
    color: #6b7a99;
    font-size: 13px;
    line-height: 1.8;
}

/* ── Outputs JSON box ──────────────────────────────────────────────────────── */
.stJson {
    background: #0d1524 !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0b0e1a; }
::-webkit-scrollbar-thumb { background: #1e2a40; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #2d3f5a; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

PLOTLY_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#7a8ba8", size=12),
        title_font=dict(family="Space Grotesk, sans-serif", color="#e8edf5", size=15),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
        colorway=["#00d4b4","#6366f1","#f59e0b","#f87171","#34d399","#a78bfa"],
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#7a8ba8")),
        margin=dict(l=16, r=16, t=40, b=16),
    )
)


def apply_theme(fig):
    fig.update_layout(**PLOTLY_TEMPLATE["layout"])
    return fig


def score_color_class(score: float) -> str:
    if score >= 85: return "mp-accent"
    if score >= 70: return "mp-warning"
    return "mp-danger"


def score_label(score: float) -> str:
    if score >= 85: return "Healthy"
    if score >= 70: return "Needs Review"
    if score >= 60: return "Cleanup Needed"
    return "High Risk"


def readiness_badge_html(level: str) -> str:
    cls = "badge-success" if level in ("Production Ready", "Operationally Ready") else \
          "badge-warning" if level in ("Review Recommended", "Cleanup Required") else "badge-danger"
    return f'<span class="badge {cls}">{level}</span>'


def metric_panel(label: str, value, helper: str = "", color_class: str = ""):
    val_cls = color_class or "mp-accent"
    st.markdown(f"""
    <div class="metric-panel">
        <div class="mp-label">{label}</div>
        <div class="mp-value {val_cls}">{value}</div>
        <div class="mp-helper">{helper}</div>
    </div>""", unsafe_allow_html=True)


def score_panel(label: str, score: float):
    cls = score_color_class(score)
    status = score_label(score)
    st.markdown(f"""
    <div class="score-panel">
        <div class="score-label">{label}</div>
        <div class="score-number {cls}">{score:.0f}</div>
        <div class="score-status {cls}">{status}</div>
    </div>""", unsafe_allow_html=True)


def section_header(eyebrow: str, title: str, subtitle: str = ""):
    sub = f'<p style="font-size:14px;color:#4a5568;margin-top:4px;margin-bottom:20px;">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div class="section-eyebrow">{eyebrow}</div>
    <div class="section-title">{title}</div>
    {sub}""", unsafe_allow_html=True)


def teal_divider():
    st.markdown('<div class="teal-divider"></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# DEMO DATA
# ─────────────────────────────────────────────────────────────────────────────

def create_demo_utility_data() -> pd.DataFrame:
    rows = []
    for i in range(1, 501):
        rows.append({
            "asset_id": f"HYD-{i:05d}" if i % 19 != 0 else "",
            "condition": ["Good", "Fair", "Poor", "Critical", "", "Broken"][i % 6],
            "install_year": 2035 if i % 41 == 0 else 1945 + (i % 78),
            "last_inspection_date": "" if i % 12 == 0 else "2024-05-01",
            "diameter_in": 999 if i % 37 == 0 else [4, 6, 8, 10, 12, 16][i % 6],
            "pressure_zone": "" if i % 14 == 0 else f"Zone {chr(65 + (i % 5))}",
            "material": ["Cast Iron", "PVC", "Ductile Iron", "", "Steel"][i % 5],
            "status": ["Active", "Inactive", "Active", "Unknown"][i % 4],
            "SHAPE": None if i % 43 == 0 else {"x": -89.70 + (i % 50) * 0.004, "y": 40.62 + (i // 50) * 0.006},
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADER
# ─────────────────────────────────────────────────────────────────────────────

def load_selected_data(data_source: str):
    df = None

    if data_source == "Demo Dataset":
        df = create_demo_utility_data()
        st.sidebar.success("✓ Demo dataset loaded — 500 assets")

    elif data_source == "Upload CSV":
        uploaded_file = st.sidebar.file_uploader("Upload municipal asset CSV", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.sidebar.success(f"✓ Loaded {len(df):,} records")

    elif data_source == "ArcGIS Layer":
        st.sidebar.markdown('<p style="font-size:12px;color:#4a5568;margin-bottom:8px;">Paste a public ArcGIS Feature Layer URL.</p>', unsafe_allow_html=True)
        layer_url = st.sidebar.text_area(
            "Layer URL",
            height=100,
            placeholder="https://.../FeatureServer/0",
        )
        max_records = st.sidebar.number_input("Max records", min_value=100, max_value=50000, value=5000, step=500)

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
            df = st.session_state["loaded_arcgis_df"]

    return df


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="padding: 16px 0 20px;">
            <div style="font-family:'Space Grotesk',sans-serif;font-size:20px;font-weight:700;color:#e8edf5;letter-spacing:-0.3px;">
                ⬡ GeoOps
            </div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#00d4b4;letter-spacing:0.15em;margin-top:3px;">
                MUNICIPAL INTELLIGENCE
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section">Data Source</div>', unsafe_allow_html=True)
        data_source = st.radio(
            "",
            ["Demo Dataset", "Upload CSV", "ArcGIS Layer"],
            label_visibility="collapsed",
        )

        st.markdown('<div class="sidebar-section">Pipeline</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#374151;line-height:2.2;">
            INTAKE<br>↓ GEO QA<br>↓ READINESS<br>↓ UTILITY INTEL<br>↓ SPATIAL INTEL<br>↓ ARCGIS EXPORT
        </div>""", unsafe_allow_html=True)

    df = load_selected_data(data_source)

    # ── Hero bar ──────────────────────────────────────────────────────────────
    records_str = f"{len(df):,}" if df is not None else "—"
    fields_str  = str(len(df.columns)) if df is not None else "—"
    st.markdown(f"""
    <div class="hero-bar">
        <div class="wordmark">
            <span class="wordmark-main">GeoOps</span>
            <span class="wordmark-tag">v2.0 · Municipal Intelligence Platform</span>
        </div>
        <div class="hero-sub">
            Decision intelligence for GIS quality assurance, utility asset risk, spatial hotspots,
            readiness scoring, and ArcGIS-aligned analyst workflows.
        </div>
        <div class="hero-stats">
            <div class="hero-stat"><span class="hero-stat-val">{records_str}</span><span class="hero-stat-label">Assets Loaded</span></div>
            <div class="hero-stat"><span class="hero-stat-val">{fields_str}</span><span class="hero-stat-label">Fields</span></div>
            <div class="hero-stat"><span class="hero-stat-val">8</span><span class="hero-stat-label">Analysis Modules</span></div>
            <div class="hero-stat"><span class="hero-stat-val">4</span><span class="hero-stat-label">Export Formats</span></div>
        </div>
    </div>""", unsafe_allow_html=True)

    if df is None:
        st.markdown("""
        <div style="text-align:center;padding:80px 0;">
            <div style="font-family:'Space Grotesk',sans-serif;font-size:18px;color:#374151;margin-bottom:8px;">
                Select a data source to begin
            </div>
            <div style="font-size:13px;color:#1f2937;">
                Choose from the sidebar: demo data, CSV upload, or a live ArcGIS Feature Layer.
            </div>
        </div>""", unsafe_allow_html=True)
        return

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tabs = st.tabs([
        "⬡  Overview",
        "◈  Assessment",
        "⚑  Issue Intel",
        "⚙  Utility Intel",
        "◉  Spatial Intel",
        "⬚  ArcGIS Fit",
        "↓  Exports",
        "◎  Roadmap",
    ])

    # ════════════════════════════════════════════════════════════════════════
    # TAB 0 — OVERVIEW
    # ════════════════════════════════════════════════════════════════════════
    with tabs[0]:
        safe_df = df.drop(columns=["SHAPE", "geometry", "geom"], errors="ignore")

        section_header("DATASET PROFILE", "Loaded Asset Overview",
                       "Quick-read snapshot of what's in your dataset before analysis runs.")

        c1, c2, c3, c4 = st.columns(4)
        with c1: metric_panel("Total Records", f"{len(df):,}", "Features loaded")
        with c2: metric_panel("Total Fields", len(df.columns), "Attributes available")
        with c3: metric_panel("Missing Values", f"{int(safe_df.isna().sum().sum()):,}", "Completeness flags", "mp-warning")
        with c4: metric_panel("Duplicate Rows", int(safe_df.duplicated().sum()), "Exact duplicates", "mp-danger" if safe_df.duplicated().sum() > 0 else "mp-accent")

        teal_divider()

        section_header("CAPABILITIES", "What GeoOps Delivers")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
            <div class="glass-card">
                <div class="glass-card-title">⬡ GIS Quality Intelligence</div>
                <div class="glass-card-body">Detects missing IDs, invalid attributes, duplicate assets, stale inspections, and geometry anomalies across your full feature dataset.</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class="glass-card">
                <div class="glass-card-title">◈ Municipal Readiness Scoring</div>
                <div class="glass-card-body">Converts technical QA findings into executive-readable GIS health, utility readiness, and asset readiness scores — zero GIS expertise required.</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown("""
            <div class="glass-card">
                <div class="glass-card-title">↓ ArcGIS-Ready Outputs</div>
                <div class="glass-card-body">Produces prioritized review layers, spatial hotspot intelligence, analyst recommendations, and CSVs ready for ArcGIS import.</div>
            </div>""", unsafe_allow_html=True)

        teal_divider()

        section_header("OPERATIONAL WORKFLOW", "Analysis Pipeline")
        st.markdown("""
        <div class="pipeline-wrap">
            <div class="pipe-node">GIS Data In</div>
            <div class="pipe-arrow">→</div>
            <div class="pipe-node">GeoQA Engine</div>
            <div class="pipe-arrow">→</div>
            <div class="pipe-node">Readiness Score</div>
            <div class="pipe-arrow">→</div>
            <div class="pipe-node">Risk + Hotspots</div>
            <div class="pipe-arrow">→</div>
            <div class="pipe-node">ArcGIS Export</div>
        </div>""", unsafe_allow_html=True)

        teal_divider()

        section_header("RAW DATA", "Dataset Preview", "First 50 records")
        st.dataframe(df.head(50), use_container_width=True, height=320)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — ASSESSMENT
    # ════════════════════════════════════════════════════════════════════════
    with tabs[1]:
        section_header("GIS HEALTH", "Full Municipal Assessment",
                       "Run the complete GeoOps pipeline — QA, readiness scoring, risk, hotspots, and export generation.")

        if not PIPELINE_AVAILABLE:
            st.info("Pipeline modules not found in this environment. Connect your `src/` package to enable full analysis.")

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
            st.markdown('<div style="height:40px;"></div>', unsafe_allow_html=True)
            st.markdown('<p style="color:#374151;font-size:14px;">Assessment results will appear here after running.</p>', unsafe_allow_html=True)
        else:
            result   = st.session_state["geoops_result"]
            readiness = result["readiness_summary"]
            issue_summary = result["issue_summary"]

            teal_divider()
            section_header("SCORES", "Executive Readiness Dashboard")

            c1, c2, c3, c4 = st.columns(4)
            with c1: score_panel("Overall GIS Health",   readiness["overall_gis_health_score"])
            with c2: score_panel("Data Quality",          readiness["data_quality_score"])
            with c3: score_panel("Utility Readiness",     readiness["utility_network_readiness_score"])
            with c4: score_panel("Asset Readiness",       readiness["asset_management_readiness_score"])

            st.markdown(f'<p style="margin-top:6px;">Readiness Level &nbsp; {readiness_badge_html(readiness["readiness_level"])}</p>', unsafe_allow_html=True)

            teal_divider()
            section_header("ISSUE SUMMARY", "Findings Breakdown")

            c1, c2, c3 = st.columns(3)
            with c1: metric_panel("Total Issues", issue_summary["total_issues"], "All QA flags")
            with c2: metric_panel("Critical", issue_summary.get("severity_breakdown", {}).get("Critical", 0), "Immediate action", "mp-danger")
            with c3: metric_panel("High Priority", issue_summary.get("severity_breakdown", {}).get("High", 0), "Near-term review", "mp-warning")

            sev = issue_summary.get("severity_breakdown", {})
            cat = issue_summary.get("category_breakdown", {})

            left, right = st.columns(2)
            with left:
                if sev:
                    fig = go.Figure(go.Pie(
                        labels=list(sev.keys()),
                        values=list(sev.values()),
                        hole=0.55,
                        marker=dict(colors=["#f87171","#f59e0b","#fbbf24","#34d399","#00d4b4"],
                                    line=dict(color="#07090f", width=2)),
                        textfont=dict(color="#e8edf5"),
                    ))
                    fig.update_layout(title_text="Severity Distribution", **PLOTLY_TEMPLATE["layout"])
                    st.plotly_chart(fig, use_container_width=True)
            with right:
                if cat:
                    cat_df = pd.DataFrame({"Category": list(cat.keys()), "Count": list(cat.values())}).sort_values("Count", ascending=True).tail(12)
                    fig = px.bar(cat_df, x="Count", y="Category", orientation="h",
                                 title="Top Issue Categories",
                                 color="Count", color_continuous_scale=[[0,"#1e3a2f"],[1,"#00d4b4"]])
                    fig.update_coloraxes(showscale=False)
                    fig = apply_theme(fig)
                    st.plotly_chart(fig, use_container_width=True)

            teal_divider()
            section_header("RECOMMENDATIONS", "Analyst Action Plan")
            for rec in result.get("recommendations", []):
                st.success(rec)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — ISSUE INTELLIGENCE
    # ════════════════════════════════════════════════════════════════════════
    with tabs[2]:
        section_header("ISSUE INTELLIGENCE", "Flagged Records & Priority Ranking")

        if "geoops_result" not in st.session_state:
            st.warning("Run the assessment first (◈ Assessment tab).")
        else:
            outputs = st.session_state["geoops_result"]["outputs"]
            issues_df    = pd.read_csv(outputs["issues_csv"])
            priorities_df = pd.read_csv(outputs["priorities_csv"])

            f1, f2 = st.columns(2)
            with f1:
                selected_sev = st.multiselect("Severity", sorted(issues_df["severity"].dropna().unique()),
                                               default=list(issues_df["severity"].dropna().unique()))
            with f2:
                selected_cat = st.multiselect("Category", sorted(issues_df["issue_category"].dropna().unique()),
                                               default=list(issues_df["issue_category"].dropna().unique()))

            filtered = issues_df[issues_df["severity"].isin(selected_sev) & issues_df["issue_category"].isin(selected_cat)]

            metric_panel("Matching Records", f"{len(filtered):,}", f"of {len(issues_df):,} total issues")

            teal_divider()
            section_header("FLAGGED RECORDS", "Issue Detail Table")
            st.dataframe(filtered, use_container_width=True, height=360)

            teal_divider()
            section_header("REVIEW PRIORITIES", "Ranked by Risk Score")
            st.dataframe(priorities_df, use_container_width=True, height=360)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 3 — UTILITY INTELLIGENCE
    # ════════════════════════════════════════════════════════════════════════
    with tabs[3]:
        section_header("UTILITY INTELLIGENCE", "Asset Risk & Maintenance Prioritization")

        if "geoops_result" not in st.session_state:
            st.warning("Run the assessment first.")
        else:
            outputs = st.session_state["geoops_result"]["outputs"]
            udf = pd.read_csv(outputs["utility_intelligence_csv"])

            c1, c2, c3 = st.columns(3)
            with c1: metric_panel("Peak Risk Score", int(udf["utility_risk_score"].max()), "Highest asset risk", "mp-danger")
            with c2: metric_panel("Critical Priority", int((udf["maintenance_priority"] == "Critical Priority").sum()), "Assets needing immediate action", "mp-danger")
            with c3: metric_panel("High Priority",    int((udf["maintenance_priority"] == "High Priority").sum()), "Near-term maintenance", "mp-warning")

            teal_divider()

            left, right = st.columns(2)
            with left:
                pri_counts = udf["maintenance_priority"].value_counts().reset_index()
                pri_counts.columns = ["Priority", "Count"]
                fig = px.bar(pri_counts, x="Priority", y="Count", title="Maintenance Priority Distribution",
                             color="Count", color_continuous_scale=[[0,"#1e2a40"],[1,"#00d4b4"]])
                fig.update_coloraxes(showscale=False)
                fig = apply_theme(fig)
                st.plotly_chart(fig, use_container_width=True)
            with right:
                fig2 = px.histogram(udf, x="utility_risk_score", nbins=20,
                                    title="Risk Score Distribution",
                                    color_discrete_sequence=["#00d4b4"])
                fig2 = apply_theme(fig2)
                st.plotly_chart(fig2, use_container_width=True)

            teal_divider()
            section_header("TOP RISK ASSETS", "Highest-Risk Records")
            st.dataframe(udf.head(25), use_container_width=True, height=360)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 4 — SPATIAL INTELLIGENCE
    # ════════════════════════════════════════════════════════════════════════
    with tabs[4]:
        section_header("SPATIAL INTELLIGENCE", "Pressure Zone Risk Hotspots")

        if "geoops_result" not in st.session_state:
            st.warning("Run the assessment first.")
        else:
            outputs = st.session_state["geoops_result"]["outputs"]
            hp_path = outputs.get("spatial_hotspots_csv")

            if not hp_path or not os.path.exists(hp_path):
                st.info("No spatial hotspot output. Dataset may not contain a `pressure_zone` field.")
            else:
                hdf = pd.read_csv(hp_path)
                if hdf.empty:
                    st.info("No hotspot patterns detected in this dataset.")
                else:
                    teal_divider()
                    section_header("ZONE COMPARISON", "Risk by Pressure Zone")
                    st.dataframe(hdf, use_container_width=True, height=280)

                    left, right = st.columns(2)
                    with left:
                        fig = px.bar(hdf, x="pressure_zone", y="avg_risk_score",
                                     title="Avg Utility Risk by Pressure Zone",
                                     text="avg_risk_score",
                                     color="avg_risk_score",
                                     color_continuous_scale=[[0,"#1e2a40"],[1,"#f59e0b"]])
                        fig.update_coloraxes(showscale=False)
                        fig = apply_theme(fig)
                        st.plotly_chart(fig, use_container_width=True)
                    with right:
                        fig2 = px.scatter(hdf, x="asset_count", y="avg_risk_score",
                                          size="critical_priority_count",
                                          color="pressure_zone",
                                          title="Zone Risk Concentration",
                                          color_discrete_sequence=["#00d4b4","#6366f1","#f59e0b","#f87171","#a78bfa"])
                        fig2 = apply_theme(fig2)
                        st.plotly_chart(fig2, use_container_width=True)

                    teal_divider()
                    section_header("HOTSPOT INSIGHTS", "Automated Observations")
                    for insight in st.session_state["geoops_result"].get("hotspot_insights", []):
                        st.warning(insight)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 5 — ARCGIS FIT
    # ════════════════════════════════════════════════════════════════════════
    with tabs[5]:
        section_header("ARCGIS INTEGRATION", "How GeoOps Fits Your Existing Workflow")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="glass-card">
                <div class="glass-card-title">⬚ Without GeoOps</div>
                <div class="glass-card-body">
                    <div class="pipeline-wrap" style="flex-direction:column;gap:6px;align-items:flex-start;">
                        <div class="pipe-node">ArcGIS Data</div>
                        <div class="pipe-arrow" style="transform:rotate(90deg)">→</div>
                        <div class="pipe-node">Manual Review</div>
                        <div class="pipe-arrow" style="transform:rotate(90deg)">→</div>
                        <div class="pipe-node">Cleanup</div>
                        <div class="pipe-arrow" style="transform:rotate(90deg)">→</div>
                        <div class="pipe-node">Delivery</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class="glass-card">
                <div class="glass-card-title">⬡ With GeoOps</div>
                <div class="glass-card-body">
                    <div class="pipeline-wrap" style="flex-direction:column;gap:6px;align-items:flex-start;">
                        <div class="pipe-node">ArcGIS Feature Layer</div>
                        <div class="pipe-arrow" style="transform:rotate(90deg)">→</div>
                        <div class="pipe-node">GeoOps Intake</div>
                        <div class="pipe-arrow" style="transform:rotate(90deg)">→</div>
                        <div class="pipe-node">GeoQA + Readiness</div>
                        <div class="pipe-arrow" style="transform:rotate(90deg)">→</div>
                        <div class="pipe-node">Issue Layer Export</div>
                        <div class="pipe-arrow" style="transform:rotate(90deg)">→</div>
                        <div class="pipe-node">Analyst Review in ArcGIS</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

        teal_divider()
        st.markdown("""
        <div class="glass-card" style="max-width:680px;">
            <div class="glass-card-title">◈ ArcGIS Remains System of Record</div>
            <div class="glass-card-body">
                GeoOps adds a decision intelligence layer around ArcGIS — it never replaces it.
                Features are loaded directly from Feature Layers, enriched with QA scores and risk rankings,
                then exported back as analyst-ready CSV layers that slot into your existing ArcGIS review workflow
                without any migration or disruption.
            </div>
        </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 6 — EXPORTS
    # ════════════════════════════════════════════════════════════════════════
    with tabs[6]:
        section_header("GENERATED OUTPUTS", "Download Assessment Files")

        if "geoops_result" not in st.session_state:
            st.warning("Run the assessment first.")
        else:
            outputs = st.session_state["geoops_result"]["outputs"]
            st.json(outputs)

            teal_divider()
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

    # ════════════════════════════════════════════════════════════════════════
    # TAB 7 — ROADMAP
    # ════════════════════════════════════════════════════════════════════════
    with tabs[7]:
        section_header("PRODUCT ROADMAP", "Development Phases")

        st.markdown("""
        <div class="roadmap-phase">
            <h4>Phase 1 — Foundation  <span class="badge badge-success" style="font-size:11px;">Complete</span></h4>
            <ul>
                <li>Data Intake &amp; schema validation</li>
                <li>GeoQA engine with severity classification</li>
                <li>Readiness scoring framework</li>
                <li>Issue layer CSV export</li>
                <li>Executive reporting</li>
            </ul>
        </div>
        <div class="roadmap-phase roadmap-phase-warning">
            <h4>Phase 2 — Decision Intelligence  <span class="badge badge-warning" style="font-size:11px;">In Progress</span></h4>
            <ul>
                <li>Utility risk intelligence engine</li>
                <li>Spatial pressure-zone hotspot analysis</li>
                <li>Operational risk summaries per zone</li>
                <li>Analyst-facing priority ranking</li>
            </ul>
        </div>
        <div class="roadmap-phase roadmap-phase-info">
            <h4>Phase 3 — ArcGIS Integration  <span class="badge badge-info" style="font-size:11px;">Planned</span></h4>
            <ul>
                <li>Authenticated ArcGIS Online access</li>
                <li>Hosted issue layer publishing</li>
                <li>Dashboard integration via ArcGIS Experience Builder</li>
            </ul>
        </div>
        <div class="roadmap-phase roadmap-phase-dim">
            <h4>Phase 4 — GeoOps Copilot  <span class="badge badge-info" style="font-size:11px;">Research</span></h4>
            <ul>
                <li>Natural-language GIS analysis queries</li>
                <li>Automated QA narrative summaries</li>
                <li>Analyst decision assistant &amp; chat interface</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
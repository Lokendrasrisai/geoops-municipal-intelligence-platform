"""
src/ui/styles.py
All CSS for the GeoOps dashboard — imported once in app.py.
"""

import streamlit as st


GOOGLE_FONTS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Space+Grotesk:wght@300;400;500;600;700"
    "&family=Inter:wght@300;400;500;600"
    "&family=JetBrains+Mono:wght@400;500"
    "&display=swap"
)

CSS = """
/* ── Reset & base ──────────────────────────────────────────────────────────── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background-color: #07090f;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% 0%, rgba(0,212,180,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 100%, rgba(99,102,241,0.06) 0%, transparent 60%);
    background-attachment: fixed;
}
#MainMenu, footer { visibility: hidden; }

/* Always show sidebar toggle button */
[data-testid="collapsedControl"] {
    display: block !important;
    visibility: visible !important;
}
.block-container { padding: 1.5rem 2rem 2rem; max-width: 1600px; }

/* ── Sidebar ───────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0b0e1a !important;
    border-right: 1px solid rgba(0,212,180,0.12);
}
[data-testid="stSidebar"] * { color: #c9d1e0 !important; }
[data-testid="stSidebar"] .stRadio label {
    padding: 8px 14px; border-radius: 8px; transition: background 0.2s;
}
[data-testid="stSidebar"] .stRadio label:hover { background: rgba(0,212,180,0.08); }

/* ── Hero bar ──────────────────────────────────────────────────────────────── */
.wordmark { display:flex; align-items:baseline; gap:10px; margin-bottom:4px; }
.wordmark-main {
    font-family:'Space Grotesk',sans-serif; font-size:32px; font-weight:700;
    letter-spacing:-0.5px; color:#e8edf5;
}
.wordmark-tag {
    font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:500;
    color:#00d4b4; letter-spacing:0.12em; text-transform:uppercase;
    padding:3px 8px; background:rgba(0,212,180,0.1);
    border:1px solid rgba(0,212,180,0.25); border-radius:4px;
}
.hero-bar {
    padding:28px 32px; border-radius:16px;
    background:linear-gradient(135deg,#0d1524 0%,#111827 100%);
    border:1px solid rgba(0,212,180,0.15); margin-bottom:28px;
    position:relative; overflow:hidden;
}
.hero-bar::before {
    content:''; position:absolute; top:-1px; left:-1px; right:-1px; height:2px;
    background:linear-gradient(90deg,transparent,#00d4b4,#6366f1,transparent);
}
.hero-sub { font-size:14px; color:#6b7a99; margin-top:8px; max-width:800px; line-height:1.6; }
.hero-stats { display:flex; gap:32px; margin-top:20px; }
.hero-stat { display:flex; flex-direction:column; }
.hero-stat-val { font-family:'JetBrains Mono',monospace; font-size:22px; font-weight:500; color:#00d4b4; }
.hero-stat-label { font-size:11px; color:#4a5568; text-transform:uppercase; letter-spacing:0.1em; margin-top:2px; }

/* ── Glass cards ───────────────────────────────────────────────────────────── */
.glass-card {
    background:rgba(13,21,36,0.85); border:1px solid rgba(255,255,255,0.07);
    border-radius:14px; padding:22px 24px; backdrop-filter:blur(12px);
    transition:border-color 0.2s,box-shadow 0.2s; height:100%;
}
.glass-card:hover { border-color:rgba(0,212,180,0.2); box-shadow:0 0 24px rgba(0,212,180,0.05); }
.glass-card-title {
    font-family:'Space Grotesk',sans-serif; font-size:13px; font-weight:600;
    color:#00d4b4; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:10px;
}
.glass-card-body { font-size:14px; color:#7a8ba8; line-height:1.65; }

/* ── Metric panels ─────────────────────────────────────────────────────────── */
.metric-panel {
    background:linear-gradient(145deg,#0d1524 0%,#111827 100%);
    border:1px solid rgba(255,255,255,0.07); border-radius:14px;
    padding:20px 22px; position:relative; overflow:hidden; margin-bottom:14px;
}
.metric-panel::after {
    content:''; position:absolute; bottom:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,212,180,0.3),transparent);
}
.mp-label { font-family:'JetBrains Mono',monospace; font-size:10px; font-weight:500; color:#4a5568; text-transform:uppercase; letter-spacing:0.15em; margin-bottom:8px; }
.mp-value { font-family:'Space Grotesk',sans-serif; font-size:36px; font-weight:700; color:#e8edf5; line-height:1; margin-bottom:6px; letter-spacing:-1px; }
.mp-helper { font-size:12px; color:#4a5568; }
.mp-accent  { color:#00d4b4; }
.mp-warning { color:#f59e0b; }
.mp-danger  { color:#f87171; }

/* ── Score panels ──────────────────────────────────────────────────────────── */
.score-panel {
    background:linear-gradient(145deg,#0d1524 0%,#111827 100%);
    border:1px solid rgba(255,255,255,0.07); border-radius:14px;
    padding:22px; text-align:center; margin-bottom:14px; position:relative; overflow:hidden;
}
.score-number { font-family:'Space Grotesk',sans-serif; font-size:48px; font-weight:700; letter-spacing:-2px; line-height:1; margin-bottom:4px; }
.score-label  { font-size:11px; color:#4a5568; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:6px; }
.score-status { font-size:12px; font-weight:600; letter-spacing:0.05em; }

/* ── Badges ────────────────────────────────────────────────────────────────── */
.badge { display:inline-flex; align-items:center; gap:5px; padding:5px 12px; border-radius:999px; font-size:12px; font-weight:600; letter-spacing:0.03em; }
.badge-success { background:rgba(0,212,180,0.12); color:#00d4b4; border:1px solid rgba(0,212,180,0.25); }
.badge-warning { background:rgba(245,158,11,0.12); color:#f59e0b; border:1px solid rgba(245,158,11,0.25); }
.badge-danger  { background:rgba(248,113,113,0.12); color:#f87171; border:1px solid rgba(248,113,113,0.25); }
.badge-info    { background:rgba(99,102,241,0.12); color:#818cf8; border:1px solid rgba(99,102,241,0.25); }

/* ── Pipeline flow ─────────────────────────────────────────────────────────── */
.pipeline-wrap { display:flex; align-items:center; gap:0; flex-wrap:wrap; margin:16px 0; }
.pipe-node {
    background:rgba(13,21,36,0.9); border:1px solid rgba(0,212,180,0.2); border-radius:8px;
    padding:10px 18px; font-family:'Space Grotesk',sans-serif; font-size:13px;
    font-weight:600; color:#c9d1e0; white-space:nowrap;
}
.pipe-arrow { color:rgba(0,212,180,0.35); font-size:18px; padding:0 4px; flex-shrink:0; }

/* ── Section headers ───────────────────────────────────────────────────────── */
.section-eyebrow { font-family:'JetBrains Mono',monospace; font-size:10px; color:#00d4b4; text-transform:uppercase; letter-spacing:0.2em; margin-bottom:6px; }
.section-title   { font-family:'Space Grotesk',sans-serif; font-size:22px; font-weight:700; color:#e8edf5; margin-bottom:4px; }

/* ── Buttons ───────────────────────────────────────────────────────────────── */
.stButton > button {
    background:linear-gradient(135deg,#00d4b4 0%,#0891b2 100%) !important;
    color:#07090f !important; border:none !important; border-radius:10px !important;
    font-family:'Space Grotesk',sans-serif !important; font-weight:700 !important;
    font-size:14px !important; height:3rem !important; letter-spacing:0.02em;
    transition:opacity 0.2s,transform 0.15s !important;
}
.stButton > button:hover { opacity:0.9 !important; transform:translateY(-1px) !important; }

/* ── Tabs ──────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] { gap:4px; background:rgba(13,21,36,0.6); border-radius:10px; padding:4px; border:1px solid rgba(255,255,255,0.06); }
.stTabs [data-baseweb="tab"] { background:transparent !important; border-radius:7px !important; color:#6b7a99 !important; font-family:'Space Grotesk',sans-serif !important; font-size:13px !important; font-weight:500 !important; padding:8px 16px !important; border:none !important; transition:all 0.2s !important; }
.stTabs [aria-selected="true"] { background:rgba(0,212,180,0.12) !important; color:#00d4b4 !important; font-weight:600 !important; }
.stTabs [data-baseweb="tab-border"],
.stTabs [data-baseweb="tab-highlight"] { display:none !important; }

/* ── Explainability panel ──────────────────────────────────────────────────── */
.explain-panel {
    background:rgba(13,21,36,0.9); border:1px solid rgba(0,212,180,0.15);
    border-radius:12px; padding:18px 22px; margin-bottom:12px;
}
.explain-narrative { font-size:13px; color:#7a8ba8; line-height:1.7; margin-bottom:14px; }
.explain-driver {
    display:flex; justify-content:space-between; align-items:center;
    padding:6px 0; border-bottom:1px solid rgba(255,255,255,0.04);
    font-size:13px;
}
.explain-driver-label { color:#c9d1e0; }
.explain-driver-pts   { font-family:'JetBrains Mono',monospace; font-size:12px; }

/* ── Roadmap ───────────────────────────────────────────────────────────────── */
.roadmap-phase {
    background:rgba(13,21,36,0.85); border:1px solid rgba(255,255,255,0.07);
    border-left:3px solid #00d4b4; border-radius:0 12px 12px 0;
    padding:18px 22px; margin-bottom:14px;
}
.roadmap-phase-warning { border-left-color:#f59e0b; }
.roadmap-phase-info    { border-left-color:#818cf8; }
.roadmap-phase-dim     { border-left-color:#374151; }
.roadmap-phase h4 { font-family:'Space Grotesk',sans-serif; font-size:14px; font-weight:700; color:#e8edf5; margin:0 0 10px; }
.roadmap-phase ul { margin:0; padding-left:18px; color:#6b7a99; font-size:13px; line-height:1.8; }

/* ── Misc ──────────────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] { border-radius:10px; overflow:hidden; border:1px solid rgba(255,255,255,0.07) !important; }
.teal-divider { height:1px; background:linear-gradient(90deg,transparent,rgba(0,212,180,0.2),transparent); margin:24px 0; }
.sidebar-section { font-family:'JetBrains Mono',monospace; font-size:10px; color:rgba(0,212,180,0.6); text-transform:uppercase; letter-spacing:0.2em; padding:14px 0 6px; border-top:1px solid rgba(255,255,255,0.06); margin-top:10px; }
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:#0b0e1a; }
::-webkit-scrollbar-thumb { background:#1e2a40; border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background:#2d3f5a; }
"""


def inject_styles() -> None:
    """Call once at the top of app.py to load all styles."""
    st.markdown(f'<link href="{GOOGLE_FONTS_URL}" rel="stylesheet">', unsafe_allow_html=True)
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

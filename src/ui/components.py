"""
src/ui/components.py
Reusable Streamlit UI components for the GeoOps dashboard.
"""

import streamlit as st


# ── Color helpers ─────────────────────────────────────────────────────────────

def score_color_class(score: float) -> str:
    if score >= 85:
        return "mp-accent"
    if score >= 70:
        return "mp-warning"
    return "mp-danger"


def score_label(score: float) -> str:
    if score >= 85:
        return "Healthy"
    if score >= 70:
        return "Needs Review"
    if score >= 60:
        return "Cleanup Needed"
    return "High Risk"


def readiness_badge_html(level: str) -> str:
    cls = (
        "badge-success" if level in ("Production Ready", "Operationally Ready")
        else "badge-warning" if level in ("Review Recommended", "Cleanup Required")
        else "badge-danger"
    )
    return f'<span class="badge {cls}">{level}</span>'


def action_badge_html(action: str) -> str:
    mapping = {
        "Escalate":       "badge-danger",
        "Replace":        "badge-danger",
        "Repair":         "badge-warning",
        "Inspect":        "badge-warning",
        "Monitor":        "badge-info",
        "Validate Data":  "badge-info",
        "Routine":        "badge-success",
    }
    cls = mapping.get(action, "badge-info")
    return f'<span class="badge {cls}">{action}</span>'


# ── Layout primitives ─────────────────────────────────────────────────────────

def teal_divider() -> None:
    st.markdown('<div class="teal-divider"></div>', unsafe_allow_html=True)


def section_header(eyebrow: str, title: str, subtitle: str = "") -> None:
    sub = (
        f'<p style="font-size:14px;color:#4a5568;margin-top:4px;margin-bottom:20px;">'
        f"{subtitle}</p>"
        if subtitle else ""
    )
    st.markdown(
        f'<div class="section-eyebrow">{eyebrow}</div>'
        f'<div class="section-title">{title}</div>'
        f"{sub}",
        unsafe_allow_html=True,
    )


# ── Metric & score panels ─────────────────────────────────────────────────────

def metric_panel(label: str, value, helper: str = "", color_class: str = "") -> None:
    val_cls = color_class or "mp-accent"
    st.markdown(
        f"""<div class="metric-panel">
            <div class="mp-label">{label}</div>
            <div class="mp-value {val_cls}">{value}</div>
            <div class="mp-helper">{helper}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def score_panel(label: str, score: float) -> None:
    cls = score_color_class(score)
    status = score_label(score)
    st.markdown(
        f"""<div class="score-panel">
            <div class="score-label">{label}</div>
            <div class="score-number {cls}">{score:.0f}</div>
            <div class="score-status {cls}">{status}</div>
        </div>""",
        unsafe_allow_html=True,
    )


# ── Explainability panel ──────────────────────────────────────────────────────

def explain_panel(explain: dict) -> None:
    """
    Render a single asset's explainability breakdown.

    explain = {
        "asset_id": "WM-00042",
        "risk_score": 78,
        "action": "Inspect",
        "narrative": "This asset scored ...",
        "drivers": [
            {"factor": "Asset Age", "points": 25, "detail": "67 years old"},
            ...
        ]
    }
    """
    action_badge = action_badge_html(explain.get("action", "Monitor"))
    score = explain.get("risk_score", 0)
    score_cls = score_color_class(score)

    drivers_html = "".join(
        f"""<div class="explain-driver">
            <span class="explain-driver-label">
                {d['factor']} — <span style="color:#4a5568">{d['detail']}</span>
            </span>
            <span class="explain-driver-pts {score_cls}">+{d['points']} pts</span>
        </div>"""
        for d in explain.get("drivers", [])
        if d["points"] > 0
    )

    st.markdown(
        f"""<div class="explain-panel">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                <span style="font-family:'Space Grotesk',sans-serif;font-weight:700;
                             font-size:15px;color:#e8edf5;">{explain.get('asset_id','—')}</span>
                <div style="display:flex;gap:10px;align-items:center;">
                    <span class="score-number {score_cls}" style="font-size:28px;">
                        {score}
                    </span>
                    {action_badge}
                </div>
            </div>
            <div class="explain-narrative">{explain.get('narrative','')}</div>
            {drivers_html}
        </div>""",
        unsafe_allow_html=True,
    )


# ── Pipeline diagram ──────────────────────────────────────────────────────────

def pipeline_diagram(steps: list[str]) -> None:
    nodes = ""
    for i, step in enumerate(steps):
        nodes += f'<div class="pipe-node">{step}</div>'
        if i < len(steps) - 1:
            nodes += '<div class="pipe-arrow">→</div>'
    st.markdown(f'<div class="pipeline-wrap">{nodes}</div>', unsafe_allow_html=True)


# ── Hero bar ──────────────────────────────────────────────────────────────────

def hero_bar(records: int | None, fields: int | None) -> None:
    records_str = f"{records:,}" if records is not None else "—"
    fields_str  = str(fields)    if fields  is not None else "—"
    st.markdown(
        f"""<div class="hero-bar">
            <div class="wordmark">
                <span class="wordmark-main">GeoOps</span>
                <span class="wordmark-tag">v2.0 · Municipal Intelligence Platform</span>
            </div>
            <div class="hero-sub">
                Decision intelligence for GIS quality assurance, utility asset risk,
                spatial hotspot analysis, readiness scoring, and ArcGIS-aligned analyst workflows.
            </div>
            <div class="hero-stats">
                <div class="hero-stat">
                    <span class="hero-stat-val">{records_str}</span>
                    <span class="hero-stat-label">Assets Loaded</span>
                </div>
                <div class="hero-stat">
                    <span class="hero-stat-val">{fields_str}</span>
                    <span class="hero-stat-label">Fields</span>
                </div>
                <div class="hero-stat">
                    <span class="hero-stat-val">9</span>
                    <span class="hero-stat-label">Analysis Modules</span>
                </div>
                <div class="hero-stat">
                    <span class="hero-stat-val">4</span>
                    <span class="hero-stat-label">Export Formats</span>
                </div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

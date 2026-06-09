from pathlib import Path
import pandas as pd


def build_html_report(
    readiness_summary: dict,
    issue_summary: dict,
    recommendations: list[str],
    utility_df: pd.DataFrame,
    hotspots_df: pd.DataFrame,
    output_path: str = "outputs/geoops_executive_report.html",
) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    top_assets_html = (
        utility_df.head(10).to_html(index=False, classes="table")
        if not utility_df.empty
        else "<p>No utility intelligence available.</p>"
    )

    hotspots_html = (
        hotspots_df.head(10).to_html(index=False, classes="table")
        if not hotspots_df.empty
        else "<p>No spatial hotspot data available.</p>"
    )

    rec_html = "".join([f"<li>{rec}</li>" for rec in recommendations])

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>GeoOps Executive Report</title>
<style>
body {{
    font-family: Arial, sans-serif;
    background: #f7faf9;
    color: #102033;
    margin: 0;
    padding: 40px;
}}
.report {{
    max-width: 1100px;
    margin: auto;
    background: white;
    border-radius: 18px;
    padding: 36px;
    box-shadow: 0 18px 44px rgba(15,23,42,0.08);
}}
h1 {{
    color: #064e3b;
    margin-bottom: 6px;
}}
.subtitle {{
    color: #64748b;
    margin-bottom: 30px;
}}
.grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 30px;
}}
.card {{
    border: 1px solid #e5edf1;
    border-radius: 14px;
    padding: 18px;
    background: #fbfefd;
}}
.label {{
    font-size: 12px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
.value {{
    font-size: 34px;
    font-weight: 800;
    color: #047857;
    margin-top: 8px;
}}
.section {{
    margin-top: 32px;
}}
.table {{
    border-collapse: collapse;
    width: 100%;
    font-size: 13px;
}}
.table th {{
    background: #ecfdf5;
    color: #064e3b;
    text-align: left;
    padding: 10px;
}}
.table td {{
    border-bottom: 1px solid #e5edf1;
    padding: 9px;
}}
.badge {{
    display: inline-block;
    padding: 7px 12px;
    border-radius: 999px;
    background: #ecfdf5;
    color: #047857;
    font-weight: 700;
}}
li {{
    margin-bottom: 8px;
}}
</style>
</head>
<body>
<div class="report">
    <h1>GeoOps Municipal Intelligence Report</h1>
    <div class="subtitle">
        Executive GIS readiness, utility risk, spatial hotspot, and QA summary.
    </div>

    <div class="grid">
        <div class="card">
            <div class="label">Overall GIS Health</div>
            <div class="value">{readiness_summary.get("overall_gis_health_score", "N/A")}</div>
        </div>
        <div class="card">
            <div class="label">Data Quality</div>
            <div class="value">{readiness_summary.get("data_quality_score", "N/A")}</div>
        </div>
        <div class="card">
            <div class="label">Utility Readiness</div>
            <div class="value">{readiness_summary.get("utility_network_readiness_score", "N/A")}</div>
        </div>
        <div class="card">
            <div class="label">Asset Readiness</div>
            <div class="value">{readiness_summary.get("asset_management_readiness_score", "N/A")}</div>
        </div>
    </div>

    <h2>Readiness Level</h2>
    <p><span class="badge">{readiness_summary.get("readiness_level", "N/A")}</span></p>

    <div class="section">
        <h2>Issue Summary</h2>
        <p><b>Total Issues:</b> {issue_summary.get("total_issues", 0)}</p>
        <p><b>Severity Breakdown:</b> {issue_summary.get("severity_breakdown", {})}</p>
        <p><b>Category Breakdown:</b> {issue_summary.get("category_breakdown", {})}</p>
    </div>

    <div class="section">
        <h2>Recommended Actions</h2>
        <ul>{rec_html}</ul>
    </div>

    <div class="section">
        <h2>Top Highest-Risk Assets</h2>
        {top_assets_html}
    </div>

    <div class="section">
        <h2>Pressure Zone Hotspots</h2>
        {hotspots_html}
    </div>

    <div class="section">
        <h2>Workflow Fit</h2>
        <p>
        GeoOps does not replace ArcGIS. It adds a decision intelligence layer that helps analysts
        identify quality issues, prioritize risky assets, summarize spatial hotspots, and export
        review-ready outputs for GIS workflows.
        </p>
    </div>
</div>
</body>
</html>
"""

    Path(output_path).write_text(html, encoding="utf-8")
    return output_path

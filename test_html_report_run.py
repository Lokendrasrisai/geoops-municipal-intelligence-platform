import pandas as pd

from src.geoqa.engine import run_geoqa, summarize_issues
from src.readiness.scoring import build_readiness_summary
from src.reporting.recommendations import generate_recommendations
from src.utility_intelligence.risk_engine import build_utility_intelligence
from src.spatial.hotspot_engine import build_pressure_zone_hotspots
from src.reporting.html_report import build_html_report


def create_sample_data():
    rows = []
    for i in range(1, 101):
        rows.append(
            {
                "asset_id": f"HYD-{i:04d}" if i % 15 != 0 else "",
                "condition": ["Good", "Fair", "Poor", "Critical", "", "Broken"][i % 6],
                "install_year": 2035 if i % 23 == 0 else 1945 + (i % 75),
                "last_inspection_date": "" if i % 10 == 0 else "2024-05-01",
                "diameter_in": 999 if i % 27 == 0 else [4, 6, 8, 10, 12, 16][i % 6],
                "pressure_zone": ["Zone A", "Zone B", "Zone C", "Zone D"][i % 4],
                "SHAPE": {"x": -89.70 + (i % 20) * 0.004, "y": 40.62 + (i // 20) * 0.006},
            }
        )
    return pd.DataFrame(rows)


def main():
    df = create_sample_data()
    issues_df = run_geoqa(df)

    readiness = build_readiness_summary(issues_df)
    issue_summary = summarize_issues(issues_df)
    recommendations = generate_recommendations(issues_df)

    utility_df = build_utility_intelligence(df, issues_df)
    hotspots_df = build_pressure_zone_hotspots(df, utility_df)

    output = build_html_report(
        readiness,
        issue_summary,
        recommendations,
        utility_df,
        hotspots_df,
    )

    print(f"HTML report generated: {output}")


if __name__ == "__main__":
    main()

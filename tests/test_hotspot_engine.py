import pandas as pd

from src.geoqa.engine import run_geoqa
from src.utility_intelligence.risk_engine import build_utility_intelligence
from src.spatial.hotspot_engine import (
    build_pressure_zone_hotspots,
    generate_hotspot_insights,
)


def create_sample_data() -> pd.DataFrame:
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
    assets_df = create_sample_data()

    issues_df = run_geoqa(assets_df)

    utility_df = build_utility_intelligence(
        assets_df,
        issues_df,
    )

    hotspots_df = build_pressure_zone_hotspots(
        assets_df,
        utility_df,
    )

    insights = generate_hotspot_insights(hotspots_df)

    print("\nPressure Zone Hotspots")
    print(hotspots_df)

    print("\nHotspot Insights")
    for insight in insights:
        print(f"- {insight}")

    hotspots_df.to_csv("outputs/test_pressure_zone_hotspots.csv", index=False)
    print("\nSaved: outputs/test_pressure_zone_hotspots.csv")


if __name__ == "__main__":
    main()
import pandas as pd

from src.geoqa.engine import run_geoqa
from src.utility_intelligence.risk_engine import build_utility_intelligence


def create_sample_data():
    return pd.DataFrame(
        [
            {
                "asset_id": "HYD-001",
                "condition": "Good",
                "install_year": 1998,
                "last_inspection_date": "2024-05-01",
                "diameter_in": 6,
                "SHAPE": {"x": -89.65, "y": 40.69},
            },
            {
                "asset_id": "HYD-002",
                "condition": "",
                "install_year": 2035,
                "last_inspection_date": "",
                "diameter_in": 999,
                "SHAPE": {"x": -89.66, "y": 40.70},
            },
            {
                "asset_id": "HYD-003",
                "condition": "Critical",
                "install_year": 1940,
                "last_inspection_date": "2018-01-01",
                "diameter_in": 16,
                "SHAPE": {"x": -89.67, "y": 40.71},
            },
        ]
    )


def main():
    df = create_sample_data()
    issues_df = run_geoqa(df)

    utility_df = build_utility_intelligence(df, issues_df)

    print("\nUtility Intelligence")
    print(utility_df)

    utility_df.to_csv("outputs/test_utility_intelligence.csv", index=False)
    print("\nSaved: outputs/test_utility_intelligence.csv")


if __name__ == "__main__":
    main()
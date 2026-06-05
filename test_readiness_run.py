import pandas as pd

from src.geoqa.engine import run_geoqa
from src.readiness.scoring import (
    assign_feature_review_priorities,
    build_readiness_summary,
)


def create_sample_data() -> pd.DataFrame:
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
                "asset_id": "HYD-002",
                "condition": "Broken",
                "install_year": 1700,
                "last_inspection_date": "2020-01-01",
                "diameter_in": "unknown",
                "SHAPE": None,
            },
            {
                "asset_id": "",
                "condition": "Poor",
                "install_year": None,
                "last_inspection_date": None,
                "diameter_in": None,
                "SHAPE": {"x": -89.67, "y": 40.71},
            },
        ]
    )


def main():
    df = create_sample_data()

    issues_df = run_geoqa(df)
    priorities_df = assign_feature_review_priorities(issues_df)
    summary = build_readiness_summary(issues_df)

    print("\nReadiness Summary")
    print(summary)

    print("\nFeature Review Priorities")
    print(priorities_df)

    priorities_df.to_csv("outputs/test_feature_priorities.csv", index=False)
    print("\nSaved: outputs/test_feature_priorities.csv")


if __name__ == "__main__":
    main()


import pandas as pd

from src.geoqa.engine import run_geoqa
from src.arcgis.issue_export import (
    export_issue_geojson,
)


def create_sample_data():

    return pd.DataFrame(
        [
            {
                "asset_id": "HYD-001",
                "condition": "Good",
                "install_year": 1998,
                "last_inspection_date": "2024-05-01",
                "diameter_in": 6,
                "SHAPE": {
                    "x": -89.65,
                    "y": 40.69,
                },
            },
            {
                "asset_id": "HYD-002",
                "condition": "",
                "install_year": 2035,
                "last_inspection_date": "",
                "diameter_in": 999,
                "SHAPE": {
                    "x": -89.66,
                    "y": 40.70,
                },
            },
            {
                "asset_id": "HYD-002",
                "condition": "Broken",
                "install_year": 1700,
                "last_inspection_date": "2020-01-01",
                "diameter_in": "unknown",
                "SHAPE": None,
            },
        ]
    )


def main():

    df = create_sample_data()

    issues_df = run_geoqa(df)

    path = export_issue_geojson(
        issues_df,
        df,
    )

    print(
        f"Issue layer exported: {path}"
    )


if __name__ == "__main__":
    main()
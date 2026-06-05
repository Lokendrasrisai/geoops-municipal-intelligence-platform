import pandas as pd

from src.pipeline.geoops_pipeline import run_geoops_pipeline


def create_demo_utility_data() -> pd.DataFrame:
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
    df = create_demo_utility_data()

    result = run_geoops_pipeline(df)

    print("\nGeoOps Pipeline Complete")
    print("========================")

    print("\nReadiness Summary")
    for key, value in result["readiness_summary"].items():
        print(f"{key}: {value}")

    print("\nIssue Summary")
    print(result["issue_summary"])

    print("\nRecommendations")
    for recommendation in result["recommendations"]:
        print(f"- {recommendation}")

    print("\nOutputs")
    for key, value in result["outputs"].items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
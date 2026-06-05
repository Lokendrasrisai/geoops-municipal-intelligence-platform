from dataclasses import asdict

import pandas as pd

from src.geoqa.checks import (
    check_duplicate_asset_id,
    check_invalid_condition,
    check_invalid_install_year,
    check_missing_asset_id,
    check_missing_condition,
    check_missing_geometry,
    check_missing_inspection_date,
    check_suspicious_diameter,
)


QA_CHECKS = [
    check_missing_asset_id,
    check_duplicate_asset_id,
    check_missing_geometry,
    check_missing_condition,
    check_invalid_condition,
    check_invalid_install_year,
    check_missing_inspection_date,
    check_suspicious_diameter,
]


def run_geoqa(df: pd.DataFrame) -> pd.DataFrame:
    """Run all GeoQA checks and return an issue dataframe."""
    all_issues = []

    for check in QA_CHECKS:
        issues = check(df)
        all_issues.extend(issues)

    if not all_issues:
        return pd.DataFrame(
            columns=[
                "feature_index",
                "asset_id",
                "issue_category",
                "issue_description",
                "severity",
                "recommended_action",
            ]
        )

    return pd.DataFrame([asdict(issue) for issue in all_issues])


def summarize_issues(issues_df: pd.DataFrame) -> dict:
    """Summarize GeoQA issue results."""
    if issues_df.empty:
        return {
            "total_issues": 0,
            "severity_breakdown": {},
            "category_breakdown": {},
        }

    return {
        "total_issues": int(len(issues_df)),
        "severity_breakdown": issues_df["severity"].value_counts().to_dict(),
        "category_breakdown": issues_df["issue_category"].value_counts().to_dict(),
    }
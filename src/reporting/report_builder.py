# src/reporting/report_builder.py

import pandas as pd


def build_report(
    readiness_summary: dict,
    issues_df: pd.DataFrame,
    priorities_df: pd.DataFrame
) -> dict:

    return {
        "executive_summary": readiness_summary,
        "total_issues": len(issues_df),
        "critical_issues": len(
            issues_df[issues_df["severity"] == "Critical"]
        ),
        "high_review_assets": len(
            priorities_df[
                priorities_df["review_priority"] == "High Review"
            ]
        ),
    }
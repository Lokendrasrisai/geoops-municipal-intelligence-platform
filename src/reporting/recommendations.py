# src/reporting/recommendations.py

import pandas as pd


def generate_recommendations(issues_df):

    recommendations = []

    counts = (
        issues_df["issue_category"]
        .value_counts()
        .to_dict()
    )

    if counts.get("Missing Inspection Date", 0) > 5:
        recommendations.append(
            "Prioritize inspection record reconciliation."
        )

    if counts.get("Duplicate Asset ID", 0) > 5:
        recommendations.append(
            "Perform asset identifier standardization."
        )

    if counts.get("Missing Geometry", 0) > 0:
        recommendations.append(
            "Investigate missing geometry records before publishing."
        )

    return recommendations
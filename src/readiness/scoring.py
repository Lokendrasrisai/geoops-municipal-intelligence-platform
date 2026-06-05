import pandas as pd


SEVERITY_PENALTIES = {
    "Critical": 5.0,
    "High": 3.0,
    "Medium": 1.5,
    "Low": 0.5,
}

SEVERITY_POINTS = {
    "Critical": 10,
    "High": 6,
    "Medium": 3,
    "Low": 1,
}


def calculate_data_quality_score(issues_df: pd.DataFrame) -> float:
    """Calculate dataset-level data quality score from GeoQA issues."""
    if issues_df.empty:
        return 100.0

    penalty = 0.0
    for severity in issues_df["severity"]:
        penalty += SEVERITY_PENALTIES.get(severity, 0.0)

    score = 100.0 - penalty
    return round(max(0.0, min(100.0, score)), 2)


def assign_feature_review_priorities(issues_df: pd.DataFrame) -> pd.DataFrame:
    """Assign review priority for each feature based on issue severity."""
    if issues_df.empty:
        return pd.DataFrame(
            columns=["feature_index", "asset_id", "review_score", "review_priority"]
        )

    rows = []

    grouped = issues_df.groupby(["feature_index", "asset_id"], dropna=False)

    for (feature_index, asset_id), group in grouped:
        score = 0

        for severity in group["severity"]:
            score += SEVERITY_POINTS.get(severity, 0)

        unique_categories = group["issue_category"].nunique()
        if unique_categories >= 3:
            score += 4

        priority = map_review_score_to_priority(score)

        rows.append(
            {
                "feature_index": feature_index,
                "asset_id": asset_id,
                "review_score": score,
                "review_priority": priority,
                "issue_count": len(group),
                "issue_categories": ", ".join(sorted(group["issue_category"].unique())),
            }
        )

    return pd.DataFrame(rows).sort_values(
        by="review_score", ascending=False
    ).reset_index(drop=True)


def map_review_score_to_priority(score: float) -> str:
    if score >= 20:
        return "Critical Review"
    if score >= 12:
        return "High Review"
    if score >= 6:
        return "Medium Review"
    if score >= 1:
        return "Low Review"
    return "Clean"


def calculate_utility_network_readiness_score(issues_df: pd.DataFrame) -> float:
    """
    Approximate Utility Network readiness based on issue categories.
    Later this will be replaced with deeper topology/connectivity checks.
    """
    if issues_df.empty:
        return 100.0

    un_keywords = [
        "Geometry",
        "Diameter",
        "Material",
        "Pressure",
        "Connectivity",
        "Duplicate Asset ID",
        "Missing Asset ID",
    ]

    un_issues = issues_df[
        issues_df["issue_category"].apply(
            lambda x: any(keyword.lower() in str(x).lower() for keyword in un_keywords)
        )
    ]

    if un_issues.empty:
        return 100.0

    penalty = sum(SEVERITY_PENALTIES.get(s, 0.0) for s in un_issues["severity"])
    return round(max(0.0, min(100.0, 100.0 - penalty)), 2)


def calculate_asset_management_readiness_score(issues_df: pd.DataFrame) -> float:
    """Approximate asset management readiness based on condition/inspection/age issues."""
    if issues_df.empty:
        return 100.0

    asset_keywords = [
        "Condition",
        "Inspection",
        "Install Year",
        "Status",
        "Missing Diameter",
    ]

    asset_issues = issues_df[
        issues_df["issue_category"].apply(
            lambda x: any(keyword.lower() in str(x).lower() for keyword in asset_keywords)
        )
    ]

    if asset_issues.empty:
        return 100.0

    penalty = sum(SEVERITY_PENALTIES.get(s, 0.0) for s in asset_issues["severity"])
    return round(max(0.0, min(100.0, 100.0 - penalty)), 2)


def calculate_overall_gis_health_score(
    data_quality_score: float,
    utility_network_score: float,
    asset_management_score: float,
) -> float:
    score = (
        0.40 * data_quality_score
        + 0.30 * utility_network_score
        + 0.30 * asset_management_score
    )
    return round(score, 2)


def classify_readiness(score: float) -> str:
    if score >= 90:
        return "Production Ready"
    if score >= 80:
        return "Operationally Ready"
    if score >= 70:
        return "Review Recommended"
    if score >= 60:
        return "Cleanup Required"
    if score >= 40:
        return "High Risk"
    return "Not Ready"


def build_readiness_summary(issues_df: pd.DataFrame) -> dict:
    data_quality = calculate_data_quality_score(issues_df)
    utility_network = calculate_utility_network_readiness_score(issues_df)
    asset_management = calculate_asset_management_readiness_score(issues_df)
    overall = calculate_overall_gis_health_score(
        data_quality, utility_network, asset_management
    )

    return {
        "data_quality_score": data_quality,
        "utility_network_readiness_score": utility_network,
        "asset_management_readiness_score": asset_management,
        "overall_gis_health_score": overall,
        "readiness_level": classify_readiness(overall),
    }
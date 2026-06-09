import pandas as pd


CONDITION_POINTS = {
    "Critical": 40,
    "Poor": 30,
    "Fair": 15,
    "Good": 5,
    "Excellent": 0,
    "Unknown": 10,
}


def calculate_asset_age_score(install_year, current_year=2026) -> int:
    try:
        age = current_year - int(install_year)
    except Exception:
        return 10

    if age >= 75:
        return 25
    if age >= 50:
        return 18
    if age >= 30:
        return 10
    if age >= 10:
        return 5
    return 0


def calculate_inspection_score(last_inspection_date) -> int:
    if pd.isna(last_inspection_date) or str(last_inspection_date).strip() == "":
        return 25

    try:
        last_date = pd.to_datetime(last_inspection_date)
        years_since = (pd.Timestamp("2026-06-08") - last_date).days / 365
    except Exception:
        return 15

    if years_since >= 5:
        return 25
    if years_since >= 3:
        return 18
    if years_since >= 1:
        return 8
    return 0


def calculate_condition_score(condition) -> int:
    if pd.isna(condition) or str(condition).strip() == "":
        return 15

    return CONDITION_POINTS.get(str(condition).strip(), 12)


def calculate_diameter_score(diameter) -> int:
    try:
        diameter = float(diameter)
    except Exception:
        return 8

    if diameter <= 0 or diameter > 120:
        return 12
    if diameter >= 16:
        return 8
    return 0


def map_risk_to_priority(score: float) -> str:
    if score >= 75:
        return "Critical Priority"
    if score >= 55:
        return "High Priority"
    if score >= 35:
        return "Medium Priority"
    if score >= 15:
        return "Low Priority"
    return "Routine"


def generate_asset_recommendation(row, risk_score: float) -> str:
    priority = map_risk_to_priority(risk_score)

    if priority == "Critical Priority":
        return "Immediate engineering review recommended before operational use."
    if priority == "High Priority":
        return "Prioritize for near-term inspection or maintenance planning."
    if priority == "Medium Priority":
        return "Review during scheduled QA or asset management update."
    if priority == "Low Priority":
        return "Monitor and validate during routine data review."
    return "No immediate action required."


def build_utility_intelligence(
    assets_df: pd.DataFrame,
    issues_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    df = assets_df.copy()

    issue_counts = {}
    critical_counts = {}

    if issues_df is not None and not issues_df.empty:
        issue_counts = issues_df.groupby("feature_index").size().to_dict()
        critical_counts = (
            issues_df[issues_df["severity"] == "Critical"]
            .groupby("feature_index")
            .size()
            .to_dict()
        )

    rows = []

    for idx, row in df.iterrows():
        age_score = calculate_asset_age_score(row.get("install_year"))
        condition_score = calculate_condition_score(row.get("condition"))
        inspection_score = calculate_inspection_score(row.get("last_inspection_date"))
        diameter_score = calculate_diameter_score(row.get("diameter_in"))

        qa_issue_score = min(issue_counts.get(idx, 0) * 4, 20)
        critical_issue_score = min(critical_counts.get(idx, 0) * 10, 20)

        total_score = (
            age_score
            + condition_score
            + inspection_score
            + diameter_score
            + qa_issue_score
            + critical_issue_score
        )

        total_score = min(100, total_score)

        asset_id = row.get("asset_id", f"row_{idx}")
        if pd.isna(asset_id) or str(asset_id).strip() == "":
            asset_id = f"row_{idx}"

        rows.append(
            {
                "feature_index": idx,
                "asset_id": asset_id,
                "utility_risk_score": total_score,
                "maintenance_priority": map_risk_to_priority(total_score),
                "age_score": age_score,
                "condition_score": condition_score,
                "inspection_score": inspection_score,
                "diameter_score": diameter_score,
                "qa_issue_score": qa_issue_score,
                "critical_issue_score": critical_issue_score,
                "recommended_action": generate_asset_recommendation(row, total_score),
            }
        )

    return pd.DataFrame(rows).sort_values(
        by="utility_risk_score",
        ascending=False,
    ).reset_index(drop=True)

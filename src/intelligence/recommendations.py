"""
src/intelligence/recommendations.py

Two-level recommendation engine for GeoOps:

1. Per-asset recommendations  — action code + rationale for individual assets
2. Dataset recommendations    — executive-level findings for the full dataset

Action codes (ordered by urgency):
    Escalate      — structural failure risk, safety concern, immediately actionable
    Replace       — asset at end-of-life with critical condition or risk score
    Repair        — known defect, schedule near-term maintenance
    Inspect       — high risk but missing condition data, send to field
    Monitor       — moderate risk, track over next inspection cycle
    Validate Data — data quality issues prevent accurate risk assessment
    Routine       — no significant risk factors, standard maintenance schedule
"""

from __future__ import annotations

import pandas as pd


# ── Per-asset recommendation ──────────────────────────────────────────────────

_SCORE_TO_ACTION = [
    (75, "Escalate"),
    (65, "Replace"),
    (50, "Repair"),
    (35, "Inspect"),
    (20, "Monitor"),
    (10, "Validate Data"),
    (0,  "Routine"),
]

_ACTION_RATIONALE = {
    "Escalate":      "Risk score indicates potential failure risk. Escalate to engineering for immediate review before operational use.",
    "Replace":       "Asset condition and age suggest end-of-life. Prioritize for capital replacement planning.",
    "Repair":        "Asset shows signs of degradation. Schedule maintenance intervention in the near term.",
    "Inspect":       "Elevated risk score without current inspection data. Deploy field inspection to validate asset condition.",
    "Monitor":       "Moderate risk — no immediate action required. Track during the next scheduled inspection cycle.",
    "Validate Data": "Data quality issues prevent accurate risk scoring. Resolve attribute errors before making maintenance decisions.",
    "Routine":       "Asset is within normal operational parameters. Standard maintenance schedule applies.",
}


def _score_to_action(risk_score: float) -> str:
    for threshold, action in _SCORE_TO_ACTION:
        if risk_score >= threshold:
            return action
    return "Routine"


def generate_asset_recommendation(risk_score: float, issues: list[str] | None = None) -> dict:
    """
    Return action code and rationale for a single asset.

    Args:
        risk_score: 0–100 utility risk score
        issues:     list of issue_category strings for this asset (optional)

    Returns:
        {"action": str, "rationale": str}
    """
    issues = issues or []

    # Override rules based on issue patterns
    issue_set = {i.lower() for i in issues}

    if "missing geometry" in issue_set or "missing asset id" in issue_set:
        if risk_score < 35:
            return {
                "action":    "Validate Data",
                "rationale": _ACTION_RATIONALE["Validate Data"],
            }

    action = _score_to_action(risk_score)

    # Bump up if critical QA issues exist alongside moderate risk
    if action in ("Monitor", "Inspect") and any(
        kw in issue_set for kw in ("duplicate asset id", "invalid condition", "future install year")
    ):
        action = "Validate Data"

    return {
        "action":    action,
        "rationale": _ACTION_RATIONALE[action],
    }


# ── Dataset-level recommendations ────────────────────────────────────────────

def generate_dataset_recommendations(
    issues_df: pd.DataFrame,
    utility_df: pd.DataFrame | None = None,
) -> list[str]:
    """
    Generate executive-level recommendations for the full dataset.

    Returns a list of plain-English recommendation strings, ordered
    from most to least urgent.
    """
    if issues_df.empty:
        return ["No significant data quality issues detected. Dataset appears ready for operational use."]

    recommendations: list[tuple[int, str]] = []  # (priority, message)

    counts = issues_df["issue_category"].value_counts().to_dict()
    total  = len(issues_df)

    sev_counts = issues_df["severity"].value_counts().to_dict()
    critical_n = sev_counts.get("Critical", 0)
    high_n     = sev_counts.get("High", 0)

    # ── Critical-severity findings ─────────────────────────────────────────────
    if critical_n > 0:
        recommendations.append((
            10,
            f"{critical_n} critical-severity issue(s) detected. "
            "These require immediate resolution before this data is used for operational planning or client delivery."
        ))

    if counts.get("Missing Asset ID", 0) > 0:
        recommendations.append((
            9,
            f"{counts['Missing Asset ID']} asset(s) are missing unique identifiers. "
            "Assets without IDs cannot be tracked, scheduled, or linked to work orders. "
            "Assign IDs from your source registry before proceeding."
        ))

    if counts.get("Duplicate Asset ID", 0) > 0:
        recommendations.append((
            9,
            f"{counts['Duplicate Asset ID']} duplicate asset ID(s) found. "
            "Duplicates will corrupt any analysis that relies on unique asset tracking. "
            "Perform an asset identifier audit and deduplicate before analysis."
        ))

    if counts.get("Missing Geometry", 0) > 0:
        recommendations.append((
            8,
            f"{counts['Missing Geometry']} feature(s) are missing geometry. "
            "These assets cannot be mapped, spatially joined, or exported to ArcGIS. "
            "Investigate and restore geometry from source records."
        ))

    # ── High-severity findings ─────────────────────────────────────────────────
    if counts.get("Missing Inspection Date", 0) > 5:
        n = counts["Missing Inspection Date"]
        recommendations.append((
            7,
            f"{n} asset(s) have no recorded inspection date. "
            "Inspection history is a primary input for risk scoring. "
            "Reconcile field inspection records and populate this field."
        ))

    if counts.get("Future Install Year", 0) > 0 or counts.get("Unrealistic Install Year", 0) > 0:
        n = counts.get("Future Install Year", 0) + counts.get("Unrealistic Install Year", 0)
        recommendations.append((
            6,
            f"{n} asset(s) have install years outside plausible bounds. "
            "Asset age is a key risk factor — incorrect years will skew risk scores. "
            "Verify against original construction or permit records."
        ))

    if counts.get("Missing Condition", 0) > 10:
        n = counts["Missing Condition"]
        recommendations.append((
            6,
            f"{n} asset(s) are missing a condition rating. "
            "Condition is the highest-weighted risk factor in the scoring model. "
            "Field assessments or recent inspection reports should populate this field."
        ))

    # ── Medium-severity findings ───────────────────────────────────────────────
    if counts.get("Suspicious Diameter", 0) > 0 or counts.get("Invalid Diameter", 0) > 0:
        n = counts.get("Suspicious Diameter", 0) + counts.get("Invalid Diameter", 0)
        recommendations.append((
            4,
            f"{n} asset(s) have diameter values outside expected ranges. "
            "Verify against utility records or physical inspections."
        ))

    if counts.get("Invalid Condition", 0) > 0:
        n = counts["Invalid Condition"]
        recommendations.append((
            4,
            f"{n} asset(s) have non-standard condition values. "
            "Standardize condition values to: Excellent, Good, Fair, Poor, Critical."
        ))

    # ── Risk-based findings (utility intelligence) ─────────────────────────────
    if utility_df is not None and not utility_df.empty:
        if "maintenance_priority" in utility_df.columns:
            crit_assets = int((utility_df["maintenance_priority"] == "Critical Priority").sum())
            high_assets = int((utility_df["maintenance_priority"] == "High Priority").sum())
            if crit_assets > 0:
                recommendations.append((
                    8,
                    f"{crit_assets} asset(s) scored Critical Priority in the risk model. "
                    "These should be reviewed by an engineer before the next planned maintenance cycle."
                ))
            if high_assets > 0:
                recommendations.append((
                    5,
                    f"{high_assets} asset(s) scored High Priority. "
                    "Include these in the next maintenance planning session."
                ))

    # Sort by priority descending, return messages only
    recommendations.sort(key=lambda x: x[0], reverse=True)
    return [msg for _, msg in recommendations]

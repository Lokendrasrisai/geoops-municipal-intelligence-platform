"""
src/intelligence/explainability.py

Explainability layer for GeoOps risk scores.

For every asset, this module produces:
  - A list of score drivers (which factors contributed, and how many points each added)
  - A human-readable narrative sentence explaining the risk level
  - The recommended action

This is what separates GeoOps from a spreadsheet.
Every flag has a reason. Every score has an explanation.
"""

from __future__ import annotations

import datetime
import pandas as pd


# ── Constants ─────────────────────────────────────────────────────────────────

_CURRENT_YEAR = datetime.date.today().year

_CONDITION_POINTS: dict[str, int] = {
    "Critical":  40,
    "Poor":      30,
    "Fair":      15,
    "Good":       5,
    "Excellent":  0,
    "Unknown":   10,
}

_ACTION_THRESHOLDS = [
    (75, "Escalate"),
    (65, "Replace"),
    (50, "Repair"),
    (35, "Inspect"),
    (20, "Monitor"),
    (10, "Validate Data"),
    (0,  "Routine"),
]


# ── Driver calculators ────────────────────────────────────────────────────────

def _age_driver(install_year) -> dict:
    try:
        age = _CURRENT_YEAR - int(install_year)
    except Exception:
        return {"factor": "Asset Age", "points": 10, "detail": "unknown install year"}

    if age >= 75:
        pts, detail = 25, f"{age} years old (>75 yr threshold)"
    elif age >= 50:
        pts, detail = 18, f"{age} years old (50–75 yr range)"
    elif age >= 30:
        pts, detail = 10, f"{age} years old (30–50 yr range)"
    elif age >= 10:
        pts, detail = 5,  f"{age} years old (10–30 yr range)"
    else:
        pts, detail = 0,  f"{age} years old (< 10 yr, new asset)"

    return {"factor": "Asset Age", "points": pts, "detail": detail}


def _condition_driver(condition) -> dict:
    if pd.isna(condition) or str(condition).strip() == "":
        return {"factor": "Condition", "points": 15, "detail": "condition not recorded"}
    pts = _CONDITION_POINTS.get(str(condition).strip(), 12)
    return {"factor": "Condition", "points": pts, "detail": f"rated '{condition}'"}


def _inspection_driver(last_inspection_date) -> dict:
    if pd.isna(last_inspection_date) or str(last_inspection_date).strip() == "":
        return {"factor": "Inspection Currency", "points": 25, "detail": "never inspected or date missing"}
    try:
        last = pd.to_datetime(last_inspection_date)
        years_since = (pd.Timestamp.today() - last).days / 365.25
    except Exception:
        return {"factor": "Inspection Currency", "points": 15, "detail": "unparseable inspection date"}

    if years_since >= 5:
        pts, detail = 25, f"{years_since:.1f} years since last inspection"
    elif years_since >= 3:
        pts, detail = 18, f"{years_since:.1f} years since last inspection"
    elif years_since >= 1:
        pts, detail = 8,  f"{years_since:.1f} years since last inspection"
    else:
        pts, detail = 0,  f"inspected {years_since:.1f} years ago (current)"

    return {"factor": "Inspection Currency", "points": pts, "detail": detail}


def _diameter_driver(diameter) -> dict:
    try:
        d = float(diameter)
    except Exception:
        return {"factor": "Diameter", "points": 8, "detail": "non-numeric value"}

    if d <= 0 or d > 120:
        return {"factor": "Diameter", "points": 12, "detail": f"{d}\" — outside valid range"}
    if d >= 16:
        return {"factor": "Diameter", "points": 8, "detail": f"{d}\" — large main, higher consequence"}
    return {"factor": "Diameter", "points": 0, "detail": f"{d}\" — standard size"}


def _qa_driver(qa_issue_count: int, critical_issue_count: int) -> list[dict]:
    drivers = []
    qa_pts = min(qa_issue_count * 4, 20)
    if qa_pts > 0:
        drivers.append({
            "factor": "Data Quality Issues",
            "points": qa_pts,
            "detail": f"{qa_issue_count} QA flag(s) detected",
        })
    crit_pts = min(critical_issue_count * 10, 20)
    if crit_pts > 0:
        drivers.append({
            "factor": "Critical QA Flags",
            "points": crit_pts,
            "detail": f"{critical_issue_count} critical severity issue(s)",
        })
    return drivers


# ── Narrative builder ─────────────────────────────────────────────────────────

def _build_narrative(asset_id: str, score: int, drivers: list[dict], action: str) -> str:
    top_drivers = sorted(drivers, key=lambda d: d["points"], reverse=True)[:3]
    top_reasons = [f"{d['factor'].lower()} ({d['detail']})" for d in top_drivers if d["points"] > 0]

    if not top_reasons:
        return f"Asset {asset_id} has a low risk score of {score}/100. No significant risk factors identified. Recommended action: {action}."

    reason_str = ", ".join(top_reasons[:-1])
    if len(top_reasons) > 1:
        reason_str += f", and {top_reasons[-1]}"
    else:
        reason_str = top_reasons[0]

    level = (
        "critical risk" if score >= 75
        else "high risk" if score >= 55
        else "moderate risk" if score >= 35
        else "low risk"
    )

    return (
        f"Asset {asset_id} has a {level} score of {score}/100, "
        f"primarily driven by {reason_str}. "
        f"Recommended action: {action}."
    )


def _resolve_action(score: int) -> str:
    for threshold, action in _ACTION_THRESHOLDS:
        if score >= threshold:
            return action
    return "Routine"


# ── Public API ────────────────────────────────────────────────────────────────

def explain_asset(
    asset_id: str,
    install_year,
    condition,
    last_inspection_date,
    diameter_in,
    risk_score: int,
    qa_issue_count: int = 0,
    critical_issue_count: int = 0,
) -> dict:
    """
    Return a full explainability dict for one asset.

    Returns:
        {
            "asset_id":    str,
            "risk_score":  int,
            "action":      str,
            "narrative":   str,
            "drivers":     [ {"factor": str, "points": int, "detail": str}, ... ]
        }
    """
    drivers = [
        _age_driver(install_year),
        _condition_driver(condition),
        _inspection_driver(last_inspection_date),
        _diameter_driver(diameter_in),
        *_qa_driver(qa_issue_count, critical_issue_count),
    ]

    action    = _resolve_action(risk_score)
    narrative = _build_narrative(asset_id, risk_score, drivers, action)

    return {
        "asset_id":   asset_id,
        "risk_score": risk_score,
        "action":     action,
        "narrative":  narrative,
        "drivers":    drivers,
    }


def explain_dataset(
    assets_df: pd.DataFrame,
    utility_df: pd.DataFrame,
    issues_df: pd.DataFrame | None = None,
    top_n: int = 10,
) -> list[dict]:
    """
    Return explainability dicts for the top_n highest-risk assets.

    Args:
        assets_df:   Raw asset DataFrame (must have asset_id, install_year, condition,
                     last_inspection_date, diameter_in columns if available)
        utility_df:  Output of build_utility_intelligence() — must have utility_risk_score
        issues_df:   GeoQA output — used to count per-asset issues
        top_n:       How many assets to explain (default 10)
    """
    issue_counts:    dict[int, int] = {}
    critical_counts: dict[int, int] = {}

    if issues_df is not None and not issues_df.empty and "feature_index" in issues_df.columns:
        issue_counts    = issues_df.groupby("feature_index").size().to_dict()
        critical_counts = (
            issues_df[issues_df["severity"] == "Critical"]
            .groupby("feature_index")
            .size()
            .to_dict()
        )

    # Merge on positional index
    merged = assets_df.copy().reset_index(drop=False)
    merged["_orig_index"] = merged["index"] if "index" in merged.columns else merged.index
    merged["utility_risk_score"] = utility_df["utility_risk_score"].values

    top = merged.nlargest(top_n, "utility_risk_score")

    results = []
    for _, row in top.iterrows():
        idx        = int(row.get("_orig_index", row.name))
        asset_id   = str(row.get("asset_id", f"row_{idx}"))
        risk_score = int(row.get("utility_risk_score", 0))

        explanation = explain_asset(
            asset_id            = asset_id,
            install_year        = row.get("install_year"),
            condition           = row.get("condition"),
            last_inspection_date= row.get("last_inspection_date"),
            diameter_in         = row.get("diameter_in"),
            risk_score          = risk_score,
            qa_issue_count      = issue_counts.get(idx, 0),
            critical_issue_count= critical_counts.get(idx, 0),
        )
        results.append(explanation)

    return results

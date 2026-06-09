import pandas as pd


def build_pressure_zone_hotspots(
    assets_df: pd.DataFrame,
    utility_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Summarize utility risk by pressure zone.
    """

    if "pressure_zone" not in assets_df.columns:
        raise ValueError("pressure_zone column required in assets_df")

    if "utility_risk_score" not in utility_df.columns:
        raise ValueError("utility_risk_score column required in utility_df")

    merged = assets_df.copy()

    merged["utility_risk_score"] = utility_df["utility_risk_score"].values
    merged["maintenance_priority"] = utility_df["maintenance_priority"].values

    summary = (
        merged.groupby("pressure_zone", dropna=False)
        .agg(
            asset_count=("asset_id", "count"),
            avg_risk_score=("utility_risk_score", "mean"),
            max_risk_score=("utility_risk_score", "max"),
            critical_priority_count=(
                "maintenance_priority",
                lambda x: int((x == "Critical Priority").sum()),
            ),
            high_priority_count=(
                "maintenance_priority",
                lambda x: int((x == "High Priority").sum()),
            ),
        )
        .reset_index()
    )

    summary["avg_risk_score"] = summary["avg_risk_score"].round(2)

    summary = summary.sort_values(
        by=["avg_risk_score", "critical_priority_count"],
        ascending=False,
    ).reset_index(drop=True)

    return summary


def generate_hotspot_insights(hotspots_df: pd.DataFrame) -> list[str]:
    """
    Generate executive-friendly hotspot insights.
    """

    if hotspots_df.empty:
        return ["No hotspot patterns detected."]

    insights = []

    top_zone = hotspots_df.iloc[0]

    insights.append(
        f"Highest average utility risk is concentrated in pressure zone '{top_zone['pressure_zone']}' "
        f"with an average risk score of {top_zone['avg_risk_score']}."
    )

    if top_zone["critical_priority_count"] > 0:
        insights.append(
            f"Pressure zone '{top_zone['pressure_zone']}' contains "
            f"{top_zone['critical_priority_count']} critical-priority assets."
        )

    high_risk_zones = hotspots_df[
        (hotspots_df["avg_risk_score"] >= 55)
        | (hotspots_df["critical_priority_count"] > 0)
    ]

    if len(high_risk_zones) > 0:
        insights.append(
            f"{len(high_risk_zones)} pressure zone(s) require focused operational review."
        )

    return insights
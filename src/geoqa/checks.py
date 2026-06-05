import pandas as pd

from src.geoqa.models import GeoQAIssue


VALID_CONDITIONS = {"Excellent", "Good", "Fair", "Poor", "Critical", "Unknown"}
VALID_STATUSES = {"Active", "Inactive", "Abandoned", "Retired", "Unknown"}


def get_asset_id(row: pd.Series, idx: int) -> str:
    for field in ["asset_id", "assetid", "ASSET_ID", "OBJECTID", "id"]:
        if field in row and pd.notna(row[field]):
            return str(row[field])
    return f"row_{idx}"


def check_missing_asset_id(df: pd.DataFrame) -> list[GeoQAIssue]:
    issues = []
    if "asset_id" not in df.columns:
        return issues

    for idx, row in df.iterrows():
        if pd.isna(row["asset_id"]) or str(row["asset_id"]).strip() == "":
            issues.append(
                GeoQAIssue(
                    feature_index=idx,
                    asset_id=f"row_{idx}",
                    issue_category="Missing Asset ID",
                    issue_description="Asset has no unique identifier.",
                    severity="Critical",
                    recommended_action="Assign a unique asset ID before publishing, migration, or client delivery.",
                )
            )
    return issues


def check_duplicate_asset_id(df: pd.DataFrame) -> list[GeoQAIssue]:
    issues = []
    if "asset_id" not in df.columns:
        return issues

    duplicated = df[df["asset_id"].duplicated(keep=False) & df["asset_id"].notna()]

    for idx, row in duplicated.iterrows():
        issues.append(
            GeoQAIssue(
                feature_index=idx,
                asset_id=str(row["asset_id"]),
                issue_category="Duplicate Asset ID",
                issue_description=f"Asset ID {row['asset_id']} appears more than once.",
                severity="Critical",
                recommended_action="Verify whether records are duplicates or whether asset IDs need correction.",
            )
        )

    return issues


def check_missing_geometry(df: pd.DataFrame) -> list[GeoQAIssue]:
    issues = []

    geometry_field = None
    for field in ["SHAPE", "geometry", "geom", "Geometry"]:
        if field in df.columns:
            geometry_field = field
            break

    if geometry_field is None:
        return issues

    for idx, row in df.iterrows():
        if row.get(geometry_field) is None or pd.isna(row.get(geometry_field)):
            issues.append(
                GeoQAIssue(
                    feature_index=idx,
                    asset_id=get_asset_id(row, idx),
                    issue_category="Missing Geometry",
                    issue_description="Feature has no usable geometry.",
                    severity="Critical",
                    recommended_action="Verify or recreate geometry before using this record in GIS workflows.",
                )
            )

    return issues


def check_missing_condition(df: pd.DataFrame) -> list[GeoQAIssue]:
    issues = []
    if "condition" not in df.columns:
        return issues

    for idx, row in df.iterrows():
        if pd.isna(row["condition"]) or str(row["condition"]).strip() == "":
            issues.append(
                GeoQAIssue(
                    feature_index=idx,
                    asset_id=get_asset_id(row, idx),
                    issue_category="Missing Condition",
                    issue_description="Asset condition is missing.",
                    severity="High",
                    recommended_action="Review inspection records or field data to populate condition.",
                )
            )
    return issues


def check_invalid_condition(df: pd.DataFrame) -> list[GeoQAIssue]:
    issues = []
    if "condition" not in df.columns:
        return issues

    for idx, row in df.iterrows():
        condition = row["condition"]
        if pd.notna(condition) and str(condition).strip() != "" and condition not in VALID_CONDITIONS:
            issues.append(
                GeoQAIssue(
                    feature_index=idx,
                    asset_id=get_asset_id(row, idx),
                    issue_category="Invalid Condition",
                    issue_description=f"Condition value '{condition}' is not recognized.",
                    severity="Medium",
                    recommended_action="Standardize condition values to accepted categories.",
                )
            )
    return issues


def check_invalid_install_year(df: pd.DataFrame, current_year: int = 2026) -> list[GeoQAIssue]:
    issues = []
    if "install_year" not in df.columns:
        return issues

    for idx, row in df.iterrows():
        year = row["install_year"]

        if pd.isna(year):
            issues.append(
                GeoQAIssue(
                    feature_index=idx,
                    asset_id=get_asset_id(row, idx),
                    issue_category="Missing Install Year",
                    issue_description="Install year is missing.",
                    severity="Medium",
                    recommended_action="Populate install year if available from source records.",
                )
            )
            continue

        try:
            year_int = int(year)
        except Exception:
            issues.append(
                GeoQAIssue(
                    feature_index=idx,
                    asset_id=get_asset_id(row, idx),
                    issue_category="Invalid Install Year",
                    issue_description=f"Install year '{year}' is not numeric.",
                    severity="Medium",
                    recommended_action="Standardize install year as a four-digit year.",
                )
            )
            continue

        if year_int > current_year:
            issues.append(
                GeoQAIssue(
                    feature_index=idx,
                    asset_id=get_asset_id(row, idx),
                    issue_category="Future Install Year",
                    issue_description=f"Install year {year_int} is later than current year.",
                    severity="High",
                    recommended_action="Verify install year from source records.",
                )
            )
        elif year_int < 1850:
            issues.append(
                GeoQAIssue(
                    feature_index=idx,
                    asset_id=get_asset_id(row, idx),
                    issue_category="Unrealistic Install Year",
                    issue_description=f"Install year {year_int} appears unrealistic.",
                    severity="High",
                    recommended_action="Verify install year from historical records.",
                )
            )

    return issues


def check_missing_inspection_date(df: pd.DataFrame) -> list[GeoQAIssue]:
    issues = []
    if "last_inspection_date" not in df.columns:
        return issues

    for idx, row in df.iterrows():
        if pd.isna(row["last_inspection_date"]) or str(row["last_inspection_date"]).strip() == "":
            issues.append(
                GeoQAIssue(
                    feature_index=idx,
                    asset_id=get_asset_id(row, idx),
                    issue_category="Missing Inspection Date",
                    issue_description="Last inspection date is missing.",
                    severity="High",
                    recommended_action="Review field inspection records and populate inspection date.",
                )
            )
    return issues


def check_suspicious_diameter(df: pd.DataFrame) -> list[GeoQAIssue]:
    issues = []
    if "diameter_in" not in df.columns:
        return issues

    for idx, row in df.iterrows():
        value = row["diameter_in"]

        if pd.isna(value):
            issues.append(
                GeoQAIssue(
                    feature_index=idx,
                    asset_id=get_asset_id(row, idx),
                    issue_category="Missing Diameter",
                    issue_description="Diameter is missing for utility asset.",
                    severity="High",
                    recommended_action="Populate diameter from source records or field inventory.",
                )
            )
            continue

        try:
            diameter = float(value)
            if diameter <= 0 or diameter > 120:
                issues.append(
                    GeoQAIssue(
                        feature_index=idx,
                        asset_id=get_asset_id(row, idx),
                        issue_category="Suspicious Diameter",
                        issue_description=f"Diameter value {diameter} appears unusual.",
                        severity="Medium",
                        recommended_action="Verify diameter against utility records.",
                    )
                )
        except Exception:
            issues.append(
                GeoQAIssue(
                    feature_index=idx,
                    asset_id=get_asset_id(row, idx),
                    issue_category="Invalid Diameter",
                    issue_description=f"Diameter value '{value}' is not numeric.",
                    severity="Medium",
                    recommended_action="Standardize diameter as a numeric value.",
                )
            )

    return issues
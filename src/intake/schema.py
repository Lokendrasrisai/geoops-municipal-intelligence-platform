from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass
class GeoOpsSchemaReport:
    total_rows: int
    total_columns: int
    columns: list[str]
    detected_latitude_field: Optional[str]
    detected_longitude_field: Optional[str]
    detected_geometry_field: Optional[str]
    detected_asset_id_field: Optional[str]


LATITUDE_CANDIDATES = ["latitude", "lat", "y", "LATITUDE", "LAT", "Y"]
LONGITUDE_CANDIDATES = ["longitude", "lon", "lng", "x", "LONGITUDE", "LON", "LNG", "X"]
GEOMETRY_CANDIDATES = ["SHAPE", "geometry", "geom", "Geometry"]
ASSET_ID_CANDIDATES = ["asset_id", "assetid", "id", "OBJECTID", "globalid", "GlobalID"]


def find_first_matching_column(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    existing = set(df.columns)
    for candidate in candidates:
        if candidate in existing:
            return candidate
    return None


def inspect_schema(df: pd.DataFrame) -> GeoOpsSchemaReport:
    """Inspect incoming dataset and detect important GIS fields."""
    return GeoOpsSchemaReport(
        total_rows=len(df),
        total_columns=len(df.columns),
        columns=list(df.columns),
        detected_latitude_field=find_first_matching_column(df, LATITUDE_CANDIDATES),
        detected_longitude_field=find_first_matching_column(df, LONGITUDE_CANDIDATES),
        detected_geometry_field=find_first_matching_column(df, GEOMETRY_CANDIDATES),
        detected_asset_id_field=find_first_matching_column(df, ASSET_ID_CANDIDATES),
    )
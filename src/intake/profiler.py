import pandas as pd


GEOMETRY_COLUMNS = ["SHAPE", "geometry", "geom", "Geometry"]


def get_non_geometry_df(df: pd.DataFrame) -> pd.DataFrame:
    """Return dataframe without geometry columns for safe profiling."""
    geometry_cols = [col for col in GEOMETRY_COLUMNS if col in df.columns]
    return df.drop(columns=geometry_cols, errors="ignore")


def profile_dataset(df: pd.DataFrame) -> dict:
    """Create a basic dataset profile for GeoOps intake."""
    safe_df = get_non_geometry_df(df)

    missing_by_column = safe_df.isna().sum().sort_values(ascending=False).to_dict()

    return {
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "columns": list(df.columns),
        "missing_by_column": {str(k): int(v) for k, v in missing_by_column.items()},
        "duplicate_rows": int(safe_df.duplicated().sum()),
        "memory_usage_mb": round(float(safe_df.memory_usage(deep=True).sum() / (1024 * 1024)), 3),
        "geometry_columns_excluded": [col for col in GEOMETRY_COLUMNS if col in df.columns],
    }
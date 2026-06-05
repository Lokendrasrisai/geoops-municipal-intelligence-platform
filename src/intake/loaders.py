from pathlib import Path
from typing import Optional

import pandas as pd


def load_csv(path: str | Path) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame."""
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    if path.suffix.lower() != ".csv":
        raise ValueError("File must be a CSV.")

    return pd.read_csv(path)


def load_geojson(path: str | Path) -> pd.DataFrame:
    """Load a GeoJSON file. Uses GeoPandas when available."""
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"GeoJSON file not found: {path}")

    if path.suffix.lower() not in [".geojson", ".json"]:
        raise ValueError("File must be GeoJSON or JSON.")

    try:
        import geopandas as gpd

        gdf = gpd.read_file(path)
        return pd.DataFrame(gdf)
    except ImportError as exc:
        raise ImportError("GeoPandas is required to load GeoJSON files.") from exc


def load_arcgis_feature_layer(layer_url: str, max_records: Optional[int] = 2000) -> pd.DataFrame:
    """
    Load a public ArcGIS Feature Layer into a DataFrame.

    This is read-only. It does not edit or publish anything.
    """
    try:
        from arcgis.features import FeatureLayer
    except ImportError as exc:
        raise ImportError("ArcGIS API for Python is required.") from exc

    if not layer_url.startswith("http"):
        raise ValueError("ArcGIS layer URL must start with http or https.")

    layer = FeatureLayer(layer_url)

    features = layer.query(
        where="1=1",
        out_fields="*",
        return_geometry=True,
        result_record_count=max_records,
    )

    try:
        return features.sdf
    except Exception:
        # Fallback if Spatially Enabled DataFrame fails
        records = []
        for feature in features.features:
            row = dict(feature.attributes)
            row["geometry"] = feature.geometry
            records.append(row)
        return pd.DataFrame(records)
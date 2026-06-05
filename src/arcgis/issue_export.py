# src/arcgis/issue_export.py

import json
from pathlib import Path


def export_issue_geojson(
    issues_df,
    original_df,
    output_path="outputs/geoqa_issue_layer.geojson",
):
    """
    Export GeoQA issues as a GIS-ready GeoJSON layer.
    """

    features = []

    geometry_field = None

    for candidate in ["SHAPE", "geometry", "geom"]:
        if candidate in original_df.columns:
            geometry_field = candidate
            break

    if geometry_field is None:
        raise ValueError(
            "No geometry column found."
        )

    for _, issue in issues_df.iterrows():

        feature_index = issue["feature_index"]

        if feature_index >= len(original_df):
            continue

        source_row = original_df.iloc[
            feature_index
        ]

        geometry = source_row[
            geometry_field
        ]

        if geometry is None:
            continue

        try:

            x = geometry["x"]
            y = geometry["y"]

            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [x, y],
                    },
                    "properties": {
                        "asset_id": issue["asset_id"],
                        "severity": issue["severity"],
                        "category": issue[
                            "issue_category"
                        ],
                        "description": issue[
                            "issue_description"
                        ],
                        "recommended_action": issue[
                            "recommended_action"
                        ],
                    },
                }
            )

        except Exception:
            pass

    geojson = {
        "type": "FeatureCollection",
        "features": features,
    }

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            geojson,
            f,
            indent=2,
        )

    return output_path
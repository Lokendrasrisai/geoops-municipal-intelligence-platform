from arcgis.features import FeatureLayer
import pandas as pd


def load_arcgis_feature_layer(
    layer_url: str,
    max_records: int = 5000,
) -> pd.DataFrame:

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

        records = []

        for feature in features.features:

            row = dict(
                feature.attributes
            )

            row["geometry"] = (
                feature.geometry
            )

            records.append(row)

        return pd.DataFrame(records)
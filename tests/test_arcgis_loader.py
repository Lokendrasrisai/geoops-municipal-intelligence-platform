from src.arcgis.feature_layer_loader import (
    load_arcgis_feature_layer,
)

LAYER_URL = (
    "https://sampleserver6.arcgisonline.com/"
    "arcgis/rest/services/"
    "Census/MapServer/3"
)

df = load_arcgis_feature_layer(
    LAYER_URL
)

print(df.head())

print(
    f"Rows: {len(df)}"
)

print(
    f"Columns: {len(df.columns)}"
)
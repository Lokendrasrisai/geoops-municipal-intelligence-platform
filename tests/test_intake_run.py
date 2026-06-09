from src.intake.loaders import load_arcgis_feature_layer
from src.intake.schema import inspect_schema
from src.intake.profiler import profile_dataset

LAYER_URL = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3"


def main():
    print("Loading ArcGIS layer...")
    df = load_arcgis_feature_layer(LAYER_URL)

    print("\nSchema Report")
    schema = inspect_schema(df)
    print(schema)

    print("\nDataset Profile")
    profile = profile_dataset(df)
    for key, value in profile.items():
        if key != "missing_by_column":
            print(f"{key}: {value}")

    print("\nTop Missing Columns")
    for col, count in list(profile["missing_by_column"].items())[:10]:
        print(f"{col}: {count}")


if __name__ == "__main__":
    main()
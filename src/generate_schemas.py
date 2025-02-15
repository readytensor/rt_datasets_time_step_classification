import os
import pandas as pd
import json
from typing import Dict, List, Union
import pprint
from utils import load_metadata, load_features_config, strip_quotes, JSONEncoder

import paths


def filter_features_for_dataset(
    dataset_name: str, field_type: str, features_config: pd.DataFrame
) -> pd.DataFrame:
    """
    Filters the features configuration for the given dataset and field type.

    Args:
    dataset_name (str): The name of the dataset.
    field_type (str): The type of field to filter for.
    features_config (pd.DataFrame): The features configuration data.

    Returns:
    pd.DataFrame: The filtered features configuration.
    """

    # Filter features related to this dataset
    dataset_df = features_config[features_config["name"] == dataset_name]
    if dataset_df.empty:
        raise ValueError(f"Error: No features for {dataset_name}")
    if field_type == "feature":
        feature_field_types = ["past_covariate", "future_covariate", "static_covariate"]
    else:
        feature_field_types = [field_type]
    filtered_features = dataset_df[dataset_df["field_type"].isin(feature_field_types)]
    return filtered_features


def create_id_section(dataset_name: str, features_config: pd.DataFrame) -> Dict:
    """
    Create the id section of the schema.

    Args:
    dataset_name (str): The name of the dataset.
    features_config (pd.DataFrame): The features configuration data.

    Returns:
    Dict: The id section of the schema.
    """
    # Filter features related to this dataset
    filtered = filter_features_for_dataset(dataset_name, "id", features_config)
    if filtered.empty or filtered.shape[0] > 1:
        raise ValueError(f"Error: No id field or more than id field for {dataset_name}")
    # Create the id section
    field_section = {
        "name": filtered["field_name"].values[0],
        "description": filtered["field_description"].values[0],
    }
    return field_section


def create_target_section(
    dataset_name: str, dataset: pd.DataFrame, features_config: pd.DataFrame
) -> Dict:
    """
    Create the target section of the schema.

    Args:
    dataset_name (str): The name of the dataset.
    dataset (pd.DataFrame): The dataset.
    features_config (pd.DataFrame): The features configuration data.

    Returns:
    Dict: The target section of the schema.
    """

    filtered = filter_features_for_dataset(dataset_name, "target", features_config)
    if filtered.empty or filtered.shape[0] > 1:
        raise ValueError(
            f"Error: No target field or more than target field for {dataset_name}"
        )

    # Create the target section
    target_name = filtered["field_name"].values[0]
    data_type = filtered["data_type"].values[0]
    field_section = {
        "name": target_name,
        "description": filtered["field_description"].values[0],
        "dataType": data_type,
        "example": dataset[target_name].dropna().iloc[0],
    }
    return field_section


def create_time_section(
    dataset_name: str, dataset: pd.DataFrame, features_config: pd.DataFrame
) -> Union[None, Dict]:
    """
    Create the time section of the schema.

    Args:
    dataset_name (str): The name of the dataset.
    dataset (pd.DataFrame): The dataset.
    features_config (pd.DataFrame): The features configuration data.

    Returns:
    Union[None, Dict]: The time section of the schema.
    """

    filtered = filter_features_for_dataset(dataset_name, "time", features_config)
    # If no time field in the dataset, return None
    if filtered.empty:
        return None

    if filtered.shape[0] > 1:
        raise ValueError(f"Error: More than one time field for {dataset_name}")

    # Create the target section
    time_field_name = filtered["field_name"].values[0]
    data_type = filtered["data_type"].values[0]
    field_section = {
        "name": time_field_name,
        "description": filtered["field_description"].values[0],
        "dataType": data_type,
        "example": dataset[time_field_name].dropna().iloc[0],
    }
    return field_section


def create_feature_section(
    dataset_name: str,
    dataset_row: pd.Series,
    dataset: pd.DataFrame,
    features_config: pd.DataFrame,
) -> List[Dict]:
    """
    Create the feature section of the schema.

    Args:
    dataset_name (str): The name of the dataset.
    dataset_row (pd.Series): The metadata for the dataset.
    dataset (pd.DataFrame): The dataset.
    features_config (pd.DataFrame): The features configuration data.

    Returns:
    List[Dict]: The features section of the schema.
    """
    # Filter features related to this dataset
    features_config = features_config[features_config["name"] == dataset_row["name"]]

    # create the features section
    features = []
    features_df = features_config[
        (features_config["name"] == dataset_name)
        & (features_config["field_type"] == "feature")
    ]
    for _, feature_row in features_df.iterrows():
        feature = {
            "name": feature_row["field_name"],
            "description": feature_row["field_description"],
            "dataType": feature_row["data_type"].upper(),
        }
        if feature_row["data_type"].upper() == "CATEGORICAL":
            feature["categories"] = sorted(
                dataset[feature_row["field_name"]].dropna().unique().tolist(), key=str
            )
        else:
            feature["example"] = dataset[feature_row["field_name"]].dropna().iloc[0]
        feature["nullable"] = dataset[feature_row["field_name"]].isnull().any()
        features.append(feature)

    return features


def generate_schemas(
    dataset_metadata: pd.DataFrame,
    processed_datasets_path: str,
    features_config: pd.DataFrame,
):
    """
    Generate the schema for each dataset.

    Args:
    dataset_metadata (pd.DataFrame): The metadata for all the datasets.
    processed_datasets_path (str): The path where the processed datasets are stored.
    features_config (pd.DataFrame): The features configuration data.
    """
    schemas = []
    dataset_names = []

    # Iterate through all datasets marked for use in the metadata
    for _, dataset_row in dataset_metadata[
        dataset_metadata["use_dataset"] == 1
    ].iterrows():

        dataset_name = dataset_row["name"].strip()
        print("Creating schema for dataset", dataset_name)
        schema = {}
        schema["title"] = dataset_row["title"]
        schema["description"] = dataset_row["description"]
        schema["modelCategory"] = dataset_row["model_category"]
        schema["schemaVersion"] = 1.0
        schema["inputDataFormat"] = "CSV"
        schema["encoding"] = dataset_row["encoding"]
        schema["frequency"] = dataset_row["frequency"]

        csv_path = os.path.join(
            processed_datasets_path, dataset_name, f"{dataset_name}.csv"
        )
        zip_path = os.path.join(
            processed_datasets_path, dataset_name, f"{dataset_name}.zip"
        )

        path = zip_path if os.path.exists(zip_path) else csv_path

        # read dataset
        dataset = pd.read_csv(path)

        schema["idField"] = create_id_section(dataset_name, features_config)

        time_section = create_time_section(dataset_name, dataset, features_config)

        if time_section is not None:
            schema["timeField"] = time_section

        schema["target"] = {
            "name": dataset_row["target_name"],
            "description": dataset_row["target_description"],
            "classes": sorted(
                dataset[dataset_row["target_name"]].dropna().unique().tolist()
            ),
        }

        schema["features"] = create_feature_section(
            dataset_name, dataset_row, dataset, features_config
        )

        schemas.append(schema)
        dataset_names.append(dataset_name)

    # Write the schemas in JSON format to disk
    for dataset_name, schema in zip(dataset_names, schemas):
        output_fpath = os.path.join(
            processed_datasets_path, dataset_name, f"{dataset_name}_schema.json"
        )
        with open(output_fpath, "w", encoding="utf-8") as file_:
            json.dump(schema, file_, cls=JSONEncoder, indent=2)


def run_schema_gen():
    """Generate the schema for each dataset."""
    dataset_metadata = load_metadata(dataset_cfg_path=paths.dataset_cfg_path)
    features_config = load_features_config(
        features_cfg_path=paths.features_cfg_path
    ).apply(strip_quotes)

    generate_schemas(
        dataset_metadata=dataset_metadata,
        processed_datasets_path=paths.processed_datasets_path,
        features_config=features_config,
    )


if __name__ == "__main__":
    run_schema_gen()

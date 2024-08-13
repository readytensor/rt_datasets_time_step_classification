import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CATEGORY = "time_step_classification"

dataset_cfg_path = os.path.join(ROOT_DIR, f"src/config/{CATEGORY}_datasets.csv")
features_cfg_path = os.path.join(ROOT_DIR, f"src/config/{CATEGORY}_datasets_fields.csv")
raw_datasets_path = os.path.join(ROOT_DIR, "datasets/raw/")
processed_datasets_path = os.path.join(ROOT_DIR, "datasets/processed/")

"""
Training pipeline constants.

IMPORTANT: values are NOT hard-coded here anymore. They are loaded once from
`config/config.yaml` (the single source of truth) and exposed under the SAME
constant names as before, so the rest of the code (config_entity.py, components)
keeps working without any change.

To tune a parameter, edit config/config.yaml — not this file.
"""

import os
import yaml

# --- Locate config/config.yaml robustly, independent of the current directory ---
# This file lives at: isd/constant/training_pipeline/__init__.py
# Project root is 4 levels up.
_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
CONFIG_FILE_PATH: str = os.path.join(_PROJECT_ROOT, "config", "config.yaml")


def _load_config(path: str = CONFIG_FILE_PATH) -> dict:
    """Read the YAML config file and return it as a dictionary."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Configuration file not found: {path}. "
            f"Expected a 'config/config.yaml' at the project root."
        )
    with open(path, "r") as yaml_file:
        return yaml.safe_load(yaml_file)


_config = _load_config()

# --- Artifacts ---------------------------------------------------------------
ARTIFACTS_DIR: str = _config["artifacts"]["root_dir"]

# --- Data Ingestion ----------------------------------------------------------
DATA_INGESTION_DIR_NAME: str = _config["data_ingestion"]["dir_name"]
DATA_INGESTION_FEATURE_STORE_DIR: str = _config["data_ingestion"]["feature_store_dir"]
DATA_INGESTION_S3_DATA_NAME: str = _config["data_ingestion"]["s3_data_name"]
DATA_BUCKET_NAME: str = _config["data_ingestion"]["data_bucket_name"]

# --- Data Validation ---------------------------------------------------------
DATA_VALIDATION_DIR_NAME: str = _config["data_validation"]["dir_name"]
DATA_VALIDATION_STATUS_FILE: str = _config["data_validation"]["status_file"]
DATA_VALIDATION_ALL_REQUIRED_FILES: list = _config["data_validation"]["required_files"]

# --- Model Trainer -----------------------------------------------------------
MODEL_TRAINER_DIR_NAME: str = _config["model_trainer"]["dir_name"]
MODEL_TRAINER_PRETRAINED_WEIGHT_URL: str = _config["model_trainer"]["pretrained_weight_url"]
MODEL_TRAINER_NO_EPOCHS: int = _config["model_trainer"]["epochs"]
MODEL_TRAINER_BATCH_SIZE: int = _config["model_trainer"]["batch_size"]

# --- Model Pusher ------------------------------------------------------------
MODEL_BUCKET_NAME: str = _config["model_pusher"]["model_bucket_name"]
S3_MODEL_NAME: str = _config["model_pusher"]["s3_model_name"]

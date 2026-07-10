"""
Tests for the central configuration (Phase 2).

These tests are fast and need no GPU, no S3 and no model. They guarantee that:
  - config/config.yaml exists and has all expected sections;
  - the constants module stays in sync with the YAML (single source of truth).
"""

import os

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "config", "config.yaml")


def _load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def test_config_file_exists():
    assert os.path.isfile(CONFIG_PATH), f"Missing config file: {CONFIG_PATH}"


def test_config_has_required_sections():
    cfg = _load_config()
    for section in (
        "artifacts",
        "data_ingestion",
        "data_validation",
        "model_trainer",
        "model_pusher",
    ):
        assert section in cfg, f"Missing config section: {section}"


def test_constants_match_config():
    """The constants exposed by the code must equal the YAML values."""
    from isd.constant.training_pipeline import (
        MODEL_TRAINER_NO_EPOCHS,
        MODEL_TRAINER_BATCH_SIZE,
        DATA_VALIDATION_ALL_REQUIRED_FILES,
        DATA_BUCKET_NAME,
    )

    cfg = _load_config()
    assert MODEL_TRAINER_NO_EPOCHS == cfg["model_trainer"]["epochs"]
    assert MODEL_TRAINER_BATCH_SIZE == cfg["model_trainer"]["batch_size"]
    assert DATA_VALIDATION_ALL_REQUIRED_FILES == cfg["data_validation"]["required_files"]
    assert DATA_BUCKET_NAME == cfg["data_ingestion"]["data_bucket_name"]

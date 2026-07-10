"""
Standalone dataset validation for the Industrial Safety Detection (YOLOv7) project.

Goal: FAIL EARLY. Catch a broken dataset *before* you waste hours (and GPU) on a
training run that was doomed from the start.

What it checks
--------------
1. The data directory exists.
2. Every required file/folder is present
   (read from config/config.yaml -> data_validation.required_files).
3. `images/` and `labels/` are non-empty folders.
4. Every image has a matching label file (same name, .txt extension).
5. `classes.names` is not empty.

The script needs NO GPU, NO S3 and NO trained model. It only reads the local
dataset, so it is safe to run anywhere (including CI).

Exit codes
----------
0 -> dataset is valid
1 -> dataset is invalid (or the data directory is missing)

Usage
-----
    python scripts/validate_dataset.py --data-dir data/processed
"""

import argparse
import logging
import os
import sys

import yaml

# Image extensions we consider as "an image" when matching images <-> labels.
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp")

# --- Logging: simple console output, no file needed for a CLI check -----------
logging.basicConfig(
    level=logging.INFO,
    format="[ %(asctime)s ] %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def _project_root() -> str:
    """Return the project root (this file lives in <root>/scripts/)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_required_files() -> list:
    """
    Read the required file list from config/config.yaml so this script stays in
    sync with the single source of truth. Falls back to a sane default if the
    config cannot be read.
    """
    default = ["images", "labels", "classes.names", "train.txt", "val.txt"]
    config_path = os.path.join(_project_root(), "config", "config.yaml")
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        return config["data_validation"]["required_files"]
    except Exception:
        logging.warning(
            "Could not read required_files from config/config.yaml; "
            "using the built-in default list."
        )
        return default


def _list_files_recursive(folder: str, extensions=None) -> list:
    """Return file names (basenames) under `folder`, optionally filtered by extension."""
    collected = []
    for root, _dirs, files in os.walk(folder):
        for name in files:
            if extensions is None or name.lower().endswith(extensions):
                collected.append(name)
    return collected


def validate(data_dir: str) -> bool:
    """Run every check and return True only if the dataset is fully valid."""
    errors = []
    warnings = []

    # 1. Data directory exists ------------------------------------------------
    if not os.path.isdir(data_dir):
        logging.error(f"Data directory does not exist: {data_dir}")
        return False
    logging.info(f"Validating dataset in: {data_dir}")

    # 2. Required files/folders present ---------------------------------------
    required = load_required_files()
    for item in required:
        path = os.path.join(data_dir, item)
        if os.path.exists(path):
            logging.info(f"  [OK]      required item present: {item}")
        else:
            errors.append(f"Missing required item: {item}")
            logging.error(f"  [MISSING] required item: {item}")

    # 3. images/ and labels/ are non-empty folders ----------------------------
    images_dir = os.path.join(data_dir, "images")
    labels_dir = os.path.join(data_dir, "labels")

    image_names = _list_files_recursive(images_dir, IMAGE_EXTENSIONS) if os.path.isdir(images_dir) else []
    label_names = _list_files_recursive(labels_dir, (".txt",)) if os.path.isdir(labels_dir) else []

    if os.path.isdir(images_dir) and not image_names:
        errors.append("The 'images' folder contains no image files.")
        logging.error("  [EMPTY]   'images' folder has no images.")
    if os.path.isdir(labels_dir) and not label_names:
        errors.append("The 'labels' folder contains no .txt label files.")
        logging.error("  [EMPTY]   'labels' folder has no labels.")

    logging.info(f"  Found {len(image_names)} images and {len(label_names)} label files.")

    # 4. Every image has a matching label -------------------------------------
    if image_names and label_names:
        label_stems = {os.path.splitext(n)[0] for n in label_names}
        images_without_label = [
            n for n in image_names if os.path.splitext(n)[0] not in label_stems
        ]
        if images_without_label:
            preview = ", ".join(images_without_label[:5])
            warnings.append(
                f"{len(images_without_label)} image(s) have no matching label "
                f"(e.g. {preview})."
            )
            logging.warning(f"  [WARN]    {len(images_without_label)} images without a label.")
        else:
            logging.info("  [OK]      every image has a matching label.")

    # 5. classes.names is not empty -------------------------------------------
    classes_path = os.path.join(data_dir, "classes.names")
    if os.path.isfile(classes_path):
        with open(classes_path, "r") as f:
            classes = [line.strip() for line in f if line.strip()]
        if not classes:
            errors.append("'classes.names' is empty.")
            logging.error("  [EMPTY]   'classes.names' has no class names.")
        else:
            logging.info(f"  [OK]      {len(classes)} class(es) declared: {classes}")

    # --- Verdict -------------------------------------------------------------
    for w in warnings:
        logging.warning(f"WARNING: {w}")

    if errors:
        logging.error("-" * 60)
        logging.error(f"DATASET INVALID — {len(errors)} error(s):")
        for e in errors:
            logging.error(f"  - {e}")
        return False

    logging.info("-" * 60)
    logging.info("DATASET VALID — all required checks passed.")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a YOLOv7 dataset before training."
    )
    parser.add_argument(
        "--data-dir",
        required=True,
        help="Path to the dataset directory to validate (e.g. data/processed).",
    )
    args = parser.parse_args()

    is_valid = validate(args.data_dir)
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()

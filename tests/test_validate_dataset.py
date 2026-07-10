"""
Tests for scripts/validate_dataset.py (Phase 4).

We build tiny fake datasets in a temporary folder (pytest's `tmp_path`), so the
tests are instant and need no real data, no GPU and no model.
"""

import validate_dataset


def _make_valid_dataset(base):
    """Create a minimal but VALID YOLOv7-style dataset under `base` (a Path)."""
    (base / "images" / "train").mkdir(parents=True)
    (base / "labels" / "train").mkdir(parents=True)
    (base / "classes.names").write_text("hardhat\nvest\n")
    (base / "train.txt").write_text("")
    (base / "val.txt").write_text("")
    for i in range(3):
        (base / "images" / "train" / f"img{i}.jpg").write_text("")
        (base / "labels" / "train" / f"img{i}.txt").write_text("0 0.5 0.5 0.2 0.2\n")
    return base


def test_valid_dataset_passes(tmp_path):
    dataset = _make_valid_dataset(tmp_path / "ds")
    assert validate_dataset.validate(str(dataset)) is True


def test_missing_required_file_fails(tmp_path):
    dataset = _make_valid_dataset(tmp_path / "ds")
    (dataset / "val.txt").unlink()  # remove a required file
    assert validate_dataset.validate(str(dataset)) is False


def test_empty_classes_names_fails(tmp_path):
    dataset = _make_valid_dataset(tmp_path / "ds")
    (dataset / "classes.names").write_text("")  # make it empty
    assert validate_dataset.validate(str(dataset)) is False


def test_missing_directory_fails(tmp_path):
    assert validate_dataset.validate(str(tmp_path / "nope")) is False


def test_required_files_loaded_from_config():
    required = validate_dataset.load_required_files()
    assert "images" in required
    assert "labels" in required
    assert "classes.names" in required

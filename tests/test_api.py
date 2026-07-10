"""
Tests for the FastAPI service (Phase 7).

These use FastAPI's TestClient, which calls the app in-process. No server, no
GPU, no trained model needed. When the model weights are absent (the normal
state before training), /predict must respond with a clear 503.
"""

import io

import pytest

fastapi = pytest.importorskip("fastapi")  # skip cleanly if FastAPI isn't installed
from fastapi.testclient import TestClient

import fastapi_app

client = TestClient(fastapi_app.app)


def test_root_ok():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "service" in resp.json()


def test_health_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "model_available" in body


def test_predict_rejects_non_image():
    files = {"file": ("notes.txt", io.BytesIO(b"hello"), "text/plain")}
    resp = client.post("/predict", files=files)
    assert resp.status_code == 400


def test_predict_without_model_returns_503(monkeypatch):
    # Force "no trained model" regardless of the local filesystem.
    monkeypatch.setattr(fastapi_app.os.path, "isfile", lambda p: False)
    files = {"file": ("img.jpg", io.BytesIO(b"\xff\xd8\xff"), "image/jpeg")}
    resp = client.post("/predict", files=files)
    assert resp.status_code == 503
    assert "training" in resp.json()["detail"].lower()

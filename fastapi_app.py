"""
FastAPI service for the Industrial Safety Detection (YOLOv7) project.

This is a small, production-style API that lives ALONGSIDE the existing Flask
app (app.py) — it does not replace it, and it does not change the YOLOv7 model.

Why FastAPI here?
  - automatic interactive docs at /docs (Swagger UI)
  - request validation and clear error codes
  - async, ASGI server (uvicorn) — the modern way to serve Python APIs

Endpoints
---------
GET  /         basic info
GET  /health   liveness check + whether the trained model is available
POST /predict  run detection on an uploaded image (returns the annotated image
               as base64). Returns 503 while the model has not been trained yet.

Run locally:
    uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
Then open http://localhost:8000/docs
"""

import base64
import os
import shutil
import subprocess
import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile

app = FastAPI(
    title="Industrial Safety Detection API",
    description="Detect industrial safety equipment with YOLOv7.",
    version="1.0.0",
)

# Path to the trained weights the Flask app also expects.
YOLO_DIR = "yolov7"
WEIGHTS_PATH = os.path.join(YOLO_DIR, "my_model.pt")

# Where uploaded images are temporarily stored.
DATA_DIR = "data"


@app.get("/")
def root():
    """Basic service information."""
    return {
        "service": "Industrial Safety Detection API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    """
    Liveness check. Also reports whether the trained model is present, so a
    load balancer or a human can tell if the service can actually predict.
    """
    return {
        "status": "ok",
        "model_available": os.path.isfile(WEIGHTS_PATH),
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Run YOLOv7 detection on an uploaded image and return the annotated image
    encoded in base64.
    """
    # 1. Validate the input is an image.
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    # 2. If the model has not been trained yet, say so clearly (do not pretend).
    if not os.path.isfile(WEIGHTS_PATH):
        raise HTTPException(
            status_code=503,
            detail="Model weights not available yet. To be completed after training.",
        )

    # 3. Save the upload to a unique temporary file.
    os.makedirs(DATA_DIR, exist_ok=True)
    input_name = f"{uuid.uuid4().hex}.jpg"
    input_path = os.path.join(DATA_DIR, input_name)
    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 4. Run detection (no shell string -> safer than os.system).
    try:
        subprocess.run(
            [
                "python", "detect.py",
                "--weights", "my_model.pt",
                "--source", os.path.join("..", input_path),
            ],
            cwd=YOLO_DIR,
            check=True,
        )

        result_path = os.path.join(YOLO_DIR, "runs", "detect", "exp", input_name)
        if not os.path.isfile(result_path):
            raise HTTPException(status_code=500, detail="Detection produced no output image.")

        with open(result_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")

        return {"image": encoded}

    except subprocess.CalledProcessError as exc:
        raise HTTPException(status_code=500, detail=f"Detection failed: {exc}")
    finally:
        # 5. Clean up temporary files and detection outputs.
        if os.path.isfile(input_path):
            os.remove(input_path)
        shutil.rmtree(os.path.join(YOLO_DIR, "runs"), ignore_errors=True)

# syntax=docker/dockerfile:1
#
# Container image for the Industrial Safety Detection (YOLOv7) web app.
# Build:  docker build -t isd-yolov7 .
# Run:    docker run -p 8080:8080 isd-yolov7
# Then open http://localhost:8080

# --- Base image -------------------------------------------------------------
# Slim Python 3.8 to match the project's target version while keeping size down.
FROM python:3.8-slim-bullseye

# Do not buffer stdout/stderr, so logs appear immediately in `docker logs`.
ENV PYTHONUNBUFFERED=1

# --- System dependencies ----------------------------------------------------
# OpenCV (cv2) needs these shared libraries at runtime.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1-mesa-glx \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# --- Working directory ------------------------------------------------------
WORKDIR /app

# --- Python dependencies ----------------------------------------------------
# Copy only the dependency files first. Docker caches this layer, so the slow
# pip install is re-run ONLY when requirements/setup change, not on every code edit.
COPY requirements.txt setup.py ./
RUN pip install --no-cache-dir -r requirements.txt

# --- Application code --------------------------------------------------------
COPY . .

# --- Networking -------------------------------------------------------------
# The Flask app listens on port 8080 (see app.py).
EXPOSE 8080

# --- Start command ----------------------------------------------------------
CMD ["python", "app.py"]

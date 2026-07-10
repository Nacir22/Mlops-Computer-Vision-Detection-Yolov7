# Industrial Safety Detection with YOLOv7 (MLOps)

End-to-end **object detection** project that trains a **YOLOv7** model to detect industrial
safety equipment (hardhats, vests, etc.) and serves predictions through a web API.
The repository is organized as a reproducible **MLOps pipeline**: data ingestion from AWS S3,
dataset validation, model training, model push to S3, and a web app for inference.

> **Status:** active refactoring toward production quality. Training metrics are not published yet
> (see [Results](#results)).

---

## Table of contents

- [Demo / What it does](#demo--what-it-does)
- [Architecture](#architecture)
- [Project structure](#project-structure)
- [Tech stack](#tech-stack)
- [Getting started](#getting-started)
- [Usage](#usage)
- [Configuration](#configuration)
- [Results](#results)
- [Roadmap](#roadmap)
- [Credits & license](#credits--license)

---

## Demo / What it does

The application exposes a small web service (Flask) with three endpoints:

| Route      | Method     | Description                                              |
|------------|------------|----------------------------------------------------------|
| `/`        | GET        | Web page to upload an image and view detections.         |
| `/train`   | GET        | Triggers the full training pipeline.                     |
| `/predict` | POST / GET | Accepts a base64 image and returns the annotated image.  |

Under the hood, `/predict` runs YOLOv7 inference (`yolov7/detect.py`) on the uploaded image
and returns the result encoded in base64.

---

## Architecture

The training pipeline is split into independent, testable stages:

```
Data Ingestion  ->  Data Validation  ->  Model Trainer  ->  Model Pusher
   (S3 pull)         (files present?)      (YOLOv7 train)     (S3 upload)
```

Diagrams for each stage are available in [`flowcharts/`](flowcharts/).

---

## Project structure

```text
Mlops-Computer-Vision-Detection-Yolov7/
├── app.py                     # Web app entry point (Flask, port 8080)
├── template.py                # Bootstrap script that scaffolds the project skeleton
├── setup.py                   # Makes `isd` an installable Python package
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container definition (to be completed)
├── data/                      # Sample images + local data folder
├── flowcharts/                # Architecture diagrams
├── notebook/                  # YOLOv7 training notebook + custom.yaml
├── templates/                 # HTML front-end (index.html)
├── isd/                       # Main Python package (Industrial Safety Detection)
│   ├── components/            # Pipeline stages
│   │   ├── data_ingestion.py
│   │   ├── data_validation.py
│   │   ├── model_trainer.py
│   │   └── model_pusher.py
│   ├── configuration/         # AWS S3 operations
│   ├── constant/              # Central constants (paths, hyper-params, bucket names)
│   ├── entity/                # Config + artifact dataclasses
│   ├── exception/             # Custom exception wrapper
│   ├── logger/                # Logging setup
│   ├── pipeline/              # Orchestrates the training stages
│   └── utils/                 # Helpers (image encode/decode, etc.)
└── yolov7/                    # Vendored YOLOv7 (WongKinYiu) — training & detection code
```

---

## Tech stack

- **Model:** YOLOv7 (`WongKinYiu/yolov7`)
- **Language:** Python 3.8
- **Deep learning:** PyTorch, TorchVision
- **Serving:** Flask + Flask-CORS
- **Cloud / storage:** AWS S3 (via `boto3`)
- **Vision / data:** OpenCV, NumPy, Pillow, Pandas

---

## Getting started

### 1. Prerequisites

- Python 3.8
- (Optional) AWS credentials configured, if you use the S3 data ingestion / model pusher stages
- (Optional) A CUDA-capable GPU for training

### 2. Create the environment

```bash
conda create -n safety python=3.8 -y
conda activate safety
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure AWS

Only needed for the S3-backed ingestion and model-push stages:

```bash
# AWS CLI install guide:
# https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
aws configure
```

---

## Usage

### Run the web app

```bash
python app.py
```

Then open <http://localhost:8080> in your browser.

### Trigger training via the API

```bash
curl http://localhost:8080/train
```

### Run inference from the command line

```bash
cd yolov7/
python detect.py --weights my_model.pt --source ../data/inputImage.jpg
```

---

## Configuration

Key parameters currently live in `isd/constant/training_pipeline/__init__.py`:

| Parameter                  | Value         | Meaning                       |
|----------------------------|---------------|-------------------------------|
| `MODEL_TRAINER_NO_EPOCHS`  | `1`           | Training epochs               |
| `MODEL_TRAINER_BATCH_SIZE` | `8`           | Batch size                    |
| `DATA_BUCKET_NAME`         | `isd-data-24` | S3 bucket holding the dataset |
| `MODEL_BUCKET_NAME`        | `isd-data-24` | S3 bucket for trained weights |

> Centralizing these into a single `config.yaml` is planned (see [Roadmap](#roadmap)).

---

## Results

| Metric                     | Value                          |
|----------------------------|--------------------------------|
| mAP@0.5                    | To be completed after training |
| mAP@0.5:0.95               | To be completed after training |
| Precision                  | To be completed after training |
| Recall                     | To be completed after training |
| Inference time (per image) | To be completed after training |

*Metrics will be filled in once a full training run is completed and evaluated on a held-out set.*

---

## Roadmap

- [ ] Centralize parameters in a `config.yaml`
- [ ] Add a dataset validation script with clear error messages
- [ ] Replace `print` statements with structured logging
- [ ] Add lightweight tests (no GPU / no large model required)
- [ ] Complete the `Dockerfile` for reproducible deployment
- [ ] Add a FastAPI service to demonstrate production-style deployment
- [ ] Publish training metrics in [Results](#results)

---

## Credits & license

- Built on top of **YOLOv7** by WongKinYiu — <https://github.com/WongKinYiu/yolov7>
- [Dataset link](https://drive.google.com/file/d/1ncxeLuWEMXkXVI79LXbA38s-Ij0d2q4E/view?usp=sharing)
- [YOLOv7 tutorial playlist](https://youtube.com/playlist?list=PLkz_y24mlSJagh6O2MIrgI-Ki-t1rhjLI)

See [`LICENSE`](LICENSE) for this repository and [`yolov7/LICENSE.md`](yolov7/LICENSE.md) for YOLOv7.

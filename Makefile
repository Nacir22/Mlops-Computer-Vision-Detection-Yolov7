# Makefile — shortcuts for common project commands.
# Usage:  make <target>       e.g.  make test
# Run `make help` to list all targets.
#
# Note (Windows): `make` is not installed by default. Use it from Git Bash or
# WSL, or run the underlying commands shown below directly.

# Dataset folder used by `make validate-data` (override: make validate-data DATA_DIR=path)
DATA_DIR ?= data/processed

.PHONY: help install install-dev validate-data test run api docker-build docker-run clean

help:  ## Show this help
	@echo "Available targets:"
	@echo "  install        Install runtime dependencies"
	@echo "  install-dev    Install test/dev dependencies (pytest)"
	@echo "  validate-data  Validate the dataset (DATA_DIR=$(DATA_DIR))"
	@echo "  test           Run the test suite"
	@echo "  run            Start the Flask app (port 8080)"
	@echo "  api            Start the FastAPI service (port 8000)"
	@echo "  docker-build   Build the Docker image"
	@echo "  docker-run     Run the Docker image (port 8080)"
	@echo "  clean          Remove caches, logs and run artifacts"

install:  ## Install runtime dependencies
	pip install -r requirements.txt

install-dev:  ## Install dev/test dependencies
	pip install -r requirements-dev.txt

validate-data:  ## Validate the dataset before training
	python scripts/validate_dataset.py --data-dir $(DATA_DIR)

test:  ## Run the test suite
	python -m pytest tests/ -q

run:  ## Start the Flask web app
	python app.py

api:  ## Start the FastAPI service with auto-reload
	uvicorn fastapi_app:app --host 0.0.0.0 --port 8000 --reload

docker-build:  ## Build the Docker image
	docker build -t isd-yolov7 .

docker-run:  ## Run the Docker image
	docker run -p 8080:8080 isd-yolov7

clean:  ## Remove caches, logs and run artifacts
	rm -rf __pycache__ */__pycache__ .pytest_cache
	rm -rf logs artifacts
	find . -type f -name "*.pyc" -delete

# 🚢 SpaceY Intelligence — Deployment & Operations Guide

## 1. Architecture Deployment Overview

SpaceY Intelligence is designed for multi-tier deployment, supporting local workstations, lightweight containerized staging environments, and production cloud infrastructure.

The platform provides two primary runtime surfaces:
1. **Interactive Streamlit Platform** (Port `8501`): Aerospace mission control dashboard, geospatial map, and scenario lab.
2. **FastAPI Microservice** (Port `8000`): High-throughput programmatic REST API for automated flight-readiness integrations.

---

## 2. Local Environment Setup

### 2.1 Prerequisites
- Python 3.10, 3.11, or 3.12
- `git`
- Virtual environment manager (`venv`, `conda`, or `virtualenv`)

### 2.2 Installation
```bash
# Clone the repository
git clone https://github.com/Arvindhbabu/Data-Science-Capstone-Project.git
cd spacey_capstone

# Create and activate virtual environment
python -m venv .venv

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Upgrade pip and install pinned dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2.3 Initialize Pipeline & Train Model Artifacts
Ensure raw data is transformed into analytics databases and the production model pipeline is trained:
```bash
# Ingest, clean, validate, and build SQLite analytics database
python scripts/prepare_data.py

# Train 7 candidate models, evaluate via 5-fold CV, and serialize best pipeline
python scripts/train_model.py
```

---

## 3. Launching Services

### 3.1 Launch Primary Streamlit Platform
```bash
streamlit run app.py
```
- Access in browser at: `http://localhost:8501`
- Includes all 8 executive, predictive, and geospatial modules.

### 3.2 Launch FastAPI Inference Microservice
```bash
uvicorn src.spacey.services.api:app --host 0.0.0.0 --port 8000 --reload
```
- Interactive Swagger UI: `http://localhost:8000/docs`
- OpenAPI Schema: `http://localhost:8000/openapi.json`
- Healthcheck: `http://localhost:8000/health`

### 3.3 Launch Legacy Compatible Dashboard
For comparison with the original legacy capstone layout:
```bash
streamlit run dashboard/app.py
```

---

## 4. Docker Container Deployment

The repository includes a production-ready, non-root `Dockerfile` configured to serve the complete platform.

### 4.1 Build Docker Image
```bash
docker build -t spacey-intelligence:latest .
```

### 4.2 Run Docker Container
```bash
docker run -d \
  --name spacey-platform \
  -p 8501:8501 \
  -p 8000:8000 \
  --restart unless-stopped \
  spacey-intelligence:latest
```

---

## 5. Multi-Container Orchestration (Docker Compose)

To run the Streamlit frontend and FastAPI backend as decoupled microservices with dedicated resource boundaries, use `docker-compose`:

```bash
# Start all services in the background
docker-compose up -d

# Check service logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services exposed:
- `streamlit-ui`: `http://localhost:8501`
- `fastapi-backend`: `http://localhost:8000`

---

## 6. Cloud Platform Deployment

### 6.1 Streamlit Community Cloud
1. Fork or push this repository to GitHub.
2. Sign in to [share.streamlit.io](https://share.streamlit.io).
3. Select your repository, set the branch to `main`, and specify `app.py` as the Main file path.
4. Streamlit Cloud automatically detects `requirements.txt` and `.streamlit/config.toml`.

### 6.2 Google Cloud Run / AWS ECS / Azure Container Apps
Because the application is fully containerized with a standard HTTP entrypoint, it can be deployed directly to serverless container runtimes:

```bash
# Example Google Cloud Run deployment:
gcloud builds submit --tag gcr.io/PROJECT_ID/spacey-intelligence
gcloud run deploy spacey-platform \
  --image gcr.io/PROJECT_ID/spacey-intelligence \
  --platform managed \
  --port 8501 \
  --memory 2Gi \
  --cpu 2 \
  --allow-unauthenticated
```

---

## 7. Configuration & Environment Variables

All settings can be configured via environment variables or modified in [`src/spacey/config.py`](file:///src/spacey/config.py):

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `SPACEY_LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `SPACEY_DB_PATH` | `data/spacey_analytics.db` | Analytical SQLite warehouse path. |
| `SPACEY_MODEL_PATH` | `models/registry/best_pipeline.joblib` | Production model pipeline artifact path. |
| `PORT` | `8501` | Application listening port. |

# SpaceY Intelligence
### Launch Analytics · Booster-Recovery Prediction · Mission Economics

[![CI](https://github.com/Arvindhbabu/Space-Y-Launch-Prediction-Capstone-Project-/actions/workflows/ci.yml/badge.svg)](https://github.com/Arvindhbabu/Space-Y-Launch-Prediction-Capstone-Project-/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-analytics%20warehouse-003B57?logo=sqlite&logoColor=white)](https://sqlite.org/)

SpaceY Intelligence is an end-to-end **launch analytics and machine-learning project** built around the IBM/Coursera Falcon 9 capstone workflow. It combines historical launch exploration, an interactive dashboard, a booster-recovery classification demo, and a configurable mission-economics simulator.

> [!IMPORTANT]
> This is an **educational and analytical demonstration**, not certified aerospace software. Model outputs are based on a small historical benchmark and must not be used to authorize or plan real missions. Economic values are illustrative assumptions, not verified industry costs or SpaceX pricing.

## Capabilities

| Area | What it provides |
|---|---|
| Executive overview | Historical launch indicators and high-level trends |
| Launch explorer | Filter launch records and explore outcome patterns |
| Geospatial intelligence | Map supported launch sites and compare their history |
| Predictive lab | Evaluate and compare hypothetical mission profiles |
| Model intelligence | Compare candidate classifiers and inspect evaluation metrics and feature attribution |
| Mission economics | Estimate expected costs, margins, and break-even recovery probability from editable assumptions |
| Data quality | Inspect schema, validation results, and processed launch records |
| FastAPI service | Health, model metadata, single/batch prediction, and economics endpoints |

## Technology stack

- **Language and data:** Python 3.12, pandas, NumPy, SQLite
- **Machine learning:** scikit-learn, preprocessing pipelines, model comparison, evaluation, permutation importance
- **Application:** Streamlit, Plotly, Folium
- **API:** FastAPI, Pydantic, Uvicorn
- **Quality and delivery:** pytest, pinned dependencies, GitHub Actions, Docker, Docker Compose

## Architecture

~~~mermaid
flowchart TD
    A[Public launch datasets] --> B[Validation and preprocessing]
    B --> C[Processed datasets]
    B --> D[(SQLite analytics warehouse)]
    C --> E[Benchmark training and evaluation]
    E --> F[Registered model and provenance metadata]
    F --> G[Streamlit dashboard]
    F --> H[FastAPI prediction service]
    D --> G
    I[Illustrative economic assumptions] --> J[Mission economics engine]
    J --> G
    J --> H
~~~

## Quick start

### 1. Create an isolated environment

**Windows PowerShell**

~~~powershell
git clone https://github.com/Arvindhbabu/SpaceY-Intelligence.git
cd SpaceY-Intelligence
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
~~~

**macOS / Linux**

~~~bash
git clone https://github.com/Arvindhbabu/SpaceY-Intelligence.git
cd SpaceY-Intelligence
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
~~~

> The clone URL above uses the recommended repository name. Rename the repository in GitHub first if that name has not been applied yet.

### 2. Check the environment and model artifact

Run these from the repository root before starting prediction features:

~~~bash
python scripts/diagnose_environment.py
python -m pip check
~~~

The preflight checks the interpreter's installed dependency pins and the scikit-learn version recorded in the registered-model metadata. It does not deserialize the model or certify model quality.

### 3. Start the Streamlit dashboard

~~~bash
python -m streamlit run app.py
~~~

Open the local URL printed by Streamlit, typically http://localhost:8501.

### 4. Optional: start the API

In a separate terminal using the same activated environment:

~~~bash
python -m uvicorn spacey.services.api:app --app-dir src --host 127.0.0.1 --port 8000
~~~

API documentation is available at http://127.0.0.1:8000/docs.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /health | Service and model readiness |
| GET | /metadata | Registered model metadata and evaluation evidence |
| POST | /predict | Predict one hypothetical scenario |
| POST | /predict/batch | Predict multiple scenarios |
| POST | /economics | Calculate illustrative mission-economics results |

The API schema is defined in `src/spacey/data/feature_schema.py` and `src/spacey/services/api.py`.

### 5. Optional: run with Docker

~~~bash
docker compose up --build
~~~

The Compose configuration exposes the dashboard on port 8501 and the API on port 8000. Interactive container behavior should be verified in the target environment; a successful image build alone does not prove every endpoint is healthy.

## Data preparation and model training

The repository includes source/processed data artifacts and a registered model. The scripts below are **optional refresh/rebuild operations** and may change local generated files:

~~~bash
python scripts/prepare_data.py
python scripts/train_model.py
~~~

Review the scripts and preserve local work before rerunning them. Data preparation can access external sources; do not assume that a local refresh will exactly reproduce a previous snapshot. The 90-record benchmark and the larger operational launch archive have different purposes and must not be treated as interchangeable samples.

## Tests and quality checks

~~~bash
python scripts/diagnose_environment.py
python -m pip check
python -m compileall -q app.py pages src scripts tests
python -m pytest tests/ -v
~~~

Use the same activated virtual environment to install dependencies, train/load the model, launch Streamlit, run the API, and execute tests. The serialized scikit-learn artifact should be loaded only in a compatible environment. If provenance and pinned versions disagree, correct the environment or retrain the model rather than patching serialized estimator attributes.

The live [GitHub Actions page](https://github.com/Arvindhbabu/Space-Y-Launch-Prediction-Capstone-Project-/actions) is the source of truth for current automation status.

## Model evaluation and limitations

- The benchmark contains only about 90 records; a holdout set of 18 examples produces uncertain estimates.
- Accuracy, ROC-AUC, precision, recall, specificity, PR-AUC, and Brier score describe different aspects of performance.
- A high recall can coexist with poor failure detection. Review the confusion matrix, specificity, calibration, and uncertainty—not a single headline metric.
- Historical association is not causation. The model does not simulate trajectories, thrust, propellant reserves, weather, sea state, vehicle condition, or other flight-dynamics variables.
- Economic recommendations are conditional outputs of a simplified assumption-based formula, not real commercial or aerospace recommendations.
- Verify source provenance, date filtering, target definitions, duplicate records, class balance, and potential dataset overlap before making claims from the analysis.

Read the [Model Card](docs/MODEL_CARD.md), [Methodology](docs/METHODOLOGY.md), [Limitations](docs/LIMITATIONS.md), [Economics Assumptions](docs/ECONOMICS_ASSUMPTIONS.md), [Verification Report](docs/VERIFICATION_REPORT.md), and [Local Environment Troubleshooting](docs/LOCAL_ENVIRONMENT_TROUBLESHOOTING.md).

## Project layout

~~~text
.
├── app.py                         # Streamlit entry point
├── pages/                         # Multipage dashboard
├── src/spacey/
│   ├── analytics/                 # SQLite analytics
│   ├── data/                      # Data loading, schemas, validation
│   ├── economics/                 # Scenario economics
│   ├── models/                    # Training, evaluation, registry
│   ├── services/                  # FastAPI service
│   └── ui/                        # UI theme and charts
├── scripts/                       # Data/model automation and preflight checks
├── data/                          # Source, processed, and SQLite artifacts
├── models/registry/                # Model artifact and metadata
├── docs/                           # Methodology, model card, limitations
├── tests/                          # Automated tests
├── .github/                        # CI and contribution templates
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── requirements.txt
~~~

## Data attribution and license

The project extends the IBM/Coursera Applied Data Science Capstone learning workflow and uses public historical launch information. Consult the data-preparation code and documentation for provenance. **SpaceY is a fictional analytical framing and is not affiliated with SpaceX.**

A software license has not yet been selected for this repository. Until a license is added, the public availability of the source code should not be interpreted as permission to redistribute or reuse it under an open-source license.

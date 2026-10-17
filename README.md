# SpaceY Intelligence
## Launch Analytics, Booster-Recovery Prediction & Mission Economics

[![CI](https://github.com/Arvindhbabu/Space-Y-Launch-Prediction-Capstone-Project-/actions/workflows/ci.yml/badge.svg)](https://github.com/Arvindhbabu/Space-Y-Launch-Prediction-Capstone-Project-/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-analytics%20warehouse-003B57?logo=sqlite&logoColor=white)](https://sqlite.org/)

SpaceY Intelligence extends the IBM/Coursera SpaceX Falcon 9 capstone into a modular analytics demonstration for exploring historical launch outcomes, estimating booster-recovery likelihoods, and examining illustrative mission-economics scenarios.

> **Important:** This is an educational decision-support project, not a certified aerospace engineering, flight-safety, or commercial-pricing system. Model outputs reflect a small historical dataset and must not be used to authorize real missions. Economic inputs are illustrative assumptions, not verified SpaceX or industry costs.

## What it includes

- **Executive overview:** launch-history indicators and summary trends.
- **Launch explorer:** filterable launch records and analytical queries backed by SQLite.
- **Geospatial intelligence:** interactive launch-site mapping.
- **Predictive lab:** scenario inputs for payload, orbit, booster block, launch site, reuse, grid fins, and landing legs.
- **Model intelligence:** candidate-model comparison, holdout metrics, and feature-importance analysis.
- **Mission economics:** expected-cost and break-even scenario calculations using configurable assumptions.
- **Data quality:** schema checks and input/data diagnostics.
- **Technical documentation:** in-app notes and project methodology.
- **FastAPI service:** health, metadata, single prediction, batch prediction, and economics endpoints.

## Architecture

```text
Public launch datasets
       |
       v
Validation and preprocessing -----> SQLite analytics warehouse
       |
       v
Benchmark model training
       |
       v
Versioned pipeline + metadata
       |
       +----> Streamlit multipage dashboard
       |
       +----> FastAPI inference/economics API
```

The model-training benchmark (90 records in the current project design) and the larger operational/history dataset serve different purposes. They should not be treated as interchangeable training samples. Dataset provenance, duplicate handling, date ranges, and target definitions are important when interpreting any metric.

## Project layout

```text
.
├── app.py                     # Streamlit entry point
├── pages/                     # Dashboard modules
├── src/spacey/
│   ├── analytics/              # SQLite analytics
│   ├── data/                   # Ingestion, schema, validation
│   ├── economics/               # Scenario cost calculations
│   ├── models/                  # Training, evaluation, registry
│   ├── services/                # FastAPI service
│   └── ui/                      # Theme and charts
├── scripts/
│   ├── prepare_data.py
│   └── train_model.py
├── data/                       # Source/processed data and SQLite database
├── models/registry/             # Serialized model and registry metadata
├── tests/                       # Automated tests
├── docs/                        # Architecture, methodology, limitations
├── requirements.txt
├── pyproject.toml
└── Dockerfile
```

## Run locally

Use Python 3.12 and run commands with the same project interpreter that installs dependencies and loads the serialized model.

### Windows PowerShell

```powershell
git clone https://github.com/Arvindhbabu/Space-Y-Launch-Prediction-Capstone-Project-.git
cd Space-Y-Launch-Prediction-Capstone-Project-

py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Confirm interpreter, dependency pins, and model-artifact provenance before loading the model
python -c "import sys, sklearn; print(sys.executable); print('scikit-learn', sklearn.__version__)"
python scripts/diagnose_environment.py

# Optional: rebuild the data artifacts and train a fresh registered model
python scripts/prepare_data.py
python scripts/train_model.py

# Launch the dashboard
python -m streamlit run app.py
```

### macOS / Linux

```bash
git clone https://github.com/Arvindhbabu/Space-Y-Launch-Prediction-Capstone-Project-.git
cd Space-Y-Launch-Prediction-Capstone-Project-
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/diagnose_environment.py
python scripts/prepare_data.py
python scripts/train_model.py
python -m streamlit run app.py
```

The data preparation script may retrieve external data and therefore requires network access. If you intend to use the checked-in dataset snapshot, inspect the script first to understand whether it overwrites local artifacts.

## Run the API

In a separate activated environment/terminal:

```bash
python -m uvicorn src.spacey.services.api:app --host 127.0.0.1 --port 8000
```

Available endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | API and model readiness |
| GET | `/metadata` | Registered-model metadata |
| POST | `/predict` | Single launch scenario |
| POST | `/predict/batch` | Multiple scenarios |
| POST | `/economics` | Illustrative mission-economics calculation |

Interactive API documentation: `http://127.0.0.1:8000/docs`.

### Example prediction request

Use the request schema defined in `src/spacey/data/feature_schema.py` and `src/spacey/services/api.py`. The API accepts the application’s scenario fields, not necessarily the raw training column names. Check that schema before copying requests from older versions of this README.

## Tests and quality checks

```bash
python -m pytest tests/ -v
```

Run tests from the same activated environment used to install requirements. A test result from one interpreter does not verify a model artifact loaded by another interpreter. Model files serialized with joblib/scikit-learn must be used in a compatible environment; when in doubt, regenerate them with the project's pinned dependencies.

CI is configured in `.github/workflows/ci.yml`. Check the live workflow badge above for the latest actual status. This README does not assert that a workflow has passed unless GitHub Actions reports it.

## Model evaluation and limitations

- The benchmark is small (90 records in the current design); holdout estimates can vary considerably with a few examples.
- ROC-AUC, precision, recall, F1, PR-AUC, and Brier score measure different properties. No single metric establishes operational readiness.
- Historical associations are not causal engineering relationships. The model does not simulate thrust, weather, trajectory, fuel reserves, sea state, hardware condition, or other physical variables.
- Thresholds, confidence labels, and costs are analytical choices that need independent validation.
- Verify data dates, target definitions, duplicate records, class balance, and any overlap between benchmark and operational datasets before drawing conclusions.

See [Model Card](docs/MODEL_CARD.md), [Methodology](docs/METHODOLOGY.md), [Limitations](docs/LIMITATIONS.md), [Economics Assumptions](docs/ECONOMICS_ASSUMPTIONS.md), [Verification Report](docs/VERIFICATION_REPORT.md), and [Local Environment Troubleshooting](docs/LOCAL_ENVIRONMENT_TROUBLESHOOTING.md).

## Data and attribution

This project was developed from the IBM/Coursera Applied Data Science Capstone learning workflow and public historical launch records. See the documentation and source files for the dataset preparation process and citations. SpaceY is a fictional analytical framing; it is not affiliated with SpaceX.

## License

See [LICENSE](LICENSE) if present in the repository. Confirm licensing and redistribution terms for each data source independently.

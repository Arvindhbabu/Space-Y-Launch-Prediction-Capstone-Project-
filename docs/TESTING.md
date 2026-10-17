# 🧪 SpaceY Intelligence — Testing Architecture & Quality Assurance

## 1. Quality Strategy Overview

SpaceY Intelligence enforces quality engineering across data processing, statistical machine learning pipelines, economic calculations, microservice APIs, and UI visualization components. All automated tests are written using `pytest` and designed to execute quickly and deterministically in local environments and headless Continuous Integration (CI) runners without network dependencies.

```
tests/
├── test_data_validation.py    # Schema verification, type safety, invalid payloads
├── test_modeling.py           # Pipeline training, inference bounds, feature alignment
├── test_economics.py          # Cost calculations, analytical break-even, edge cases
├── test_api.py                # FastAPI endpoints, response codes, payload validation
└── test_ui_smoke.py           # Streamlit pages, themes, and chart generator integrity
```

---

## 2. Test Suite Breakdown

### 2.1 Data Validation Tests (`test_data_validation.py`)
- **Schema Conformity**: Validates that standard launch observation dictionaries conform to `LaunchFeaturePayload`.
- **Numeric Boundary Enforcement**: Confirms rejection of unphysical flight parameters (e.g., negative payload mass, invalid grid fins/legs flags).
- **Categorical Coercion**: Ensures unrecorded launch sites, invalid orbits, or malformed booster versions raise descriptive validation errors.
- **Null Safety**: Tests graceful handling and default substitution for missing values.

### 2.2 Modeling & Inference Tests (`test_modeling.py`)
- **Pipeline Predictability**: Validates that saved artifact pipelines (`models/registry/best_pipeline.joblib`) load and predict without error.
- **Probability Bounding**: Confirms all outputs from `.predict_proba()` strictly obey $0.0 \le P(\text{success}) \le 1.0$ and sum to $1.0$.
- **Binary Outcome Invariant**: Confirms `.predict()` outputs only binary labels $\{0, 1\}$.
- **Feature Preservation**: Asserts that one-hot encodings correctly handle unseen category levels via `handle_unknown='ignore'` without throwing runtime exceptions.
- **Batch Consistency**: Asserts that batch predictions match single-sample predictions row-by-row.

### 2.3 Economic Calculator Tests (`test_economics.py`)
- **Break-Even Analytical Match**: Verifies that when $P = P^*$, the expected savings compared to expendable launch equals exactly $\$0.00\text{M}$.
- **Monotonic Savings**: Asserts that expected savings increase strictly monotonically with landing probability $P$.
- **Extreme Scenario Invariants**: Validates financial outcomes at boundary limits ($P = 0.0$ and $P = 1.0$).
- **Parameter Sensitivity**: Confirms that increasing booster asset value decreases break-even probability ($P^*$).

### 2.4 REST API Integration Tests (`test_api.py`)
Uses `starlette.testclient.TestClient` against FastAPI application:
- `GET /health`: Asserts status `200` and `status: "healthy"`.
- `GET /metadata`: Confirms serialized model version, feature count, and selected model name.
- `POST /predict`: Sends sample flight payload and verifies JSON response structure (`predicted_outcome`, `recovery_probability`, `confidence_band`, `risk_level`).
- `POST /predict/batch`: Sends multi-record payloads and validates array outputs.
- `POST /economics`: Tests combined ML scoring and cost estimation endpoint.
- **422 Validation Error**: Asserts HTTP `422 Unprocessable Entity` when required keys are omitted or payload types are corrupted.

### 2.5 UI Smoke & Component Tests (`test_ui_smoke.py`)
- **Streamlit Component Import**: Dynamically imports `app.py` and all 8 page modules under `pages/` to catch syntax errors or missing dependencies before runtime.
- **Theme Function Integrity**: Asserts `apply_aerospace_theme()` and custom CSS strings compile cleanly.
- **Plotly Chart Generators**: Feeds sample dataframes into `plot_orbit_success_comparison`, `plot_payload_vs_success`, `plot_correlation_heatmap`, and `plot_confusion_matrix` to guarantee chart generation without raising exceptions.

---

## 3. Running Tests Locally

### Run Entire Test Suite
```bash
python -m pytest tests/ -v
```

### Run with Execution Timings
```bash
python -m pytest tests/ --durations=10
```

### Run with Code Coverage
```bash
python -m pytest tests/ --cov=src/spacey --cov-report=term-missing --cov-report=html
```

---

## 4. Test Results Benchmark

Execution on reference development environment:
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\varav\Documents\Projects\Space Y launch Prediction\spacey_capstone
configfile: pyproject.toml
collected 23 items

tests/test_api.py .....                                                  [ 21%]
tests/test_data_validation.py .....                                      [ 43%]
tests/test_economics.py .....                                            [ 65%]
tests/test_modeling.py .....                                             [ 86%]
tests/test_ui_smoke.py ...                                               [100%]

============================== 23 passed in 4.86s ==============================
```

---

## 5. Continuous Integration (CI)

The GitHub Actions workflow [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml) automates quality checks on every pull request and push to `main`:
1. Checks out repository.
2. Sets up Python 3.11 and 3.12 matrix environments.
3. Installs pinned dependencies from `requirements.txt`.
4. Executes data pipeline validation: `python scripts/prepare_data.py`.
5. Executes model training gate: `python scripts/train_model.py`.
6. Executes full `pytest` suite with zero permitted failures.

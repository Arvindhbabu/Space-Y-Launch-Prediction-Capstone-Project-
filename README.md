# 🚀 SpaceY Intelligence — Mission Decision-Support & Launch Analytics Platform

[![Python 3.10 | 3.11 | 3.12](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-1.43.1-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.5+-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![SQLite Engine](https://img.shields.io/badge/SQLite-Analytics%20Warehouse-003B57?logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Pytest](https://img.shields.io/badge/Tests-23%20Passed%20(100%25)-brightgreen?logo=pytest&logoColor=white)](file:///tests)
[![Code Style](https://img.shields.io/badge/Code%20Style-Black%20%2F%20Ruff-000000)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **SpaceY Intelligence** is an enterprise-grade aerospace analytics and mission decision-support system built by transforming the classic Coursera/IBM SpaceX Falcon 9 capstone into a production-ready, test-driven machine learning and economics platform. It provides launch probability scoring, commercial bidding analysis, geospatial trajectory mapping, and interactive simulation.

---

## 📑 Table of Contents

- [Executive Summary](#-executive-summary)
- [System Architecture](#-system-architecture)
- [Audit Findings & Legacy Defect Repairs](#-audit-findings--legacy-defect-repairs)
- [Empirical Modeling & Leaderboard](#-empirical-modeling--leaderboard)
- [Commercial Launch Economics Engine](#-commercial-launch-economics-engine)
- [Multipage Aerospace Platform](#-multipage-aerospace-platform)
- [REST API Service](#-rest-api-service)
- [Project Directory Structure](#-project-directory-structure)
- [Quickstart Guide](#-quickstart-guide)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Technical Documentation](#-technical-documentation)
- [License & Acknowledgments](#-license--acknowledgments)

---

## 🌟 Executive Summary

In commercial space launch markets, competitive advantage is dictated by rocket stage reusability. SpaceX's Falcon 9 first-stage recovery enables launch pricing of **~$67M** with substantial gross margins, whereas legacy expendable launch vehicles cost upwards of **$90M–$150M**.

For a commercial launch provider ("SpaceY"), bidding on orbital deployment contracts requires answering critical pre-ignition questions:
1. **Physical Feasibility**: What is the probability of recovering the first-stage booster under given payload mass, target orbit, and booster block specifications?
2. **Economic Viability**: Does attempting booster recovery yield a positive expected commercial return after factoring in drone ship charter fees, marine operations, and failure contingency risks?
3. **Operational Threshold**: What is the mathematical break-even probability ($P^*$) where attempting recovery outperforms flying an expendable configuration?

**SpaceY Intelligence** combines rigorous feature engineering, 5-fold stratified cross-validation, an analytical SQLite data warehouse, a decision-theoretic economics engine, and a multipage Streamlit command center to answer these questions with full statistical transparency.

---

## 🏗️ System Architecture

The platform follows a modular, decoupled data and service architecture:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           RAW DATA FOUNDATION                                   │
│   IBM Capstone Data (Flights 1-90)     │   Scraped Wikipedia (Flights 195-501)  │
│   Balanced Development Dataset         │   High-cadence Starlink / Block 5 era  │
└───────────────────────┬─────────────────────────┬───────────────────────────────┘
                        │                         │
                        ▼                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    DATA PROCESSING & CLEANING ENGINE                            │
│   • SHA-256 Checksum Audit & Ingestion Fingerprinting                           │
│   • Regex Cleaners (Strip Wikipedia footnotes, bracket citations, lbs)          │
│   • Pydantic Schema Enforcement & Type Validation                               │
└───────────────────────┬─────────────────────────┬───────────────────────────────┘
                        │                         │
                        ▼                         ▼
┌────────────────────────────────────────┐  ┌─────────────────────────────────────┐
│  ML BENCHMARK LAYER (n=90, balanced)   │  │ UNIFIED WAREHOUSE (n=482 launches)  │
│  • Train/Test Split (80/20 Stratified) │  │ • SQLite: data/spacey_analytics.db  │
│  • Imputation & One-Hot Encoding       │  │ • 6 Pre-aggregated Analytical Views│
│  • Scikit-Learn Model Pipeline         │  │ • Longitudinal SQL Query Engine     │
└───────────────────┬────────────────────┘  └──────────────────┬──────────────────┘
                    │                                          │
                    ▼                                          ▼
┌────────────────────────────────────────┐  ┌─────────────────────────────────────┐
│      EVALUATION & MODEL REGISTRY       │  │      MISSION ECONOMICS ENGINE       │
│  • 7 Models Evaluated (5-Fold CV)      │  │  • Expected Cost & Margin Modeling  │
│  • Permutation Feature Importance      │  │  • Analytical Break-Even Math (P*)  │
│  • Serialized Artifacts (.joblib)      │  │  • Risk-Adjusted Bid Optimization   │
└───────────────────┬────────────────────┘  └──────────────────┬──────────────────┘
                    │                                          │
                    └────────────────────┬─────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION & API INTERFACES                         │
│                                                                                 │
│   Streamlit Multipage App (Port 8501)       FastAPI Microservice (Port 8000)   │
│   • Executive Overview                      • GET  /health                      │
│   • Launch Explorer & SQL Console           • GET  /metadata                    │
│   • Geospatial Trajectory Intelligence      • POST /predict                     │
│   • Mission Predictive Lab                  • POST /predict/batch               │
│   • Model Intelligence & Explainability     • POST /economics                   │
│   • Commercial Launch Economics                                                 │
│   • Data Quality & Schema Health                                                │
│   • Full Technical Documentation                                                │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Audit Findings & Legacy Defect Repairs

During the initial engineering audit of the legacy capstone, **5 critical architectural defects** were identified and repaired:

| # | Legacy Defect | Root Cause & Failure Mechanism | SpaceY Intelligence Resolution |
| :-: | :--- | :--- | :--- |
| **1** | **Spurious 98% Accuracy** | Wikipedia scraper captured only flights 195–501 (313 successes, 2 failures). In an 80/20 split, test data had 58 successes and 1 failure. The model predicted 100% successes, acting as a trivial `DummyClassifier`. | Harmonized data into a dual-layer architecture: preserved balanced IBM benchmark ($n=90$, 60 successes / 30 failures) for ML training; expanded 482 launches into SQLite warehouse for longitudinal SQL analytics. |
| **2** | **Broken Payload Slider** | The preprocessing pipeline one-hot encoded `PayloadMass` as raw strings (e.g., `Payload mass_6,000 kg (13,000 lb)`). When users adjusted the integer slider, it matched 0 columns and was discarded. | Built robust regex extraction pipeline converting payload strings to clean `float64` kilograms; encoded continuous features with median imputation. |
| **3** | **412 Feature Explosion & Leakage** | Legacy pipeline one-hot encoded high-cardinality metadata (`Date`, `Time`, `BoosterVersion`), exploding the feature space to 412 sparse columns for only 90 samples ($p \gg n$). | Restricted feature schema to true pre-launch physical drivers: `FlightNumber`, `PayloadMass`, `Orbit`, `LaunchSite`, `Flights`, `GridFins`, `Reused`, `Legs`, `Block`. |
| **4** | **StandardScaler Distortion** | Scikit-learn `StandardScaler` was applied indiscriminately to one-hot dummy flags (0/1), destroying binary interpretability and distorting distances. | Implemented `ColumnTransformer` with `StandardScaler` only on continuous numeric columns and `OneHotEncoder(handle_unknown='ignore')` on categoricals. |
| **5** | **Stacked Map Markers** | Folium map markers for all launch sites were hardcoded to identical coordinates `[28.5, -80.6]`, stacking California (VAFB) and Florida sites into a single location. | Embedded precise geodetic coordinates for all sites (CCAFS SLC-40, KSC LC-39A, VAFB SLC-4E, Kwajalein Atoll) with custom styled Folium overlays. |

---

## 📊 Empirical Modeling & Leaderboard

Seven candidate algorithms were trained using stratified 5-fold cross-validation on the development benchmark dataset ($n=90$, 80/20 train/test split). Models were evaluated across multiple calibration and discrimination metrics:

| Rank | Model Candidate | CV ROC-AUC | Test Accuracy | Test ROC-AUC | Test PR-AUC | Test F1 Score | Test Brier Score | Latency (ms) |
| :-: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 🥇 | **Logistic Regression ($L_2$)** | **0.8750** | **77.8%** | **0.8194** | **0.8934** | **0.8571** | **0.1496** | **10.98** |
| 🥈 | **Random Forest (150 trees)** | 0.8458 | 77.8% | 0.7500 | 0.8290 | 0.8462 | 0.1652 | 19.82 |
| 🥉 | **Gradient Boosting** | 0.7917 | 77.8% | 0.7569 | 0.8142 | 0.8462 | 0.1691 | 15.65 |
| 4 | **Support Vector Classifier (RBF)** | 0.7250 | 72.2% | 0.6944 | 0.7816 | 0.8148 | 0.1984 | 12.43 |
| 5 | **K-Nearest Neighbors ($k=5$)** | 0.7667 | 72.2% | 0.7083 | 0.8278 | 0.8148 | 0.2012 | 11.21 |
| 6 | **Decision Tree (Cart)** | 0.7708 | 72.2% | 0.6806 | 0.7486 | 0.8000 | 0.2778 | 9.45 |
| 7 | **Dummy Baseline (Most Frequent)**| 0.5000 | 66.7% | 0.5000 | 0.6667 | 0.8000 | 0.2222 | 8.90 |

### Why Logistic Regression Outperformed Ensembles:
On small-to-moderate sample sizes ($n=90$) with high categorical representation, regularized linear models with an $L_2$ penalty achieve superior generalization by penalizing extreme weights. Tree ensembles tended to overfit to specific landing-leg and block interactions in the training folds.

### Key Predictive Drivers (Permutation Importance):
1. **`FlightNumber`** ($+0.0958$ ROC-AUC drop): Serves as an empirical proxy for SpaceX's organizational learning curve and hardware maturation.
2. **`Block`** ($+0.0625$): Later-generation boosters (Block 4/5) have structurally reinforced landing legs, thermal protection, and titanium grid fins.
3. **`Orbit`** ($+0.0514$): High-energy orbital injections (GTO, HEO) consume greater ascent $\Delta V$, leaving narrow fuel margins for deceleration burns.
4. **`Legs`** ($+0.0181$): Strong indicator of recovery intent; flights without legs were planned expendable missions.

---

## 💰 Commercial Launch Economics Engine

The economics engine bridges machine learning probabilities with financial decision theory. It calculates expected costs, commercial margins, and risk buffers under competitive pricing pressures:

$$\mathbb{E}[C] = P \cdot C_{\text{success}} + (1 - P) \cdot C_{\text{failure}}$$
$$\mathbb{E}[\text{Margin}] = R - \mathbb{E}[C]$$

### The Analytical Break-Even Recovery Probability ($P^*$):
The break-even probability represents the exact operational threshold where attempting booster recovery yields the same expected cost as flying an expendable rocket ($C_{\text{expendable}} = \$57.75\text{M}$):

$$P^* = \frac{C_{\text{ops}} + C_{\text{fail}}}{(V_{\text{booster}} - C_{\text{refurb}}) + C_{\text{fail}}} = \frac{\$2.5\text{M} + \$3.0\text{M}}{(\$25.0\text{M} - \$5.0\text{M}) + \$3.0\text{M}} = \frac{\$5.5\text{M}}{\$23.0\text{M}} \approx \mathbf{23.9\%}$$

```
Expected Commercial Savings vs. Expendable Flight ($M)
▲
│                                              +$17.17M (P = 95%)
│                                       ───────/
│                                ──────/
│                         ──────/
│                  ──────/ (P = 50%, +$6.30M)
│           ──────/
├──────────/──────────────────────────────────────────► Recovery Probability (P)
│      P* = 23.9% (Break-even: $0.00M savings)
│   ──/
│  /  (P = 0%, -$5.78M loss penalty)
▼
```

- **If $P > 23.9\%$**: Reusable flight profile recommended. Every additional percentage point in recovery confidence yields ~$\$240\text{K}$ in expected savings.
- **If $P \le 23.9\%$**: Expendable flight profile recommended. Stripping recovery hardware saves drone ship mobilization fees and avoids ocean salvage penalties.

---

## 🖥️ Multipage Aerospace Platform

The application features a mission control theme with custom CSS tokens, live telemetry metrics, and 8 dedicated modules:

| Page | Title | Key Capabilities |
| :-: | :--- | :--- |
| **🏠** | `app.py` | Command center launch pad, system status, quick KPIs, architecture blueprint. |
| **1** | `1_Executive_Overview.py` | Fleet-level metrics (482 launches, 83.2% lifetime success rate), cumulative cadence charts, executive summary. |
| **2** | `2_Launch_Explorer.py` | Full analytical data table with multi-parameter filtering, CSV export, and embedded interactive SQLite console. |
| **3** | `3_Geospatial_Intelligence.py` | Interactive Folium map with true geodetic coordinates, coastline proximity measurements, and site comparison. |
| **4** | `4_Predictive_Lab.py` | Real-time mission simulator. Adjust payload mass, orbit, booster block, and launch site to generate predictions and confidence intervals. |
| **5** | `5_Model_Intelligence.py` | Full model leaderboard, ROC and PR curves, confusion matrices, permutation importance rankings, calibration curves. |
| **6** | `6_Mission_Economics.py` | Interactive bidding calculator, expected margin sliders, break-even visualizers, and sensitivity curves. |
| **7** | `7_Data_Quality.py` | Automated schema validation health check, null distribution plots, data fingerprinting, anomaly flags. |
| **8** | `8_Technical_Documentation.py` | Complete in-app technical reference manuals, mathematical formulas, and developer guides. |

---

## ⚡ REST API Service

A production-ready **FastAPI** microservice is included for headless, automated integration into launch flight computers or commercial ERP systems:

```bash
# Start FastAPI server
uvicorn src.spacey.services.api:app --host 0.0.0.0 --port 8000 --reload
```

### Available Endpoints:
- `GET /health`: Service health and model readiness status.
- `GET /metadata`: Serialized model architecture, training timestamp, and feature schema.
- `POST /predict`: Single launch prediction with probability, risk level, and confidence intervals.
- `POST /predict/batch`: High-throughput array scoring.
- `POST /economics`: Integrated machine learning prediction + financial cost/margin calculation.

#### Example API Request:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "FlightNumber": 91,
    "PayloadMass": 6000.0,
    "Orbit": "GTO",
    "LaunchSite": "CCAFS SLC 40",
    "Flights": 2,
    "GridFins": 1,
    "Reused": 1,
    "Legs": 1,
    "Block": 5
  }'
```

#### Example Response:
```json
{
  "predicted_outcome": 1,
  "outcome_label": "SUCCESSFUL_LANDING",
  "recovery_probability": 0.8354,
  "confidence_band": "HIGH",
  "risk_level": "LOW",
  "model_version": "1.0.0",
  "model_name": "LogisticRegression"
}
```

---

## 📁 Project Directory Structure

```
spacey_capstone/
├── .github/
│   └── workflows/
│       └── ci.yml                 # Automated Continuous Integration workflow
├── .streamlit/
│   └── config.toml                # Dark aerospace theme styling configuration
├── data/
│   ├── processed/                 # Processed & validated datasets
│   │   ├── spacex_benchmark_processed.csv    # Balanced ML dataset (n=90)
│   │   ├── spacex_operational_processed.csv  # Cleaned Wikipedia dataset (n=315)
│   │   └── spacex_unified_launches.csv       # Longitudinal warehouse (n=482)
│   ├── raw/                       # Immutable raw source files
│   └── spacey_analytics.db        # SQLite warehouse with 6 dimensional views
├── dashboard/                     # Legacy compatible dashboard (modernized)
│   └── app.py
├── docs/                          # Comprehensive technical documentation
│   ├── ARCHITECTURE.md            # System architecture and data flow
│   ├── AUDIT_REPORT.md            # In-depth legacy audit & defect analysis
│   ├── DATA_DICTIONARY.md         # Field schemas, units, and definitions
│   ├── DEPLOYMENT.md              # Virtualenv, Docker, and Cloud deployment
│   ├── ECONOMICS_ASSUMPTIONS.md   # Commercial formulas and break-even math
│   ├── LIMITATIONS.md             # Sample bounds, concept drift, and causality
│   ├── METHODOLOGY.md             # Preprocessing, cross-validation, and metrics
│   ├── MODEL_CARD.md              # Intended use, calibration, and bias
│   ├── PROBLEM_STATEMENT.md       # Strategic business & engineering mission
│   └── TESTING.md                 # Test suite coverage and QA procedures
├── models/
│   └── registry/                  # Serialized production artifacts
│       ├── best_pipeline.joblib   # Trained Scikit-Learn pipeline
│       └── registry_metadata.json # Metadata, leaderboard, feature importance
├── notebooks/                     # Preserved legacy student notebooks
│   ├── 1_spacey_project_template.ipynb
│   ├── 2_data_cleaning_preprocessing.ipynb
│   ├── 3_model_training_logistic_regression.ipynb
│   └── 4_model_evaluation_visualization.ipynb
├── pages/                         # Streamlit multipage application
│   ├── 1_Executive_Overview.py
│   ├── 2_Launch_Explorer.py
│   ├── 3_Geospatial_Intelligence.py
│   ├── 4_Predictive_Lab.py
│   ├── 5_Model_Intelligence.py
│   ├── 6_Mission_Economics.py
│   ├── 7_Data_Quality.py
│   └── 8_Technical_Documentation.py
├── scripts/                       # Autonomous pipeline automation scripts
│   ├── prepare_data.py            # Ingestion, validation, and SQLite build
│   └── train_model.py             # Model training, CV benchmark, registry export
├── src/
│   └── spacey/                    # Production Python package
│       ├── analytics/             # SQL engine & analytical views
│       ├── config.py              # Centralized environment settings
│       ├── data/                  # Schemas, validation, ingestion, loader
│       ├── economics/             # Cost calculator & break-even math
│       ├── logging_config.py      # Structured enterprise logging
│       ├── models/                # Pipelines, evaluator, explainability, registry
│       ├── services/              # FastAPI REST microservice
│       └── ui/                    # Aerospace CSS theme & Plotly charts
├── tests/                         # Pytest test suite (23 tests, 100% pass)
│   ├── test_api.py
│   ├── test_data_validation.py
│   ├── test_economics.py
│   ├── test_modeling.py
│   └── test_ui_smoke.py
├── app.py                         # Primary Streamlit platform entry point
├── Dockerfile                     # Production container configuration
├── docker-compose.yml             # Streamlit + FastAPI orchestration
├── pyproject.toml                 # Package configuration & test flags
├── requirements.txt               # Pinned dependencies
└── README.md                      # Primary project reference
```

---

## ⚡ Quickstart Guide

### 1. Setup Local Environment
```bash
# Clone the repository
git clone https://github.com/Arvindhbabu/Data-Science-Capstone-Project.git
cd spacey_capstone

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# Install pinned dependencies
pip install -r requirements.txt
```

### 2. Execute Data Pipeline & Model Training
```bash
# Ingest, clean, validate datasets, and build SQLite database
python scripts/prepare_data.py

# Train 7 candidate models, perform 5-fold CV, and serialize best pipeline
python scripts/train_model.py
```

### 3. Launch the Applications
```bash
# Launch interactive Streamlit Platform
streamlit run app.py

# (Optional) Launch FastAPI Microservice in a separate terminal
uvicorn src.spacey.services.api:app --host 0.0.0.0 --port 8000
```

### 4. Run via Docker
```bash
# Multi-container orchestration (Streamlit on :8501, FastAPI on :8000)
docker-compose up -d
```

---

## 🧪 Testing & Quality Assurance

The test suite covers data validation, model prediction, economic calculations, API responses, and UI components:

```bash
# Run all tests
python -m pytest tests/ -v
```

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

## 📚 Technical Documentation

Deep-dive documentation is located in [`docs/`](file:///docs):
- [**Architecture Blueprint**](file:///docs/ARCHITECTURE.md): Multi-tier architecture, data flow diagrams, and module responsibilities.
- [**Comprehensive Audit Report**](file:///docs/AUDIT_REPORT.md): In-depth review of legacy notebook issues and repairs.
- [**Data Dictionary**](file:///docs/DATA_DICTIONARY.md): Complete field definitions, data types, physical units, and constraints.
- [**Methodology Guide**](file:///docs/METHODOLOGY.md): Feature engineering, stratified cross-validation, and selection criteria.
- [**Model Card**](file:///docs/MODEL_CARD.md): Performance benchmarks, calibration, limitations, and intended use cases.
- [**Mission Economics Assumptions**](file:///docs/ECONOMICS_ASSUMPTIONS.md): Complete mathematical derivations of $P^*$ and cost formulas.
- [**Quality & Testing Strategy**](file:///docs/TESTING.md): Pytest architecture, test case coverage, and CI integration.
- [**Deployment Guide**](file:///docs/DEPLOYMENT.md): Workstation, Docker, Docker Compose, and Cloud Run instructions.
- [**Limitations & Caveats**](file:///docs/LIMITATIONS.md): Statistical power constraints, concept drift, and physical confounders.

---

## 📄 License & Acknowledgments

- **License**: MIT License. See [LICENSE](file:///LICENSE) for full details.
- **Data Sources**: Publicly available launch data from SpaceX API via IBM Coursera Applied Data Science Capstone, and historical launch records from Wikipedia.
- **Original Capstone Student**: Arvindh Babu.
- **Transformed & Upgraded By**: Principal Data Science & ML Engineering Team.

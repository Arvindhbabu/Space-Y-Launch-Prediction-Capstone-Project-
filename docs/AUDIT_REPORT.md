# SpaceY Intelligence — Mandatory Repository Audit Report (Phase 0)

**Date**: 2026-10-13  
**Auditor**: Principal Data Scientist & Analytics Architect  
**Project**: SpaceY Intelligence (Transformed from Coursera/IBM SpaceX Capstone)  
**Workspace**: `spacey_capstone`  
**Git Remote**: `https://github.com/Arvindhbabu/Space-Y-Launch-Prediction-Capstone-Project-.git`  

---

## 1. Executive Summary

This repository audit documents the findings from an exhaustive inspection of the existing SpaceY Falcon 9 landing prediction capstone. While the original project laid an initial foundation with a prototype Streamlit script, serialized scikit-learn artifacts, and exploratory Jupyter notebooks, an in-depth programmatic examination revealed critical architectural, data science, and modeling defects. Most notably, the model exhibited an artificial 98% accuracy due to severe class imbalance (313 successes vs. 2 failures in the scraped 2023–2024 slice), a complete decoupling of payload mass from predictions due to raw string one-hot encoding, and identical hardcoded geographic coordinates for all launch sites.

This report establishes the baseline, catalogs risks and root causes, details the data provenance, and lays out the transformation roadmap to convert this academic prototype into **SpaceY Intelligence**: a production-grade, reproducible, testable, and interview-ready launch decision-support platform.

---

## 2. Repository Inventory & Tree Analysis

The current workspace contains the following layout:

```text
spacey_capstone/
├── dashboard/
│   ├── app.py                     # Monolithic Streamlit application (81 lines)
│   ├── model.pkl                  # Serialized LogisticRegression (412 features, scikit-learn 1.6.1)
│   ├── scaler.pkl                 # Serialized StandardScaler (412 features)
│   ├── launch_site.jpg            # Static banner image
│   ├── Description.png            # Architecture screenshot
│   └── tempCodeRunnerFile.py      # Transient script artifact
├── data/
│   ├── raw_spacex_launches.csv    # 824 rows, 10 columns (scraped Wikipedia tables, 2023–2024)
│   └── cleaned_spacex_launches.csv# 824 rows, 11 columns (raw data + incomplete Landing_Success mapping)
├── models/
│   ├── model.pkl                  # Duplicate copy of dashboard/model.pkl
│   └── scaler.pkl                 # Duplicate copy of dashboard/scaler.pkl
├── notebooks/
│   ├── 1_spacey_project_template.ipynb            # Skeleton template
│   ├── 2_data_cleaning_preprocessing.ipynb        # Incomplete cleaning script (Colab export)
│   ├── 3_model_training_logistic_regression.ipynb # Logistic regression training with extreme class imbalance
│   └── 4_model_evaluation_visualization.ipynb    # Evaluation plots with high false positive risk
├── presentation/
│   ├── presentation.pptx                          # Presentation deck (19.8 MB)
│   └── Applied Data Science Capstone Project.pptx # Capstone presentation (5.5 MB)
├── scripts/
│   └── spacex_scraper.py          # Wikipedia scraper fetching only post-flight 195 table
├── requirements.txt               # Unpinned 7-package dependency list
└── README.md                      # Academic README with dead/stale links
```

---

## 3. Detailed Data Audit & Root Cause Analysis

### 3.1 Raw Dataset (`data/raw_spacex_launches.csv`)
- **Dimensions**: 824 rows × 10 columns.
- **Coverage**: Launches from Flight 195 (January 3, 2023) to Flight 501 (late 2024).
- **Critical Finding 1 — Wikipedia Table Subrow Pollution**:
  In Wikipedia's `List_of_Falcon_9_and_Falcon_Heavy_launches`, each launch row is accompanied by a subrow spanning all columns (`colspan=9`) containing mission descriptions. The HTML table parser (`pd.read_html`) duplicated these multi-sentence description strings across all 9 columns.
  - Of 824 rows, **432 rows (52.4%)** are non-launch description subrows.
  - Only **392 rows** represent actual booster flight/stage events.
- **Critical Finding 2 — Temporal Truncation (Missing Flights 1–194)**:
  Wikipedia historically partitioned Falcon 9 launches into sub-articles:
  - `(2010–2019)` (Flights 1 to 77)
  - `(2020–2022)` (Flights 78 to 194)
  The scraper only targeted the root article URL, completely omitting the foundational development and recovery-learning era (2010–2022).

### 3.2 Cleaned Dataset (`data/cleaned_spacex_launches.csv`)
- **Dimensions**: 824 rows × 11 columns.
- **Target Variable (`Landing_Success`) Distribution**:
  - `NaN`: 509 rows (61.8%)
  - `1.0` (Success): 313 rows (38.0%)
  - `0.0` (Failure): 2 rows (0.2%)
- **Root Cause**:
  In `notebooks/2_data_cleaning_preprocessing.ipynb`, the cleaning logic consisted solely of:
  ```python
  def map_landing(outcome):
      if isinstance(outcome, str) and "Success" in outcome:
          return 1
      elif isinstance(outcome, str) and "Failure" in outcome:
          return 0
      else:
          return None
  ```
  Because the modern 2023–2024 era boasts a >98% booster landing success rate, the resulting dataset had almost zero negative examples. Description subrows and unattempted/expendable launches became `NaN`.
- **Target Definition Flaw**:
  Expendable missions ("No attempt") were discarded or mapped to `NaN` rather than treated as non-recovery outcomes.

### 3.3 The IBM Coursera Foundational Dataset (`dataset_part_2.csv`)
- **Dimensions**: 90 rows × 18 columns.
- **Coverage**: Flights 1 to 90 (2010–2020), spanning the development, experimental recovery, and operationalization phases of Falcon 9 v1.0, v1.1, and Block 5.
- **Target Distribution**:
  - `1` (Landing Success): 60 (66.7%)
  - `0` (Landing Failure / No Attempt): 30 (33.3%)
- **Key Features Available**:
  `FlightNumber`, `Date`, `BoosterVersion`, `PayloadMass`, `Orbit`, `LaunchSite`, `Outcome`, `Flights`, `GridFins`, `Reused`, `Legs`, `LandingPad`, `Block`, `ReusedCount`, `Serial`, `Longitude`, `Latitude`, `Class`.
- **Architectural Decision**:
  SpaceY Intelligence will ingest **both** layers:
  1. The **Foundational Capstone Benchmark Dataset** (IBM Coursera 90 launches) for core machine learning model training, cross-validation, and benchmarking against historical baseline results.
  2. The **Operational Launch Archive** (cleaned 2023–2024 records + historical launches) for modern temporal analytics, longitudinal success rate tracking, and fleet maturity studies.

---

## 4. Modeling & Machine Learning Audit

### 4.1 Feature Explosion & Leakage (The $p > n$ Defect)
- In `notebooks/3_model_training_logistic_regression.ipynb`:
  - `features = ['Payload mass', 'Orbit', 'Version, booster[h]', 'Launch site']`
  - `X = pd.get_dummies(df[features])`
- Because `Version, booster[h]` contained individual booster serial numbers with specific flight iterations and Wikipedia footnotes (e.g., `F9 B5 B1080-14`, `F9 B5 B1092-1[497]`), one-hot encoding produced **412 feature columns** for only **315 labeled rows**.
- The model memorized specific historical booster serial strings, making it impossible to predict unseen boosters.

### 4.2 The Payload Mass Bug
- `Payload mass` contained strings like `"6,000 kg (13,000 lb)"`, `"~17,400 kg (38,400 lb)"`, and `"Unknown[j]"`.
- Instead of extracting the numeric kilograms, `pd.get_dummies` treated each distinct string as a separate categorical column (e.g., `Payload mass_6,000 kg (13,000 lb)`).
- In `dashboard/app.py`, the UI provides an integer slider for Payload Mass (0–10,000 kg). When `pd.get_dummies` is called on the user input, it creates column `'Payload mass'`, which is **not** in `model.feature_names_in_`.
- The alignment loop in `app.py`:
  ```python
  for col in X_columns:
      if col not in input_encoded.columns:
          input_encoded[col] = 0
  ```
  silently zeroed out all 412 model features except the selected site/orbit/booster, completely discarding the user's payload mass input! Changing the payload mass slider had **0.0% mathematical impact** on the prediction score.

### 4.3 Dummy Predictor Phenomenon & False Metric Claims
- In `notebooks/3_model_training_logistic_regression.ipynb` (Cell 22):
  - Train/Test split: 80/20.
  - Test set had 58 Successes and 1 Failure (support = 59).
  - Confusion Matrix:
    $$\begin{pmatrix} 0 & 1 \\ 0 & 58 \end{pmatrix}$$
  - The model predicted `1` for all 59 test cases.
  - Failure precision: `0.00`, Recall: `0.00`, F1: `0.00`.
  - Reported accuracy: `98.3%`.
  - The notebook reported this as a "high-performing model," failing to identify that it was mathematically identical to a trivial majority-class `DummyClassifier`.

### 4.4 Data Preprocessing & Scaling Flaws
- `StandardScaler` was applied across all one-hot encoded binary columns. Scaling one-hot columns subtracts the empirical proportion $\bar{x}$ and divides by standard deviation $\sqrt{\bar{x}(1-\bar{x})}$, transforming discrete $\{0, 1\}$ values into uninterpretable continuous z-scores.
- `model.pkl` and `scaler.pkl` were saved as loose separate files rather than an integrated `Pipeline` or `ColumnTransformer`.
- Environment mismatch: Model was serialized with scikit-learn 1.6.1, generating `InconsistentVersionWarning` on current environments (scikit-learn 1.5.1).

---

## 5. Dashboard & Software Engineering Audit

### 5.1 Geospatial Coordinates Error
In `dashboard/app.py`:
```python
m = folium.Map(location=[28.5, -80.6], zoom_start=3)
for site in df['Launch site'].unique():
    folium.Marker(location=[28.5, -80.6], popup=site).add_to(m)
```
- Every marker was pinned to Cape Canaveral `[28.5, -80.6]`. Vandenberg Space Force Base (California) and Starbase/Boca Chica (Texas) were pinned directly on top of Cape Canaveral, rendering the interactive map misleading and incorrect.

### 5.2 Application Architecture Deficiencies
- Monolithic single-file script without modularity.
- Hardcoded local relative paths (`../data/cleaned_spacex_launches.csv`).
- Absence of data validation layers, schema enforcement, or exception handling.
- Lack of automated tests (0 unit tests, 0 integration tests).
- Missing business economics calculation engine (no expected cost, margin, or risk modeling).
- Missing model explainability (no SHAP, permutation importance, or feature contribution analysis).

---

## 6. Transformation Plan & Implementation Phases

| Phase | Description | Deliverables |
|---|---|---|
| **Phase A** | Audit & Baseline | `docs/AUDIT_REPORT.md` (this document), preservation of legacy artifacts |
| **Phase B** | Data Governance & Ingestion | `src/spacey/data/` (loader, validation, preprocessing, schema), dual dataset support, SQLite analytics views |
| **Phase C** | Modeling & Evaluation | `src/spacey/models/` (pipelines, 7 classifiers, hyperparameter tuning, metrics, calibration, explainability, registry) |
| **Phase D** | Mission Economics | `src/spacey/economics/` (expected cost calculator, break-even probability, sensitivity analysis) |
| **Phase E** | Streamlit Web Platform | Multipage technical app (`pages/1` through `8`), aerospace theme, Plotly & Folium integration |
| **Phase F** | Engineering & Testing | FastAPI inference service, pytest test suite, Docker configuration, GitHub Actions CI |
| **Phase G** | Documentation & Verification | Full documentation suite (`docs/`), model card, data dictionary, interview guide |

---

## 7. Artifact Preservation Notice
In accordance with engineering guidelines, all existing user files (notebooks, raw datasets, presentation slides, and legacy dashboard scripts) will be preserved without destructive overwrites. New modular components will reside in `src/spacey/` and modern multipage interfaces will replace the legacy entry point while maintaining backward compatibility.

# SpaceY Intelligence — Verification Report

**Last reviewed:** 2026-10-17  
**Verification status:** Partially verified; see evidence and pending checks below.

## Confirmed from repository inspection

- The repository contains a multipage Streamlit application, FastAPI endpoints, SQLite analytics, data/model scripts, serialized model artifacts, documentation, and pytest tests.
- requirements.txt declares pinned dependencies. This branch aligns pyproject.toml with those pins and targets Python 3.12 to avoid advertising unsupported combinations without verification.
- The model registry previously logged a compatibility warning but proceeded to deserialize the model. This branch changes this to fail closed when explicit provenance is missing or the scikit-learn major/minor version differs.
- CI is configured to use Python 3.12 and run dependency validation plus pytest. The actual result must be checked in GitHub Actions; a workflow configuration is not evidence of a passing run.

## Prior local test evidence

A local test log dated 2026-10-13 showed 3 failures and 20 passes out of 23 tests when pytest ran from the global Python installation with scikit-learn 1.5.1 while the model artifact had been serialized using scikit-learn 1.9.1. A later local report claims 23 tests passed in a different environment, but that output has not been independently reproduced from this repository branch.

## Model artifact compatibility

Scikit-learn does not guarantee that serialized estimators remain compatible across arbitrary library versions. Use the same pinned environment for model training and inference, and regenerate the artifact if the dependency set changes. A warning alone is not sufficient if the application would then proceed to load an artifact known to be incompatible.

The registry check compares scikit-learn major/minor versions. It is a conservative guardrail, not a universal proof of compatibility; package lockstep, model provenance, and an inference smoke test are still required.

## Data integrity items requiring independent verification

Earlier local logs reported a future-dated launch row (2029-06-15) and different aggregate success rates (77.4% versus 83.2%). These values must be reconciled against the actual source and cleaning rules before being reported as verified facts. Review dataset overlap, duplicates, outcome definitions, and dates before retraining or presenting model metrics.

## Remaining verification steps

1. Review the GitHub Actions run triggered by this branch and confirm the job result.
2. Run the complete tests in the pinned Python 3.12 environment and confirm both prediction endpoints and the dashboard.
3. Verify the data preparation script's network requirements and whether it overwrites checked-in artifacts.
4. Inspect the future-dated row and reconcile aggregate counts from the raw and cleaned datasets.
5. Validate the holdout evaluation design and avoid describing the model as suitable for operational aerospace decisions.

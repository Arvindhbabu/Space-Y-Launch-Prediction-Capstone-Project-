# SpaceY Intelligence — Model Card

## Summary

This document describes the registered educational classifier and the evidence recorded in the repository's model metadata. It is **not a production-readiness approval**.

## Model details

| Field | Description |
|---|---|
| Model identifier | SpaceY recovery classifier v1 |
| Pipeline | scikit-learn preprocessing pipeline with Logistic Regression classifier |
| Artifact | `models/registry/best_pipeline.joblib` |
| Provenance | `models/registry/registry_metadata.json` |
| Recorded training environment | Python 3.12.10, scikit-learn 1.9.1 (from registry metadata; runtime compatibility must be checked before loading) |
| Target | Historical recovery outcome class as defined by the dataset preparation pipeline |

## Intended use

Appropriate uses include classroom demonstrations, model-evaluation exercises, historical pattern exploration, and comparison of hypothetical inputs through the dashboard.

The model is **not** intended for vehicle guidance, launch authorization, certified range safety, commercial pricing decisions, engineering certification, or real mission planning.

## Data and evaluation design

The current registry metadata describes a 90-record benchmark with a stratified 72-record training partition and an 18-record holdout partition. The recorded holdout partition contains 12 positive and 6 negative examples.

The small sample size means a small number of records can materially change the reported metrics. Dataset provenance, temporal validity, duplicate handling, target definition, and separation between the benchmark and operational archive must be examined before interpreting results.

## Recorded holdout results

The values below reproduce the current registered metadata snapshot; retraining may change them.

| Metric | Recorded value | Interpretation |
|---|---:|---|
| Accuracy | 0.7778 | Fraction of holdout records correctly classified |
| ROC-AUC | 0.8194 | Ranking ability across probability thresholds |
| PR-AUC | 0.8934 | Precision-recall performance summary |
| Precision | 0.7500 | Fraction of predicted successes that were positive |
| Recall | 1.0000 | Fraction of actual positive outcomes identified |
| Specificity | 0.3333 | Fraction of actual negative outcomes identified |
| F1 score | 0.8571 | Harmonic mean of precision and recall |
| Brier score | 0.1496 | Mean squared probability error; lower is better |
| Recorded inference latency | 18.15 ms | Snapshot value in model registry metadata; environment and measurement details may affect this value |

### Confusion matrix

The recorded 18-record holdout confusion matrix is TN = 2, FP = 4, FN = 0, TP = 12.

The specificity of 0.3333 is a material limitation: only two of six negative outcomes were correctly identified at the recorded decision threshold. The high recall must not be presented without this context.

## Features and interpretation

The registered feature set contains payload mass, booster flight count, block, flight sequence number, launch site, orbit, grid fins, landing legs, and reuse indicator. These are historical statistical predictors—not a physical simulation.

The registry's permutation importance values are uncertain on this small holdout. Importance measures indicate model dependence, not causation, engineering necessity, or a guarantee that changing a feature will change the real-world outcome.

## Known limitations and risks

- The benchmark and holdout sample are small.
- Historical launch practices, hardware, targets, and recovery techniques change over time.
- The dataset does not model all relevant physical and environmental conditions.
- Predicted probabilities can be miscalibrated outside the sampled data distribution.
- A single random holdout is not a robust estimate of future performance.
- Economic outputs depend on user-provided illustrative assumptions and are separate from aerospace validation.

## Recommended evaluation before further claims

Use temporally aware validation where possible; report confidence intervals or repeated-split variability; audit leakage, class balance, missingness, dates, and duplicate/overlapping records; calibrate probabilities on data separate from the final test set; and evaluate failure detection explicitly. Do not use the current model for operational aerospace decisions.

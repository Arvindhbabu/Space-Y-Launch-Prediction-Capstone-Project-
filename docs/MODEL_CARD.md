# SpaceY Intelligence — Production Model Card

## 1. Model Details
- **Model Identifier**: `SpaceY-Recovery-Classifier-v1.0`
- **Architecture**: `LogisticRegression` (with integrated `ColumnTransformer` preprocessing)
- **Framework**: `scikit-learn 1.5.1`
- **Serialization**: `models/registry/best_pipeline.joblib`
- **Trained On**: Foundational Benchmark Capstone Dataset ($n=90$, 2010–2020)
- **Primary Objective**: Binary classification of first-stage Falcon 9 booster recovery success vs. failure/unattempted.

---

## 2. Intended Use & Target Users
- **Intended Use**: Operational scenario simulation, preliminary launch bidding decision-support, sensitivity analysis, and comparative flight analytics.
- **Target Users**: Mission analysts, launch operations architects, and commercial bidding teams.
- **Out-of-Scope Use**: Real-time flight control, onboard guidance, navigation, and control (GNC), or certified aerospace range safety clearance.

---

## 3. Training & Evaluation Data
- **Training Partition**: 72 flights (48 successes, 24 failures).
- **Holdout Test Partition**: 18 flights (12 successes, 6 failures).
- **Feature Set**: Pre-launch knowable features only (`PayloadMass`, `Flights`, `Block`, `FlightNumber`, `LaunchSite`, `Orbit`, `GridFins`, `Legs`, `Reused`).

---

## 4. Empirical Evaluation Metrics (Holdout Partition)

| Metric | Holdout Value | Description |
|---|---|---|
| **ROC-AUC** | **0.8194** | Ability to rank recovery successes above recovery failures |
| **F1-Score** | **0.8571** | Harmonic mean of precision and recall |
| **Accuracy** | **0.7778** | Overall correct classification rate |
| **Precision** | **0.7500** | Fraction of predicted recoveries that were true successes |
| **Recall (Sensitivity)** | **1.0000** | Fraction of actual recoveries correctly predicted |
| **Specificity** | **0.3333** | Fraction of actual failures correctly identified |
| **PR-AUC (Avg Precision)**| **0.8934** | Area under the precision-recall curve |
| **Brier Score** | **0.1496** | Mean squared difference between predicted probability and true label (lower is better) |
| **Inference Latency** | **~10.98 ms** | Average single-scenario inference latency |

### Confusion Matrix (Holdout $n=18$)
$$\begin{pmatrix} \text{TN} = 2 & \text{FP} = 4 \\ \text{FN} = 0 & \text{TP} = 12 \end{pmatrix}$$

---

## 5. Model Selection Justification (Why Logistic Regression Won)
In comparative testing across 7 models (including Random Forest, Gradient Boosting, SVM, KNN, Decision Tree, and Dummy Baseline):
- High-capacity ensemble models (Random Forest, Gradient Boosting) achieved holdout ROC-AUC of $0.7500 - 0.7569$.
- On small-to-medium sample sizes with high feature-to-sample ratios in categorical dummies, ensemble trees tend to overfit to idiosyncratic training splits.
- Regularized Logistic Regression ($L_2$ penalty) generalized with superior smoothness and calibration, achieving the highest holdout ROC-AUC (**0.8194**) and highest PR-AUC (**0.8934**).

---

## 6. Top Feature Drivers (Permutation Importance on Test Partition)
1. `FlightNumber` (+0.0958 ROC-AUC drop): Captures organizational learning and procedure refinement over time.
2. `Block` (+0.0625): Design iterations from Block 1 to Block 5 dramatically improved thermal and structural landing capability.
3. `Orbit` (+0.0514): Orbital velocity requirements directly impact stage separation speed and propellant margin.
4. `Legs` (+0.0181): Essential physical equipment for touchdown.
5. `LaunchSite` (+0.0167): Complex geography correlates with orbital corridors.

---

## 7. Limitations & Caveats
- Calibrated primarily on historical Falcon 9 recovery testing flights.
- High recall (1.00) paired with moderate specificity (0.33) indicates the model leans optimistic on recovery, reflecting the empirical success trajectory of the vehicle.
- Sea-state ocean conditions (wave swell height > 3m) and upper-atmosphere winds are unmodeled environmental variables.

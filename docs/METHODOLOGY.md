# SpaceY Intelligence — Applied Data Science & Modeling Methodology

## 1. Data Governance & Preprocessing Pipeline

### 1.1 Ingestion & Cleaning
- **Dual Layer Architecture**:
  1. *Foundational Development Dataset* (90 flights, 2010–2020): Preserves the experimental era where SpaceX developed atmospheric reentry steering, drone ship barges, and landing leg deployments. Yields a balanced class distribution ($66.7\%$ success, $33.3\%$ failure) for rigorous classifier training and evaluation.
  2. *Operational Scraped Dataset* (392 flight events, 2023–2024): Cleans Wikipedia launch tables by filtering out over 400 description subrows, parsing raw payload strings into numerical kilograms via regex, and mapping complex strings to canonical coordinates.
- **Payload Imputation Strategy**:
  - Missing payloads are **never replaced with zero**. Zero payload represents a physically absurd rocket launch and distorts fuel-to-weight models. Missing payload mass is imputed using the median of known payloads within the training partition.
- **Categorical Harmonization**:
  - Launch site aliases (`"Cape Canaveral, SLC-40"`, `"CCAFS"`, `"SLC-40"`) are mapped to canonical keys with verified coordinates.
  - Orbits are normalized into 11 valid orbital regimes.

---

## 2. Machine Learning Pipeline Architecture

### 2.1 Preprocessing Isolation (`ColumnTransformer`)
To eliminate target leakage, feature preprocessing is packaged inside scikit-learn Pipelines:
- **Numerical Features** (`PayloadMass`, `Flights`, `Block`, `FlightNumber`):
  - `SimpleImputer(strategy='median')`
  - `StandardScaler()` (z-score normalization: $\frac{x - \mu}{\sigma}$)
- **Categorical Features** (`LaunchSite`, `Orbit`):
  - `SimpleImputer(strategy='most_frequent')`
  - `OneHotEncoder(handle_unknown='ignore', sparse_output=False)`
- **Binary Features** (`GridFins`, `Legs`, `Reused`):
  - `SimpleImputer(strategy='most_frequent')`
  - Passthrough (preserves discrete $\{0, 1\}$ values without distortion)

### 2.2 Model Selection & Cross-Validation Strategy
- **Partitioning**: 80% Train ($n=72$, 48 successes, 24 failures), 20% Holdout Test ($n=18$, 12 successes, 6 failures) using Stratified Splitting (`stratify=y`).
- **Inner Tuning**: 5-Fold Stratified Cross-Validation (`StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`) optimizing ROC-AUC across 7 candidate algorithms:
  1. `DummyClassifier(strategy='most_frequent')` (Baseline)
  2. `LogisticRegression` ($L_2$ regularization, grid searching $C$ and solvers)
  3. `DecisionTreeClassifier` (tuning `max_depth`, `min_samples_split`, `criterion`)
  4. `SVC(probability=True)` (tuning $C$ and kernels: linear, rbf)
  5. `KNeighborsClassifier` (tuning neighbors and weights)
  6. `RandomForestClassifier` (tuning trees, depth, split constraints)
  7. `GradientBoostingClassifier` (tuning learning rate, estimators, depth)
- **Holdout Evaluation**: The selected pipeline is evaluated on the completely unseen holdout set to report final metrics.

---

## 3. Explainability & Scenario Attribution

- **Permutation Feature Importance**: Evaluated on holdout data by measuring the drop in ROC-AUC when each feature is randomly shuffled.
- **Local Feature Attribution**: For any user-defined scenario, each feature is perturbed to the baseline dataset median/mode, and the resulting delta in recovery probability is computed:
  $$\Delta P_i = P(\mathbf{x}) - P(\mathbf{x}_{\setminus i, \text{baseline}})$$
  This provides transparent insight into whether an input parameter pushes the score towards success (+) or failure (-).

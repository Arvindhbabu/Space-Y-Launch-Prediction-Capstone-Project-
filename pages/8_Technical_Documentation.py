"""
SpaceY Intelligence - Page 8: Technical Documentation & Interview Guide
Architecture diagrams, mathematical methodologies, model cards, and technical interview discussions.
"""

import sys
from pathlib import Path

# Add src to sys.path
root_dir = Path(__file__).resolve().parent.parent
src_dir = root_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import streamlit as st
from spacey.ui.theme import (
    apply_spacey_theme,
    render_page_header,
    render_section_header,
    get_gradient_icon_html,
)

st.set_page_config(page_title="Technical Documentation | SpaceY Intelligence", layout="wide")
apply_spacey_theme()

render_page_header(
    title="Technical Documentation & Architecture",
    subtitle="End-to-end system design, mathematical specifications, modeling governance, and interview guide.",
    badge_text="ENGINEERING SPECIFICATION",
    icon="book",
    variant="slate",
)

doc_tab1, doc_tab2, doc_tab3, doc_tab4, doc_tab5 = st.tabs([
    "System Architecture",
    "Modeling Methodology",
    "Economics Equations",
    "Limitations & Risks",
    "Technical Interview Guide",
])

with doc_tab1:
    render_section_header(
        title="System Architecture & Data Flow",
        subtitle="Decoupled pipeline layers spanning raw ingestion, analytical warehouse, and inference boundaries.",
        icon="layers",
        variant="blue",
    )
    st.markdown("""
```
+-----------------------------------------------------------------------+
|                         DATA INGESTION LAYER                          |
|  - IBM Coursera Capstone S3 (90 Dev Flights, 2010-2020)               |
|  - Local Scraped Wikipedia Archive (392 Operational Flights, 2023-24)  |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                     DATA PREPARATION & VALIDATION                     |
|  - Footnote/Citation Stripping & Subrow Filtering                     |
|  - Numerical Kilogram Payload Extraction                              |
|  - Site Coordinate Normalization (CCAFS, KSC, VAFB)                   |
|  - Strict Binary Target Construction (Class: 1=Success, 0=Failure)    |
+-----------------------------------------------------------------------+
                |                                       |
                v                                       v
+-------------------------------+       +-------------------------------+
|     SQL ANALYTICS ENGINE      |       |      MACHINE LEARNING ENGINE  |
|  - SQLite Database            |       |  - ColumnTransformer Preproc  |
|  - 6 Dimensional Views        |       |  - 7 Candidate Classifiers    |
|  - Denominator Enforcements   |       |  - 5-Fold Stratified CV Grid  |
|  - Time & Reuse Trends        |       |  - Model Registry & Metadata  |
+-------------------------------+       +-------------------------------+
                |                                       |
                +-------------------+-------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                    MISSION DECISION & UI PLATFORM                     |
|  - Streamlit Multipage Application (8 Active Modules)                 |
|  - Commercial Launch Economics Engine (Expected Cost & Margins)       |
|  - Local Permutation Feature Attribution & Sensitivity Curves         |
|  - Optional Typed FastAPI Inference Boundary                          |
+-----------------------------------------------------------------------+
```
    """)

with doc_tab2:
    render_section_header(
        title="Machine Learning Formulation & Leakage Prevention",
        subtitle="Formal target definition, pre-launch physical feature space, and cross-validation integrity.",
        icon="cpu",
        variant="purple",
    )
    st.markdown("""
    #### 1. Target Definition
    The prediction target is defined as binary first-stage recovery outcome:
    - **Class 1 (Recovery Success)**: Successful landing on an Autonomous Spaceport Drone Ship (ASDS) or Ground Landing Zone (RTLS).
    - **Class 0 (Recovery Failure / Loss)**: Ocean crash, splashdown, landing pad explosion, or mission where booster was deliberately expended without recovery gear.

    #### 2. Strict Pre-Launch Feature Set (Zero Data Leakage)
    To guarantee real-world inference validity, predictive models are fed **only** features that are physically and contractually known prior to vehicle liftoff:
    - **Numerical Features**: `PayloadMass` (kg), `Flights` (stage flight iteration count), `Block` (engine and thermal protection architecture version), `FlightNumber` (historical flight sequence).
    - **Categorical Features**: `LaunchSite` (CCAFS SLC 40, KSC LC 39A, VAFB SLC 4E), `Orbit` (LEO, GTO, ISS, SSO, etc.).
    - **Binary Features**: `GridFins` (aerodynamic steerable fins), `Legs` (deployable landing gear), `Reused` (flight-proven booster).
    - **Excluded Leakage Features**: `Booster landing`, `LandingPad`, `Launch outcome`, `Outcome`, recovery ship names, telemetry post-stage-separation, and customer recovery statements.

    #### 3. Cross-Validation & Preprocessing Integrity
    - Preprocessing (`ColumnTransformer`) is fit **strictly on training partitions** inside the scikit-learn `Pipeline`.
    - Categoricals are encoded with `OneHotEncoder(handle_unknown='ignore')`.
    - Numerical features are median-imputed and z-score normalized.
    - Models are optimized via 5-Fold Stratified CV on training data, evaluated against an independent holdout test partition.
    """)

with doc_tab3:
    render_section_header(
        title="Mission Economics Mathematical Formulation",
        subtitle="Expected value equations, financial trade-offs, and closed-form break-even solution.",
        icon="dollar",
        variant="amber",
    )
    st.markdown("""
    #### Expected Cost Equation
    $$\mathbb{E}[\text{Cost}] = P \cdot \text{Cost}_{\text{success}} + (1 - P) \cdot \text{Cost}_{\text{failure}}$$
    Where:
    - $\text{Cost}_{\text{success}} = (C_{\text{base}} + C_{\text{ops}} - (V_{\text{booster}} - C_{\text{refurb}})) \cdot (1 + \text{Reserve})$
    - $\text{Cost}_{\text{failure}} = (C_{\text{base}} + C_{\text{ops}} + C_{\text{contingency}}) \cdot (1 + \text{Reserve})$
    - $\text{Cost}_{\text{expendable}} = C_{\text{base}} \cdot (1 + \text{Reserve})$

    #### Break-Even Recovery Probability Threshold ($P^*$)
    Setting Expected Cost equal to Expendable Baseline Cost yields the analytical threshold:
    $$P^* = \frac{C_{\text{ops}} + C_{\text{contingency}}}{(V_{\text{booster}} - C_{\text{refurb}}) + C_{\text{contingency}}}$$
    If $P_{\text{pred}} > P^*$, attempting booster recovery has positive expected value.
    """)

with doc_tab4:
    render_section_header(
        title="Operational Limitations & Data Caveats",
        subtitle="Sample size bounds, distribution drift from Block 1 to Block 5, and maritime physics.",
        icon="alert",
        variant="rose",
    )
    st.markdown("""
    1. **Small Sample Size for Early Failures**: Falcon 9 failure observations occurred primarily during early development flights (2010–2016). Modern operational flights have near-zero failure rates.
    2. **Concept Drift & Fleet Maturity**: Falcon 9 Block 5 represents a mature vehicle. Applying models trained on early Block 1–4 failures to modern missions requires understanding technological distribution shift.
    3. **Unmodeled Atmospheric & Marine Hazards**: Real recovery operations are bounded by high-altitude wind shear during supersonic retro-propulsion, sea surface swells exceeding 3 meters at the drone ship, and localized GPS loss.
    4. **Illustrative Financial Assumptions**: Launch economics calculations are commercial scenario models and do not represent proprietary SpaceX cost ledgers or government defense contracts.
    """)

with doc_tab5:
    render_section_header(
        title="Technical Interview Guide",
        subtitle="Key data science, machine learning, and systems architecture discussion points.",
        icon="book",
        variant="cyan",
    )
    st.markdown("""
    #### Q1: Why did Logistic Regression outperform tree ensembles like Random Forest on holdout ROC-AUC?
    **Answer**: On smaller datasets ($n=90$ in the foundational benchmark), high-capacity ensembles like Random Forest and Gradient Boosting risk overfitting to idiosyncratic feature combinations (e.g. memorizing specific flight indices). A regularized linear model (`LogisticRegression` with $L_2$ regularization) fits a smooth hyper-plane that generalizes with lower variance out-of-sample.

    #### Q2: What was the root cause of the 98% accuracy in the legacy capstone?
    **Answer**: The legacy script scraped only Wikipedia launches post-flight 195 (2023–2024), where Block 5 achieved near-100% landing success. Out of 59 test cases, 58 were successes and 1 was failure. The model predicted 100% successes, acting as a trivial majority classifier. Precision and recall on the minority class (failure) were exactly 0.00.

    #### Q3: How did you fix the Payload Mass feature bug?
    **Answer**: The legacy script ran `pd.get_dummies` directly on unparsed text strings like `"6,000 kg (13,000 lb)"`, creating 50+ categorical dummy columns. When the user entered an integer `5000` via the slider, the column was missing from the dummy feature set and silently dropped. We implemented regex parsing to extract raw numeric kilograms (`float`), median-imputed missing values, and scaled it through a `ColumnTransformer`.

    #### Q4: How is data leakage prevented?
    **Answer**: We strictly isolate pre-launch knowable features (`PayloadMass`, `LaunchSite`, `Orbit`, `Flights`, `Block`, `GridFins`, `Legs`, `Reused`) from post-launch recovery telemetry (`LandingPad`, `Booster landing`, `Outcome`). Furthermore, all preprocessing statistics (imputer medians, scaler means, encoder categories) are learned exclusively on training folds.

    #### Q5: How do you distinguish discrimination from probability calibration?
    **Answer**: Discrimination (measured by ROC-AUC and F1) evaluates whether the model ranks positive instances higher than negative instances. Calibration (measured by Brier score and reliability curves) evaluates whether a predicted probability of 0.80 truly corresponds to an 80% empirical recovery rate. We evaluate both separately.
    """)

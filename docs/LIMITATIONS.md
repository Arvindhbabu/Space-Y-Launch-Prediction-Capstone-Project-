# ⚠️ SpaceY Intelligence — Model Limitations & Critical Scientific Assumptions

## 1. Executive Summary

SpaceY Intelligence is an evidence-based mission decision-support and launch analytics system. To ensure responsible aerospace and business applications, engineers, data scientists, and mission executives must understand the statistical boundaries, data limitations, and physics constraints inherent in the historical dataset and modeling approach.

---

## 2. Statistical & Dataset Limitations

### 2.1 Sample Size Constraints ($n = 90$)
- **Benchmark Training Sample**: The balanced benchmark dataset used for model training and evaluation consists of 90 historical Falcon 9 launches (2010–2020), containing 60 successful landings and 30 landing failures / expendable flights.
- **Statistical Power**: An $n=90$ dataset limits the statistical power of complex non-linear architectures (e.g., deep neural networks, heavily parameterized gradient boosted ensembles). This explains why regularized linear models (Logistic Regression with $L_2$ penalty) outperform complex ensembles on out-of-sample generalization.
- **Sparse Stratification**: Certain orbit categories (e.g., `ES-L1`, `SO`, `GEO`, `HEO`) contain only 1 to 2 historical flights, meaning individual flight anomalies heavily skew category-level conditional probabilities.

### 2.2 Longitudinal Concept Drift (Block 1 to Block 5)
- **Evolutionary Hardware Upgrades**: SpaceX Falcon 9 underwent radical design iterations between Flight 1 (2010) and Flight 90+ (2020+):
  - *Falcon 9 v1.0 / Block 1*: 9 Merlin 1C engines, square layout, no grid fins, unguided ocean splashdown attempts.
  - *Falcon 9 v1.1 / Block 2-3*: Merlin 1D Octaweb arrangement, first deployable landing legs, initial drone ship tests.
  - *Falcon 9 Block 4*: Titanium grid fins, uprated thrust, high-temperature recovery.
  - *Falcon 9 Block 5*: Inconel bolted octaweb, reusable thermal protection, retractable legs, designed for 10+ flights per booster.
- **The "Learning Curve" Effect**: Early booster landing failures were part of an aggressive physical testing campaign. Predicting modern Block 5 missions using historical aggregate data may underestimate today's near-perfect operational recovery rates (>99%).

### 2.3 Extreme Class Imbalance in Recent Operations
- As uncovered in our audit of the Wikipedia scrape (Flights 195–501, 2023–2024), 313 of 315 missions succeeded, representing a **99.36% success rate**.
- Training machine learning classifiers naively on this recent window causes models to collapse into constant predictors ($\hat{y} = 1$). SpaceY Intelligence resolves this by segregating the balanced development benchmark ($n=90$) from the expanded longitudinal analytical warehouse ($n=482$).

---

## 3. Unobserved Physical Variables & Confounders

The model relies on mission metadata available prior to ignition. Several critical physical factors governing actual recovery dynamics are absent from public records:

| Unobserved Factor | Physical Impact | Impact on Model Calibration |
| :--- | :--- | :--- |
| **Ocean Sea State & Wave Height** | High swell causes drone ship deck pitching and roll, inducing booster tip-over or leg slippage. | Missions flagged as favorable may fail recovery due purely to local maritime weather. |
| **Upper Atmosphere Wind Shear** | High dynamic pressure ($Q_{\text{max}}$) winds alter trajectory fuel margins. | Increased fuel burn during ascent leaves insufficient propellant for boostback/re-entry burns. |
| **Booster Pre-Flight Re-use Count** | Wear on turbopump bearings, thermal barrier coatings, and propellant valves. | Later-generation flight counts (>15 re-flights) carry distinct wear profiles not captured in basic `FlightNumber`. |
| **Telemetry Sensor Status** | Throttle valve hysteresis, helium pressurization leaks, grid fin hydraulic pressure. | Telemetry anomalies during descent cannot be anticipated prior to liftoff. |

---

## 4. Causality vs. Correlation

### 4.1 Landing Legs and Grid Fins
- The presence of landing legs (`Legs = 1`) and grid fins (`GridFins = 1`) exhibits a high positive correlation with landing success ($r > 0.6$).
- **Causal Interpretation Warning**: Fitting landing legs does not physically cause a rocket to land successfully. Rather, SpaceX engineers only attached expensive landing legs on missions where the flight profile, trajectory, and payload mass left sufficient propellant reserve to attempt recovery. Legs act as a proxy for *engineering intent* and *available propellant margin*.

### 4.2 Payload Mass Confounding
- Heavy payloads (e.g., >8,000 kg to GTO) deplete stage 1 propellants during ascent, forcing the booster to fly downrange to an Autonomous Spaceport Drone Ship (ASDS) or fly fully expendable.
- Light payloads (e.g., <4,000 kg to LEO) allow RTLS (Return To Launch Site) landing directly on concrete pads (LZ-1, LZ-2, LZ-4), which has historically achieved higher recovery success than marine drone ship touchdowns.

---

## 5. Guidance for Mission Decision-Makers

1. **Prior Probability Role**: SpaceY Intelligence predictions should serve as an initial probabilistic risk prior during commercial contract negotiations and bid structuring.
2. **Propellant Margin Verification**: Model scores must be coupled with trajectory simulation software (e.g., flight dynamics trajectory simulators) to verify actual $\Delta V$ reserves for three-engine boostback and entry burns.
3. **Marine Asset Scheduling**: Financial break-even recommendations ($P > 23.9\%$) should be cross-checked against seasonal ocean storm forecasts before deploying marine drone ship assets.

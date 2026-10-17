# 💰 SpaceY Intelligence — Commercial Launch Economics & Decision Assumptions

## 1. Commercial Strategic Context

SpaceY operates as an agile, private aerospace enterprise competing for commercial satellite, civil government, and orbital constellation deployment contracts. In modern launch markets, competitor pricing is dominated by SpaceX's reusable Falcon 9 architecture, which advertises standard list prices of approximately **$67.0M** for commercial payloads while maintaining high gross margins due to first-stage booster recovery. Legacy expendable providers (e.g., ULA Atlas V / Vulcan, Arianespace Ariane 6) price missions between **$90M and $150M+**, suffering from single-use hardware write-offs.

To price competitively while guaranteeing positive operating margins, SpaceY must evaluate the **net risk-adjusted cost** of each flight profile. If an orbital mission (such as heavy payload to GTO or high-energy interplanetary trajectories) consumes all booster propellant margins, attempting booster recovery introduces maritime drone ship deployment costs, risk of booster structural failure, and recovery crew mobilization without tangible salvage benefit.

The SpaceY Mission Economics Engine models these trade-offs rigorously, converting probabilistic model outputs ($P_{\text{recovery}}$) into actionable financial guidance.

---

## 2. Core Economic Model & Mathematical Formulation

### 2.1 Baseline Parameters

| Parameter | Symbol | Default Value | Aerospace / Industry Justification |
| :--- | :---: | :---: | :--- |
| **Contract Revenue** | $R$ | **$67.0M** | Competitive market launch fee charged to commercial satellite customer. |
| **Baseline Mission Cost** | $C_{\text{base}}$ | **$55.0M** | Base manufacturing, propellants, range fees, integration, and upper stage cost. |
| **Recovery Ops Cost** | $C_{\text{ops}}$ | **$2.5M** | Autonomous Spaceport Drone Ship (ASDS) tugboat charter, marine crew, radar, recovery tracking. |
| **Booster Asset Value** | $V_{\text{booster}}$ | **$25.0M** | Estimated asset valuation of an intact, reusable first-stage booster (~45-50% of vehicle capital cost). |
| **Refurbishment Cost** | $C_{\text{refurb}}$ | **$5.0M** | Ultrasonic non-destructive inspection, heat-shield restoration, turbopump overhaul, and requalification. |
| **Failure Contingency** | $C_{\text{fail}}$ | **$3.0M** | Marine search, debris tracking, salvage operations, anomaly investigation, and insurance deductible. |
| **Risk Reserve Multiplier** | $\mu_{\text{res}}$ | **5.0%** ($1.05$) | Operational contingency buffer across all expenditure lines. |

---

### 2.2 Cost Functions by Flight Outcome

Let the net hardware salvage benefit be defined as:
$$\Delta V_{\text{net}} = V_{\text{booster}} - C_{\text{refurb}}$$
Under default parameters:
$$\Delta V_{\text{net}} = \$25.0\text{M} - \$5.0\text{M} = \$20.0\text{M}$$

#### Scenario A: Successful Booster Recovery
When the first stage safely lands on a drone ship or landing pad:
$$C_{\text{success}} = \left( C_{\text{base}} + C_{\text{ops}} - \Delta V_{\text{net}} \right) \times (1 + \mu_{\text{res}})$$
$$C_{\text{success}} = (\$55.0\text{M} + \$2.5\text{M} - \$20.0\text{M}) \times 1.05 = \$37.5\text{M} \times 1.05 = \$39.375\text{M}$$

#### Scenario B: Recovery Attempt Failed (Ocean Impact / Anomaly)
When recovery is attempted but the booster fails entry burn, loses aerodynamic control, or suffers hard landing:
$$C_{\text{failure}} = \left( C_{\text{base}} + C_{\text{ops}} + C_{\text{fail}} \right) \times (1 + \mu_{\text{res}})$$
$$C_{\text{failure}} = (\$55.0\text{M} + \$2.5\text{M} + \$3.0\text{M}) \times 1.05 = \$60.5\text{M} \times 1.05 = \$63.525\text{M}$$

#### Scenario C: Deliberate Expendable Mission Baseline (No Recovery Attempted)
When no landing hardware (legs, grid fins) is flown and no marine assets are deployed:
$$C_{\text{expendable}} = C_{\text{base}} \times (1 + \mu_{\text{res}}) = \$55.0\text{M} \times 1.05 = \$57.750\text{M}$$

---

### 2.3 Expected Value & Margin Formulation

Given a machine learning predicted landing probability $P \in [0, 1]$:
$$\mathbb{E}[C] = P \cdot C_{\text{success}} + (1 - P) \cdot C_{\text{failure}}$$
$$\mathbb{E}[\text{Margin}] = R - \mathbb{E}[C]$$
$$\mathbb{E}[\text{Margin \%}] = \frac{\mathbb{E}[\text{Margin}]}{R} \times 100\%$$
$$\text{Expected Savings vs Expendable} = C_{\text{expendable}} - \mathbb{E}[C]$$

---

## 3. Derivation of the Break-Even Recovery Probability ($P^*$)

The commercial break-even point occurs when attempting recovery yields the exact same expected cost as flying an expendable mission:
$$\mathbb{E}[C] = C_{\text{expendable}}$$
$$P^* \cdot C_{\text{success}} + (1 - P^*) \cdot C_{\text{failure}} = C_{\text{expendable}}$$
$$C_{\text{failure}} - P^* \left( C_{\text{failure}} - C_{\text{success}} \right) = C_{\text{expendable}}$$
$$P^* = \frac{C_{\text{failure}} - C_{\text{expendable}}}{C_{\text{failure}} - C_{\text{success}}}$$

Substituting the algebraic expressions:
$$C_{\text{failure}} - C_{\text{expendable}} = \left( C_{\text{ops}} + C_{\text{fail}} \right) \times (1 + \mu_{\text{res}})$$
$$C_{\text{failure}} - C_{\text{success}} = \left( \Delta V_{\text{net}} + C_{\text{fail}} \right) \times (1 + \mu_{\text{res}})$$

Notice the contingency buffer $(1 + \mu_{\text{res}})$ cancels out:
$$P^* = \frac{C_{\text{ops}} + C_{\text{fail}}}{(V_{\text{booster}} - C_{\text{refurb}}) + C_{\text{fail}}}$$

Evaluating with default baseline values:
$$P^* = \frac{\$2.5\text{M} + \$3.0\text{M}}{(\$25.0\text{M} - \$5.0\text{M}) + \$3.0\text{M}} = \frac{\$5.5\text{M}}{\$20.0\text{M} + \$3.0\text{M}} = \frac{\$5.5\text{M}}{\$23.0\text{M}} \approx 0.2391 \quad (23.9\%)$$

### Strategic Implication:
- If the model predicts **$P > 23.9\%$**, the commercial expected value of attempting booster recovery is strictly positive.
- If $P < 23.9\%$, the incremental expenses of recovery vessels and failure investigation outweigh the expected salvage value. Flight planning should strip landing legs and burn propellant for maximum payload insertion performance.

---

## 4. Sensitivity Scenarios

| Landing Confidence $P$ | Expected Cost | Expected Margin ($) | Margin (%) | Savings vs Expendable | Flight Recommendation |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **0.0%** (Certain Loss) | $63.53M | $3.48M | 5.19% | -$5.78M | **EXPENDABLE** |
| **23.9%** ($P^*$ Break-even) | $57.75M | $9.25M | 13.81% | $0.00M | **NEUTRAL THRESHOLD** |
| **50.0%** (Toss-up) | $51.45M | $15.55M | 23.21% | +$6.30M | **RECOVERY FAVORABLE** |
| **75.0%** (High Confidence) | $45.41M | $21.59M | 32.22% | +$12.34M | **RECOVERY HIGHLY ADVANTAGEOUS** |
| **95.0%** (Mature Block 5) | $40.58M | $26.42M | 39.43% | +$17.17M | **RECOVERY STANDARD OPERATING PROFILE** |

---

## 5. Bid Evaluation Policy

The SpaceY Intelligence platform codifies these calculations into executive recommendations:
1. **Aggressive Commercial Bidding ($P \ge 70\%$)**:
   - Offer standard commercial discount ($62M - $67M) to win competitive commercial tenders.
   - Retain healthy gross margins exceeding 30%.
2. **Conservative Strategic Bidding ($25\% \le P < 70\%$)**:
   - Price at $67M - $75M.
   - Allocate marine drone ship assets while hedging with third-party launch risk insurance.
3. **High-Energy / Heavy Lift Missions ($P < 25\%$)**:
   - Offer dedicated expendable flight profile priced between $80M - $95M.
   - Still undercuts legacy expendable competitors ($110M - $150M) while protecting SpaceY from recovery loss penalties.

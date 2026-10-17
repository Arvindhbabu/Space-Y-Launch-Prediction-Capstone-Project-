# Mission Economics — Assumptions and Equations

## Purpose and scope

The Mission Economics module demonstrates how uncertain recovery outcomes can be connected to a simplified expected-cost calculation. It is an educational simulator, not a financial forecast, pricing guide, or aerospace operations recommendation.

**Every default monetary input is an illustrative assumption selected for the application.** The defaults are not verified SpaceX costs, current launch prices, supplier quotations, insurance terms, or audited company financials. Change the inputs to explore how assumptions affect results.

## Configurable inputs

All monetary values are in millions of dollars (USD), unless stated otherwise.

| Input | Default | Meaning in this simulation |
|---|---:|---|
| Contract revenue | 67.0 | Assumed revenue for one hypothetical mission |
| Baseline mission cost | 55.0 | Assumed base cost before recovery-specific adjustments |
| Recovery operations cost | 2.5 | Assumed incremental cost for a recovery attempt |
| Booster asset value | 25.0 | Assumed value assigned to a successfully recovered booster |
| Refurbishment cost | 5.0 | Assumed inspection/refurbishment cost |
| Failure contingency | 3.0 | Assumed additional cost in a failed-recovery scenario |
| Risk reserve | 5% | Assumed contingency multiplier applied to modeled costs |

These inputs are user-adjustable in the application/API. They should be replaced with independently sourced values before the calculator is used for any real business analysis.

## Equations implemented by the simulator

Let:
- (R) be assumed contract revenue.
- (C_b) be baseline mission cost.
- (C_o) be recovery operations cost.
- (V_b) be assumed recovered-booster asset value.
- (C_r) be refurbishment cost.
- (C_f) be failure contingency.
- (mu) be the risk-reserve percentage expressed as a decimal.
- (p) be the recovery probability supplied to the calculator, clipped to the interval ([0,1]).

The risk-reserve multiplier is:

[
m = 1 + mu
]

Net assumed hardware benefit:

[
V_{net} = V_b - C_r
]

Modeled cost in the success scenario:

[
C_s = (C_b + C_o - V_{net})m
]

Modeled cost in the failure scenario:

[
C_f^{*} = (C_b + C_o + C_f)m
]

Modeled expendable baseline:

[
C_e = C_bm
]

Expected modeled cost:

[
E[C] = pC_s + (1-p)C_f^{*}
]

Expected modeled margin and margin percentage:

[
E[M] = R - E[C]
]

[
E[M%] = rac{E[M]}{R}	imes100%
]

Expected savings relative to the simulated expendable baseline:

[
S = C_e - E[C]
]

In this implementation, the reported break-even probability is derived by equating expected recovery cost to the modeled expendable baseline. With positive net recovery benefit:

[
p^* =
rac{C_o + C_f}{(V_b-C_r)+C_f}
]

The code clips the computed threshold to ([0,1]). If the net-benefit denominator is non-positive, it sets the threshold to 1.0. See `src/spacey/economics/calculator.py` for the precise implementation.

## Interpretation guardrails

- The formula simplifies costs into a small number of categories; actual launch economics are much more complex.
- It does not include financing, vehicle-development amortization, payload-specific performance penalties, schedule risk, taxes, detailed insurance, range availability, contract terms, or many other commercial factors.
- A positive expected savings value means only that the supplied assumptions favor one modeled scenario over another.
- A threshold is mathematically conditional on the chosen inputs. It is not a universal recovery success threshold.
- The recovery probability is produced by a small-sample educational classifier and should not be treated as a validated operational probability.
- Outputs must not be used as real-world bid, procurement, launch, or recovery instructions.

## Implementation and tests

The calculations are implemented in `src/spacey/economics/calculator.py`. Regression tests for standard inputs, break-even behavior, probability clipping, and sensitivity calculations are in `tests/test_economics.py`.

"""
SpaceY Intelligence - Launch Economics & Decision Support Engine
Computes expected costs, margins, break-even probabilities, and risk sensitivities
under reusable vs expendable commercial bidding scenarios.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd


@dataclass
class MissionEconomicParameters:
    """Configurable financial and operational assumptions for a commercial launch bid."""
    contract_revenue_m: float = 67.0         # Expected launch contract price charged to customer ($M)
    baseline_mission_cost_m: float = 55.0     # Baseline expendable rocket manufacturing & launch cost ($M)
    recovery_ops_cost_m: float = 2.5          # Incremental operational cost to attempt recovery (drone ship, marine crew) ($M)
    booster_asset_value_m: float = 25.0       # Net asset value of recovered first-stage booster ($M)
    refurbishment_cost_m: float = 5.0         # Cost to inspect, refurbish, and requalify recovered booster ($M)
    failure_contingency_m: float = 3.0        # Unsuccessful landing salvage, investigation, or ocean loss contingency ($M)
    risk_reserve_pct: float = 5.0             # General operational contingency buffer (%)


@dataclass
class EconomicEvaluationResult:
    """Encapsulates detailed financial calculations and decision metrics."""
    expected_cost_m: float
    expected_margin_m: float
    expected_margin_pct: float
    cost_if_success_m: float
    margin_if_success_m: float
    cost_if_failure_m: float
    margin_if_failure_m: float
    expendable_cost_m: float
    expendable_margin_m: float
    expected_savings_vs_expendable_m: float
    break_even_probability: float
    recommendation: str
    risk_summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "expected_cost_m": self.expected_cost_m,
            "expected_margin_m": self.expected_margin_m,
            "expected_margin_pct": self.expected_margin_pct,
            "cost_if_success_m": self.cost_if_success_m,
            "margin_if_success_m": self.margin_if_success_m,
            "cost_if_failure_m": self.cost_if_failure_m,
            "margin_if_failure_m": self.margin_if_failure_m,
            "expendable_cost_m": self.expendable_cost_m,
            "expendable_margin_m": self.expendable_margin_m,
            "expected_savings_vs_expendable_m": self.expected_savings_vs_expendable_m,
            "break_even_probability": self.break_even_probability,
            "recommendation": self.recommendation,
            "risk_summary": self.risk_summary,
        }


def evaluate_launch_economics(
    p_recovery: float,
    params: Optional[MissionEconomicParameters] = None,
) -> EconomicEvaluationResult:
    """
    Evaluates expected cost and commercial margin under recovery uncertainty.
    p_recovery: Predicted first-stage recovery score (0.0 to 1.0).
    """
    if params is None:
        params = MissionEconomicParameters()

    p = float(np.clip(p_recovery, 0.0, 1.0))
    reserve_mult = 1.0 + (params.risk_reserve_pct / 100.0)

    # Net economic benefit of recovered hardware
    net_recovery_benefit = params.booster_asset_value_m - params.refurbishment_cost_m

    # Cost scenario A: Successful recovery
    # Base cost + recovery marine ops - net value of recovered hardware
    cost_success = (params.baseline_mission_cost_m + params.recovery_ops_cost_m - net_recovery_benefit) * reserve_mult
    margin_success = params.contract_revenue_m - cost_success

    # Cost scenario B: Unsuccessful recovery / crash / loss
    # Base cost + recovery marine ops + ocean loss contingency
    cost_failure = (params.baseline_mission_cost_m + params.recovery_ops_cost_m + params.failure_contingency_m) * reserve_mult
    margin_failure = params.contract_revenue_m - cost_failure

    # Expected value (Weighted by recovery probability)
    expected_cost = (p * cost_success) + ((1.0 - p) * cost_failure)
    expected_margin = params.contract_revenue_m - expected_cost
    expected_margin_pct = (expected_margin / params.contract_revenue_m) * 100.0 if params.contract_revenue_m > 0 else 0.0

    # Benchmark: Expendable launch baseline (no recovery attempted)
    cost_expendable = params.baseline_mission_cost_m * reserve_mult
    margin_expendable = params.contract_revenue_m - cost_expendable
    expected_savings = cost_expendable - expected_cost

    # Mathematical Break-Even Recovery Probability
    # Break-even where Expected Cost == Expendable Cost
    # Cost_Failure - P * (Cost_Failure - Cost_Success) = Cost_Expendable
    delta_total_benefit = (net_recovery_benefit + params.failure_contingency_m) * reserve_mult
    incremental_risk = (params.recovery_ops_cost_m + params.failure_contingency_m) * reserve_mult

    if delta_total_benefit > 0:
        p_breakeven = incremental_risk / delta_total_benefit
        p_breakeven = float(np.clip(p_breakeven, 0.0, 1.0))
    else:
        p_breakeven = 1.0

    # Business Recommendation
    if p >= p_breakeven:
        recommendation = (
            f"RECOVERY ECONOMICALLY ADVANTAGEOUS: Predicted recovery probability ({p*100:.1f}%) "
            f"exceeds the commercial break-even threshold ({p_breakeven*100:.1f}%). "
            f"Expected cost savings versus expendable launch: ${expected_savings:+.2f}M."
        )
    else:
        recommendation = (
            f"EXPENDABLE FLIGHT PREFERRED: Predicted recovery probability ({p*100:.1f}%) "
            f"is below the break-even threshold ({p_breakeven*100:.1f}%). "
            f"Attempting recovery yields a negative expected return of ${expected_savings:+.2f}M."
        )

    risk_summary = (
        f"Worst-case downside (crash): ${cost_failure:.2f}M (Margin: ${margin_failure:+.2f}M). "
        f"Best-case upside (full recovery): ${cost_success:.2f}M (Margin: ${margin_success:+.2f}M)."
    )

    return EconomicEvaluationResult(
        expected_cost_m=round(expected_cost, 2),
        expected_margin_m=round(expected_margin, 2),
        expected_margin_pct=round(expected_margin_pct, 1),
        cost_if_success_m=round(cost_success, 2),
        margin_if_success_m=round(margin_success, 2),
        cost_if_failure_m=round(cost_failure, 2),
        margin_if_failure_m=round(margin_failure, 2),
        expendable_cost_m=round(cost_expendable, 2),
        expendable_margin_m=round(margin_expendable, 2),
        expected_savings_vs_expendable_m=round(expected_savings, 2),
        break_even_probability=round(p_breakeven, 4),
        recommendation=recommendation,
        risk_summary=risk_summary,
    )


def compute_probability_sensitivity_curve(
    params: Optional[MissionEconomicParameters] = None,
    step: float = 0.05,
) -> pd.DataFrame:
    """
    Computes expected costs and margins across full probability spectrum [0.0 to 1.0].
    """
    if params is None:
        params = MissionEconomicParameters()

    probs = np.arange(0.0, 1.001, step)
    records = []
    for p in probs:
        res = evaluate_launch_economics(p, params)
        records.append({
            "Recovery_Probability": round(float(p), 2),
            "Expected_Cost_M": res.expected_cost_m,
            "Expected_Margin_M": res.expected_margin_m,
            "Expected_Savings_M": res.expected_savings_vs_expendable_m,
            "Is_Profitable": res.expected_margin_m > 0,
        })
    return pd.DataFrame(records)

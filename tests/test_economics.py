"""
Unit Tests for Mission Economics & Commercial Decision-Support
"""

import pytest
import numpy as np
from spacey.economics.calculator import (
    MissionEconomicParameters,
    evaluate_launch_economics,
    compute_probability_sensitivity_curve,
)


def test_economics_calculation_standard():
    params = MissionEconomicParameters(
        contract_revenue_m=67.0,
        baseline_mission_cost_m=55.0,
        recovery_ops_cost_m=2.5,
        booster_asset_value_m=25.0,
        refurbishment_cost_m=5.0,
        failure_contingency_m=3.0,
        risk_reserve_pct=0.0,
    )

    # If recovery probability is 1.0 (certain success)
    res_1 = evaluate_launch_economics(1.0, params)
    # Cost = Base (55) + Ops (2.5) - (Asset (25) - Refurb (5)) = 57.5 - 20 = 37.5
    assert res_1.expected_cost_m == 37.5
    assert res_1.expected_margin_m == 67.0 - 37.5
    assert res_1.cost_if_success_m == 37.5

    # If recovery probability is 0.0 (certain failure)
    res_0 = evaluate_launch_economics(0.0, params)
    # Cost = Base (55) + Ops (2.5) + Contingency (3.0) = 60.5
    assert res_0.expected_cost_m == 60.5
    assert res_0.expected_margin_m == 67.0 - 60.5
    assert res_0.cost_if_failure_m == 60.5


def test_economics_breakeven_probability():
    params = MissionEconomicParameters(
        contract_revenue_m=67.0,
        baseline_mission_cost_m=55.0,
        recovery_ops_cost_m=2.5,
        booster_asset_value_m=25.0,
        refurbishment_cost_m=5.0,
        failure_contingency_m=3.0,
        risk_reserve_pct=0.0,
    )
    res = evaluate_launch_economics(0.5, params)
    p_star = res.break_even_probability
    assert 0.0 <= p_star <= 1.0

    # At break-even probability, Expected Cost must equal Expendable Cost ($55.0M)
    res_be = evaluate_launch_economics(p_star, params)
    assert abs(res_be.expected_cost_m - 55.0) < 0.1


def test_probability_boundaries_and_clipping():
    params = MissionEconomicParameters()
    # Test out-of-bound probabilities are clipped safely
    res_high = evaluate_launch_economics(1.5, params)
    res_low = evaluate_launch_economics(-0.5, params)

    assert res_high.expected_cost_m == evaluate_launch_economics(1.0, params).expected_cost_m
    assert res_low.expected_cost_m == evaluate_launch_economics(0.0, params).expected_cost_m


def test_sensitivity_curve():
    curve = compute_probability_sensitivity_curve()
    assert len(curve) == 21  # 0.0 to 1.0 in 0.05 steps
    # Margin should strictly increase as recovery probability increases
    margins = curve["Expected_Margin_M"].tolist()
    assert margins[-1] > margins[0]

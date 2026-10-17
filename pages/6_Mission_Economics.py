"""
SpaceY Intelligence - Page 6: Mission Economics
Commercial launch decision-support, expected-cost analysis, margin calculator, and break-even sensitivity.
"""

import sys
from pathlib import Path

# Add src to sys.path
root_dir = Path(__file__).resolve().parent.parent
src_dir = root_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import streamlit as st
import pandas as pd
from spacey.ui.theme import (
    apply_spacey_theme,
    render_page_header,
    render_section_header,
    render_callout,
    clean_html,
)
from spacey.ui.charts import plot_economics_sensitivity
from spacey.economics.calculator import (
    MissionEconomicParameters,
    evaluate_launch_economics,
    compute_probability_sensitivity_curve,
)

st.set_page_config(page_title="Mission Economics | SpaceY Intelligence", layout="wide")
apply_spacey_theme()

render_page_header(
    title="Mission Economics & Decision Support",
    subtitle="Evaluate commercial launch bidding strategy, expected contribution margins, and break-even recovery probability thresholds.",
    badge_text="COMMERCIAL STRATEGY",
    icon="dollar",
    variant="amber",
)

render_callout(
    "<strong>Commercial Scenario Context</strong>: In commercial launch bidding against competitors, first-stage recovery provides significant asset reusability savings. However, recovery incurs marine operations and propellant reserves. This module computes the expected financial return under recovery probability uncertainty.",
    variant="blue",
)

st.markdown("---")

# Sidebar Financial Assumptions Form
st.sidebar.markdown("""
<div style="font-weight: 700; color: #0F172A; font-size: 1.05rem; margin-bottom: 12px;">
    Financial Assumptions ($M USD)
</div>
""", unsafe_allow_html=True)

rev = st.sidebar.number_input("Contract Revenue ($M)", min_value=10.0, max_value=200.0, value=67.0, step=1.0)
base_cost = st.sidebar.number_input("Baseline Expendable Build Cost ($M)", min_value=10.0, max_value=150.0, value=55.0, step=1.0)
recov_ops = st.sidebar.number_input("Recovery Ops Cost ($M)", min_value=0.5, max_value=20.0, value=2.5, step=0.5)
booster_val = st.sidebar.number_input("Booster Residual Asset Value ($M)", min_value=5.0, max_value=60.0, value=25.0, step=1.0)
refurb = st.sidebar.number_input("Refurbishment & Requalification ($M)", min_value=1.0, max_value=30.0, value=5.0, step=0.5)
contingency = st.sidebar.number_input("Crash / Loss Contingency ($M)", min_value=0.0, max_value=20.0, value=3.0, step=0.5)
reserve = st.sidebar.slider("General Risk Reserve Buffer (%)", min_value=0.0, max_value=25.0, value=5.0, step=1.0)

econ_params = MissionEconomicParameters(
    contract_revenue_m=rev,
    baseline_mission_cost_m=base_cost,
    recovery_ops_cost_m=recov_ops,
    booster_asset_value_m=booster_val,
    refurbishment_cost_m=refurb,
    failure_contingency_m=contingency,
    risk_reserve_pct=reserve,
)

# Recovery Probability Slider
render_section_header(
    title="Scenario Recovery Probability Assessment",
    subtitle="Adjust estimated first-stage recovery likelihood to observe expected financial return.",
    icon="sliders",
    variant="amber",
)
p_input = st.slider(
    "Estimated First-Stage Recovery Probability",
    min_value=0.0,
    max_value=1.0,
    value=0.75,
    step=0.01,
    format="%.2f",
)

# Run calculation
res = evaluate_launch_economics(p_input, params=econ_params)

# Metric KPI Row
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    st.metric("Expected Mission Cost", f"${res.expected_cost_m:.2f}M")
with col_kpi2:
    st.metric("Expected Contribution Margin", f"${res.expected_margin_m:.2f}M", f"{res.expected_margin_pct:.1f}% Margin")
with col_kpi3:
    st.metric("Expected Savings vs Expendable", f"${res.expected_savings_vs_expendable_m:+.2f}M")
with col_kpi4:
    st.metric("Break-Even Recovery Probability", f"{res.break_even_probability*100:.1f}%")

st.markdown("---")

# Recommendation Banner
if p_input >= res.break_even_probability:
    render_callout(f"<strong>STRATEGIC COMMERCIAL RECOMMENDATION</strong>: {res.recommendation}", variant="emerald")
else:
    render_callout(f"<strong>STRATEGIC COMMERCIAL RECOMMENDATION</strong>: {res.recommendation}", variant="amber")

st.markdown("---")

col_sens, col_matrix = st.columns([1.2, 0.8])

with col_sens:
    render_section_header(
        title="Recovery Probability Sensitivity Curve",
        subtitle="Expected margins and costs plotted across all possible landing probabilities.",
        icon="chart",
        variant="emerald",
    )
    curve_df = compute_probability_sensitivity_curve(params=econ_params)
    st.plotly_chart(
        plot_economics_sensitivity(curve_df, breakeven_p=res.break_even_probability),
        use_container_width=True,
    )

with col_matrix:
    render_section_header(
        title="Commercial Flight Alternatives Matrix",
        subtitle="Comparison of expected, best-case, worst-case, and expendable profiles.",
        icon="layers",
        variant="blue",
    )
    matrix_df = pd.DataFrame({
        "Commercial Metric": [
            "Mission Profile",
            "Hardware Outcome",
            "Total Scenario Cost ($M)",
            "Contribution Margin ($M)",
            "Margin Percentage (%)",
        ],
        "Attempt Recovery (Expected)": [
            f"Recovery Attempted (P={p_input*100:.0f}%)",
            "Probabilistic Expectation",
            f"${res.expected_cost_m:.2f}M",
            f"${res.expected_margin_m:+.2f}M",
            f"{res.expected_margin_pct:.1f}%",
        ],
        "Best Case (Recovery Success)": [
            "Successful Recovery",
            "Booster Retained for Reuse",
            f"${res.cost_if_success_m:.2f}M",
            f"${res.margin_if_success_m:+.2f}M",
            f"{(res.margin_if_success_m/rev)*100:.1f}%",
        ],
        "Worst Case (Recovery Loss)": [
            "Attempt Failed",
            "Hardware Lost at Sea",
            f"${res.cost_if_failure_m:.2f}M",
            f"${res.margin_if_failure_m:+.2f}M",
            f"{(res.margin_if_failure_m/rev)*100:.1f}%",
        ],
        "Expendable Baseline": [
            "Deliberately Expended",
            "No Recovery Attempted",
            f"${res.expendable_cost_m:.2f}M",
            f"${res.expendable_margin_m:+.2f}M",
            f"{(res.expendable_margin_m/rev)*100:.1f}%",
        ],
    })
    st.dataframe(matrix_df, use_container_width=True, hide_index=True)

st.markdown("---")
render_section_header(
    title="Mathematical Formulation & Financial Equations",
    subtitle="Closed-form expressions for expected cost and analytical break-even threshold.",
    icon="activity",
    variant="purple",
)
st.latex(r"""
\mathbb{E}[\text{Cost}] = P \cdot \big(C_{\text{base}} + C_{\text{ops}} - (V_{\text{booster}} - C_{\text{refurb}})\big) + (1 - P) \cdot \big(C_{\text{base}} + C_{\text{ops}} + C_{\text{contingency}}\big)
""")
st.latex(r"""
P^* = \frac{C_{\text{ops}} + C_{\text{contingency}}}{(V_{\text{booster}} - C_{\text{refurb}}) + C_{\text{contingency}}}
""")
st.caption("Disclaimer: Financial figures are illustrative commercial scenario models and do not represent proprietary SpaceX or customer contracts.")

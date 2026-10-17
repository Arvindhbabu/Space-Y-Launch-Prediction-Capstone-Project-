"""
SpaceY Intelligence - Page 4: Predictive Lab
Validated scenario prediction, calibrated recovery scoring, local attribution, and scenario comparisons.
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
import numpy as np

from spacey.ui.theme import (
    apply_spacey_theme,
    render_page_header,
    render_section_header,
    clean_html,
)
from spacey.ui.charts import plot_scenario_attribution
from spacey.data.feature_schema import LaunchScenarioInput, STANDARDIZED_SITES, VALID_ORBITS
from spacey.data.loader import load_and_prepare_benchmark_data
from spacey.models.registry import load_registered_model
from spacey.models.explainability import explain_single_scenario

st.set_page_config(page_title="Predictive Lab | SpaceY Intelligence", layout="wide")
apply_spacey_theme()

render_page_header(
    title="Predictive Scenario Lab",
    subtitle="Simulate proposed launch scenarios and compute calibrated first-stage recovery likelihoods with local feature attribution.",
    badge_text="INFERENCE & DECISION ENGINE",
    icon="flask",
    variant="purple",
)

pipeline, metadata = load_registered_model()
ref_df, _ = load_and_prepare_benchmark_data()

if pipeline is None:
    st.error("No active model pipeline found in the registry. Run 'python scripts/train_model.py' to generate artifacts.")
    st.stop()

# Mode Selection: Single Scenario vs Side-by-Side Comparison
mode = st.radio("Simulation Mode", ["Single Scenario Evaluation", "Side-by-Side Scenario Comparison"], horizontal=True)

st.markdown("---")


def render_scenario_input_form(prefix: str = "A", default_mass: float = 5000.0, default_flights: int = 1):
    """Renders a validated scenario input form."""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        mass = st.slider(f"Payload Mass (kg) [{prefix}]", min_value=100.0, max_value=20000.0, value=default_mass, step=250.0)
        site = st.selectbox(f"Launch Site [{prefix}]", STANDARDIZED_SITES, key=f"site_{prefix}")
    with col2:
        orbit = st.selectbox(f"Target Orbit [{prefix}]", VALID_ORBITS, index=0, key=f"orbit_{prefix}")
        flights = st.number_input(f"Booster Flight Count [{prefix}]", min_value=1, max_value=25, value=default_flights, key=f"flights_{prefix}")
    with col3:
        block = st.slider(f"Booster Block Version [{prefix}]", min_value=1, max_value=5, value=5, key=f"block_{prefix}")
        reused = st.selectbox(f"Flight-Proven (Reused) [{prefix}]", [("Yes (Reused)", 1), ("No (Maiden)", 0)], format_func=lambda x: x[0], key=f"reused_{prefix}")[1]
    with col4:
        grid_fins = st.selectbox(f"Equipped with Grid Fins [{prefix}]", [("Yes (Equipped)", 1), ("No", 0)], format_func=lambda x: x[0], key=f"gf_{prefix}")[1]
        legs = st.selectbox(f"Equipped with Landing Legs [{prefix}]", [("Yes (Equipped)", 1), ("No", 0)], format_func=lambda x: x[0], key=f"legs_{prefix}")[1]

    scenario = LaunchScenarioInput(
        payload_mass=mass,
        launch_site=site,
        orbit=orbit,
        flights=flights,
        grid_fins=grid_fins,
        legs=legs,
        block=block,
        reused=reused,
    )
    return scenario


if mode == "Single Scenario Evaluation":
    render_section_header(
        title="Proposed Launch Profile Inputs",
        subtitle="Configure physical mission parameters for forward probability simulation.",
        icon="sliders",
        variant="blue",
    )
    scenario_a = render_scenario_input_form(prefix="A", default_mass=5000.0, default_flights=2)

    scenario_df = pd.DataFrame([scenario_a.to_feature_dict()])
    scenario_df["FlightNumber"] = 90

    # Model inference
    proba = float(pipeline.predict_proba(scenario_df)[0][1])
    threshold = metadata.get("selected_decision_threshold", 0.50)
    pred_class = 1 if proba >= threshold else 0

    st.markdown("---")
    render_section_header(
        title="Model Assessment & Telemetry Output",
        subtitle="Calibrated inference score, decision threshold margin, and predicted landing outcome.",
        icon="target",
        variant="purple",
    )

    col_res1, col_res2, col_res3, col_res4 = st.columns(4)
    with col_res1:
        if pred_class == 1:
            card_html = """
            <div class="telemetry-card" style="border-left:4px solid #059669;">
            <div class="telemetry-title" style="color:#059669;">Predicted Classification</div>
            <div style="font-size:1.35rem;font-weight:800;color:#059669;">SUCCESSFUL RECOVERY</div>
            <div style="font-size:0.8rem;color:#64748B;">Class 1 (Landing Zone / ASDS)</div>
            </div>
            """
            st.markdown(clean_html(card_html), unsafe_allow_html=True)
        else:
            card_html = """
            <div class="telemetry-card" style="border-left:4px solid #DC2626;">
            <div class="telemetry-title" style="color:#DC2626;">Predicted Classification</div>
            <div style="font-size:1.35rem;font-weight:800;color:#DC2626;">RECOVERY AT RISK</div>
            <div style="font-size:0.8rem;color:#64748B;">Class 0 (Expendable / Ocean Loss)</div>
            </div>
            """
            st.markdown(clean_html(card_html), unsafe_allow_html=True)

    with col_res2:
        st.metric("Recovery Likelihood", f"{proba * 100:.1f}%")
    with col_res3:
        st.metric("Decision Cutoff", f"{threshold * 100:.0f}%")
    with col_res4:
        delta_p = (proba - threshold) * 100
        st.metric("Margin vs Cutoff", f"{delta_p:+.1f}%")

    st.markdown("---")
    col_attr, col_limits = st.columns([1.2, 0.8])

    with col_attr:
        render_section_header(
            title="Local Feature Attribution",
            subtitle="Feature-level shift in predicted recovery likelihood vs reference baseline.",
            icon="activity",
            variant="cyan",
        )
        explanations = explain_single_scenario(pipeline, scenario_df, ref_df)
        st.plotly_chart(plot_scenario_attribution(explanations), width="stretch")

    with col_limits:
        render_section_header(
            title="Operational Limitations & Evidence Notes",
            subtitle="Caveats regarding causal interpretation and unobserved physical variables.",
            icon="alert",
            variant="amber",
        )
        lim_html = f"""
        <div class="telemetry-card">
        <p><strong>Active Pipeline</strong>: <code>{metadata.get('model_name', 'Trained Classifier')}</code></p>
        <p><strong>Holdout Evaluation</strong>: ROC-AUC: <b>{metadata.get('evaluation_metrics', {}).get('roc_auc', 0.0):.3f}</b>, F1: <b>{metadata.get('evaluation_metrics', {}).get('f1_score', 0.0):.3f}</b>.</p>
        <p><strong>Causality Notice</strong>: Feature attribution reflects statistical associations observed across historical test flights. It does not replace structural engineering or computational fluid dynamics (CFD) simulations.</p>
        <p style="margin-bottom:0;"><strong>Environmental Variables</strong>: Unmodeled physical factors (e.g. upper-atmosphere shear winds, sea-state swell height on recovery barge, thermal tile degradation) can decisively affect actual landings.</p>
        </div>
        """
        st.markdown(clean_html(lim_html), unsafe_allow_html=True)

else:
    # Side-by-Side Comparison
    render_section_header(
        title="Side-by-Side Scenario Simulation",
        subtitle="Compare predicted recovery likelihoods between two alternative mission profiles.",
        icon="sliders",
        variant="blue",
    )
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown(clean_html('<div style="font-weight:700;color:#2563EB;font-size:1.05rem;margin-bottom:12px;">Scenario Baseline (A)</div>'), unsafe_allow_html=True)
        scen_a = render_scenario_input_form(prefix="A", default_mass=3500.0, default_flights=1)
        df_a = pd.DataFrame([scen_a.to_feature_dict()])
        df_a["FlightNumber"] = 90
        proba_a = float(pipeline.predict_proba(df_a)[0][1])

    with col_right:
        st.markdown(clean_html('<div style="font-weight:700;color:#059669;font-size:1.05rem;margin-bottom:12px;">Proposed Scenario (B)</div>'), unsafe_allow_html=True)
        scen_b = render_scenario_input_form(prefix="B", default_mass=7500.0, default_flights=3)
        df_b = pd.DataFrame([scen_b.to_feature_dict()])
        df_b["FlightNumber"] = 90
        proba_b = float(pipeline.predict_proba(df_b)[0][1])

    st.markdown("---")
    render_section_header(
        title="Scenario Comparison Telemetry",
        subtitle="Side-by-side probability delta and input parameter matrix.",
        icon="chart",
        variant="purple",
    )

    col_cmp1, col_cmp2, col_cmp3 = st.columns(3)
    with col_cmp1:
        st.metric("Scenario A Likelihood", f"{proba_a * 100:.1f}%")
    with col_cmp2:
        st.metric("Scenario B Likelihood", f"{proba_b * 100:.1f}%")
    with col_cmp3:
        delta_ab = (proba_b - proba_a) * 100
        st.metric("Delta Likelihood (B vs A)", f"{delta_ab:+.1f}%")

    st.markdown(clean_html("<div style='margin-top:16px;margin-bottom:8px;font-weight:700;color:#0F172A;'>Direct Parameter Comparison Matrix</div>"), unsafe_allow_html=True)
    comparison_table = pd.DataFrame({
        "Parameter": ["Payload Mass (kg)", "Launch Site", "Orbit", "Booster Flights", "Booster Block", "Reused", "Grid Fins", "Landing Legs", "Recovery Probability"],
        "Scenario A": [f"{scen_a.payload_mass:,.0f}", scen_a.launch_site, scen_a.orbit, scen_a.flights, f"Block {scen_a.block}", "Yes" if scen_a.reused else "No", "Yes" if scen_a.grid_fins else "No", "Yes" if scen_a.legs else "No", f"{proba_a*100:.1f}%"],
        "Scenario B": [f"{scen_b.payload_mass:,.0f}", scen_b.launch_site, scen_b.orbit, scen_b.flights, f"Block {scen_b.block}", "Yes" if scen_b.reused else "No", "Yes" if scen_b.grid_fins else "No", "Yes" if scen_b.legs else "No", f"{proba_b*100:.1f}%"],
    })
    st.dataframe(comparison_table, width="stretch", hide_index=True)

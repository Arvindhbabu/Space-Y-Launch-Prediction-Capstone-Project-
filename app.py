"""
SpaceY Intelligence - Mission Analytics & Decision-Support Platform
Main Streamlit Application Entry Point.
"""

import sys
from pathlib import Path

# Add src to sys.path
root_dir = Path(__file__).resolve().parent
src_dir = root_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import streamlit as st
from spacey.ui.theme import (
    apply_spacey_theme,
    render_page_header,
    render_section_header,
    render_callout,
    get_gradient_icon_html,
    clean_html,
)
from spacey.data.loader import load_and_prepare_unified_data
from spacey.models.registry import load_registered_model

st.set_page_config(
    page_title="SpaceY Intelligence | Mission Decision-Support",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_spacey_theme()

render_page_header(
    title="SpaceY Intelligence Platform",
    subtitle="Evidence-driven launch analytics, booster recovery prediction, and commercial mission decision-support.",
    badge_text="MISSION CONTROL SUITE 1.0",
    icon="rocket",
    variant="blue",
)

# System Status Bar
col_status1, col_status2, col_status3, col_status4 = st.columns(4)

with st.spinner("Connecting to telemetry & registry data..."):
    df, report = load_and_prepare_unified_data()
    pipeline, metadata = load_registered_model()

with col_status1:
    st.metric("Total Launches", f"{len(df)} Flights")
with col_status2:
    overall_sr = (df["Class"].mean() * 100) if not df.empty else 0.0
    st.metric("Recovery Rate", f"{overall_sr:.1f}%")
with col_status3:
    model_name = metadata.get("model_name", "Uncalibrated Baseline") if metadata else "Not Deployed"
    st.metric("Production Model", model_name.replace("_", " "))
with col_status4:
    holdout_auc = metadata.get("evaluation_metrics", {}).get("roc_auc", 0.0) if metadata else 0.0
    st.metric("Holdout ROC-AUC", f"{holdout_auc:.3f}")

st.markdown("---")

# Platform Architecture Overview
col_left, col_right = st.columns([1.2, 0.8])

with col_left:
    render_section_header(
        title="Executive Mission Briefing",
        subtitle="Foundations and core problem formulation for commercial launch decision-making.",
        icon="target",
        variant="blue",
    )

    st.markdown("""
    **SpaceY Intelligence** transforms an academic Falcon 9 landing prediction capstone into an applied 
    data science platform for commercial launch decision-makers.

    #### Core Analytical Objectives:
    1. **Historical Determinants**: Which technical and orbital factors govern first-stage recovery success?
    2. **Dimensional Variance**: How do recovery rates shift across launch complexes, orbital inclinations, payload masses, and fleet iterations?
    3. **Defensible Modeling**: Which classification algorithm demonstrates the highest out-of-sample generalization without target leakage?
    4. **Uncertainty & Attribution**: How reliable is a predicted probability for a proposed mission profile, and what features drive the score?
    5. **Commercial Economics**: How does recovery probability impact expected mission cost, contribution margins, and commercial bidding strategy?
    6. **Decision Boundaries**: What operational assumptions, sea-state risks, and sample limitations must leadership consider before acting?
    """)

    render_callout(
        "<strong>Operational Advisory Notice</strong>: This platform is an analytics and decision-support system designed for preliminary commercial evaluation. It is not an onboard aerospace flight-control or safety-of-flight system.",
        variant="blue",
    )

with col_right:
    render_section_header(
        title="Platform Navigation",
        subtitle="Select a specialized analytical module from the sidebar.",
        icon="compass",
        variant="cyan",
    )

    nav_items = [
        ("1. Executive Overview", "pages/1_Executive_Overview.py", "High-level KPIs, macro success trajectories, and operational insights.", "chart", "blue"),
        ("2. Launch Explorer", "pages/2_Launch_Explorer.py", "Interactive multi-filter slice-and-dice data table and payload distributions.", "database", "cyan"),
        ("3. Geospatial Intelligence", "pages/3_Geospatial_Intelligence.py", "Interactive Folium map with verified launch complex coordinates.", "globe", "emerald"),
        ("4. Predictive Lab", "pages/4_Predictive_Lab.py", "Scenario input form, calibrated recovery prediction, and attribution.", "flask", "purple"),
        ("5. Model Intelligence", "pages/5_Model_Intelligence.py", "7-model benchmarking, ROC curves, calibration, and feature importances.", "cpu", "blue"),
        ("6. Mission Economics", "pages/6_Mission_Economics.py", "Commercial bidding calculator, break-even probability, and sensitivity curves.", "dollar", "amber"),
        ("7. Data Quality & Ops", "pages/7_Data_Quality.py", "Automated schema auditing, missing data reports, and data provenance.", "shield", "emerald"),
        ("8. Technical Documentation", "pages/8_Technical_Documentation.py", "Mathematical methodology, data dictionary, model card, and interview guide.", "book", "slate"),
    ]

    for title, path, desc, icon, variant in nav_items:
        icon_html = get_gradient_icon_html(icon_name=icon, size=28, variant=variant)
        card_html = f"""
        <div class="telemetry-card" style="padding:12px 16px;margin-bottom:10px;display:flex;align-items:center;">
        {icon_html}
        <div>
        <div style="font-weight:700;color:#0F172A;font-size:0.95rem;">{title}</div>
        <div style="font-size:0.82rem;color:#64748B;">{desc}</div>
        </div>
        </div>
        """
        st.markdown(clean_html(card_html), unsafe_allow_html=True)

st.markdown("---")
render_callout(
    "Use the sidebar navigation to explore modules, or start with <strong>1_Executive_Overview</strong>.",
    variant="blue",
)

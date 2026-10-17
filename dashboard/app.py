"""
SpaceY Intelligence - Legacy Dashboard Compatibility Entry Point
Maintains backward compatibility with 'streamlit run dashboard/app.py'
while utilizing the new validated pipeline, real coordinates, and modular architecture.
"""

import sys
import os
from pathlib import Path

# Add src to sys.path
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

from spacey.ui.theme import (
    apply_spacey_theme,
    render_page_header,
    render_section_header,
    render_callout,
    clean_html,
)
from spacey.config import LAUNCH_SITES, VALID_ORBITS
from spacey.data.loader import load_and_prepare_unified_data
from spacey.models.registry import load_registered_model

st.set_page_config(page_title="SpaceY Launch Dashboard", layout="wide")
apply_spacey_theme()

render_page_header(
    title="SpaceY Launch Dashboard (Modernized)",
    subtitle="Direct interactive predictor with validated feature schema and geodetic launch complex mapping.",
    badge_text="COMPATIBILITY INTERFACE",
    icon="rocket",
    variant="blue",
)

render_callout(
    "<strong>Platform Notice</strong>: This repository has been expanded into the full <strong>SpaceY Intelligence Multipage Platform</strong>. You can explore all 8 specialized analytical, economic, and geospatial modules by running <code>streamlit run app.py</code> from the root directory.",
    variant="blue",
)

# Load real registered assets and data
pipeline, metadata = load_registered_model()
df, _ = load_and_prepare_unified_data()

# Sidebar inputs
st.sidebar.markdown("""
<div style="font-weight: 700; color: #0F172A; font-size: 1.05rem; margin-bottom: 12px;">
    Launch Prediction Input
</div>
""", unsafe_allow_html=True)

mass = st.sidebar.slider("Payload Mass (kg)", 100, 20000, 5000, step=250)
site = st.sidebar.selectbox("Launch Site", list(LAUNCH_SITES.keys()))
orbit = st.sidebar.selectbox("Orbit", VALID_ORBITS)
flights = st.sidebar.number_input("Booster Flights", min_value=1, max_value=25, value=2)
block = st.sidebar.slider("Booster Block", 1, 5, 5)
reused = st.sidebar.selectbox("Flight-Proven Reused", [1, 0], format_func=lambda x: "Yes" if x == 1 else "No")
grid_fins = st.sidebar.selectbox("Grid Fins", [1, 0], format_func=lambda x: "Yes" if x == 1 else "No")
legs = st.sidebar.selectbox("Landing Legs", [1, 0], format_func=lambda x: "Yes" if x == 1 else "No")

# Construct input dataframe matching model feature schema
input_df = pd.DataFrame([{
    "PayloadMass": float(mass),
    "LaunchSite": site,
    "Orbit": orbit,
    "Flights": int(flights),
    "GridFins": int(grid_fins),
    "Legs": int(legs),
    "Block": int(block),
    "Reused": int(reused),
    "FlightNumber": 90,
}])

if pipeline is not None:
    proba = float(pipeline.predict_proba(input_df)[0][1])
    threshold = metadata.get("selected_decision_threshold", 0.50) if metadata else 0.50
    prediction = 1 if proba >= threshold else 0

    render_section_header(
        title="Launch Prediction Result",
        subtitle="Forward likelihood computation from registered production pipeline.",
        icon="target",
        variant="purple",
    )

    if prediction == 1:
        render_callout(f"<strong>BOOSTER RECOVERY SUCCESSFUL</strong> — Calibrated Likelihood: <strong>{proba * 100:.1f}%</strong>", variant="emerald")
    else:
        render_callout(f"<strong>BOOSTER RECOVERY AT RISK / EXPENDABLE</strong> — Calibrated Likelihood: <strong>{proba * 100:.1f}%</strong>", variant="rose")
else:
    st.warning("Model pipeline artifact not found. Please run 'python scripts/train_model.py' to generate.")

st.markdown("---")

# Correct Geographic Map (fixing the bug where all sites were stacked on Cape Canaveral)
render_section_header(
    title="Launch Site Map (Verified Coordinates)",
    subtitle="Accurate geographic positions across Florida and California complexes.",
    icon="globe",
    variant="emerald",
)

m = folium.Map(location=[32.5, -98.0], zoom_start=4, tiles="CartoDB positron")
for s_name, s_meta in LAUNCH_SITES.items():
    folium.Marker(
        location=[s_meta["latitude"], s_meta["longitude"]],
        popup=f"<b>{s_name}</b><br>{s_meta['location']}",
        tooltip=s_name,
        icon=folium.Icon(color="blue", icon="plane", prefix="fa"),
    ).add_to(m)
st_folium(m, width=700, height=400)

st.markdown("---")

# Orbit Plot
render_section_header(
    title="Orbit vs Landing Success Rate",
    subtitle="Historical empirical recovery rates by target orbit inclination.",
    icon="chart",
    variant="cyan",
)

orbit_plot = df.groupby("Orbit")["Class"].agg(
    success_rate=("mean", lambda x: round(x * 100, 1)),
    total_launches="count"
).reset_index()

fig = px.bar(
    orbit_plot,
    x="Orbit",
    y="success_rate",
    text="total_launches",
    labels={"success_rate": "Success Rate (%)", "total_launches": "Launches"},
    color_discrete_sequence=["#2563EB"],
)
fig.update_layout(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#F8FAFC",
    font=dict(color="#0F172A", family="'Plus Jakarta Sans', sans-serif"),
    xaxis=dict(gridcolor="#E2E8F0"),
    yaxis=dict(gridcolor="#E2E8F0"),
    margin=dict(l=40, r=40, t=20, b=40),
)
st.plotly_chart(fig, width="stretch")
"""
SpaceY Intelligence - Page 2: Launch Explorer
Interactive dimensional filtering, telemetry distributions, and historical record inspection.
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
import plotly.express as px
from spacey.ui.theme import (
    apply_spacey_theme,
    render_page_header,
    render_section_header,
    get_gradient_icon_html,
    clean_html,
)
from spacey.data.loader import load_and_prepare_unified_data

st.set_page_config(page_title="Launch Explorer | SpaceY Intelligence", layout="wide")
apply_spacey_theme()

render_page_header(
    title="Launch Explorer",
    subtitle="Slice-and-dice historical mission telemetry across launch sites, payload classes, orbits, and eras.",
    badge_text="TELEMETRY ARCHIVE",
    icon="database",
    variant="cyan",
)

df, _ = load_and_prepare_unified_data()

# Sidebar Filters
st.sidebar.markdown(clean_html('<div style="font-weight:700;color:#0F172A;font-size:1.05rem;margin-bottom:12px;">Filter Parameters</div>'), unsafe_allow_html=True)

# Era Filter
era_options = ["All Eras"] + sorted(df["Era"].dropna().unique().tolist())
selected_era = st.sidebar.selectbox("Mission Era", era_options)

# Site Filter
site_options = sorted(df["LaunchSite"].dropna().unique().tolist())
selected_sites = st.sidebar.multiselect("Launch Complex", site_options, default=site_options)

# Orbit Filter
orbit_options = sorted(df["Orbit"].dropna().unique().tolist())
selected_orbits = st.sidebar.multiselect("Target Orbit", orbit_options, default=orbit_options)

# Payload Mass Filter
min_payload = float(df["PayloadMass"].min())
max_payload = float(df["PayloadMass"].max())
payload_range = st.sidebar.slider(
    "Payload Mass Range (kg)",
    min_value=0.0,
    max_value=max_payload + 1000.0,
    value=(0.0, max_payload + 1000.0),
    step=250.0,
)

# Outcome Filter
outcome_choice = st.sidebar.radio("Landing Outcome", ["All Outcomes", "Successful Landings Only", "Failures / Unattempted Only"])

# Apply Filters
filtered = df.copy()

if selected_era != "All Eras":
    filtered = filtered[filtered["Era"] == selected_era]

if selected_sites:
    filtered = filtered[filtered["LaunchSite"].isin(selected_sites)]

if selected_orbits:
    filtered = filtered[filtered["Orbit"].isin(selected_orbits)]

filtered = filtered[
    (filtered["PayloadMass"] >= payload_range[0]) &
    (filtered["PayloadMass"] <= payload_range[1])
]

if outcome_choice == "Successful Landings Only":
    filtered = filtered[filtered["Class"] == 1]
elif outcome_choice == "Failures / Unattempted Only":
    filtered = filtered[filtered["Class"] == 0]

# Metrics Row for Filtered Slice
m1, m2, m3, m4 = st.columns(4)
filtered_count = len(filtered)
filtered_succ = int(filtered["Class"].sum()) if not filtered.empty else 0
filtered_sr = (filtered["Class"].mean() * 100) if not filtered.empty else 0.0
filtered_avg_mass = filtered["PayloadMass"].mean() if not filtered.empty else 0.0

with m1:
    st.metric("Filtered Launches", f"{filtered_count:,}")
with m2:
    st.metric("Landing Successes", f"{filtered_succ:,}")
with m3:
    st.metric("Slice Recovery Rate", f"{filtered_sr:.1f}%")
with m4:
    st.metric("Avg Payload Mass", f"{filtered_avg_mass:,.0f} kg")

st.markdown("---")

# Visualizations
col_v1, col_v2 = st.columns([1.2, 0.8])

with col_v1:
    render_section_header(
        title="Payload Mass vs. Flight Sequence",
        subtitle="Distribution of delivered mass across historical flight progression.",
        icon="rocket",
        variant="blue",
    )
    if not filtered.empty:
        fig_scatter = px.scatter(
            filtered,
            x="FlightNumber",
            y="PayloadMass",
            color="LandingOutcome",
            hover_data=["Date", "LaunchSite", "Orbit", "Flights"],
            labels={"FlightNumber": "Sequential Flight #", "PayloadMass": "Payload Mass (kg)"},
            color_discrete_map={"Success": "#059669", "Failure": "#DC2626", "None": "#64748B"},
        )
        fig_scatter.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#F8FAFC",
            font=dict(color="#0F172A", family="'Plus Jakarta Sans', sans-serif"),
            xaxis=dict(gridcolor="#E2E8F0"),
            yaxis=dict(gridcolor="#E2E8F0"),
            legend=dict(bgcolor="rgba(255, 255, 255, 0.9)", bordercolor="#E2E8F0", borderwidth=1),
            margin=dict(l=40, r=40, t=20, b=40),
        )
        st.plotly_chart(fig_scatter, width="stretch")
    else:
        st.warning("No records match the selected filter criteria.")

with col_v2:
    render_section_header(
        title="Payload Distribution by Complex",
        subtitle="Quartiles and spread across launch facilities.",
        icon="layers",
        variant="purple",
    )
    if not filtered.empty:
        fig_box = px.box(
            filtered,
            x="LaunchSite",
            y="PayloadMass",
            color="LaunchSite",
            labels={"PayloadMass": "Payload (kg)", "LaunchSite": "Complex"},
            color_discrete_sequence=["#2563EB", "#0891B2", "#7C3AED"],
        )
        fig_box.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#F8FAFC",
            font=dict(color="#0F172A", family="'Plus Jakarta Sans', sans-serif"),
            showlegend=False,
            xaxis=dict(gridcolor="#E2E8F0"),
            yaxis=dict(gridcolor="#E2E8F0"),
            margin=dict(l=40, r=40, t=20, b=40),
        )
        st.plotly_chart(fig_box, width="stretch")

st.markdown("---")

# Interactive Data Table & Export
render_section_header(
    title="Historical Launch Records Table",
    subtitle="Detailed flight telemetry records for selected filter slice.",
    icon="database",
    variant="cyan",
)

cols_to_show = [
    "FlightNumber", "Date", "LaunchSite", "Orbit", "PayloadMass",
    "Flights", "Block", "Reused", "LandingOutcome", "Class", "Era"
]
available_show_cols = [c for c in cols_to_show if c in filtered.columns]

st.dataframe(
    filtered[available_show_cols],
    width="stretch",
    hide_index=True,
)

# CSV Download
csv_data = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Export Filtered Telemetry (CSV)",
    data=csv_data,
    file_name="spacey_filtered_launches.csv",
    mime="text/csv",
)

"""
SpaceY Intelligence - Page 1: Executive Overview
High-level KPIs, macro success trajectories, and core analytical findings.
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
)
from spacey.ui.charts import plot_annual_trends, plot_site_success_rates, plot_orbit_success_rates
from spacey.data.loader import load_and_prepare_unified_data
from spacey.analytics.sql_engine import SpaceYAnalyticsDB

st.set_page_config(page_title="Executive Overview | SpaceY Intelligence", layout="wide")
apply_spacey_theme()

render_page_header(
    title="Executive Overview",
    subtitle="Macro performance indicators, fleet evolution, and historical first-stage landing recovery trends.",
    badge_text="STRATEGIC ANALYTICS",
    icon="chart",
    variant="blue",
)

# Load data and query SQLite views
df, _ = load_and_prepare_unified_data()
db = SpaceYAnalyticsDB()

summary_df = db.get_overall_summary()
annual_df = db.get_annual_trends()
site_df = db.get_site_analytics()
orbit_df = db.get_orbit_analytics()
reuse_df = db.get_booster_reuse_analytics()

# KPI Row
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

tot_launches = int(summary_df["total_launches"].iloc[0])
tot_succ = int(summary_df["total_successful_landings"].iloc[0])
overall_sr = float(summary_df["overall_success_rate_pct"].iloc[0])
avg_payload = float(summary_df["avg_payload_mass_kg"].iloc[0])

# Era breakdown
bench_mask = df["Era"].str.contains("Foundational", na=False)
bench_sr = (df[bench_mask]["Class"].mean() * 100) if bench_mask.any() else 0.0
ops_mask = df["Era"].str.contains("Operational", na=False)
ops_sr = (df[ops_mask]["Class"].mean() * 100) if ops_mask.any() else 0.0

with kpi1:
    st.metric("Total Flights", f"{tot_launches:,}", "Unified Archive")
with kpi2:
    st.metric("Overall Recovery", f"{overall_sr:.1f}%", f"{tot_succ} Landings")
with kpi3:
    st.metric("Foundational Era", f"{bench_sr:.1f}%", "2010–2020 Phase")
with kpi4:
    st.metric("Operational Era", f"{ops_sr:.1f}%", "Block 5 Fleet")
with kpi5:
    st.metric("Avg Payload Mass", f"{avg_payload:,.0f} kg", "Per Mission")

st.markdown("---")

# Main Macro Visualizations
col_chart1, col_chart2 = st.columns([1.2, 0.8])

with col_chart1:
    st.plotly_chart(plot_annual_trends(annual_df), use_container_width=True)

with col_chart2:
    st.plotly_chart(plot_site_success_rates(site_df), use_container_width=True)

col_chart3, col_chart4 = st.columns([1, 1])

with col_chart3:
    st.plotly_chart(plot_orbit_success_rates(orbit_df.head(8)), use_container_width=True)

with col_chart4:
    render_section_header(
        title="Key Empirical Findings",
        subtitle="Operational takeaways distilled from 482 flight records.",
        icon="search",
        variant="purple",
    )

    st.markdown("""
    - **Fleet Maturity Effect**: Falcon 9 booster recovery underwent a dramatic structural shift:
      - **Foundational Era (2010–2020)**: **66.7% success rate** (testing experimental grid fins, ocean splashdowns, and drone ship barges).
      - **Modern Operational Era (2023–2024)**: **79.8% recovery rate** (including deliberate expendable missions) and **>98% on attempted landings**.
    - **Booster Reuse Advantage**: Reused flight-proven boosters demonstrate a **94.0% recovery success rate**, compared to **34.3% on maiden booster flights** (due to early experimental prototypes).
    - **Orbital Profile Impact**: High-energy missions to Geostationary Transfer Orbit (GTO) demand higher stage separation velocity, necessitating ocean drone ship recoveries (ASDS) with tighter propellant margins.
    - **Launch Complex Specialization**: Cape Canaveral SLC-40 and Kennedy LC-39A handle high-cadence equatorial and ISS flights, while Vandenberg SLC-4E supports polar and Sun-Synchronous (SSO) orbits.
    """)

    render_section_header(
        title="Booster Reuse Performance Breakdown",
        subtitle="Success rates by stage flight iteration status.",
        icon="layers",
        variant="cyan",
    )
    st.dataframe(reuse_df, use_container_width=True, hide_index=True)

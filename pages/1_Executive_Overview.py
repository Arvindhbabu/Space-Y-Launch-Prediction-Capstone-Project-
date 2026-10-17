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
ops_dates = pd.to_datetime(df.loc[ops_mask, "Date"], errors="coerce").dropna()
ops_period = (
    f"{ops_dates.min().year}–{ops_dates.max().year}"
    if not ops_dates.empty
    else "No dated records"
)

def summarize_rate(mask: pd.Series) -> str:
    sample = df.loc[mask, "Class"].dropna()
    if sample.empty:
        return "not available (n=0)"
    return f"{sample.mean() * 100:.1f}% (n={len(sample):,})"

foundational_summary = summarize_rate(bench_mask)
operational_summary = summarize_rate(ops_mask)
reused_mask = pd.to_numeric(df["Reused"], errors="coerce").eq(1)
maiden_mask = pd.to_numeric(df["Reused"], errors="coerce").eq(0)
reused_summary = summarize_rate(reused_mask)
maiden_summary = summarize_rate(maiden_mask)

with kpi1:
    st.metric("Total Flights", f"{tot_launches:,}", "Unified Archive")
with kpi2:
    st.metric("Overall Recovery", f"{overall_sr:.1f}%", f"{tot_succ} Landings")
with kpi3:
    st.metric("Foundational Era", f"{bench_sr:.1f}%", "2010–2020 Phase")
with kpi4:
    st.metric("Operational Era", f"{ops_sr:.1f}%", f"{ops_period} · n={int(ops_mask.sum()):,}")
with kpi5:
    st.metric("Avg Payload Mass", f"{avg_payload:,.0f} kg", "Per Mission")

st.markdown("---")

# Main Macro Visualizations
col_chart1, col_chart2 = st.columns([1.2, 0.8])

with col_chart1:
    st.plotly_chart(plot_annual_trends(annual_df), width="stretch")

with col_chart2:
    st.plotly_chart(plot_site_success_rates(site_df), width="stretch")

col_chart3, col_chart4 = st.columns([1, 1])

with col_chart3:
    st.plotly_chart(plot_orbit_success_rates(orbit_df.head(8)), width="stretch")

with col_chart4:
    render_section_header(
        title="Key Empirical Findings",
        subtitle=f"Current archive: {len(df):,} records. Rates below are recalculated from this dataset.",
        icon="search",
        variant="purple",
    )

    st.markdown(
        f"""
    - **Observed era comparison:** Foundational records have a recovery-outcome rate of **{foundational_summary}**. The current operational archive spans **{ops_period}** with a rate of **{operational_summary}**. These are descriptive values from the currently loaded records, not a controlled comparison.
    - **Booster reuse association:** Flight-proven booster records show **{reused_summary}** versus **{maiden_summary}** for maiden-flight records. This association is not causal; reused and maiden missions can differ in mission profile and selection.
    - **Outcome interpretation:** The transformed target includes launch records with no attempted recovery or deliberate stage expenditure in the unsuccessful class. A class of 0 should not be interpreted automatically as hardware failure or as the probability of failure on an attempted landing.
    - **Mission context:** Compare launch-site and orbit groupings using the charts above and their sample sizes. These historical correlations do not model trajectory, weather, sea state, propellant margins, vehicle health, or other physical constraints.
    """
    )

    render_section_header(
        title="Booster Reuse Performance Breakdown",
        subtitle="Success rates by stage flight iteration status.",
        icon="layers",
        variant="cyan",
    )
    st.dataframe(reuse_df, width="stretch", hide_index=True)

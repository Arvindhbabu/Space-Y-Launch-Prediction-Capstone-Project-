"""
SpaceY Intelligence - Page 3: Geospatial Intelligence
Interactive Folium geospatial mapping with verified coordinates, site statistics, and recovery zones.
"""

import sys
from pathlib import Path

# Add src to sys.path
root_dir = Path(__file__).resolve().parent.parent
src_dir = root_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from spacey.config import LAUNCH_SITES
from spacey.ui.theme import (
    apply_spacey_theme,
    render_page_header,
    render_section_header,
    get_gradient_icon_html,
    clean_html,
)
from spacey.data.loader import load_and_prepare_unified_data
from spacey.analytics.sql_engine import SpaceYAnalyticsDB

st.set_page_config(page_title="Geospatial Intelligence | SpaceY Intelligence", layout="wide")
apply_spacey_theme()

render_page_header(
    title="Geospatial Intelligence",
    subtitle="Interactive geographic telemetry of primary SpaceX orbital launch complexes and recovery zones.",
    badge_text="GEOSPATIAL ASSETS",
    icon="globe",
    variant="emerald",
)

df, _ = load_and_prepare_unified_data()
db = SpaceYAnalyticsDB()
site_stats = db.get_site_analytics()

# Summary row for complexes
col_c1, col_c2, col_c3 = st.columns(3)

cols = [col_c1, col_c2, col_c3]
for idx, (site_name, meta) in enumerate(LAUNCH_SITES.items()):
    site_row = site_stats[site_stats["LaunchSite"] == site_name]
    tot = int(site_row["total_launches"].iloc[0]) if not site_row.empty else 0
    sr = float(site_row["success_rate_pct"].iloc[0]) if not site_row.empty else 0.0
    succ = int(site_row["successful_landings"].iloc[0]) if not site_row.empty else 0

    with cols[idx]:
        card_html = f"""
        <div class="telemetry-card">
        <div class="telemetry-title" style="color:#059669;">{site_name}</div>
        <div style="font-size:1.15rem;font-weight:700;color:#0F172A;margin-bottom:4px;">{meta['location']}</div>
        <div style="font-size:0.85rem;color:#64748B;margin-bottom:12px;">{meta['full_name']}</div>
        <div style="display:flex;justify-content:space-between;border-top:1px solid #E2E8F0;padding-top:10px;font-size:0.9rem;">
        <span style="color:#475569;">Total Launches: <b style="color:#0F172A;">{tot}</b></span>
        <span style="color:#475569;">Success Rate: <b style="color:#059669;">{sr:.1f}%</b></span>
        </div>
        </div>
        """
        st.markdown(clean_html(card_html), unsafe_allow_html=True)

st.markdown("---")

col_map, col_details = st.columns([1.3, 0.7])

with col_map:
    render_section_header(
        title="Continental Launch Sites Map",
        subtitle="Geodetic coordinates and operational radii across launch facilities.",
        icon="globe",
        variant="blue",
    )

    # Center map on USA continental view with crisp light tiles
    m = folium.Map(
        location=[32.5, -98.0],
        zoom_start=4,
        tiles="OpenStreetMap",
    )

    # Add verified complex markers
    for site_name, meta in LAUNCH_SITES.items():
        lat = meta["latitude"]
        lon = meta["longitude"]
        site_row = site_stats[site_stats["LaunchSite"] == site_name]
        tot = int(site_row["total_launches"].iloc[0]) if not site_row.empty else 0
        sr = float(site_row["success_rate_pct"].iloc[0]) if not site_row.empty else 0.0

        popup_html = f"""
        <div style="font-family: sans-serif; font-size: 12px; width: 200px; color: #0F172A;">
            <b style="font-size: 14px; color: #2563EB;">{site_name}</b><br>
            <i>{meta['location']}</i><br><br>
            <b>Total Launches:</b> {tot}<br>
            <b>Success Rate:</b> {sr:.1f}%<br>
            <b>Coordinates:</b> {lat:.4f}, {lon:.4f}<br>
            <b>Operator:</b> {meta['operator']}
        </div>
        """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{site_name} ({sr:.1f}% Recovery)",
            icon=folium.Icon(color="blue", icon="plane", prefix="fa"),
        ).add_to(m)

        # Volume circle
        folium.Circle(
            location=[lat, lon],
            radius=min(tot * 1500, 350000),
            color="#2563EB",
            fill=True,
            fill_color="#3B82F6",
            fill_opacity=0.18,
            weight=1.5,
        ).add_to(m)

    st_folium(m, width="100%", height=500)

with col_details:
    render_section_header(
        title="Recovery Zone Architecture",
        subtitle="Operational recovery trajectory mechanics and marine stationing.",
        icon="target",
        variant="cyan",
    )

    st.markdown("""
    Distinguishing the launch origin from the recovery landing zone is essential for operational analysis:

    #### 1. Ground Pad Landing (RTLS)
    - **Landing Zones**: LZ-1 and LZ-2 (Cape Canaveral), LZ-4 (Vandenberg).
    - **Trajectory**: Booster performs a complete boost-back burn reversing its velocity vector towards the launch site.
    - **Constraint**: Consumes up to 15% more propellant, viable only for light payloads or low-energy orbits.

    #### 2. Autonomous Spaceport Drone Ship (ASDS)
    - **Vessels**:
      - *Just Read the Instructions* (JRTI) — Atlantic / Port Canaveral
      - *A Shortfall of Gravitas* (ASOG) — Atlantic / Port Canaveral
      - *Of Course I Still Love You* (OCISLY) — Pacific / Port of Long Beach
    - **Stationing**: Deployed 300 to 650 km downrange along the ballistic orbital inclination corridor.
    - **Operational Factor**: Susceptible to heavy swell, high deck winds, and marine weather hazards.
    """)

st.markdown("---")
render_section_header(
    title="Comprehensive Complex Performance Table",
    subtitle="Summary of historical flights, recoveries, and average mass delivered.",
    icon="database",
    variant="emerald",
)
st.dataframe(site_stats, width="stretch", hide_index=True)

"""
SpaceY Intelligence - Page 7: Data Quality & Operations
Automated schema validation, missing-value diagnostics, provenance tracking, and data refresh controls.
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
    get_gradient_icon_html,
    clean_html,
)
from spacey.data.loader import (
    load_and_prepare_benchmark_data,
    load_and_prepare_operational_data,
    load_and_prepare_unified_data,
)
from spacey.data.ingestion import compute_file_fingerprint
from spacey.config import (
    BENCHMARK_PROCESSED_CSV,
    OPERATIONAL_PROCESSED_CSV,
    UNIFIED_LAUNCHES_CSV,
    RAW_SPACEX_CSV,
    BENCHMARK_RAW_CSV,
)

st.set_page_config(page_title="Data Quality & Ops | SpaceY Intelligence", layout="wide")
apply_spacey_theme()

render_page_header(
    title="Data Quality & Operations",
    subtitle="Continuous data governance, schema compliance verification, missing-value auditing, and provenance fingerprinting.",
    badge_text="DATA GOVERNANCE",
    icon="shield",
    variant="emerald",
)

# Load data and reports
bench_df, bench_report = load_and_prepare_benchmark_data()
ops_df, ops_report = load_and_prepare_operational_data()
unified_df, unified_report = load_and_prepare_unified_data()

# Status Banner
q1, q2, q3 = st.columns(3)

with q1:
    status_label = "Schema Valid" if bench_report.schema_valid else "Schema Invalid"
    status_color = "#059669" if bench_report.schema_valid else "#DC2626"
    card1 = f"""
    <div class="telemetry-card" style="border-left:4px solid {status_color};">
    <div class="telemetry-title" style="color:{status_color};">Benchmark Capstone Layer</div>
    <div style="font-size:1.25rem;font-weight:800;color:#0F172A;">{status_label}</div>
    <div style="color:#64748B;font-size:0.85rem;margin-top:4px;">
    Rows: <b>{bench_report.total_rows}</b> | Columns: <b>{bench_report.total_columns}</b>
    </div>
    </div>
    """
    st.markdown(clean_html(card1), unsafe_allow_html=True)

with q2:
    status_label = "Schema Valid" if ops_report.schema_valid else "Schema Invalid"
    status_color = "#059669" if ops_report.schema_valid else "#DC2626"
    card2 = f"""
    <div class="telemetry-card" style="border-left:4px solid {status_color};">
    <div class="telemetry-title" style="color:{status_color};">Operational Scraped Layer</div>
    <div style="font-size:1.25rem;font-weight:800;color:#0F172A;">{status_label}</div>
    <div style="color:#64748B;font-size:0.85rem;margin-top:4px;">
    Rows: <b>{ops_report.total_rows}</b> | Columns: <b>{ops_report.total_columns}</b>
    </div>
    </div>
    """
    st.markdown(clean_html(card2), unsafe_allow_html=True)

with q3:
    status_label = "Schema Valid" if unified_report.schema_valid else "Schema Invalid"
    status_color = "#059669" if unified_report.schema_valid else "#DC2626"
    card3 = f"""
    <div class="telemetry-card" style="border-left:4px solid {status_color};">
    <div class="telemetry-title" style="color:{status_color};">Unified Longitudinal Archive</div>
    <div style="font-size:1.25rem;font-weight:800;color:#0F172A;">{status_label}</div>
    <div style="color:#64748B;font-size:0.85rem;margin-top:4px;">
    Rows: <b>{unified_report.total_rows}</b> | Columns: <b>{unified_report.total_columns}</b>
    </div>
    </div>
    """
    st.markdown(clean_html(card3), unsafe_allow_html=True)

st.markdown("---")

# Missing Value Audit Table
render_section_header(
    title="Missing Value & Data Completeness Audit",
    subtitle="Feature-by-feature null distribution and completeness ratios.",
    icon="search",
    variant="blue",
)

dataset_choice = st.selectbox("Select Layer to Inspect", ["Benchmark Capstone Layer", "Operational Scraped Layer", "Unified Archive"])

active_report = bench_report if dataset_choice == "Benchmark Capstone Layer" else (ops_report if dataset_choice == "Operational Scraped Layer" else unified_report)

miss_df = pd.DataFrame({
    "Column Name": list(active_report.missing_counts.keys()),
    "Missing Count": list(active_report.missing_counts.values()),
    "Missing Percentage (%)": list(active_report.missing_percentages.values()),
})
miss_df = miss_df.sort_values(by="Missing Count", ascending=False).reset_index(drop=True)

st.dataframe(miss_df, use_container_width=True, hide_index=True)

st.markdown("---")

# Provenance Fingerprints Table
render_section_header(
    title="Data Provenance & Cryptographic Fingerprints",
    subtitle="SHA-256 integrity checksums for immutable raw data and processed outputs.",
    icon="shield",
    variant="emerald",
)

provenance_records = [
    {
        "Layer": "Benchmark Raw Cache",
        "Path": str(BENCHMARK_RAW_CSV.relative_to(root_dir)),
        "SHA-256 Fingerprint": compute_file_fingerprint(BENCHMARK_RAW_CSV),
        "Source Provenance": "IBM Coursera S3 Object Storage",
    },
    {
        "Layer": "Scraped Raw Archive",
        "Path": str(RAW_SPACEX_CSV.relative_to(root_dir)),
        "SHA-256 Fingerprint": compute_file_fingerprint(RAW_SPACEX_CSV),
        "Source Provenance": "Wikipedia SpaceX Launch Tables",
    },
    {
        "Layer": "Benchmark Processed",
        "Path": str(BENCHMARK_PROCESSED_CSV.relative_to(root_dir)),
        "SHA-256 Fingerprint": compute_file_fingerprint(BENCHMARK_PROCESSED_CSV),
        "Source Provenance": "SpaceY Data Preprocessing Pipeline",
    },
    {
        "Layer": "Operational Processed",
        "Path": str(OPERATIONAL_PROCESSED_CSV.relative_to(root_dir)),
        "SHA-256 Fingerprint": compute_file_fingerprint(OPERATIONAL_PROCESSED_CSV),
        "Source Provenance": "SpaceY Data Preprocessing Pipeline",
    },
    {
        "Layer": "Unified Flight Archive",
        "Path": str(UNIFIED_LAUNCHES_CSV.relative_to(root_dir)),
        "SHA-256 Fingerprint": compute_file_fingerprint(UNIFIED_LAUNCHES_CSV),
        "Source Provenance": "SpaceY Harmonization Pipeline",
    },
]

st.dataframe(pd.DataFrame(provenance_records), use_container_width=True, hide_index=True)

st.markdown("---")

# Pipeline Trigger
render_section_header(
    title="Controlled Pipeline Refresh",
    subtitle="Manually trigger data re-ingestion, validation, and SQLite warehouse rebuild.",
    icon="activity",
    variant="purple",
)
st.markdown("Triggering refresh will re-ingest data layers, execute validation checks, and re-populate the SQLite analytical database.")

if st.button("Trigger End-to-End Pipeline Refresh"):
    with st.spinner("Executing pipeline ingestion, cleaning, and SQLite database rebuild..."):
        try:
            b_df, _ = load_and_prepare_benchmark_data(force_refresh=True)
            o_df, _ = load_and_prepare_operational_data(force_refresh=True)
            u_df, _ = load_and_prepare_unified_data(force_refresh=True)
            st.success("Data pipeline refreshed successfully! All analytical views updated.")
            st.rerun()
        except Exception as e:
            st.error(f"Error during pipeline refresh: {str(e)}")

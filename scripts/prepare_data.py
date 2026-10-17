"""
SpaceY Intelligence - Data Preparation & Pipeline Execution Script
Runs data ingestion, preprocessing, validation, and analytical database creation.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import pandas as pd

# Add src to pythonpath
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from spacey.data.loader import (
    load_and_prepare_benchmark_data,
    load_and_prepare_operational_data,
    load_and_prepare_unified_data,
)
from spacey.analytics.sql_engine import SpaceYAnalyticsDB


def main():
    print("=" * 60)
    print("🚀 SPACEY INTELLIGENCE — DATA PIPELINE EXECUTION")
    print("=" * 60)
    in_venv = (sys.prefix != sys.base_prefix)
    print(f"Active Interpreter:   {sys.executable}")
    print(f"Python Version:       {sys.version.split()[0]}")
    print(f"Virtual Env Active:   {'Yes (.venv)' if in_venv else 'NO (Global Python - Not Recommended)'}")
    print("=" * 60)

    print("\n1. Ingesting & Preprocessing Benchmark Capstone Dataset...")
    bench_df, bench_report = load_and_prepare_benchmark_data(force_refresh=True)
    print(f"   Benchmark dataset shape: {bench_df.shape}")
    print(f"   Schema valid: {bench_report.schema_valid}")
    print(f"   Target distribution: {bench_report.target_distribution}")

    print("\n2. Ingesting & Preprocessing Operational Scraped Dataset...")
    ops_df, ops_report = load_and_prepare_operational_data(force_refresh=True)
    print(f"   Operational dataset shape: {ops_df.shape}")
    print(f"   Schema valid: {ops_report.schema_valid}")
    print(f"   Target distribution: {ops_report.target_distribution}")

    print("\n3. Building Harmonized Longitudinal Flight Archive...")
    unified_df, unified_report = load_and_prepare_unified_data(force_refresh=True)
    print(f"   Unified archive shape: {unified_df.shape}")
    valid_dt = pd.to_datetime(unified_df['Date'].dropna(), errors='coerce')
    print(f"   Earliest date: {valid_dt.min().strftime('%Y-%m-%d')}, Latest date: {valid_dt.max().strftime('%Y-%m-%d')}")
    print(f"   Total successful landings: {unified_df['Class'].sum()} / {len(unified_df)} ({unified_df['Class'].mean()*100:.1f}%)")

    print("\n4. Initializing SQLite Analytics Database & Views...")
    db = SpaceYAnalyticsDB()
    db.initialize_database(unified_df)

    print("\n--- SQL VIEW 1: OVERALL SUMMARY ---")
    print(db.get_overall_summary())

    print("\n--- SQL VIEW 2: LAUNCH SITE ANALYTICS ---")
    print(db.get_site_analytics())

    print("\n--- SQL VIEW 3: ORBIT ANALYTICS (Top 5) ---")
    print(db.get_orbit_analytics().head(5))

    print("\n--- SQL VIEW 5: PAYLOAD MASS BANDS ---")
    print(db.get_payload_bands())

    print("\n--- SQL VIEW 6: BOOSTER REUSE ANALYTICS ---")
    print(db.get_booster_reuse_analytics())

    print("\n✅ Data pipeline execution and analytical database generation complete!")


if __name__ == "__main__":
    main()

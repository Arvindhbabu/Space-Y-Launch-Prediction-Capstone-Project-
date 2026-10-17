"""
SpaceY Intelligence - Primary Data Access and Loader Service
Coordinates ingestion, preprocessing, validation, and local persistence.
"""

from pathlib import Path
from typing import Tuple, Optional
import pandas as pd

from spacey.config import (
    BENCHMARK_PROCESSED_CSV,
    OPERATIONAL_PROCESSED_CSV,
    UNIFIED_LAUNCHES_CSV,
    RAW_SPACEX_CSV,
    BENCHMARK_RAW_CSV,
)
from spacey.data.ingestion import fetch_ibm_benchmark_dataset, load_local_raw_launches
from spacey.data.preprocessing import (
    clean_ibm_benchmark_dataset,
    clean_raw_wikipedia_dataset,
    build_unified_flight_archive,
)
from spacey.data.validation import validate_dataset, DataQualityReport
from spacey.logging_config import setup_logger

logger = setup_logger("spacey.loader")


def load_and_prepare_benchmark_data(force_refresh: bool = False) -> Tuple[pd.DataFrame, DataQualityReport]:
    """
    Loads, cleans, and validates the benchmark capstone dataset (90 launches).
    Saves processed dataset to data/processed/spacex_benchmark_processed.csv.
    """
    if not force_refresh and BENCHMARK_PROCESSED_CSV.exists():
        logger.info("Loading processed benchmark dataset from disk cache: %s", BENCHMARK_PROCESSED_CSV)
        df = pd.read_csv(BENCHMARK_PROCESSED_CSV)
        report = validate_dataset(df, dataset_name="Benchmark Capstone Dataset")
        return df, report

    # Ingest raw benchmark
    raw_df, meta = fetch_ibm_benchmark_dataset()
    if raw_df is None:
        raise RuntimeError(f"Could not acquire benchmark dataset: {meta.get('error')}")

    cleaned_df = clean_ibm_benchmark_dataset(raw_df)
    report = validate_dataset(cleaned_df, dataset_name="Benchmark Capstone Dataset")

    BENCHMARK_PROCESSED_CSV.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(BENCHMARK_PROCESSED_CSV, index=False)
    logger.info("Saved validated benchmark dataset to %s", BENCHMARK_PROCESSED_CSV)
    return cleaned_df, report


def load_and_prepare_operational_data(force_refresh: bool = False) -> Tuple[pd.DataFrame, DataQualityReport]:
    """
    Loads, cleans, and validates the operational Wikipedia dataset.
    Saves processed dataset to data/processed/spacex_operational_processed.csv.
    """
    if not force_refresh and OPERATIONAL_PROCESSED_CSV.exists():
        logger.info("Loading processed operational dataset from disk cache: %s", OPERATIONAL_PROCESSED_CSV)
        df = pd.read_csv(OPERATIONAL_PROCESSED_CSV)
        report = validate_dataset(df, dataset_name="Operational Launch Dataset")
        return df, report

    raw_df, meta = load_local_raw_launches(RAW_SPACEX_CSV)
    if raw_df is None:
        raise RuntimeError(f"Could not load raw Wikipedia launches: {meta.get('error')}")

    cleaned_df = clean_raw_wikipedia_dataset(raw_df)
    report = validate_dataset(cleaned_df, dataset_name="Operational Launch Dataset")

    OPERATIONAL_PROCESSED_CSV.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(OPERATIONAL_PROCESSED_CSV, index=False)
    logger.info("Saved validated operational dataset to %s", OPERATIONAL_PROCESSED_CSV)
    return cleaned_df, report


def load_and_prepare_unified_data(force_refresh: bool = False) -> Tuple[pd.DataFrame, DataQualityReport]:
    """
    Constructs unified longitudinal flight archive across both eras.
    """
    if not force_refresh and UNIFIED_LAUNCHES_CSV.exists():
        logger.info("Loading processed unified dataset from disk cache: %s", UNIFIED_LAUNCHES_CSV)
        df = pd.read_csv(UNIFIED_LAUNCHES_CSV)
        report = validate_dataset(df, dataset_name="Unified Historical Launch Archive")
        return df, report

    bench_df, _ = load_and_prepare_benchmark_data(force_refresh=force_refresh)
    ops_df, _ = load_and_prepare_operational_data(force_refresh=force_refresh)

    unified_df = build_unified_flight_archive(bench_df, ops_df)
    report = validate_dataset(unified_df, dataset_name="Unified Historical Launch Archive")

    UNIFIED_LAUNCHES_CSV.parent.mkdir(parents=True, exist_ok=True)
    unified_df.to_csv(UNIFIED_LAUNCHES_CSV, index=False)
    logger.info("Saved unified flight archive to %s", UNIFIED_LAUNCHES_CSV)
    return unified_df, report

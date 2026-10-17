"""
SpaceY Intelligence - Configuration Module
Centralized configuration, paths, constants, and geographic coordinates.
"""

import os
from pathlib import Path
from typing import Dict, Any

# Root directory of the repository
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# Data directories
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Model and registry directories
MODELS_DIR = ROOT_DIR / "models"
REGISTRY_DIR = MODELS_DIR / "registry"

# Reports and docs
REPORTS_DIR = ROOT_DIR / "reports"
DOCS_DIR = ROOT_DIR / "docs"

# SQLite analytical database
SQLITE_DB_PATH = DATA_DIR / "spacey_analytics.db"

# Data file paths
RAW_SPACEX_CSV = DATA_DIR / "raw_spacex_launches.csv"
CLEANED_SPACEX_CSV = DATA_DIR / "cleaned_spacex_launches.csv"
BENCHMARK_RAW_CSV = RAW_DATA_DIR / "spacex_ibm_benchmark_raw.csv"
BENCHMARK_PROCESSED_CSV = PROCESSED_DATA_DIR / "spacex_benchmark_processed.csv"
OPERATIONAL_PROCESSED_CSV = PROCESSED_DATA_DIR / "spacex_operational_processed.csv"
UNIFIED_LAUNCHES_CSV = PROCESSED_DATA_DIR / "spacex_unified_launches.csv"

# Remote source endpoints
IBM_BENCHMARK_URL = (
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_2.csv"
)
SPACEX_API_URL = "https://api.spacexdata.com/v4/launches"

# Reproducibility
RANDOM_STATE = 42

# Launch site metadata and exact verified coordinates
LAUNCH_SITES: Dict[str, Dict[str, Any]] = {
    "CCAFS SLC 40": {
        "full_name": "Cape Canaveral Space Force Station Space Launch Complex 40",
        "latitude": 28.561857,
        "longitude": -80.577366,
        "operator": "SpaceX / US Space Force",
        "location": "Cape Canaveral, Florida",
        "aliases": ["CCAFS SLC 40", "Cape Canaveral, SLC‑40", "Cape Canaveral, SLC-40", "CCSFS SLC 40"],
    },
    "KSC LC 39A": {
        "full_name": "Kennedy Space Center Launch Complex 39A",
        "latitude": 28.608058,
        "longitude": -80.603956,
        "operator": "SpaceX / NASA",
        "location": "Merritt Island, Florida",
        "aliases": ["KSC LC 39A", "Kennedy, LC‑39A", "Kennedy, LC-39A", "LC-39A"],
    },
    "VAFB SLC 4E": {
        "full_name": "Vandenberg Space Force Base Space Launch Complex 4E",
        "latitude": 34.632834,
        "longitude": -120.610746,
        "operator": "SpaceX / US Space Force",
        "location": "Santa Barbara County, California",
        "aliases": ["VAFB SLC 4E", "Vandenberg, SLC‑4E", "Vandenberg, SLC-4E", "SLC-4E"],
    },
}

# Standardized Orbit Types
VALID_ORBITS = [
    "LEO",      # Low Earth Orbit
    "ISS",      # International Space Station
    "PO",       # Polar Orbit
    "GTO",      # Geostationary Transfer Orbit
    "GEO",      # Geosynchronous Earth Orbit
    "SSO",      # Sun-Synchronous Orbit
    "MEO",      # Medium Earth Orbit
    "HEO",      # Highly Elliptical Orbit
    "ES-L1",    # Earth-Sun Lagrange 1
    "VLEO",     # Very Low Earth Orbit
    "SO",       # Sub-Orbital
]

# Leakage-Safe Feature Definitions for Predictive Modeling
# Features strictly knowable prior to vehicle launch:
NUMERICAL_FEATURES = [
    "PayloadMass",      # Payload mass in kg
    "Flights",          # Flight number of this specific booster (1 = maiden flight, 2+ = reused)
    "Block",            # Booster block design iteration (1 to 5)
    "FlightNumber",     # Historical sequential SpaceX launch sequence number
]

CATEGORICAL_FEATURES = [
    "LaunchSite",       # Standardized launch site (CCAFS SLC 40, KSC LC 39A, VAFB SLC 4E)
    "Orbit",            # Mission orbital destination
]

BINARY_FEATURES = [
    "GridFins",         # Equipped with hypersonic grid fins (1 or 0)
    "Legs",             # Equipped with deployable landing legs (1 or 0)
    "Reused",           # Vehicle is flight-proven / reused booster (1 or 0)
]

TARGET_COLUMN = "Class"  # 1 = Successful Landing (ASDS / RTLS), 0 = Failure / Ocean Crash / Unattempted

# Ensure directories exist
for d in [RAW_DATA_DIR, PROCESSED_DATA_DIR, REGISTRY_DIR, REPORTS_DIR, DOCS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

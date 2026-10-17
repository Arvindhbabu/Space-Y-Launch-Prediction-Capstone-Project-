"""
SpaceY Intelligence - Data Preprocessing and Harmonization Pipeline
Cleans raw historical records, normalizes features, extracts numeric telemetry,
and harmonizes disparate launch data layers without data leakage.
"""

import re
from typing import Optional, Tuple, Any
import pandas as pd
import numpy as np

from spacey.config import LAUNCH_SITES, VALID_ORBITS
from spacey.data.feature_schema import SITE_ALIASES, STANDARDIZED_SITES
from spacey.logging_config import setup_logger

logger = setup_logger("spacey.preprocessing")

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def clean_text_field(val: Any) -> str:
    """Removes Wikipedia footnote brackets like [17], [h], non-breaking spaces, and leading/trailing whitespace."""
    if pd.isna(val):
        return ""
    s = str(val).replace("\xa0", " ").replace("\u2011", "-")
    # Remove citation brackets like [12], [h], [j]
    s = re.sub(r"\[.*?\]", "", s)
    return s.strip()


def extract_payload_kg(val: Any) -> Optional[float]:
    """
    Extracts numerical payload mass in kilograms from text strings.
    E.g. '6,000 kg (13,000 lb)' -> 6000.0, '~17,400 kg (38,400 lb)' -> 17400.0.
    Returns None for 'Unknown' or invalid strings (NEVER silently replaces with zero).
    """
    if pd.isna(val):
        return None
    s = str(val).replace("\xa0", " ").replace(",", "").replace("\u2011", "-")
    s = re.sub(r"\[.*?\]", "", s)
    if "unknown" in s.lower():
        return None

    # Search for pattern with kg
    match = re.search(r"~?(\d+(?:\.\d+)?)\s*kg", s, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass

    # Fallback: search for first numeric integer > 50
    nums = re.findall(r"\d+", s)
    if nums:
        try:
            val_candidate = float(nums[0])
            if val_candidate > 50:
                return val_candidate
        except ValueError:
            pass
    return None


def clean_launch_site(val: Any) -> str:
    """Maps various launch site string aliases into verified canonical names."""
    cleaned = clean_text_field(val)
    # Check direct alias
    for alias, standard in SITE_ALIASES.items():
        if alias.lower() in cleaned.lower():
            return standard
    return "CCAFS SLC 40"  # default fallback if unidentifiable


def clean_orbit(val: Any) -> str:
    """Standardizes orbital regime string into canonical categories."""
    cleaned = clean_text_field(val).upper()
    if "POLAR" in cleaned:
        return "PO"
    if "SUN-SYNCHRONOUS" in cleaned or "SUN SYNCHRONOUS" in cleaned:
        return "SSO"
    for o in VALID_ORBITS:
        if o in cleaned:
            return o
    return "LEO"


def parse_date_and_year(val: Any) -> Tuple[Optional[str], Optional[int]]:
    """Extracts ISO date string YYYY-MM-DD and Year integer from date text."""
    if pd.isna(val):
        return None, None
    s = clean_text_field(val)
    # Match Month Day, Year
    match = re.search(r"([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})", s)
    if match:
        month_str, day_str, year_str = match.groups()
        try:
            dt = pd.to_datetime(f"{month_str} {day_str} {year_str}")
            return dt.strftime("%Y-%m-%d"), int(year_str)
        except Exception:
            return None, int(year_str)
    # Try year only
    year_match = re.search(r"\b(20\d{2})\b", s)
    if year_match:
        return None, int(year_match.group(1))
    return None, None


def clean_raw_wikipedia_dataset(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the raw Wikipedia-scraped DataFrame (2023-2024 launches).
    Filters out the 400+ table subrows, parses payload mass, standardizes features,
    and constructs verified target variable.
    """
    logger.info("Cleaning raw Wikipedia launch records (rows: %d)", len(raw_df))

    # Step 1: Filter out Wikipedia mission description subrows
    def is_valid_launch_event(row: pd.Series) -> bool:
        dt_str = str(row.get("Date and time (UTC)", ""))
        if len(dt_str) > 75:
            return False
        # Must contain a valid month name
        return any(m in dt_str for m in MONTH_NAMES)

    valid_mask = raw_df.apply(is_valid_launch_event, axis=1)
    df = raw_df[valid_mask].copy().reset_index(drop=True)
    logger.info("Retained %d valid launch event rows after filtering description subrows", len(df))

    # Standardize column mappings
    df["FlightNo_Clean"] = df["Flight No."].apply(clean_text_field)
    date_tuples = df["Date and time (UTC)"].apply(parse_date_and_year)
    raw_dates = [t[0] for t in date_tuples]
    years = [t[1] if t[1] is not None else 2023 for t in date_tuples]
    df["Year"] = years
    df["Date"] = [
        raw_dates[i] if raw_dates[i] is not None else f"{years[i]}-06-15"
        for i in range(len(raw_dates))
    ]

    df["LaunchSite"] = df["Launch site"].apply(clean_launch_site)
    df["Orbit"] = df["Orbit"].apply(clean_orbit)
    df["PayloadMass"] = df["Payload mass"].apply(extract_payload_kg)

    # Impute missing payload mass with median of known payloads (never with 0)
    median_payload = df["PayloadMass"].median()
    df["PayloadMass"] = df["PayloadMass"].fillna(median_payload)

    # Extract booster details
    booster_str = df["Version, booster[h]"].astype(str)
    # Check flight number iteration (e.g. B1060-15 -> 15 flights)
    def extract_flights_count(s: str) -> int:
        match = re.search(r"B\d{4}[-‑](\d+)", s)
        if match:
            return int(match.group(1))
        return 1

    df["Flights"] = booster_str.apply(extract_flights_count)
    df["Reused"] = (df["Flights"] > 1).astype(int)
    df["Block"] = 5  # Modern Falcon 9 is Block 5
    df["GridFins"] = 1  # Standard on modern recovery missions
    df["Legs"] = 1      # Standard on modern recovery missions

    # Target: Landing outcome classification
    def parse_recovery_outcome(outcome_val: Any) -> Tuple[int, str]:
        s = clean_text_field(outcome_val)
        if not s or "no attempt" in s.lower() or "unattempted" in s.lower():
            return 0, "No Attempt"
        if "success" in s.lower():
            pad = "ASDS" if any(ds in s for ds in ["ASOG", "JRTI", "OCISLY"]) else "RTLS"
            return 1, f"Success ({pad})"
        if "failure" in s.lower():
            return 0, "Failure"
        return 0, "Expended / Unrecovered"

    recovery_info = df["Booster landing"].apply(parse_recovery_outcome)
    df["Class"] = [r[0] for r in recovery_info]
    df["LandingOutcome"] = [r[1] for r in recovery_info]

    # Geographic coordinates
    df["Latitude"] = df["LaunchSite"].apply(lambda s: LAUNCH_SITES[s]["latitude"])
    df["Longitude"] = df["LaunchSite"].apply(lambda s: LAUNCH_SITES[s]["longitude"])
    df["Era"] = "Modern Operational (2023-2024)"

    cleaned_cols = [
        "Date", "Year", "LaunchSite", "Orbit", "PayloadMass",
        "Flights", "GridFins", "Legs", "Block", "Reused",
        "LandingOutcome", "Class", "Latitude", "Longitude", "Era"
    ]
    return df[cleaned_cols]


def clean_ibm_benchmark_dataset(ibm_raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and validates the foundational IBM Coursera Capstone dataset (90 launches, 2010-2020).
    Ensures correct data types, leakage safety, and coordinate normalization.
    """
    logger.info("Cleaning IBM benchmark capstone dataset (rows: %d)", len(ibm_raw_df))
    df = ibm_raw_df.copy()

    # Standardize column names
    col_rename = {
        "FlightNumber": "FlightNumber",
        "Date": "Date",
        "PayloadMass": "PayloadMass",
        "Orbit": "Orbit",
        "LaunchSite": "LaunchSite",
        "Flights": "Flights",
        "GridFins": "GridFins",
        "Reused": "Reused",
        "Legs": "Legs",
        "Block": "Block",
        "Class": "Class",
    }
    df = df.rename(columns=col_rename)

    # Clean launch site
    df["LaunchSite"] = df["LaunchSite"].apply(clean_launch_site)
    df["Orbit"] = df["Orbit"].apply(clean_orbit)

    # Impute missing payload mass with median (if any)
    if df["PayloadMass"].isnull().any():
        med_val = df["PayloadMass"].median()
        df["PayloadMass"] = df["PayloadMass"].fillna(med_val)

    # Parse date and year
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
    df["Year"] = pd.to_datetime(df["Date"]).dt.year

    # Ensure binary indicators
    df["GridFins"] = df["GridFins"].astype(bool).astype(int)
    df["Reused"] = df["Reused"].astype(bool).astype(int)
    df["Legs"] = df["Legs"].astype(bool).astype(int)
    df["Block"] = df["Block"].fillna(1).astype(int)
    df["Flights"] = df["Flights"].fillna(1).astype(int)
    df["Class"] = df["Class"].astype(int)

    # Coordinates
    df["Latitude"] = df["LaunchSite"].apply(lambda s: LAUNCH_SITES[s]["latitude"])
    df["Longitude"] = df["LaunchSite"].apply(lambda s: LAUNCH_SITES[s]["longitude"])

    # Outcome description
    if "Outcome" in df.columns:
        df["LandingOutcome"] = df["Outcome"].fillna("Unknown")
    else:
        df["LandingOutcome"] = df["Class"].apply(lambda c: "Success" if c == 1 else "Failure")

    df["Era"] = "Foundational Development (2010-2020)"

    return df


def build_unified_flight_archive(
    benchmark_df: pd.DataFrame,
    operational_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Harmonizes benchmark development dataset and modern operational dataset
    into a comprehensive historical flight record for longitudinal analytics.
    """
    logger.info("Harmonizing benchmark (%d rows) and operational (%d rows) records", len(benchmark_df), len(operational_df))
    unified = pd.concat([benchmark_df, operational_df], ignore_index=True)
    unified = unified.sort_values(by="Date", ascending=True).reset_index(drop=True)
    unified["FlightNumber"] = range(1, len(unified) + 1)
    logger.info("Unified flight archive created with %d total records", len(unified))
    return unified

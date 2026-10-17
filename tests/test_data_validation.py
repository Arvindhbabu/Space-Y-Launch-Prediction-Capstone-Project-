"""
Unit Tests for Data Validation & Quality Assurance
"""

import pytest
import pandas as pd
import numpy as np

from spacey.data.validation import validate_dataset, DataQualityReport
from spacey.data.preprocessing import (
    extract_payload_kg,
    clean_text_field,
    clean_launch_site,
    clean_orbit,
    clean_raw_wikipedia_dataset,
    parse_recovery_outcome,
)
from spacey.data.feature_schema import LaunchScenarioInput


def test_extract_payload_kg():
    # Valid extractions
    assert extract_payload_kg("6,000 kg (13,000 lb)") == 6000.0
    assert extract_payload_kg("~17,400 kg (38,400 lb)") == 17400.0
    assert extract_payload_kg("500 kg") == 500.0
    assert extract_payload_kg("15000") == 15000.0

    # Never replace Unknown with 0!
    assert extract_payload_kg("Unknown[j]") is None
    assert extract_payload_kg(None) is None
    assert extract_payload_kg(np.nan) is None


def test_clean_text_field():
    assert clean_text_field("Cape Canaveral, SLC‑40[17]") == "Cape Canaveral, SLC-40"
    assert clean_text_field("Unknown[j]") == "Unknown"
    assert clean_text_field("F9 B5 B1060‑15") == "F9 B5 B1060-15"


def test_clean_launch_site_aliases():
    assert clean_launch_site("Cape Canaveral, SLC-40") == "CCAFS SLC 40"
    assert clean_launch_site("Kennedy, LC-39A") == "KSC LC 39A"
    assert clean_launch_site("Vandenberg, SLC-4E") == "VAFB SLC 4E"
    assert clean_launch_site("CCAFS SLC 40") == "CCAFS SLC 40"


def test_clean_orbit():
    assert clean_orbit("LEO") == "LEO"
    assert clean_orbit("Polar LEO") == "PO"
    assert clean_orbit("GTO") == "GTO"
    assert clean_orbit("Sun-synchronous") == "SSO"


def test_validate_dataset_empty_and_none():
    rep_none = validate_dataset(None)
    assert not rep_none.schema_valid
    assert len(rep_none.validation_errors) > 0

    rep_empty = validate_dataset(pd.DataFrame())
    assert not rep_empty.schema_valid
    assert rep_empty.total_rows == 0


def test_validate_dataset_valid():
    df = pd.DataFrame({
        "FlightNumber": [1, 2],
        "PayloadMass": [5000.0, 3000.0],
        "LaunchSite": ["CCAFS SLC 40", "KSC LC 39A"],
        "Orbit": ["LEO", "GTO"],
        "Class": [1, 0],
    })
    rep = validate_dataset(df)
    assert rep.schema_valid
    assert rep.total_rows == 2
    assert rep.target_distribution["counts"] == {"1": 1, "0": 1}


def test_validate_dataset_invalid_target():
    df = pd.DataFrame({
        "FlightNumber": [1, 2],
        "PayloadMass": [5000.0, 3000.0],
        "Class": [1, 5],  # Invalid target
    })
    rep = validate_dataset(df)
    assert not rep.schema_valid
    assert any("not strictly binary" in e for e in rep.validation_errors)


def test_scenario_input_validation():
    # Valid input
    scen = LaunchScenarioInput(
        payload_mass=4500.0,
        launch_site="Cape Canaveral, SLC-40",  # Tests alias resolution
        orbit="leo",                          # Tests case normalization
        flights=2,
    )
    assert scen.launch_site == "CCAFS SLC 40"
    assert scen.orbit == "LEO"

    # Invalid input bounds
    with pytest.raises(ValueError):
        LaunchScenarioInput(payload_mass=-100.0)

    with pytest.raises(ValueError):
        LaunchScenarioInput(launch_site="Invalid Site Name")



def test_wikipedia_cleaning_drops_incomplete_and_future_dates_without_fabricating():
    raw = pd.DataFrame({
        "Flight No.": ["F-001", "F-002", "F-003"],
        "Date and time (UTC)": [
            "December 12, 2024 10:00 UTC",
            "May 4, 2029 10:00 UTC",
            "June 2024",
        ],
        "Launch site": ["Cape Canaveral, SLC-40"] * 3,
        "Orbit": ["LEO"] * 3,
        "Payload mass": ["6,000 kg (13,000 lb)"] * 3,
        "Version, booster[h]": ["F9 B5 B1060-15"] * 3,
        "Booster landing": ["Success (JRTI)", "Unsuccessful landing", "Success"],
    })

    cleaned = clean_raw_wikipedia_dataset(raw, as_of_date="2024-12-31")

    assert cleaned["Date"].tolist() == ["2024-12-12"]
    assert cleaned["Year"].tolist() == [2024]
    assert cleaned["Era"].tolist() == ["Modern Operational"]


def test_recovery_outcome_does_not_treat_unsuccessful_as_success():
    assert parse_recovery_outcome("Unsuccessful landing") == (0, "Failure")
    assert parse_recovery_outcome("Failure") == (0, "Failure")
    assert parse_recovery_outcome("No attempt") == (0, "No Attempt")
    assert parse_recovery_outcome("Success (JRTI)") == (1, "Success (ASDS)")

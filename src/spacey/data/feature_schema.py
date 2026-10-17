"""
SpaceY Intelligence - Feature Schema and Contract Definitions
Defines valid schemas, pre-launch feature requirements, leakage tags, and scenario contracts.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
from spacey.config import LAUNCH_SITES, VALID_ORBITS, NUMERICAL_FEATURES, CATEGORICAL_FEATURES, BINARY_FEATURES, TARGET_COLUMN


SITE_ALIASES: Dict[str, str] = {
    # CCAFS SLC 40
    "CCAFS SLC 40": "CCAFS SLC 40",
    "Cape Canaveral, SLC-40": "CCAFS SLC 40",
    "Cape Canaveral, SLC‑40": "CCAFS SLC 40",
    "CCAFS": "CCAFS SLC 40",
    "CCSFS SLC 40": "CCAFS SLC 40",
    # KSC LC 39A
    "KSC LC 39A": "KSC LC 39A",
    "Kennedy, LC-39A": "KSC LC 39A",
    "Kennedy, LC‑39A": "KSC LC 39A",
    "LC-39A": "KSC LC 39A",
    # VAFB SLC 4E
    "VAFB SLC 4E": "VAFB SLC 4E",
    "Vandenberg, SLC-4E": "VAFB SLC 4E",
    "Vandenberg, SLC‑4E": "VAFB SLC 4E",
    "SLC-4E": "VAFB SLC 4E",
}

STANDARDIZED_SITES = list(LAUNCH_SITES.keys())

FEATURE_METADATA: Dict[str, Dict[str, Any]] = {
    "PayloadMass": {
        "type": "float",
        "unit": "kg",
        "description": "Total mass of payload cargo delivered to orbit",
        "min": 100.0,
        "max": 25000.0,
        "default": 5000.0,
        "leakage_risk": "SAFE_PRE_LAUNCH",
    },
    "LaunchSite": {
        "type": "categorical",
        "options": STANDARDIZED_SITES,
        "description": "Designated launch complex for the mission",
        "default": "CCAFS SLC 40",
        "leakage_risk": "SAFE_PRE_LAUNCH",
    },
    "Orbit": {
        "type": "categorical",
        "options": VALID_ORBITS,
        "description": "Target orbital regime for deployment",
        "default": "LEO",
        "leakage_risk": "SAFE_PRE_LAUNCH",
    },
    "Flights": {
        "type": "int",
        "description": "Number of times this booster stage has flown (1 = maiden flight)",
        "min": 1,
        "max": 25,
        "default": 1,
        "leakage_risk": "SAFE_PRE_LAUNCH",
    },
    "GridFins": {
        "type": "int",
        "description": "Whether vehicle is equipped with aerodynamic titanium/aluminum grid fins (1 or 0)",
        "options": [0, 1],
        "default": 1,
        "leakage_risk": "SAFE_PRE_LAUNCH",
    },
    "Legs": {
        "type": "int",
        "description": "Whether vehicle is equipped with deployable carbon-fiber landing legs (1 or 0)",
        "options": [0, 1],
        "default": 1,
        "leakage_risk": "SAFE_PRE_LAUNCH",
    },
    "Block": {
        "type": "int",
        "description": "Booster design iteration block version (Block 1 through Block 5)",
        "min": 1,
        "max": 5,
        "default": 5,
        "leakage_risk": "SAFE_PRE_LAUNCH",
    },
    "Reused": {
        "type": "int",
        "description": "Whether the first-stage core is flight-proven (1) or newly manufactured (0)",
        "options": [0, 1],
        "default": 0,
        "leakage_risk": "SAFE_PRE_LAUNCH",
    },
}


class LaunchScenarioInput(BaseModel):
    """
    Validated Pydantic contract for a proposed launch scenario prediction.
    Strictly accepts only pre-launch knowable features to prevent target leakage.
    """
    payload_mass: float = Field(
        default=5000.0,
        ge=0.0,
        le=30000.0,
        description="Payload mass in kilograms"
    )
    launch_site: str = Field(
        default="CCAFS SLC 40",
        description="Launch complex identifier"
    )
    orbit: str = Field(
        default="LEO",
        description="Target orbital trajectory"
    )
    flights: int = Field(
        default=1,
        ge=1,
        le=30,
        description="Total flights count for this booster stage"
    )
    grid_fins: int = Field(
        default=1,
        ge=0,
        le=1,
        description="Equipped with grid fins (1=Yes, 0=No)"
    )
    legs: int = Field(
        default=1,
        ge=0,
        le=1,
        description="Equipped with landing legs (1=Yes, 0=No)"
    )
    block: int = Field(
        default=5,
        ge=1,
        le=5,
        description="Falcon 9 booster architecture block version (1-5)"
    )
    reused: int = Field(
        default=0,
        ge=0,
        le=1,
        description="Booster has flown previously (1=Yes, 0=No)"
    )

    @field_validator("launch_site")
    @classmethod
    def validate_site(cls, v: str) -> str:
        cleaned = SITE_ALIASES.get(v.strip(), v.strip())
        if cleaned not in STANDARDIZED_SITES:
            raise ValueError(
                f"Unknown launch site '{v}'. Must be one of: {STANDARDIZED_SITES}"
            )
        return cleaned

    @field_validator("orbit")
    @classmethod
    def validate_orbit(cls, v: str) -> str:
        clean_orbit = v.strip().upper()
        if clean_orbit not in VALID_ORBITS:
            # Check if case-insensitive match or prefix
            for valid in VALID_ORBITS:
                if valid.upper() == clean_orbit:
                    return valid
            raise ValueError(
                f"Unknown orbit '{v}'. Must be one of: {VALID_ORBITS}"
            )
        return clean_orbit

    def to_feature_dict(self) -> Dict[str, Any]:
        """Maps scenario into standardized training feature column names."""
        return {
            "PayloadMass": float(self.payload_mass),
            "LaunchSite": str(self.launch_site),
            "Orbit": str(self.orbit),
            "Flights": int(self.flights),
            "GridFins": int(self.grid_fins),
            "Legs": int(self.legs),
            "Block": int(self.block),
            "Reused": int(self.reused),
        }

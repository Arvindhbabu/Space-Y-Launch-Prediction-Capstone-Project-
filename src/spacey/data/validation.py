"""
SpaceY Intelligence - Data Validation and Quality Assurance
Provides schema checks, data health diagnostics, and structured data quality reporting.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from spacey.config import VALID_ORBITS, TARGET_COLUMN
from spacey.data.feature_schema import STANDARDIZED_SITES


@dataclass
class DataQualityReport:
    """Encapsulates comprehensive data quality findings and schema health."""
    dataset_name: str
    total_rows: int
    total_columns: int
    column_names: List[str]
    missing_counts: Dict[str, int]
    missing_percentages: Dict[str, float]
    duplicate_rows_count: int
    target_distribution: Dict[str, Any]
    schema_valid: bool
    validation_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_name": self.dataset_name,
            "total_rows": self.total_rows,
            "total_columns": self.total_columns,
            "column_names": self.column_names,
            "missing_counts": self.missing_counts,
            "missing_percentages": self.missing_percentages,
            "duplicate_rows_count": self.duplicate_rows_count,
            "target_distribution": self.target_distribution,
            "schema_valid": self.schema_valid,
            "validation_errors": self.validation_errors,
            "warnings": self.warnings,
        }


def validate_dataset(
    df: Optional[pd.DataFrame],
    dataset_name: str = "SpaceX Launch Dataset",
    require_target: bool = True,
) -> DataQualityReport:
    """
    Performs rigorous data quality audit on a DataFrame.
    Gracefully handles empty, corrupt, or missing DataFrames.
    """
    errors: List[str] = []
    warnings: List[str] = []

    if df is None:
        return DataQualityReport(
            dataset_name=dataset_name,
            total_rows=0,
            total_columns=0,
            column_names=[],
            missing_counts={},
            missing_percentages={},
            duplicate_rows_count=0,
            target_distribution={},
            schema_valid=False,
            validation_errors=["Dataset is None / Not loaded"],
        )

    if df.empty:
        return DataQualityReport(
            dataset_name=dataset_name,
            total_rows=0,
            total_columns=len(df.columns),
            column_names=list(df.columns),
            missing_counts={},
            missing_percentages={},
            duplicate_rows_count=0,
            target_distribution={},
            schema_valid=False,
            validation_errors=["Dataset is empty (0 rows)"],
        )

    total_rows = len(df)
    total_cols = len(df.columns)
    col_names = list(df.columns)

    # Missing values
    missing_counts = df.isnull().sum().to_dict()
    missing_percentages = {
        col: round((count / total_rows) * 100, 2)
        for col, count in missing_counts.items()
    }

    # Duplicates
    dup_count = int(df.duplicated().sum())
    if dup_count > 0:
        warnings.append(f"Detected {dup_count} duplicated rows.")

    # Target audit
    target_dist: Dict[str, Any] = {}
    target_col = None
    for cand in ["Class", "Landing_Success", "class", "target"]:
        if cand in df.columns:
            target_col = cand
            break

    if require_target:
        if target_col is None:
            errors.append(f"Mandatory target column '{TARGET_COLUMN}' not found.")
        else:
            vc = df[target_col].value_counts(dropna=False).to_dict()
            target_dist["counts"] = {str(k): int(v) for k, v in vc.items()}
            # Check for non-binary or NaN target
            nan_targets = int(df[target_col].isna().sum())
            if nan_targets > 0:
                warnings.append(f"Target column '{target_col}' has {nan_targets} NaN values ({nan_targets/total_rows*100:.1f}%).")
            unique_targets = set(df[target_col].dropna().unique())
            valid_binary = unique_targets.issubset({0, 1, 0.0, 1.0})
            if not valid_binary:
                errors.append(f"Target values {unique_targets} are not strictly binary {0, 1}.")

    # Feature value sanity checks
    if "PayloadMass" in df.columns:
        neg_payload = (df["PayloadMass"] < 0).sum()
        if neg_payload > 0:
            errors.append(f"PayloadMass contains {neg_payload} negative values.")

    if "LaunchSite" in df.columns:
        invalid_sites = set(df["LaunchSite"].dropna().unique()) - set(STANDARDIZED_SITES)
        if invalid_sites:
            warnings.append(f"Non-standard launch sites observed: {list(invalid_sites)[:5]}")

    if "Orbit" in df.columns:
        invalid_orbits = set(df["Orbit"].dropna().str.upper().unique()) - set(VALID_ORBITS)
        if invalid_orbits:
            warnings.append(f"Uncommon orbit types observed: {list(invalid_orbits)[:5]}")

    is_valid = len(errors) == 0

    return DataQualityReport(
        dataset_name=dataset_name,
        total_rows=total_rows,
        total_columns=total_cols,
        column_names=col_names,
        missing_counts=missing_counts,
        missing_percentages=missing_percentages,
        duplicate_rows_count=dup_count,
        target_distribution=target_dist,
        schema_valid=is_valid,
        validation_errors=errors,
        warnings=warnings,
    )

"""
SpaceY Intelligence - Model Registry and Artifact Management
Provides deterministic saving, loading, versioning, provenance metadata serialization,
and runtime environment compatibility verification.
"""

import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import joblib
import sklearn
import numpy as np
import pandas as pd

from spacey.config import REGISTRY_DIR
from spacey.logging_config import setup_logger

logger = setup_logger("spacey.registry")

ARTIFACT_FILENAME = "best_pipeline.joblib"
METADATA_FILENAME = "registry_metadata.json"


def check_model_compatibility(
    metadata: Optional[Dict[str, Any]],
    raise_on_incompatible: bool = False,
) -> Dict[str, Any]:
    """
    Validates and reports compatibility between training and inference environments.

    Serialized scikit-learn estimators (joblib/pickle) rely on internal class structures
    that can differ across minor scikit-learn releases (e.g. 1.5.x vs 1.9.x). Serialized
    models should always be executed in a matching, compatible virtual environment.
    """
    if not metadata:
        return {
            "is_compatible": True,
            "warning": "No metadata provided for compatibility check.",
        }

    package_versions = metadata.get("package_versions", {})
    train_sklearn = str(package_versions.get("scikit-learn") or metadata.get("sklearn_version", "unknown"))
    train_python = str(package_versions.get("python") or metadata.get("python_version", "unknown"))

    current_sklearn = str(sklearn.__version__)
    current_python = str(sys.version.split()[0])

    def get_major_minor(v_str: str) -> str:
        parts = v_str.strip().split(".")
        if len(parts) >= 2:
            return f"{parts[0]}.{parts[1]}"
        return v_str

    train_sk_mm = get_major_minor(train_sklearn)
    curr_sk_mm = get_major_minor(current_sklearn)

    is_compatible = (train_sk_mm == curr_sk_mm)

    report = {
        "is_compatible": is_compatible,
        "training_sklearn": train_sklearn,
        "inference_sklearn": current_sklearn,
        "training_python": train_python,
        "inference_python": current_python,
    }

    if not is_compatible:
        msg = (
            f"Model Compatibility Mismatch: Artifact was serialized with scikit-learn {train_sklearn} "
            f"(Python {train_python}), but inference environment is running scikit-learn {current_sklearn} "
            f"(Python {current_python}). Serialized scikit-learn estimators are not guaranteed to be "
            f"binary-compatible across different minor versions. Please load and execute this model inside "
            f"the designated project virtual environment (.venv) or retrain using the current environment."
        )
        logger.warning(msg)
        report["warning"] = msg
        if raise_on_incompatible:
            raise RuntimeError(msg)
    else:
        logger.info(
            "Model compatibility verified: training scikit-learn %s matches inference runtime %s (Python %s)",
            train_sklearn, current_sklearn, current_python
        )
        report["message"] = "Environment is fully compatible."

    return report


def save_model_artifact(
    pipeline,
    metadata: Dict[str, Any],
    registry_dir: Path = REGISTRY_DIR,
) -> Tuple[Path, Path]:
    """
    Persists trained Pipeline and corresponding governance metadata into the registry.
    Records Python, scikit-learn, numpy, pandas, and joblib provenance.
    """
    registry_dir.mkdir(parents=True, exist_ok=True)
    model_path = registry_dir / ARTIFACT_FILENAME
    meta_path = registry_dir / METADATA_FILENAME

    metadata["saved_at"] = datetime.now(timezone.utc).isoformat()
    metadata["package_versions"] = {
        "scikit-learn": sklearn.__version__,
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "joblib": joblib.__version__,
        "python": sys.version.split()[0],
    }
    metadata["python_version"] = sys.version
    metadata["sklearn_version"] = sklearn.__version__

    joblib.dump(pipeline, model_path)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info("Persisted model pipeline to %s and metadata to %s", model_path, meta_path)
    return model_path, meta_path


def load_registered_model(registry_dir: Path = REGISTRY_DIR) -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
    """
    Loads active registered Pipeline and governance metadata from the model registry.
    Validates environment compatibility between training and runtime.
    Returns (None, None) gracefully if registry is empty.
    """
    model_path = registry_dir / ARTIFACT_FILENAME
    meta_path = registry_dir / METADATA_FILENAME

    if not model_path.exists() or not meta_path.exists():
        logger.warning("No registered model artifact found in %s", registry_dir)
        return None, None

    metadata = None
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        check_model_compatibility(metadata, raise_on_incompatible=False)
    except Exception as meta_exc:
        logger.warning("Could not read registry metadata for compatibility check: %s", meta_exc)

    try:
        pipeline = joblib.load(model_path)
        logger.info("Loaded registered model '%s' successfully", metadata.get("model_name", "Unknown") if metadata else "Unknown")
        return pipeline, metadata
    except Exception as exc:
        logger.error(
            "Failed to deserialize registered model from %s: %s. "
            "Serialized scikit-learn models must be loaded in a compatible environment matching training.",
            model_path, str(exc)
        )
        return None, metadata

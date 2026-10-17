"""
Unit Tests for Machine Learning Pipeline & Evaluation
"""

import pytest
import pandas as pd
import numpy as np
from spacey.config import NUMERICAL_FEATURES, CATEGORICAL_FEATURES, BINARY_FEATURES, TARGET_COLUMN
from spacey.models.pipeline import build_preprocessor, build_model_pipeline
from spacey.models.evaluator import evaluate_classifier_predictions
from spacey.models.registry import load_registered_model, check_model_compatibility
from sklearn.linear_model import LogisticRegression


def test_preprocessor_fitting():
    df = pd.DataFrame({
        "PayloadMass": [2000.0, 5000.0, np.nan],
        "Flights": [1, 2, 3],
        "Block": [1, 5, 5],
        "FlightNumber": [1, 2, 3],
        "LaunchSite": ["CCAFS SLC 40", "KSC LC 39A", "VAFB SLC 4E"],
        "Orbit": ["LEO", "GTO", "SSO"],
        "GridFins": [0, 1, 1],
        "Legs": [0, 1, 1],
        "Reused": [0, 1, 1],
    })
    preproc = build_preprocessor()
    transformed = preproc.fit_transform(df)

    assert transformed.shape[0] == 3
    # Check that imputation replaced NaN without errors
    assert not np.isnan(transformed).any()


def test_evaluator_metrics():
    y_true = np.array([1, 1, 0, 0, 1, 0])
    y_pred = np.array([1, 1, 0, 1, 1, 0])
    y_proba = np.array([0.9, 0.8, 0.1, 0.6, 0.85, 0.2])

    metrics = evaluate_classifier_predictions(y_true, y_pred, y_proba, model_name="TestModel")

    assert metrics["accuracy"] == pytest.approx(5 / 6, abs=1e-3)
    assert 0.0 <= metrics["roc_auc"] <= 1.0
    assert 0.0 <= metrics["brier_score"] <= 1.0
    assert metrics["confusion_matrix"]["tp"] == 3
    assert metrics["confusion_matrix"]["fp"] == 1
    assert metrics["confusion_matrix"]["fn"] == 0
    assert metrics["confusion_matrix"]["tn"] == 2


def test_registered_model_inference():
    pipeline, metadata = load_registered_model()
    assert pipeline is not None
    assert metadata is not None

    # Verify model artifact environment compatibility check
    compat = check_model_compatibility(metadata)
    assert compat["is_compatible"] is True

    # Test single-scenario prediction
    scenario = pd.DataFrame([{
        "PayloadMass": 5000.0,
        "LaunchSite": "CCAFS SLC 40",
        "Orbit": "LEO",
        "Flights": 2,
        "GridFins": 1,
        "Legs": 1,
        "Block": 5,
        "Reused": 1,
        "FlightNumber": 90,
    }])

    proba = pipeline.predict_proba(scenario)[0][1]
    pred = pipeline.predict(scenario)[0]

    assert 0.0 <= proba <= 1.0
    assert pred in [0, 1]

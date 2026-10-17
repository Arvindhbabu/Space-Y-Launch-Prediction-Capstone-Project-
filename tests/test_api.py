"""
Integration Tests for FastAPI Prediction & Economics Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from spacey.services.api import app

client = TestClient(app)


def test_api_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "SpaceY Intelligence API"
    assert data["model_loaded"] is True


def test_api_metadata_endpoint():
    resp = client.get("/metadata")
    assert resp.status_code == 200
    data = resp.json()
    assert "model_name" in data
    assert "evaluation_metrics" in data
    assert "features" in data


def test_api_predict_single_scenario():
    payload = {
        "payload_mass": 5000.0,
        "launch_site": "CCAFS SLC 40",
        "orbit": "LEO",
        "flights": 2,
        "grid_fins": 1,
        "legs": 1,
        "block": 5,
        "reused": 1,
    }
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["predicted_class"] in [0, 1]
    assert 0.0 <= data["recovery_probability"] <= 1.0
    assert data["decision_threshold"] == 0.50
    assert len(data["local_attribution"]) > 0


def test_api_predict_invalid_scenario():
    # Negative payload mass
    payload = {
        "payload_mass": -500.0,
        "launch_site": "CCAFS SLC 40",
        "orbit": "LEO",
    }
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 422  # Unprocessable Entity (Pydantic validation failure)


def test_api_predict_batch():
    batch_payload = {
        "scenarios": [
            {
                "payload_mass": 3500.0,
                "launch_site": "CCAFS SLC 40",
                "orbit": "LEO",
                "flights": 1,
                "grid_fins": 1,
                "legs": 1,
                "block": 5,
                "reused": 0,
            },
            {
                "payload_mass": 9500.0,
                "launch_site": "KSC LC 39A",
                "orbit": "GTO",
                "flights": 4,
                "grid_fins": 1,
                "legs": 1,
                "block": 5,
                "reused": 1,
            },
        ]
    }
    resp = client.post("/predict/batch", json=batch_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_scenarios"] == 2
    assert len(data["predictions"]) == 2


def test_api_economics_endpoint():
    econ_payload = {
        "recovery_probability": 0.80,
        "contract_revenue_m": 67.0,
        "baseline_mission_cost_m": 55.0,
        "recovery_ops_cost_m": 2.5,
        "booster_asset_value_m": 25.0,
        "refurbishment_cost_m": 5.0,
        "failure_contingency_m": 3.0,
        "risk_reserve_pct": 5.0,
    }
    resp = client.post("/economics", json=econ_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "expected_cost_m" in data
    assert "expected_margin_m" in data
    assert "break_even_probability" in data
    assert data["expected_cost_m"] > 0.0

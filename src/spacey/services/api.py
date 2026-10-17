"""
SpaceY Intelligence - FastAPI Microservice for Launch Prediction & Mission Economics
Typed REST endpoints with Pydantic contracts, input validation, and model provenance.
"""

import sys
from pathlib import Path

# Ensure src directory is in sys.path when invoked via uvicorn CLI
src_dir = Path(__file__).resolve().parent.parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import pandas as pd
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict

from spacey.data.feature_schema import LaunchScenarioInput
from spacey.models.registry import load_registered_model
from spacey.models.explainability import explain_single_scenario
from spacey.data.loader import load_and_prepare_benchmark_data
from spacey.economics.calculator import (
    MissionEconomicParameters,
    evaluate_launch_economics,
    EconomicEvaluationResult,
)

app = FastAPI(
    title="SpaceY Intelligence API",
    description="Mission decision-support, first-stage recovery prediction, and commercial launch economics API.",
    version="1.0.0",
)

# Load global model and reference data on startup
pipeline, metadata = load_registered_model()
try:
    ref_df, _ = load_and_prepare_benchmark_data()
except Exception:
    ref_df = pd.DataFrame()


class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    status: str
    service: str
    timestamp: str
    model_loaded: bool
    model_name: Optional[str] = None


class PredictionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    predicted_class: int
    predicted_outcome: str
    recovery_probability: float
    decision_threshold: float
    margin_vs_threshold_pct: float
    model_name: str
    local_attribution: List[Dict[str, Any]]
    disclaimer: str


class BatchPredictionRequest(BaseModel):
    scenarios: List[LaunchScenarioInput]


class BatchPredictionResponse(BaseModel):
    total_scenarios: int
    predictions: List[PredictionResponse]


class EconomicsRequest(BaseModel):
    recovery_probability: float = Field(ge=0.0, le=1.0, default=0.75)
    contract_revenue_m: float = Field(ge=1.0, default=67.0)
    baseline_mission_cost_m: float = Field(ge=1.0, default=55.0)
    recovery_ops_cost_m: float = Field(ge=0.1, default=2.5)
    booster_asset_value_m: float = Field(ge=1.0, default=25.0)
    refurbishment_cost_m: float = Field(ge=0.1, default=5.0)
    failure_contingency_m: float = Field(ge=0.0, default=3.0)
    risk_reserve_pct: float = Field(ge=0.0, le=50.0, default=5.0)


@app.get("/health", response_model=HealthResponse)
def get_health():
    """Health check endpoint indicating service availability and model loading status."""
    return HealthResponse(
        status="healthy",
        service="SpaceY Intelligence API",
        timestamp=datetime.now(timezone.utc).isoformat(),
        model_loaded=pipeline is not None,
        model_name=metadata.get("model_name") if metadata else None,
    )


@app.get("/metadata")
def get_metadata():
    """Returns active model governance metadata, evaluation metrics, and feature schemas."""
    if metadata is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model metadata is unavailable. Model registry may be empty.",
        )
    return metadata


@app.post("/predict", response_model=PredictionResponse)
def predict_scenario(scenario: LaunchScenarioInput):
    """Predicts booster landing success probability and generates feature attribution for a single scenario."""
    if pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Predictive pipeline is not loaded.",
        )

    scenario_dict = scenario.to_feature_dict()
    scenario_dict["FlightNumber"] = 90  # Reference flight sequence for modern missions
    input_df = pd.DataFrame([scenario_dict])

    proba = float(pipeline.predict_proba(input_df)[0][1])
    threshold = metadata.get("selected_decision_threshold", 0.50) if metadata else 0.50
    pred_class = 1 if proba >= threshold else 0
    outcome_label = "Successful Landing (ASDS/RTLS)" if pred_class == 1 else "Recovery Loss / Expendable"

    # Local feature attribution
    attribution = []
    if not ref_df.empty:
        attribution = explain_single_scenario(pipeline, input_df, ref_df)

    return PredictionResponse(
        predicted_class=pred_class,
        predicted_outcome=outcome_label,
        recovery_probability=round(proba, 4),
        decision_threshold=threshold,
        margin_vs_threshold_pct=round((proba - threshold) * 100, 2),
        model_name=metadata.get("model_name", "Trained Classifier") if metadata else "Unknown",
        local_attribution=attribution,
        disclaimer=(
            "Advisory decision-support only. Probabilities represent historical statistical "
            "correlations and do not constitute certified aerospace flight authorizations."
        ),
    )


@app.post("/predict/batch", response_model=BatchPredictionResponse)
def predict_batch(request: BatchPredictionRequest):
    """Batch prediction endpoint for multi-scenario simulations."""
    if pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Predictive pipeline is not loaded.",
        )

    responses = [predict_scenario(scen) for scen in request.scenarios]
    return BatchPredictionResponse(
        total_scenarios=len(responses),
        predictions=responses,
    )


@app.post("/economics")
def calculate_economics(req: EconomicsRequest):
    """Calculates expected mission cost, contribution margin, and break-even probability."""
    params = MissionEconomicParameters(
        contract_revenue_m=req.contract_revenue_m,
        baseline_mission_cost_m=req.baseline_mission_cost_m,
        recovery_ops_cost_m=req.recovery_ops_cost_m,
        booster_asset_value_m=req.booster_asset_value_m,
        refurbishment_cost_m=req.refurbishment_cost_m,
        failure_contingency_m=req.failure_contingency_m,
        risk_reserve_pct=req.risk_reserve_pct,
    )
    result = evaluate_launch_economics(req.recovery_probability, params)
    return result.to_dict()

"""
Smoke Tests for Streamlit UI Components & Charts
"""

import pytest
import pandas as pd
from spacey.ui.charts import (
    plot_confusion_matrix,
    plot_roc_curve,
    plot_calibration_curve,
    plot_orbit_success_rates,
    plot_site_success_rates,
    plot_annual_trends,
    plot_economics_sensitivity,
    plot_scenario_attribution,
)
from spacey.analytics.sql_engine import SpaceYAnalyticsDB


def test_ui_charts_generation():
    # Confusion matrix
    cm_dict = {"tn": 2, "fp": 4, "fn": 0, "tp": 12}
    fig_cm = plot_confusion_matrix(cm_dict)
    assert fig_cm is not None

    # ROC curve
    roc_pts = [{"fpr": 0.0, "tpr": 0.0}, {"fpr": 0.2, "tpr": 0.8}, {"fpr": 1.0, "tpr": 1.0}]
    fig_roc = plot_roc_curve(roc_pts, 0.85)
    assert fig_roc is not None

    # Calibration curve
    calib_pts = [{"prob_pred": 0.2, "prob_true": 0.25}, {"prob_pred": 0.8, "prob_true": 0.78}]
    fig_calib = plot_calibration_curve(calib_pts, 0.14)
    assert fig_calib is not None

    # Orbit chart
    orbit_df = pd.DataFrame({
        "Orbit": ["LEO", "GTO"],
        "success_rate_pct": [80.0, 65.0],
        "total_launches": [100, 30],
    })
    fig_orbit = plot_orbit_success_rates(orbit_df)
    assert fig_orbit is not None

    # Site chart
    site_df = pd.DataFrame({
        "LaunchSite": ["CCAFS SLC 40", "KSC LC 39A"],
        "success_rate_pct": [78.0, 82.0],
        "successful_landings": [78, 41],
        "total_launches": [100, 50],
    })
    fig_site = plot_site_success_rates(site_df)
    assert fig_site is not None

    # Economics sensitivity
    sens_df = pd.DataFrame({
        "Recovery_Probability": [0.0, 0.5, 1.0],
        "Expected_Margin_M": [5.0, 15.0, 25.0],
        "Expected_Cost_M": [60.0, 50.0, 40.0],
    })
    fig_sens = plot_economics_sensitivity(sens_df, 0.25)
    assert fig_sens is not None


def test_sql_database_engine():
    db = SpaceYAnalyticsDB()
    summary = db.get_overall_summary()
    assert not summary.empty
    assert "total_launches" in summary.columns
    assert summary["total_launches"].iloc[0] > 0

"""
SpaceY Intelligence - Page 5: Model Intelligence
Benchmarking leaderboard, ROC curves, calibration analysis, and permutation feature importance.
"""

import sys
from pathlib import Path

# Add src to sys.path
root_dir = Path(__file__).resolve().parent.parent
src_dir = root_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import streamlit as st
import pandas as pd
import plotly.express as px
from spacey.ui.theme import (
    apply_spacey_theme,
    render_page_header,
    render_section_header,
    get_gradient_icon_html,
    clean_html,
)
from spacey.ui.charts import (
    plot_confusion_matrix,
    plot_roc_curve,
    plot_calibration_curve,
)
from spacey.models.registry import load_registered_model

st.set_page_config(page_title="Model Intelligence | SpaceY Intelligence", layout="wide")
apply_spacey_theme()

render_page_header(
    title="Model Intelligence & Evaluation Lab",
    subtitle="Rigorous cross-validation benchmarks, discrimination curves, probability calibration, and feature attribution.",
    badge_text="ML QUALITY GATES",
    icon="cpu",
    variant="blue",
)

pipeline, metadata = load_registered_model()

if metadata is None:
    st.error("No model evaluation metadata found. Please train models first using 'python scripts/train_model.py'.")
    st.stop()

# Leaderboard section
render_section_header(
    title="Multi-Model Cross-Validation & Holdout Benchmark Leaderboard",
    subtitle="7 candidate architectures evaluated under strict leakage prevention protocols.",
    icon="award",
    variant="blue",
)

st.markdown("""
All models were tuned via **5-Fold Stratified Cross-Validation** on training folds, with preprocessing (`ColumnTransformer`)
fitted strictly within fold partitions. The final evaluation was computed on an independent **20% holdout test partition** (18 launches: 12 successes, 6 failures).
""")

leaderboard_data = metadata.get("all_models_comparison", [])
if leaderboard_data:
    lead_df = pd.DataFrame(leaderboard_data)
    st.dataframe(lead_df, use_container_width=True, hide_index=True)

st.markdown("---")

win_name = metadata.get("model_name", "Winning Model")
win_metrics = metadata.get("evaluation_metrics", {})

render_section_header(
    title=f"Selected Production Pipeline: {win_name.replace('_', ' ')}",
    subtitle="Top-ranked out-of-sample generalizer with optimal ROC-AUC and probability calibration.",
    icon="check",
    variant="emerald",
)

kpi_m1, kpi_m2, kpi_m3, kpi_m4, kpi_m5 = st.columns(5)
with kpi_m1:
    st.metric("Holdout Accuracy", f"{win_metrics.get('accuracy', 0.0):.1%}")
with kpi_m2:
    st.metric("Holdout ROC-AUC", f"{win_metrics.get('roc_auc', 0.0):.3f}")
with kpi_m3:
    st.metric("Holdout F1-Score", f"{win_metrics.get('f1_score', 0.0):.3f}")
with kpi_m4:
    st.metric("Brier Calibration Score", f"{win_metrics.get('brier_score', 0.0):.3f}")
with kpi_m5:
    st.metric("Inference Latency", f"{win_metrics.get('inference_latency_ms', 0.0):.2f} ms")

st.markdown("---")

# Visual Diagnostic Curves
col_plot1, col_plot2 = st.columns(2)

with col_plot1:
    cm_dict = win_metrics.get("confusion_matrix", {"tn": 2, "fp": 4, "fn": 0, "tp": 12})
    st.plotly_chart(plot_confusion_matrix(cm_dict, model_name=win_name), use_container_width=True)

with col_plot2:
    roc_points = win_metrics.get("roc_curve", [])
    roc_auc = win_metrics.get("roc_auc", 0.5)
    st.plotly_chart(plot_roc_curve(roc_points, roc_auc, model_name=win_name), use_container_width=True)

col_plot3, col_plot4 = st.columns(2)

with col_plot3:
    calib_points = win_metrics.get("calibration_curve", [])
    brier_score = win_metrics.get("brier_score", 0.2)
    st.plotly_chart(plot_calibration_curve(calib_points, brier_score), use_container_width=True)

with col_plot4:
    render_section_header(
        title="Decision Trade-Off & Error Analysis",
        subtitle="Operational costs of false positive versus false negative classifications.",
        icon="alert",
        variant="amber",
    )
    card_html = f"""
    <div class="telemetry-card">
    <ul style="padding-left:20px;margin-bottom:0;">
    <li style="margin-bottom:8px;"><strong>False Positive (FP) Risk</strong>: Model predicts recovery, but booster is lost at sea.
    <br><span style="color:#64748B;">Operational Cost: Incurs drone ship deployment, recovery fleet mobilization, and loss of residual hardware value.</span></li>
    <li style="margin-bottom:8px;"><strong>False Negative (FN) Risk</strong>: Model predicts crash/failure, leading to expending a booster that could have been recovered.
    <br><span style="color:#64748B;">Operational Cost: Forfeits $20M+ in reusability hardware asset savings.</span></li>
    <li><strong>Current Model Balance</strong>:
    <br>False Negatives: <b>{cm_dict.get('fn', 0)}</b> (High Sensitivity / Recall = <b>{win_metrics.get('recall', 0.0):.1%}</b>)
    <br>False Positives: <b>{cm_dict.get('fp', 0)}</b> (Specificity = <b>{win_metrics.get('specificity', 0.0):.1%}</b>)</li>
    </ul>
    </div>
    """
    st.markdown(clean_html(card_html), unsafe_allow_html=True)

st.markdown("---")

# Global Permutation Feature Importance
render_section_header(
    title="Global Permutation Feature Importance (Unseen Test Data)",
    subtitle="Drop in out-of-sample ROC-AUC when feature column is independently shuffled.",
    icon="activity",
    variant="purple",
)
perm_data = metadata.get("top_features_importance", [])
if perm_data:
    perm_df = pd.DataFrame(perm_data)
    fig_perm = px.bar(
        perm_df,
        x="Importance_Mean",
        y="Feature",
        error_x="Importance_Std",
        orientation="h",
        labels={"Importance_Mean": "Mean ROC-AUC Drop", "Feature": "Input Feature"},
        color="Importance_Mean",
        color_continuous_scale=[[0, "#93C5FD"], [1, "#1D4ED8"]],
    )
    fig_perm.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC",
        font=dict(color="#0F172A", family="'Plus Jakarta Sans', sans-serif"),
        xaxis=dict(gridcolor="#E2E8F0"),
        yaxis=dict(gridcolor="#E2E8F0", autorange="reversed"),
        margin=dict(l=60, r=40, t=20, b=40),
    )
    st.plotly_chart(fig_perm, use_container_width=True)

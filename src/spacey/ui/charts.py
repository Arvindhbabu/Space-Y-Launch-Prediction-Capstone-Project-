"""
SpaceY Intelligence - Modern Interactive Plotly Visualization Components
Generates clean, light-themed, publication-grade interactive charts with sample counts,
denominators, and high-contrast professional color palettes.
"""

from typing import List, Dict, Any
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Professional Light Theme Tokens
CHART_THEME = {
    "paper_bgcolor": "#FFFFFF",
    "plot_bgcolor": "#F8FAFC",
    "font": {"color": "#0F172A", "family": "'Plus Jakarta Sans', -apple-system, sans-serif"},
    "gridcolor": "#E2E8F0",
}


def plot_confusion_matrix(cm_dict: Dict[str, int], model_name: str = "Model") -> go.Figure:
    """Renders an interactive confusion matrix heatmap."""
    z = [
        [cm_dict["tn"], cm_dict["fp"]],
        [cm_dict["fn"], cm_dict["tp"]],
    ]
    x = ["Predicted Failure (0)", "Predicted Success (1)"]
    y = ["Actual Failure (0)", "Actual Success (1)"]

    annotations = []
    for i, row in enumerate(z):
        for j, val in enumerate(row):
            label = "TN" if (i == 0 and j == 0) else ("FP" if (i == 0 and j == 1) else ("FN" if (i == 1 and j == 0) else "TP"))
            annotations.append(
                dict(
                    x=x[j],
                    y=y[i],
                    text=f"<b>{val}</b><br><span style='font-size:11px; color:#475569;'>({label})</span>",
                    showarrow=False,
                    font=dict(color="#0F172A" if val < 8 else "#FFFFFF", size=16),
                )
            )

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=x,
            y=y,
            colorscale=[[0, "#EFF6FF"], [1, "#2563EB"]],
            showscale=False,
        )
    )
    fig.update_layout(
        title=f"Confusion Matrix: {model_name}",
        annotations=annotations,
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=CHART_THEME["font"],
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(gridcolor=CHART_THEME["gridcolor"]),
        yaxis=dict(gridcolor=CHART_THEME["gridcolor"]),
    )
    return fig


def plot_roc_curve(roc_points: List[Dict[str, float]], roc_auc: float, model_name: str = "Model") -> go.Figure:
    """Renders interactive ROC curve with diagonal no-discrimination baseline."""
    df = pd.DataFrame(roc_points)
    fig = go.Figure()

    # ROC curve
    fig.add_trace(
        go.Scatter(
            x=df["fpr"],
            y=df["tpr"],
            mode="lines",
            name=f"{model_name} (AUC = {roc_auc:.3f})",
            line=dict(color="#2563EB", width=3),
        )
    )

    # 45-degree reference line
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            name="Random Baseline (AUC = 0.500)",
            line=dict(color="#94A3B8", dash="dash", width=2),
        )
    )

    fig.update_layout(
        title=f"ROC Curve — {model_name} (AUC: {roc_auc:.3f})",
        xaxis_title="False Positive Rate (1 - Specificity)",
        yaxis_title="True Positive Rate (Sensitivity / Recall)",
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=CHART_THEME["font"],
        legend=dict(x=0.05, y=0.05, bgcolor="rgba(255, 255, 255, 0.9)", bordercolor="#E2E8F0", borderwidth=1),
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(gridcolor=CHART_THEME["gridcolor"], range=[0, 1]),
        yaxis=dict(gridcolor=CHART_THEME["gridcolor"], range=[0, 1.05]),
    )
    return fig


def plot_calibration_curve(calib_points: List[Dict[str, float]], brier_score: float) -> go.Figure:
    """Renders calibration curve comparing predicted probabilities with true empirical frequency."""
    fig = go.Figure()

    if calib_points:
        df = pd.DataFrame(calib_points)
        fig.add_trace(
            go.Scatter(
                x=df["prob_pred"],
                y=df["prob_true"],
                mode="lines+markers",
                name=f"Model (Brier: {brier_score:.3f})",
                line=dict(color="#0891B2", width=3),
                marker=dict(size=8, color="#0284C7"),
            )
        )

    # Perfectly calibrated line
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            name="Perfect Calibration",
            line=dict(color="#94A3B8", dash="dash", width=2),
        )
    )

    fig.update_layout(
        title=f"Probability Calibration Curve (Brier: {brier_score:.3f})",
        xaxis_title="Mean Predicted Probability",
        yaxis_title="Observed Fraction of Positives",
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=CHART_THEME["font"],
        legend=dict(x=0.05, y=0.85, bgcolor="rgba(255, 255, 255, 0.9)", bordercolor="#E2E8F0", borderwidth=1),
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(gridcolor=CHART_THEME["gridcolor"], range=[0, 1]),
        yaxis=dict(gridcolor=CHART_THEME["gridcolor"], range=[0, 1]),
    )
    return fig


def plot_orbit_success_rates(orbit_df: pd.DataFrame) -> go.Figure:
    """Renders landing success rate by orbit with sample counts."""
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=orbit_df["Orbit"],
            y=orbit_df["success_rate_pct"],
            text=[f"{sr:.1f}%<br>(n={tot})" for sr, tot in zip(orbit_df["success_rate_pct"], orbit_df["total_launches"])],
            textposition="auto",
            marker=dict(
                color=orbit_df["success_rate_pct"],
                colorscale=[[0, "#93C5FD"], [1, "#1D4ED8"]],
                line=dict(color="#1E40AF", width=1),
            ),
        )
    )
    fig.update_layout(
        title="Landing Success Rate by Orbit Destination (with Sample Counts)",
        xaxis_title="Orbit Destination",
        yaxis_title="Landing Success Rate (%)",
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=CHART_THEME["font"],
        yaxis=dict(range=[0, 115], gridcolor=CHART_THEME["gridcolor"]),
        xaxis=dict(gridcolor=CHART_THEME["gridcolor"]),
        margin=dict(l=40, r=40, t=50, b=40),
    )
    return fig


def plot_site_success_rates(site_df: pd.DataFrame) -> go.Figure:
    """Renders landing success rate by launch complex."""
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=site_df["LaunchSite"],
            y=site_df["success_rate_pct"],
            text=[f"{sr:.1f}%<br>({succ}/{tot})" for sr, succ, tot in zip(site_df["success_rate_pct"], site_df["successful_landings"], site_df["total_launches"])],
            textposition="auto",
            marker=dict(
                color="#0284C7",
                line=dict(color="#0369A1", width=1),
            ),
        )
    )
    fig.update_layout(
        title="Landing Success Rate by Launch Complex (Successes / Total Launches)",
        xaxis_title="Launch Complex",
        yaxis_title="Landing Success Rate (%)",
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=CHART_THEME["font"],
        yaxis=dict(range=[0, 115], gridcolor=CHART_THEME["gridcolor"]),
        xaxis=dict(gridcolor=CHART_THEME["gridcolor"]),
        margin=dict(l=40, r=40, t=50, b=40),
    )
    return fig


def plot_annual_trends(annual_df: pd.DataFrame) -> go.Figure:
    """Renders dual-axis annual launch cadence and success rate trajectory."""
    fig = go.Figure()

    # Launch Volume Bars
    fig.add_trace(
        go.Bar(
            x=annual_df["Year"],
            y=annual_df["total_launches"],
            name="Total Launches",
            marker=dict(color="#93C5FD", line=dict(color="#3B82F6", width=1)),
            yaxis="y1",
        )
    )

    # Success Rate Line
    fig.add_trace(
        go.Scatter(
            x=annual_df["Year"],
            y=annual_df["success_rate_pct"],
            name="Landing Success Rate (%)",
            mode="lines+markers",
            line=dict(color="#059669", width=3),
            marker=dict(size=8, color="#047857"),
            yaxis="y2",
        )
    )

    fig.update_layout(
        title="Annual Launch Cadence & Landing Success Rate Trajectory",
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=CHART_THEME["font"],
        xaxis=dict(gridcolor=CHART_THEME["gridcolor"], title="Year"),
        yaxis=dict(title="Launch Volume (Flights)", gridcolor=CHART_THEME["gridcolor"]),
        yaxis2=dict(
            title="Success Rate (%)",
            overlaying="y",
            side="right",
            range=[0, 105],
            gridcolor=CHART_THEME["gridcolor"],
        ),
        legend=dict(x=0.05, y=0.95, bgcolor="rgba(255, 255, 255, 0.9)", bordercolor="#E2E8F0", borderwidth=1),
        margin=dict(l=40, r=50, t=50, b=40),
    )
    return fig


def plot_economics_sensitivity(curve_df: pd.DataFrame, breakeven_p: float) -> go.Figure:
    """Renders sensitivity of expected margin and cost across recovery probabilities."""
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=curve_df["Recovery_Probability"] * 100,
            y=curve_df["Expected_Margin_M"],
            mode="lines",
            name="Expected Margin ($M)",
            line=dict(color="#059669", width=3),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=curve_df["Recovery_Probability"] * 100,
            y=curve_df["Expected_Cost_M"],
            mode="lines",
            name="Expected Cost ($M)",
            line=dict(color="#DC2626", width=2.5, dash="dot"),
        )
    )

    # Break-even vertical threshold line
    fig.add_vline(
        x=breakeven_p * 100,
        line_dash="dash",
        line_color="#D97706",
        line_width=2,
        annotation_text=f"Break-Even: {breakeven_p*100:.1f}%",
        annotation_position="top left",
    )

    fig.update_layout(
        title="Mission Economics Sensitivity to Recovery Probability",
        xaxis_title="Recovery Probability (%)",
        yaxis_title="Amount ($M USD)",
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=CHART_THEME["font"],
        legend=dict(x=0.05, y=0.95, bgcolor="rgba(255, 255, 255, 0.9)", bordercolor="#E2E8F0", borderwidth=1),
        xaxis=dict(gridcolor=CHART_THEME["gridcolor"]),
        yaxis=dict(gridcolor=CHART_THEME["gridcolor"]),
        margin=dict(l=40, r=40, t=50, b=40),
    )
    return fig


def plot_scenario_attribution(explanations: List[Dict[str, Any]]) -> go.Figure:
    """Renders local feature contribution attribution for a single scenario."""
    df = pd.DataFrame(explanations)
    colors = ["#059669" if imp >= 0 else "#DC2626" for imp in df["impact"]]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=df["feature"],
            x=df["impact"] * 100,
            orientation="h",
            marker=dict(color=colors),
            text=[f"{imp*100:+.1f}%" for imp in df["impact"]],
            textposition="auto",
        )
    )
    fig.update_layout(
        title="Local Feature Contribution Attribution vs Baseline",
        xaxis_title="Shift in Recovery Likelihood (%)",
        yaxis_title="Input Feature",
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=CHART_THEME["font"],
        xaxis=dict(gridcolor=CHART_THEME["gridcolor"]),
        yaxis=dict(gridcolor=CHART_THEME["gridcolor"], autorange="reversed"),
        margin=dict(l=80, r=40, t=50, b=40),
    )
    return fig

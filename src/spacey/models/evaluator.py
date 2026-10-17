"""
SpaceY Intelligence - Comprehensive Model Evaluation Engine
Computes discrimination, calibration, confusion matrices, and latency benchmarks.
"""

import time
from typing import Dict, Any, Tuple
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    roc_curve,
    precision_recall_curve,
)
from sklearn.calibration import calibration_curve


def evaluate_classifier_predictions(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray,
    model_name: str = "Classifier",
) -> Dict[str, Any]:
    """
    Computes a complete, defensible evaluation suite for binary classification.
    Safely handles edge cases like class imbalance or zero division.
    """
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)
    y_proba = np.asarray(y_proba).astype(float)

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    # Discrimination metrics
    acc = float(accuracy_score(y_true, y_pred))
    bal_acc = float(balanced_accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0

    # Probabilistic metrics
    try:
        roc_auc = float(roc_auc_score(y_true, y_proba))
    except Exception:
        roc_auc = 0.5

    try:
        pr_auc = float(average_precision_score(y_true, y_proba))
    except Exception:
        pr_auc = float(np.mean(y_true))

    brier = float(brier_score_loss(y_true, y_proba))

    # ROC curve points
    fpr_arr, tpr_arr, _ = roc_curve(y_true, y_proba)
    roc_points = [{"fpr": round(float(f), 4), "tpr": round(float(t), 4)} for f, t in zip(fpr_arr, tpr_arr)]

    # Precision-Recall curve points
    prec_arr, rec_arr, _ = precision_recall_curve(y_true, y_proba)
    pr_points = [{"precision": round(float(p), 4), "recall": round(float(r), 4)} for p, r in zip(prec_arr, rec_arr)]

    # Calibration curve (5 bins for small-to-medium datasets)
    try:
        prob_true, prob_pred = calibration_curve(y_true, y_proba, n_bins=5, strategy="uniform")
        calib_points = [
            {"prob_pred": round(float(pp), 4), "prob_true": round(float(pt), 4)}
            for pp, pt in zip(prob_pred, prob_true)
        ]
    except Exception:
        calib_points = []

    return {
        "model_name": model_name,
        "sample_size": len(y_true),
        "accuracy": round(acc, 4),
        "balanced_accuracy": round(bal_acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "specificity": round(spec, 4),
        "f1_score": round(f1_score(y_true, y_pred, zero_division=0), 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "brier_score": round(brier, 4),
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        },
        "roc_curve": roc_points,
        "pr_curve": pr_points,
        "calibration_curve": calib_points,
    }


def measure_inference_latency(pipeline, X_sample, n_iterations: int = 50) -> float:
    """Measures single-scenario inference latency in milliseconds."""
    # Warmup
    _ = pipeline.predict_proba(X_sample.iloc[:1])
    start = time.perf_counter()
    for _ in range(n_iterations):
        _ = pipeline.predict_proba(X_sample.iloc[:1])
    total = time.perf_counter() - start
    return round((total / n_iterations) * 1000.0, 3)

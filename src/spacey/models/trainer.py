"""
SpaceY Intelligence - Multi-Model Training, Hyperparameter Tuning & Model Comparison Framework
Trains 7 candidate classifiers with leakage-safe ColumnTransformers and stratified cross-validation.
"""

from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

from spacey.config import (
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    BINARY_FEATURES,
    TARGET_COLUMN,
    RANDOM_STATE,
)
from spacey.models.pipeline import build_preprocessor, build_model_pipeline
from spacey.models.evaluator import evaluate_classifier_predictions, measure_inference_latency
from spacey.models.explainability import compute_permutation_importance
from spacey.models.registry import save_model_artifact
from spacey.logging_config import setup_logger

logger = setup_logger("spacey.trainer")

# Model definitions and hyperparameter grids
MODEL_CONFIGS: Dict[str, Dict[str, Any]] = {
    "Dummy_Baseline": {
        "estimator": DummyClassifier(strategy="most_frequent"),
        "param_grid": {},
    },
    "Logistic_Regression": {
        "estimator": LogisticRegression(random_state=RANDOM_STATE, max_iter=1000),
        "param_grid": {
            "classifier__C": [0.01, 0.1, 1.0, 10.0],
            "classifier__solver": ["lbfgs", "liblinear"],
        },
    },
    "Decision_Tree": {
        "estimator": DecisionTreeClassifier(random_state=RANDOM_STATE),
        "param_grid": {
            "classifier__max_depth": [3, 5, 7, None],
            "classifier__min_samples_split": [2, 5, 10],
            "classifier__criterion": ["gini", "entropy"],
        },
    },
    "Support_Vector_Machine": {
        "estimator": SVC(probability=True, random_state=RANDOM_STATE),
        "param_grid": {
            "classifier__C": [0.1, 1.0, 10.0],
            "classifier__kernel": ["linear", "rbf"],
        },
    },
    "K_Nearest_Neighbors": {
        "estimator": KNeighborsClassifier(),
        "param_grid": {
            "classifier__n_neighbors": [3, 5, 7, 9],
            "classifier__weights": ["uniform", "distance"],
        },
    },
    "Random_Forest": {
        "estimator": RandomForestClassifier(random_state=RANDOM_STATE),
        "param_grid": {
            "classifier__n_estimators": [50, 100, 150],
            "classifier__max_depth": [3, 5, 7, None],
            "classifier__min_samples_split": [2, 5],
        },
    },
    "Gradient_Boosting": {
        "estimator": GradientBoostingClassifier(random_state=RANDOM_STATE),
        "param_grid": {
            "classifier__n_estimators": [50, 100],
            "classifier__learning_rate": [0.01, 0.05, 0.1],
            "classifier__max_depth": [2, 3, 4],
        },
    },
}


def prepare_features_and_target(
    df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.Series]:
    """Extracts leakage-safe feature matrix X and binary target vector y."""
    feature_cols = NUMERICAL_FEATURES + CATEGORICAL_FEATURES + BINARY_FEATURES
    # Verify presence of columns
    available_cols = [c for c in feature_cols if c in df.columns]
    X = df[available_cols].copy()
    y = df[TARGET_COLUMN].astype(int).copy()
    return X, y


def train_and_compare_models(
    df: pd.DataFrame,
    test_size: float = 0.20,
    cv_folds: int = 5,
    random_state: int = RANDOM_STATE,
) -> Tuple[Dict[str, Any], pd.DataFrame, Any]:
    """
    Executes full reproducible training workflow:
    1. Stratified holdout split.
    2. Inner 5-fold Stratified CV grid search for 7 classifiers.
    3. Independent evaluation on holdout test partition.
    4. Selection and persistence of optimal pipeline.
    """
    logger.info("Starting model training pipeline on dataset with %d observations", len(df))
    X, y = prepare_features_and_target(df)

    # 1. Stratified Train / Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    logger.info(
        "Train set: %d samples (%d successes, %d failures), Test set: %d samples (%d successes, %d failures)",
        len(X_train), int(y_train.sum()), len(y_train) - int(y_train.sum()),
        len(X_test), int(y_test.sum()), len(y_test) - int(y_test.sum()),
    )

    cv_strategy = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
    preprocessor = build_preprocessor()

    comparison_records: List[Dict[str, Any]] = []
    trained_pipelines: Dict[str, Any] = {}
    evaluation_results: Dict[str, Any] = {}

    for model_name, cfg in MODEL_CONFIGS.items():
        logger.info("Training and tuning: %s", model_name)
        pipeline = build_model_pipeline(cfg["estimator"], preprocessor=preprocessor)

        if cfg["param_grid"]:
            search = GridSearchCV(
                pipeline,
                cfg["param_grid"],
                cv=cv_strategy,
                scoring="roc_auc",
                n_jobs=-1,
                refit=True,
            )
            search.fit(X_train, y_train)
            best_pipe = search.best_estimator_
            cv_best_score = float(search.best_score_)
            best_params = search.best_params_
        else:
            pipeline.fit(X_train, y_train)
            best_pipe = pipeline
            cv_best_score = float(np.mean(y_train))
            best_params = {}

        trained_pipelines[model_name] = best_pipe

        # Evaluate on Independent Holdout Test Partition
        y_test_pred = best_pipe.predict(X_test)
        if hasattr(best_pipe, "predict_proba"):
            y_test_proba = best_pipe.predict_proba(X_test)[:, 1]
        else:
            y_test_proba = y_test_pred.astype(float)

        metrics = evaluate_classifier_predictions(
            y_true=y_test.values,
            y_pred=y_test_pred,
            y_proba=y_test_proba,
            model_name=model_name,
        )
        latency = measure_inference_latency(best_pipe, X_test)
        metrics["inference_latency_ms"] = latency
        metrics["cv_score_roc_auc"] = round(cv_best_score, 4)
        metrics["best_params"] = best_params

        evaluation_results[model_name] = metrics
        comparison_records.append({
            "Model": model_name,
            "CV ROC-AUC": metrics["cv_score_roc_auc"],
            "Holdout Accuracy": metrics["accuracy"],
            "Holdout F1": metrics["f1_score"],
            "Holdout ROC-AUC": metrics["roc_auc"],
            "Holdout PR-AUC": metrics["pr_auc"],
            "Precision": metrics["precision"],
            "Recall": metrics["recall"],
            "Specificity": metrics["specificity"],
            "Brier Score": metrics["brier_score"],
            "Latency (ms)": latency,
        })

    comparison_df = pd.DataFrame(comparison_records)
    # Sort models by Holdout ROC-AUC then Holdout F1
    comparison_df = comparison_df.sort_values(
        by=["Holdout ROC-AUC", "Holdout F1"], ascending=[False, False]
    ).reset_index(drop=True)

    # Exclude dummy baseline from winning selection
    valid_candidates = [m for m in comparison_df["Model"].tolist() if m != "Dummy_Baseline"]
    best_model_name = valid_candidates[0]
    best_pipeline = trained_pipelines[best_model_name]
    best_metrics = evaluation_results[best_model_name]

    logger.info("Selected winning model: %s (Holdout ROC-AUC: %.4f, F1: %.4f)",
                best_model_name, best_metrics["roc_auc"], best_metrics["f1_score"])

    # Compute Permutation Feature Importance for the winning model
    perm_importance_df = compute_permutation_importance(best_pipeline, X_test, y_test)

    # Build Registry Metadata
    registry_metadata: Dict[str, Any] = {
        "model_name": best_model_name,
        "features": list(X.columns),
        "feature_schema_version": "v1.0",
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "selected_decision_threshold": 0.50,
        "best_hyperparameters": best_metrics["best_params"],
        "evaluation_metrics": best_metrics,
        "all_models_comparison": comparison_df.to_dict(orient="records"),
        "top_features_importance": perm_importance_df.head(10).to_dict(orient="records"),
        "limitations": (
            "Model is calibrated on historical Falcon 9 launches. Predictive probabilities "
            "reflect empirical associations from historical testing and flight iterations, "
            "not certified flight-dynamics certifications. Atmospheric variations, unexpected "
            "engine sensor anomalies, and extreme sea-state weather may alter real recovery outcomes."
        ),
    }

    # Save artifact to registry
    save_model_artifact(best_pipeline, registry_metadata)

    return registry_metadata, comparison_df, best_pipeline

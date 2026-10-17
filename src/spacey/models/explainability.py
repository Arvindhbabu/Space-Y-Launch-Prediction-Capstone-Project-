"""
SpaceY Intelligence - Model Explainability and Scenario Attribution
Implements Permutation Importance, Logistic Coefficients, and Local Scenario Attribution.
"""

from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance

from spacey.logging_config import setup_logger

logger = setup_logger("spacey.explainability")


def get_feature_names_from_preprocessor(preprocessor) -> List[str]:
    """Extracts human-readable feature names after ColumnTransformer encoding."""
    try:
        return list(preprocessor.get_feature_names_out())
    except Exception:
        # Fallback names
        names = []
        for name, trans, cols in preprocessor.transformers_:
            if name == "num":
                names.extend([f"num__{c}" for c in cols])
            elif name == "cat":
                names.extend([f"cat__{c}" for c in cols])
            elif name == "bin":
                names.extend([f"bin__{c}" for c in cols])
        return names


def compute_permutation_importance(
    pipeline,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    n_repeats: int = 10,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Computes model-agnostic permutation feature importance on unseen data.
    Measures the drop in ROC-AUC or accuracy when each feature column is shuffled.
    """
    logger.info("Computing permutation importance across %d test observations", len(X_val))
    result = permutation_importance(
        pipeline,
        X_val,
        y_val,
        n_repeats=n_repeats,
        random_state=random_state,
        scoring="roc_auc",
    )
    df = pd.DataFrame({
        "Feature": X_val.columns,
        "Importance_Mean": result.importances_mean,
        "Importance_Std": result.importances_std,
    })
    df = df.sort_values(by="Importance_Mean", ascending=False).reset_index(drop=True)
    return df


def explain_single_scenario(
    pipeline,
    scenario_df: pd.DataFrame,
    reference_df: pd.DataFrame,
) -> List[Dict[str, Any]]:
    """
    Computes local feature contribution attribution for a single scenario input.
    Evaluates sensitivity by perturbing each feature to the reference baseline.
    """
    base_proba = float(pipeline.predict_proba(scenario_df)[0][1])

    explanations = []
    for col in scenario_df.columns:
        perturbed = scenario_df.copy()
        # Replace feature with reference mean or mode
        if col in reference_df.columns:
            if pd.api.types.is_numeric_dtype(reference_df[col]):
                ref_val = reference_df[col].median()
            else:
                ref_val = reference_df[col].mode()[0]
            perturbed[col] = ref_val
            new_proba = float(pipeline.predict_proba(perturbed)[0][1])
            # Impact: how much having the current value changes probability vs baseline reference
            impact = base_proba - new_proba

            val_str = str(scenario_df[col].iloc[0])
            explanations.append({
                "feature": col,
                "current_val": val_str,
                "reference_val": str(ref_val),
                "impact": round(impact, 4),
                "direction": "Favorable (+)" if impact >= 0 else "Unfavorable (-)",
                "description": f"Value '{val_str}' shifts recovery likelihood by {impact*100:+.1f}% vs baseline ({ref_val})",
            })

    # Sort by absolute magnitude of impact
    explanations.sort(key=lambda x: abs(x["impact"]), reverse=True)
    return explanations

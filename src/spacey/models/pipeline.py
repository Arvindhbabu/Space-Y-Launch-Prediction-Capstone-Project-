"""
SpaceY Intelligence - Machine Learning Preprocessing & Pipeline Architecture
Constructs leakage-safe ColumnTransformers and full scikit-learn Pipelines.
"""

from typing import List, Optional
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

from spacey.config import NUMERICAL_FEATURES, CATEGORICAL_FEATURES, BINARY_FEATURES


def build_preprocessor(
    numerical_cols: Optional[List[str]] = None,
    categorical_cols: Optional[List[str]] = None,
    binary_cols: Optional[List[str]] = None,
) -> ColumnTransformer:
    """
    Builds an isolated ColumnTransformer that imputes and encodes features.
    Learns parameters ONLY on training partitions.
    """
    num_cols = numerical_cols or NUMERICAL_FEATURES
    cat_cols = categorical_cols or CATEGORICAL_FEATURES
    bin_cols = binary_cols or BINARY_FEATURES

    # Numerical pipeline: Median imputation + Standard Scaling
    num_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    # Categorical pipeline: Frequent imputation + One-Hot Encoding (safe for unseen levels)
    cat_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    # Binary pipeline: Mode imputation + Passthrough
    bin_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_pipeline, num_cols),
            ("cat", cat_pipeline, cat_cols),
            ("bin", bin_pipeline, bin_cols),
        ],
        remainder="drop",
    )
    return preprocessor


def build_model_pipeline(classifier, preprocessor: Optional[ColumnTransformer] = None) -> Pipeline:
    """
    Packages preprocessor and estimator into a unified inference Pipeline.
    Prevents loose scalers and ensures consistent transformation in deployment.
    """
    if preprocessor is None:
        preprocessor = build_preprocessor()

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )

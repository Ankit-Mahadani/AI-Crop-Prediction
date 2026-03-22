"""
Data Preprocessing Module
Handles loading, cleaning, encoding, scaling, and splitting the crop yield dataset.
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

# ── Column definitions ──────────────────────────────────────────────────────
CATEGORICAL_FEATURES = [
    "Region",
    "Soil_Type",
    "Crop_Type",
    "Weather_Condition",
    "Fertilizer_Used",
    "Irrigation_Used",
]
NUMERICAL_FEATURES = [
    "Rainfall_mm",
    "Temperature_Celsius",
    "Days_to_Harvest",
]
TARGET = "Yield_tons_per_hectare"

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "crop_yield.csv")


def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    """Load raw CSV and return a DataFrame."""
    df = pd.read_csv(path)
    # Standardise column names  (strip spaces, title-case common variants)
    df.columns = df.columns.str.strip()
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows missing the target; fill/drop other NaNs."""
    df = df.dropna(subset=[TARGET])

    # Fill numerical NaNs with median
    for col in NUMERICAL_FEATURES:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    # Fill categorical NaNs with mode
    for col in CATEGORICAL_FEATURES:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].mode()[0])

    return df.reset_index(drop=True)


def build_preprocessor() -> ColumnTransformer:
    """Build a sklearn ColumnTransformer for encoding + scaling."""
    cat_pipeline = Pipeline(steps=[
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])
    num_pipeline = Pipeline(steps=[
        ("scaler", StandardScaler())
    ])
    preprocessor = ColumnTransformer(transformers=[
        ("cat", cat_pipeline, CATEGORICAL_FEATURES),
        ("num", num_pipeline, NUMERICAL_FEATURES),
    ], remainder="drop")
    return preprocessor


def load_and_preprocess(path: str = DATA_PATH, test_size: float = 0.2, random_state: int = 42):
    """
    Full pipeline: load → clean → split → fit preprocessor.

    Returns
    -------
    X_train_proc, X_test_proc, y_train, y_test, preprocessor, feature_names
    """
    df = load_data(path)
    df = clean_data(df)

    # Ensure expected columns are present
    all_features = CATEGORICAL_FEATURES + NUMERICAL_FEATURES
    missing = [c for c in all_features + [TARGET] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in dataset: {missing}")

    X = df[all_features]
    y = df[TARGET].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    preprocessor = build_preprocessor()
    X_train_proc = preprocessor.fit_transform(X_train)
    X_test_proc = preprocessor.transform(X_test)

    # Derive human-readable feature names after encoding
    cat_encoder = preprocessor.named_transformers_["cat"]["onehot"]
    cat_names = list(cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES))
    feature_names = cat_names + NUMERICAL_FEATURES

    return X_train_proc, X_test_proc, y_train, y_test, preprocessor, feature_names


if __name__ == "__main__":
    X_tr, X_te, y_tr, y_te, prep, fnames = load_and_preprocess()
    print(f"Train shape : {X_tr.shape}")
    print(f"Test shape  : {X_te.shape}")
    print(f"Features    : {len(fnames)}")

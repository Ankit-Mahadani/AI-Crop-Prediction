"""
Predictor & Optimiser
Loads saved model artefacts and provides predict/optimise API.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import joblib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from preprocessing.preprocess import CATEGORICAL_FEATURES, NUMERICAL_FEATURES

MODELS_DIR        = os.path.join(os.path.dirname(__file__), "..", "models")
BEST_MODEL_PATH   = os.path.join(MODELS_DIR, "best_model.pkl")
PREPROCESSOR_PATH = os.path.join(MODELS_DIR, "preprocessor.pkl")
RESULTS_PATH      = os.path.join(MODELS_DIR, "results.json")
FEATURE_IMP_PATH  = os.path.join(MODELS_DIR, "feature_importance.json")

_model       = None
_preprocessor = None


def load_artifacts():
    """Load model + preprocessor into module-level cache."""
    global _model, _preprocessor
    if _model is None:
        if not os.path.exists(BEST_MODEL_PATH):
            raise FileNotFoundError(
                "Model not found. Run `python models/train.py` first."
            )
        _model        = joblib.load(BEST_MODEL_PATH)
        _preprocessor = joblib.load(PREPROCESSOR_PATH)
    return _model, _preprocessor


def _build_df(input_dict: dict) -> pd.DataFrame:
    """Convert raw input dict to a single-row DataFrame."""
    all_cols = CATEGORICAL_FEATURES + NUMERICAL_FEATURES
    row = {col: input_dict.get(col) for col in all_cols}
    return pd.DataFrame([row])


def predict_yield(input_dict: dict) -> float:
    """
    Predict crop yield from a feature dictionary.

    Parameters
    ----------
    input_dict : dict  — must contain all CATEGORICAL_FEATURES + NUMERICAL_FEATURES

    Returns
    -------
    float : predicted yield in tons/hectare (rounded to 4 dp)
    """
    model, preprocessor = load_artifacts()
    df = _build_df(input_dict)
    X  = preprocessor.transform(df)
    pred = model.predict(X)[0]
    return max(0.0, round(float(pred), 4))


def optimize_yield(input_dict: dict) -> dict:
    """
    Compare all 4 combinations of Fertilizer_Used × Irrigation_Used.

    Parameters
    ----------
    input_dict : dict — same as predict_yield; Fertilizer_Used / Irrigation_Used
                        values are overridden internally.

    Returns
    -------
    dict with keys:
        combinations : list of {fertilizer, irrigation, predicted_yield}
        best         : combination with highest predicted_yield
        improvement  : yield gain vs worst combination
    """
    combos = [
        ("No",  "No"),
        ("Yes", "No"),
        ("No",  "Yes"),
        ("Yes", "Yes"),
    ]

    results = []
    for fert, irr in combos:
        inp = dict(input_dict)
        inp["Fertilizer_Used"] = fert
        inp["Irrigation_Used"] = irr
        pred = predict_yield(inp)
        results.append({
            "fertilizer": fert,
            "irrigation": irr,
            "predicted_yield": pred,
        })

    best    = max(results, key=lambda x: x["predicted_yield"])
    worst   = min(results, key=lambda x: x["predicted_yield"])
    gain    = round(best["predicted_yield"] - worst["predicted_yield"], 4)

    return {
        "combinations": results,
        "best": best,
        "improvement_over_worst": gain,
    }


def get_model_info() -> dict:
    """Return model results and feature importance from saved JSON files."""
    info = {}
    if os.path.exists(RESULTS_PATH):
        with open(RESULTS_PATH) as f:
            info["results"] = json.load(f)
    if os.path.exists(FEATURE_IMP_PATH):
        with open(FEATURE_IMP_PATH) as f:
            raw = json.load(f)
            # Return top-15 features for display
            top15 = dict(list(raw.items())[:15])
            info["feature_importance"] = top15
    return info

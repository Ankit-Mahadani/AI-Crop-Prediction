"""
Model Training Script
Trains Linear Regression, Random Forest, and XGBoost; evaluates each;
saves the best model and preprocessor to disk.
"""

import os
import sys
import json
import time
import warnings
import numpy as np
import joblib

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import cross_val_score
from xgboost import XGBRegressor

from preprocessing.preprocess import load_and_preprocess

warnings.filterwarnings("ignore")

# ── Paths ────────────────────────────────────────────────────────────────────
MODELS_DIR = os.path.dirname(__file__)
BEST_MODEL_PATH   = os.path.join(MODELS_DIR, "best_model.pkl")
PREPROCESSOR_PATH = os.path.join(MODELS_DIR, "preprocessor.pkl")
RESULTS_PATH      = os.path.join(MODELS_DIR, "results.json")
FEATURE_IMP_PATH  = os.path.join(MODELS_DIR, "feature_importance.json")


def evaluate_model(name, model, X_train, X_test, y_train, y_test, cv=5):
    """Fit, evaluate and return metrics dict."""
    t0 = time.time()
    model.fit(X_train, y_train)
    train_time = round(time.time() - t0, 2)

    y_pred = model.predict(X_test)
    rmse   = round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 4)
    mae    = round(float(mean_absolute_error(y_test, y_pred)), 4)
    r2     = round(float(r2_score(y_test, y_pred)), 4)

    cv_scores = cross_val_score(model, X_train, y_train,
                                scoring="r2", cv=cv)
    cv_mean   = round(float(cv_scores.mean()), 4)
    cv_std    = round(float(cv_scores.std()), 4)

    print(f"  {name:<30} RMSE={rmse:.4f}  MAE={mae:.4f}  R²={r2:.4f}  "
          f"CV-R²={cv_mean:.4f}±{cv_std:.4f}  [{train_time}s]")

    return {
        "name": name,
        "rmse": rmse,
        "mae": mae,
        "r2": r2,
        "cv_r2_mean": cv_mean,
        "cv_r2_std": cv_std,
        "train_time_sec": train_time,
    }


def get_feature_importance(model, feature_names):
    """Extract feature importances if available."""
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_)
    else:
        return {}

    # Normalise to 0-1
    total = importances.sum()
    if total == 0:
        return {}
    rel = importances / total

    paired = sorted(zip(feature_names, rel.tolist()),
                    key=lambda x: x[1], reverse=True)
    return {name: round(val, 6) for name, val in paired}


def train():
    print("=" * 60)
    print("  AI Crop Yield Prediction – Model Training")
    print("=" * 60)

    # ── Load data ────────────────────────────────────────────────
    print("\n[1/4] Loading & preprocessing data …")
    X_train, X_test, y_train, y_test, preprocessor, feature_names = load_and_preprocess()
    print(f"      Train: {X_train.shape}  |  Test: {X_test.shape}")

    # ── Define models ────────────────────────────────────────────
    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=200, max_depth=None,
            random_state=42, n_jobs=-1
        ),
        "XGBoost": XGBRegressor(
            n_estimators=300, learning_rate=0.05,
            max_depth=6, subsample=0.8,
            colsample_bytree=0.8, random_state=42,
            verbosity=0
        ),
    }

    # ── Train & evaluate ─────────────────────────────────────────
    print("\n[2/4] Training & evaluating models …")
    results = []
    trained = {}
    for name, model in models.items():
        metrics = evaluate_model(
            name, model, X_train, X_test, y_train, y_test
        )
        results.append(metrics)
        trained[name] = model

    # ── Select best ──────────────────────────────────────────────
    best_result = max(results, key=lambda m: m["r2"])
    best_name   = best_result["name"]
    best_model  = trained[best_name]
    print(f"\n[3/4] Best model: {best_name}  (R²={best_result['r2']})")

    # ── Feature importance ───────────────────────────────────────
    fi = get_feature_importance(best_model, feature_names)

    # ── Save artefacts ───────────────────────────────────────────
    print("\n[4/4] Saving model artefacts …")
    joblib.dump(best_model,   BEST_MODEL_PATH)
    joblib.dump(preprocessor, PREPROCESSOR_PATH)

    # Tag best model in results
    for r in results:
        r["is_best"] = (r["name"] == best_name)
    with open(RESULTS_PATH, "w") as f:
        json.dump({"models": results, "best": best_name}, f, indent=2)

    with open(FEATURE_IMP_PATH, "w") as f:
        json.dump(fi, f, indent=2)

    print(f"      best_model.pkl    → {BEST_MODEL_PATH}")
    print(f"      preprocessor.pkl  → {PREPROCESSOR_PATH}")
    print(f"      results.json      → {RESULTS_PATH}")
    print(f"      feature_importance.json → {FEATURE_IMP_PATH}")
    print("\n✅  Training complete!")
    return best_model, best_result


if __name__ == "__main__":
    train()

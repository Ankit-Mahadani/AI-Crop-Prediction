"""
FastAPI Backend
Exposes /predict and /optimize endpoints with CORS.
Also serves the frontend static files.
"""

import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional

# Project root on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.predictor import predict_yield, optimize_yield, get_model_info, load_artifacts, recommend_top_crops

# ── App init ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Crop Yield Prediction API",
    description="Predict crop yield (tons/ha) and optimise farming conditions with ML.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# ── Pydantic schemas ─────────────────────────────────────────────────────────
class PredictRequest(BaseModel):
    Region: str                   = Field(..., example="North")
    Soil_Type: str                = Field(..., example="Sandy")
    Crop_Type: str                = Field(..., example="Wheat")
    Rainfall_mm: float            = Field(..., example=500.0)
    Temperature_Celsius: float    = Field(..., example=25.0)
    Fertilizer_Used: str          = Field(..., example="Yes")
    Irrigation_Used: str          = Field(..., example="Yes")
    Weather_Condition: str        = Field(..., example="Sunny")
    Days_to_Harvest: float        = Field(..., example=90.0)


class OptimizeRequest(BaseModel):
    Region: str                   = Field(..., example="North")
    Soil_Type: str                = Field(..., example="Sandy")
    Crop_Type: str                = Field(..., example="Wheat")
    Rainfall_mm: float            = Field(..., example=500.0)
    Temperature_Celsius: float    = Field(..., example=25.0)
    Weather_Condition: str        = Field(..., example="Sunny")
    Days_to_Harvest: float        = Field(..., example=90.0)


# ── Routes ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    """Pre-load model artefacts at server start."""
    try:
        load_artifacts()
        print("✅ Model artefacts loaded successfully.")
    except FileNotFoundError as e:
        print(f"⚠️  {e}")


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "AI Crop Yield Prediction API is running 🌾"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


@app.get("/model-info", tags=["Model"])
def model_info():
    """Return model comparison results and top feature importances."""
    try:
        return get_model_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict", tags=["Prediction"])
def predict(request: PredictRequest):
    """
    Predict crop yield for given farming conditions.

    Returns predicted yield in tons/hectare.
    """
    try:
        inp = request.model_dump()
        yield_val = predict_yield(inp)
        return {
            "predicted_yield": yield_val,
            "unit": "tons/hectare",
            "inputs": inp,
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/optimize", tags=["Optimization"])
def optimize(request: OptimizeRequest):
    """
    Compare all 4 combinations of Fertilizer × Irrigation and recommend the best.

    Returns a ranked list of combinations with predicted yields and the optimal choice.
    """
    try:
        inp = request.model_dump()
        result = optimize_yield(inp)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/recommend-crop", tags=["Recommendation"])
def recommend_crop(request: PredictRequest):
    """
    Recommend the top 3 crops based on soil and weather conditions.
    """
    try:
        inp = request.model_dump()
        result = recommend_top_crops(inp)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/frontend", include_in_schema=False)
def serve_frontend():
    """Serve the main frontend HTML page."""
    html_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"error": "Frontend not found"}

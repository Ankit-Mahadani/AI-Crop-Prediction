@echo off
echo ============================================================
echo   AI Crop Yield Prediction - Quick Start
echo ============================================================
echo.

echo [1/4] Installing dependencies...
pip install -r requirements.txt
echo.

echo [2/4] Generating synthetic data (use real Kaggle CSV for best results)...
python data\generate_synthetic.py
echo.

echo [3/4] Training ML models...
python models\train.py
echo.

echo [4/4] Starting API server...
echo    Open http://localhost:8000/frontend in your browser
echo.
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000

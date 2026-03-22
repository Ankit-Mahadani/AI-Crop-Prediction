# AI Crop Yield Prediction System

> An end-to-end machine learning system that predicts crop yield (tons/hectare) and recommends optimal farming strategies using multiple regression models.

---

## 🌾 Problem Statement

Agricultural yield prediction is critical for food security and resource planning. This system leverages machine learning to:
- **Predict** crop yield based on region, soil, weather, and management factors
- **Optimize** farming decisions by comparing Fertilizer × Irrigation combinations
- **Explain** model behavior through feature importance visualization

---

## 📁 Project Structure

```
AI-Crop-Prediction/
├── data/
│   ├── raw/                    ← Place crop_yield.csv here
│   └── generate_synthetic.py  ← Generate demo data if Kaggle CSV is unavailable
├── models/
│   ├── train.py                ← Train all models, save best
│   ├── best_model.pkl          ← Saved best model (after training)
│   ├── preprocessor.pkl        ← Fitted preprocessor
│   ├── results.json            ← Model comparison metrics
│   └── feature_importance.json ← Feature weights
├── preprocessing/
│   └── preprocess.py           ← Data loading, encoding, scaling, splitting
├── api/
│   └── main.py                 ← FastAPI backend (/predict, /optimize)
├── frontend/
│   ├── index.html              ← Premium UI
│   ├── style.css               ← Dark glassmorphism theme
│   └── app.js                  ← API integration, Chart.js charts
├── utils/
│   ├── predictor.py            ← Predict & optimize functions
│   └── visualize.py            ← Matplotlib plots
├── outputs/plots/              ← Generated chart PNGs
├── requirements.txt
└── README.md
```

---

## 📊 Dataset

**Source**: [Agriculture Crop Yield – Kaggle](https://www.kaggle.com/datasets/samuelotiattakorah/agriculture-crop-yield)

| Feature | Type | Description |
|---|---|---|
| Region | Categorical | North, South, East, West |
| Soil_Type | Categorical | Sandy, Clay, Loam, Silt, Peaty, Chalky |
| Crop_Type | Categorical | Wheat, Rice, Maize, Barley, Soybean, Cotton, Sugarcane, Coffee |
| Rainfall_mm | Numeric | Annual rainfall in millimeters |
| Temperature_Celsius | Numeric | Average temperature (°C) |
| Fertilizer_Used | Categorical | Yes / No |
| Irrigation_Used | Categorical | Yes / No |
| Weather_Condition | Categorical | Sunny, Rainy, Cloudy, Windy |
| Days_to_Harvest | Numeric | Growing period in days |
| **Yield_tons_per_hectare** | **Target** | **Crop yield in tons/ha** |

---

## 🛠️ Setup & Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Dataset

**Option A — Real Kaggle dataset:**
1. Download from [Kaggle](https://www.kaggle.com/datasets/samuelotiattakorah/agriculture-crop-yield)
2. Place `crop_yield.csv` in `data/raw/`

**Option B — Synthetic demo data:**
```bash
python data/generate_synthetic.py
```

### 3. Train Models

```bash
python models/train.py
```

### 4. Start API Server

```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Open Frontend

Visit **http://localhost:8000/frontend** in your browser.

---

## 🤖 Models Used

| Model | Description |
|---|---|
| **Linear Regression** | Baseline model — fast, interpretable |
| **Random Forest** | Ensemble of 200 decision trees — handles non-linearity |
| **XGBoost** | Gradient boosting — typically best performance |

The system automatically selects the model with the highest R² score on the test set.

---

## 📈 Sample Results (Synthetic Data)

| Model | RMSE | MAE | R² | CV R² |
|---|---|---|---|---|
| Linear Regression | ~0.60 | ~0.48 | ~0.72 | ~0.71 |
| Random Forest | ~0.38 | ~0.29 | ~0.88 | ~0.87 |
| **XGBoost** | **~0.35** | **~0.26** | **~0.90** | **~0.89** |

> Results vary with the real Kaggle dataset.

---

## 🔌 API Endpoints

### `GET /`
Health check.

### `GET /model-info`
Returns model comparison results and top feature importances.

### `POST /predict`
Predict crop yield.

**Request body:**
```json
{
  "Region": "North",
  "Soil_Type": "Loam",
  "Crop_Type": "Wheat",
  "Rainfall_mm": 600,
  "Temperature_Celsius": 22,
  "Fertilizer_Used": "Yes",
  "Irrigation_Used": "Yes",
  "Weather_Condition": "Sunny",
  "Days_to_Harvest": 95
}
```

**Response:**
```json
{
  "predicted_yield": 4.2315,
  "unit": "tons/hectare"
}
```

### `POST /optimize`
Compare all 4 Fertilizer × Irrigation combinations.

**Request body:** Same as `/predict` but without `Fertilizer_Used` / `Irrigation_Used`.

**Response:**
```json
{
  "combinations": [...],
  "best": { "fertilizer": "Yes", "irrigation": "Yes", "predicted_yield": 4.93 },
  "improvement_over_worst": 1.21
}
```

---

## ⚡ Optimization Module

The system tests all 4 combinations:
| Fertilizer | Irrigation |
|---|---|
| No | No |
| Yes | No |
| No | Yes |
| **Yes** | **Yes** |

The best combination is highlighted in the UI with a bar chart comparison.

---

## 🎨 Frontend Features

- 🌑 Dark glassmorphism theme with animated background
- 📋 Interactive form with all crop features
- 🔮 Animated yield counter display
- ⚡ Optimization bar chart (Chart.js)
- 🤖 Live model performance comparison panel
- 📱 Responsive for all screen sizes

---

## 🔮 Future Improvements

- [ ] Real-time weather API integration (OpenWeatherMap)
- [ ] Explainable AI (SHAP values)
- [ ] Crop recommendation (classification mode)
- [ ] Deployment on Render / Railway
- [ ] Historical yield tracking dashboard
- [ ] Multi-language support for farmers

---

## 👨‍💻 Author

Built for AI/ML College Exhibition Project  
Stack: Python · FastAPI · Scikit-Learn · XGBoost · Chart.js · HTML/CSS

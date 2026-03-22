"""
Generate synthetic crop yield data for demo/testing when the real dataset
is not available. Produces a CSV compatible with the Kaggle dataset schema.

Usage:
    python data/generate_synthetic.py
"""

import os
import numpy as np
import pandas as pd

np.random.seed(42)
N = 5000

REGIONS            = ["North", "South", "East", "West"]
SOIL_TYPES         = ["Sandy", "Clay", "Loam", "Silt", "Peaty", "Chalky"]
CROP_TYPES         = ["Wheat", "Rice", "Maize", "Barley", "Soybean", "Cotton", "Sugarcane", "Coffee"]
WEATHER_CONDITIONS = ["Sunny", "Rainy", "Cloudy", "Windy"]
YES_NO             = ["Yes", "No"]

# Base yield by crop (tons/hectare) — realistic rough averages
CROP_BASE = {
    "Wheat": 3.5, "Rice": 4.2, "Maize": 5.0, "Barley": 3.0,
    "Soybean": 2.8, "Cotton": 1.5, "Sugarcane": 60.0, "Coffee": 1.0,
}
# Normalize Sugarcane to ~5 for dataset coherence
CROP_BASE["Sugarcane"] = 5.5

def generate():
    region    = np.random.choice(REGIONS, N)
    soil      = np.random.choice(SOIL_TYPES, N)
    crop      = np.random.choice(CROP_TYPES, N)
    weather   = np.random.choice(WEATHER_CONDITIONS, N)
    rainfall  = np.random.uniform(50, 1500, N)
    temp      = np.random.uniform(10, 45, N)
    days      = np.random.randint(60, 180, N).astype(float)
    fert      = np.random.choice(YES_NO, N, p=[0.65, 0.35])
    irr       = np.random.choice(YES_NO, N, p=[0.6, 0.4])

    # Compute yield with realistic relationships
    base      = np.array([CROP_BASE[c] for c in crop])
    fert_mult = np.where(fert == "Yes", 1.25, 1.0)
    irr_mult  = np.where(irr  == "Yes", 1.18, 1.0)
    rain_eff  = np.clip(rainfall / 500, 0.5, 1.5)
    temp_eff  = 1 - 0.02 * np.abs(temp - 25)   # optimal near 25°C
    temp_eff  = np.clip(temp_eff, 0.5, 1.2)
    noise     = np.random.normal(0, 0.3, N)

    y = base * fert_mult * irr_mult * rain_eff * temp_eff + noise
    y = np.clip(y, 0.1, 12.0).round(4)

    df = pd.DataFrame({
        "Region":                  region,
        "Soil_Type":               soil,
        "Crop_Type":               crop,
        "Rainfall_mm":             rainfall.round(2),
        "Temperature_Celsius":     temp.round(2),
        "Fertilizer_Used":         fert,
        "Irrigation_Used":         irr,
        "Weather_Condition":       weather,
        "Days_to_Harvest":         days,
        "Yield_tons_per_hectare":  y,
    })

    out = os.path.join(os.path.dirname(__file__), "raw", "crop_yield.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    df.to_csv(out, index=False)
    print(f"✅ Generated {N} synthetic samples → {out}")
    return df


if __name__ == "__main__":
    generate()

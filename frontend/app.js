/**
 * CropAI – Frontend Application Logic
 * Handles form collection, API calls, and result rendering.
 */

const API_BASE = window.location.origin;

// ── State ─────────────────────────────────────────────────────────────────
let fertilizerVal = "Yes";
let irrigationVal = "Yes";
let optChartInstance = null;

// ── DOM refs ──────────────────────────────────────────────────────────────
const form          = document.getElementById("cropForm");
const predictBtn    = document.getElementById("predictBtn");
const optimizeBtn   = document.getElementById("optimizeBtn");
const formError     = document.getElementById("formError");
const resultsArea   = document.getElementById("resultsArea");
const predCard      = document.getElementById("predictionCard");
const optCard       = document.getElementById("optimizationCard");
const modelBadge    = document.getElementById("model-badge");

// ── Toggle buttons ────────────────────────────────────────────────────────
document.querySelectorAll(".toggle-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const field = btn.dataset.field;
    const val   = btn.dataset.val;

    // Deactivate siblings in same group
    document.querySelectorAll(`.toggle-btn[data-field="${field}"]`).forEach(b => b.classList.remove("active"));
    btn.classList.add("active");

    if (field === "fertilizer") fertilizerVal = val;
    if (field === "irrigation")  irrigationVal = val;
  });
});

// ── Collect form data ──────────────────────────────────────────────────────
function collectFormData() {
  const data = {
    Region:               document.getElementById("region").value,
    Soil_Type:            document.getElementById("soilType").value,
    Crop_Type:            document.getElementById("cropType").value,
    Weather_Condition:    document.getElementById("weather").value,
    Rainfall_mm:          parseFloat(document.getElementById("rainfall").value),
    Temperature_Celsius:  parseFloat(document.getElementById("temperature").value),
    Days_to_Harvest:      parseFloat(document.getElementById("days").value),
    Fertilizer_Used:      fertilizerVal,
    Irrigation_Used:      irrigationVal,
  };
  return data;
}

function validateForm(data) {
  const required = ["Region","Soil_Type","Crop_Type","Weather_Condition",
                    "Rainfall_mm","Temperature_Celsius","Days_to_Harvest"];
  for (const key of required) {
    if (data[key] === "" || data[key] === null || Number.isNaN(data[key])) {
      return `Please fill in: ${key.replace(/_/g," ")}`;
    }
  }
  return null;
}

// ── Show error ──────────────────────────────────────────────────────────────
function showError(msg) {
  formError.textContent = msg;
  formError.classList.remove("hidden");
  setTimeout(() => formError.classList.add("hidden"), 5000);
}

// ── Animated counter ────────────────────────────────────────────────────────
function animateCounter(el, targetVal, duration = 800) {
  const start = performance.now();
  const from  = 0;
  function tick(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased    = progress < 0.5
      ? 2 * progress * progress
      : 1 - Math.pow(-2 * progress + 2, 2) / 2;
    el.textContent = (from + (targetVal - from) * eased).toFixed(2);
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

// ── Yield interpretation ────────────────────────────────────────────────────
function interpretYield(val) {
  if (val < 1)   return "⚠️ Very low yield — consider improving soil and resources.";
  if (val < 2.5) return "🟡 Below average yield — irrigation or fertilization may help.";
  if (val < 4)   return "🟢 Average yield — conditions are adequate.";
  if (val < 6)   return "✅ Good yield — your conditions are well-optimized.";
  return              "🚀 Excellent yield — optimal farming conditions!";
}

// ── Render prediction ───────────────────────────────────────────────────────
function renderPrediction(result) {
  const yieldVal  = result.predicted_yield;
  const maxYield  = 10; // approximate max scale
  const pct       = Math.min((yieldVal / maxYield) * 100, 100);

  document.getElementById("yieldValue").textContent        = "0.00";
  document.getElementById("yieldBar").style.width          = "0%";
  document.getElementById("yieldInterpret").textContent    = interpretYield(yieldVal);

  predCard.classList.remove("hidden");
  resultsArea.classList.remove("hidden");

  // Animate
  requestAnimationFrame(() => {
    document.getElementById("yieldBar").style.width = `${pct}%`;
    animateCounter(document.getElementById("yieldValue"), yieldVal);
  });

  predCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ── Render optimization ─────────────────────────────────────────────────────
function renderOptimization(result) {
  const combos = result.combinations;
  const best   = result.best;

  // Best combo banner
  const bestEl = document.getElementById("bestCombo");
  bestEl.innerHTML = `
    <div>
      <div class="best-label">🏆 Recommended Strategy</div>
      <div class="best-value">
        Fertilizer: <strong>${best.fertilizer}</strong>
        &nbsp;·&nbsp;
        Irrigation: <strong>${best.irrigation}</strong>
        &nbsp;·&nbsp;
        Yield: <strong style="color:var(--green)">${best.predicted_yield.toFixed(2)} t/ha</strong>
      </div>
    </div>
    <div style="color:var(--text-secondary);font-size:0.82rem;">
      Gain vs worst: +${result.improvement_over_worst.toFixed(2)} t/ha
    </div>
  `;

  // Chart
  const labels = combos.map(c => `F:${c.fertilizer[0]} / I:${c.irrigation[0]}`);
  const values = combos.map(c => c.predicted_yield);
  const bgColors = combos.map(c =>
    (c.fertilizer === best.fertilizer && c.irrigation === best.irrigation)
      ? "rgba(74,222,128,0.75)"
      : "rgba(96,165,250,0.55)"
  );
  const borderColors = combos.map(c =>
    (c.fertilizer === best.fertilizer && c.irrigation === best.irrigation)
      ? "#4ade80"
      : "#60a5fa"
  );

  if (optChartInstance) optChartInstance.destroy();
  const ctx = document.getElementById("optChart").getContext("2d");
  optChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Predicted Yield (t/ha)",
        data: values,
        backgroundColor: bgColors,
        borderColor: borderColors,
        borderWidth: 2,
        borderRadius: 10,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.parsed.y.toFixed(2)} tons/hectare`
          }
        }
      },
      scales: {
        x: {
          ticks: { color: "#8892b0" },
          grid:  { color: "rgba(99,120,220,0.1)" },
        },
        y: {
          ticks:  { color: "#8892b0" },
          grid:   { color: "rgba(99,120,220,0.1)" },
          title:  { display: true, text: "Yield (t/ha)", color: "#8892b0" },
          beginAtZero: true,
        }
      }
    }
  });

  // Table
  const tbody = document.getElementById("optTableBody");
  tbody.innerHTML = "";
  const sorted = [...combos].sort((a,b) => b.predicted_yield - a.predicted_yield);
  sorted.forEach(c => {
    const isBest = c.fertilizer === best.fertilizer && c.irrigation === best.irrigation;
    const tr = document.createElement("tr");
    if (isBest) tr.classList.add("best-row");
    tr.innerHTML = `
      <td>${c.fertilizer}</td>
      <td>${c.irrigation}</td>
      <td><strong>${c.predicted_yield.toFixed(4)}</strong></td>
      <td>${isBest ? '<span class="tag-best">✓ Best</span>' : '<span class="tag-other">—</span>'}</td>
    `;
    tbody.appendChild(tr);
  });

  optCard.classList.remove("hidden");
  resultsArea.classList.remove("hidden");
  optCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ── Real-Time Weather ──────────────────────────────────────────────────────
const fetchWeatherBtn = document.getElementById("fetchWeatherBtn");
const cityInput = document.getElementById("cityInput");

fetchWeatherBtn.addEventListener("click", async () => {
  const city = cityInput.value.trim();
  if (!city) {
    showError("Please enter a city name to fetch weather.");
    return;
  }
  
  fetchWeatherBtn.classList.add("loading");
  fetchWeatherBtn.disabled = true;
  formError.classList.add("hidden");
  
  try {
    // 1. Geocode
    const geoRes = await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}&count=1&language=en&format=json`);
    const geoData = await geoRes.json();
    if (!geoData.results || geoData.results.length === 0) {
      throw new Error("City not found.");
    }
    const { latitude, longitude, name, country } = geoData.results[0];
    
    // 2. Weather
    const wRes = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m&daily=precipitation_sum&timezone=auto&past_days=30`);
    const wData = await wRes.json();
    
    const tempInput = document.getElementById("temperature");
    const rainInput = document.getElementById("rainfall");
    const daysInput = document.getElementById("days");
    
    tempInput.value = wData.current.temperature_2m;
    
    const pastRain = wData.daily.precipitation_sum.filter(r => r !== null).reduce((a, b) => a + b, 0);
    const days = parseFloat(daysInput.value) || 90;
    // Estimate total rainfall over crop duration based on past 30 days average
    const estRainfall = (pastRain / 30) * days;
    rainInput.value = Math.max(10, Math.round(estRainfall));
    
    cityInput.value = `${name}, ${country}`;
    
    // Flash inputs to show they updated
    tempInput.style.transition = "background-color 0.3s";
    rainInput.style.transition = "background-color 0.3s";
    tempInput.style.backgroundColor = "rgba(74,222,128,0.2)";
    rainInput.style.backgroundColor = "rgba(74,222,128,0.2)";
    setTimeout(() => {
      tempInput.style.backgroundColor = "";
      rainInput.style.backgroundColor = "";
    }, 800);
    
  } catch (ex) {
    showError(`❌ Weather API: ${ex.message}`);
  } finally {
    fetchWeatherBtn.classList.remove("loading");
    fetchWeatherBtn.disabled = false;
  }
});

// ── Predict ────────────────────────────────────────────────────────────────
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  formError.classList.add("hidden");

  const data = collectFormData();
  const err  = validateForm(data);
  if (err) { showError(err); return; }

  predictBtn.classList.add("loading");
  predictBtn.disabled = true;

  try {
    const res = await fetch(`${API_BASE}/predict`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(data),
    });
    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Prediction failed");
    }
    const result = await res.json();
    renderPrediction(result);
  } catch (ex) {
    showError(`❌ ${ex.message}`);
  } finally {
    predictBtn.classList.remove("loading");
    predictBtn.disabled = false;
  }
});

// ── Optimize ───────────────────────────────────────────────────────────────
optimizeBtn.addEventListener("click", async () => {
  formError.classList.add("hidden");

  const full = collectFormData();
  const { Fertilizer_Used, Irrigation_Used, ...data } = full;  // strip fert/irr

  const err = validateForm({ ...data, Rainfall_mm: full.Rainfall_mm,
    Temperature_Celsius: full.Temperature_Celsius, Days_to_Harvest: full.Days_to_Harvest });
  if (err) { showError(err); return; }

  optimizeBtn.classList.add("loading");
  optimizeBtn.disabled = true;

  try {
    const res = await fetch(`${API_BASE}/optimize`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(data),
    });
    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Optimization failed");
    }
    const result = await res.json();
    renderOptimization(result);
  } catch (ex) {
    showError(`❌ ${ex.message}`);
  } finally {
    optimizeBtn.classList.remove("loading");
    optimizeBtn.disabled = false;
  }
});

// ── Recommend Crop ─────────────────────────────────────────────────────────
const recommendCropBtn = document.getElementById("recommendCropBtn");
const recCard          = document.getElementById("recommendationCard");

recommendCropBtn.addEventListener("click", async () => {
  formError.classList.add("hidden");
  
  const data = collectFormData();
  data.Crop_Type = "Wheat"; // dummy bypass for validation
  const err = validateForm(data);
  if (err) { showError(err); return; }
  
  recommendCropBtn.classList.add("loading");
  recommendCropBtn.disabled = true;
  
  try {
    const res = await fetch(`${API_BASE}/recommend-crop`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(data),
    });
    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Recommendation failed");
    }
    const result = await res.json();
    
    // Render setup
    const tbody = document.getElementById("recommendTableBody");
    tbody.innerHTML = "";
    
    result.forEach((item, index) => {
      const tr = document.createElement("tr");
      if (index === 0) tr.classList.add("best-row");
      tr.innerHTML = `
        <td>#${index + 1} ${index === 0 ? '🏆' : ''}</td>
        <td><strong>${item.crop}</strong></td>
        <td><strong style="color: ${index === 0 ? 'var(--green)' : 'inherit'}">${item.predicted_yield.toFixed(4)}</strong></td>
      `;
      tbody.appendChild(tr);
    });
    
    recCard.classList.remove("hidden");
    resultsArea.classList.remove("hidden");
    recCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
    
  } catch (ex) {
    showError(`❌ ${ex.message}`);
  } finally {
    recommendCropBtn.classList.remove("loading");
    recommendCropBtn.disabled = false;
  }
});

// ── Load model info on page load ───────────────────────────────────────────
async function loadModelInfo() {
  try {
    const res = await fetch(`${API_BASE}/model-info`);
    if (!res.ok) throw new Error("Could not load model info");
    const info = await res.json();

    // Update header badge
    if (info.results?.best) {
      modelBadge.textContent = `Best: ${info.results.best}`;
    }

    // Render model comparison
    const container = document.getElementById("modelInfoContent");
    if (!info.results?.models) {
      container.textContent = "Model info unavailable. Please train the model first.";
      return;
    }

    const grid = document.createElement("div");
    grid.className = "model-grid";
    info.results.models.forEach(m => {
      const card = document.createElement("div");
      card.className = `model-item${m.is_best ? " best-model" : ""}`;
      card.innerHTML = `
        <div class="model-name">
          ${m.is_best ? '<span class="model-crown">👑</span>' : ""}
          ${m.name}
        </div>
        <div class="model-metrics">
          <div class="metric-row">
            <span class="metric-key">R² Score</span>
            <span class="metric-value${m.is_best ? " good" : ""}">${m.r2.toFixed(4)}</span>
          </div>
          <div class="metric-row">
            <span class="metric-key">RMSE</span>
            <span class="metric-value">${m.rmse.toFixed(4)}</span>
          </div>
          <div class="metric-row">
            <span class="metric-key">MAE</span>
            <span class="metric-value">${m.mae.toFixed(4)}</span>
          </div>
          <div class="metric-row">
            <span class="metric-key">CV R²</span>
            <span class="metric-value">${m.cv_r2_mean.toFixed(4)} ±${m.cv_r2_std.toFixed(4)}</span>
          </div>
        </div>
      `;
      grid.appendChild(card);
    });
    container.innerHTML = "";
    container.appendChild(grid);
  } catch (e) {
    document.getElementById("modelInfoContent").textContent =
      "⚠️ Run `python models/train.py` to train the model, then restart the API server.";
    modelBadge.textContent = "Model not trained";
  }
}

loadModelInfo();

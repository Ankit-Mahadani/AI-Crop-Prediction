"""
Visualization Utilities
Generates feature importance, model comparison, and optimization plots.
"""

import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

MODELS_DIR   = os.path.join(os.path.dirname(__file__), "..", "models")
OUTPUTS_DIR  = os.path.join(os.path.dirname(__file__), "..", "outputs", "plots")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# ── Style ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#0f1117",
    "axes.facecolor":   "#1a1e2e",
    "axes.edgecolor":   "#3d4466",
    "axes.labelcolor":  "#c8cce8",
    "xtick.color":      "#c8cce8",
    "ytick.color":      "#c8cce8",
    "text.color":       "#e0e3f8",
    "grid.color":       "#2a2f4a",
    "figure.dpi":       120,
})

GREEN  = "#4ade80"
BLUE   = "#60a5fa"
PURPLE = "#a78bfa"
ORANGE = "#fb923c"
COLORS = [GREEN, BLUE, PURPLE, ORANGE]


def plot_feature_importance(top_n: int = 15, save: bool = True) -> str:
    fi_path = os.path.join(MODELS_DIR, "feature_importance.json")
    if not os.path.exists(fi_path):
        raise FileNotFoundError("feature_importance.json not found. Run training first.")

    with open(fi_path) as f:
        fi = json.load(f)

    items = list(fi.items())[:top_n]
    names  = [i[0] for i in items]
    values = [i[1] for i in items]

    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.barh(names[::-1], values[::-1],
                   color=[BLUE if v < max(values) else GREEN for v in values[::-1]],
                   edgecolor="none", height=0.65)

    for bar, val in zip(bars, values[::-1]):
        ax.text(bar.get_width() + 0.002, bar.get_y() + bar.get_height() / 2,
                f"{val:.4f}", va="center", fontsize=8, color="#e0e3f8")

    ax.set_title("Feature Importance (Top 15)", fontsize=14, fontweight="bold",
                 color="#e0e3f8", pad=12)
    ax.set_xlabel("Relative Importance", fontsize=10)
    ax.grid(axis="x", linewidth=0.5, alpha=0.5)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()

    out_path = os.path.join(OUTPUTS_DIR, "feature_importance.png")
    if save:
        plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"✅ Saved: {out_path}")
    return out_path


def plot_model_comparison(save: bool = True) -> str:
    res_path = os.path.join(MODELS_DIR, "results.json")
    if not os.path.exists(res_path):
        raise FileNotFoundError("results.json not found. Run training first.")

    with open(res_path) as f:
        data = json.load(f)

    models  = [m["name"] for m in data["models"]]
    rmse    = [m["rmse"] for m in data["models"]]
    mae     = [m["mae"]  for m in data["models"]]
    r2      = [m["r2"]   for m in data["models"]]

    x = np.arange(len(models))
    width = 0.25

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.suptitle("Model Performance Comparison", fontsize=15,
                 fontweight="bold", color="#e0e3f8", y=1.02)

    for ax, metric, vals, color, label in [
        (axes[0], "RMSE (↓ better)", rmse, ORANGE, "RMSE"),
        (axes[1], "MAE  (↓ better)", mae,  BLUE,   "MAE"),
        (axes[2], "R²   (↑ better)", r2,   GREEN,  "R²"),
    ]:
        bars = ax.bar(x, vals, color=color, edgecolor="none", width=0.55)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                    f"{val:.4f}", ha="center", va="bottom", fontsize=8, color="#e0e3f8")
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=15, ha="right", fontsize=9)
        ax.set_title(metric, fontsize=10, color="#c8cce8")
        ax.grid(axis="y", linewidth=0.5, alpha=0.4)
        ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    out_path = os.path.join(OUTPUTS_DIR, "model_comparison.png")
    if save:
        plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"✅ Saved: {out_path}")
    return out_path


def plot_optimization_results(opt_result: dict, save: bool = True) -> str:
    combos  = opt_result["combinations"]
    labels  = [f"F={c['fertilizer'][:1]}/I={c['irrigation'][:1]}" for c in combos]
    yields  = [c["predicted_yield"] for c in combos]
    colors  = [GREEN if c == opt_result["best"] else BLUE for c in combos]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, yields, color=colors, edgecolor="none", width=0.55)

    for bar, val in zip(bars, yields):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                f"{val:.2f}", ha="center", va="bottom", fontsize=10, fontweight="bold",
                color="#e0e3f8")

    legend_patches = [
        mpatches.Patch(color=GREEN, label="Best Combo"),
        mpatches.Patch(color=BLUE,  label="Other Combos"),
    ]
    ax.legend(handles=legend_patches, fontsize=9)
    ax.set_title("Yield Optimization: Fertilizer × Irrigation", fontsize=13,
                 fontweight="bold", color="#e0e3f8", pad=10)
    ax.set_ylabel("Predicted Yield (tons/ha)", fontsize=10)
    ax.grid(axis="y", linewidth=0.5, alpha=0.4)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()

    out_path = os.path.join(OUTPUTS_DIR, "optimization_results.png")
    if save:
        plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"✅ Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    plot_feature_importance()
    plot_model_comparison()
    print("All plots saved to outputs/plots/")

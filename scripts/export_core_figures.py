from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from runtime_checks import ensure_packages, ensure_supported_runtime

ensure_supported_runtime()
ensure_packages([
    "numpy",
    "pandas",
    "matplotlib",
    "seaborn",
])

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from project_paths import build_paths, require_paths

sns.set_theme(style="whitegrid")


def finish_plot(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()


def main() -> None:
    paths = build_paths()
    require_paths(paths, ["PGA_BRIDGE_CSV", "EDR_CSV", "SVI_CSV", "ML_PREDICTIONS_CSV"])

    figures_dir = paths["FIGURES_DIR"]
    pga_df = pd.read_csv(paths["PGA_BRIDGE_CSV"], low_memory=False)
    edr_df = pd.read_csv(paths["EDR_CSV"], low_memory=False)
    svi_df = pd.read_csv(paths["SVI_CSV"], low_memory=False)
    ml_df = pd.read_csv(paths["ML_PREDICTIONS_CSV"], low_memory=False)

    plot_df = pga_df.dropna(subset=["latitude", "longitude"]).copy()
    if not plot_df.empty:
        plt.figure(figsize=(8, 6))
        plt.scatter(plot_df["longitude"], plot_df["latitude"], s=5, alpha=0.5)
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.title("Bridge Locations in California")
        plt.grid(True, alpha=0.3)
        finish_plot(figures_dir / "core_bridge_locations.png")

    pga_plot_df = pga_df.dropna(subset=["pga"]).copy()
    if not pga_plot_df.empty:
        plt.figure(figsize=(8, 6))
        plt.hist(pga_plot_df["pga"], bins=40, color="#33658A", edgecolor="white")
        plt.xlabel("PGA")
        plt.ylabel("Count")
        plt.title("Distribution of Sampled PGA Values")
        plt.grid(True, alpha=0.3)
        finish_plot(figures_dir / "core_pga_distribution.png")

    class_counts = edr_df["HWB_CLASS"].dropna().value_counts().sort_values(ascending=False)
    if not class_counts.empty:
        plt.figure(figsize=(10, 6))
        class_counts.plot(kind="bar", color="#2F6690")
        plt.xlabel("HWB Class")
        plt.ylabel("Count")
        plt.title("Distribution of HAZUS Bridge Classes")
        plt.grid(True, axis="y", alpha=0.3)
        finish_plot(figures_dir / "core_hazus_class_distribution.png")

    edr_plot_df = edr_df.dropna(subset=["EDR"]).copy()
    if not edr_plot_df.empty:
        plt.figure(figsize=(8, 6))
        plt.hist(edr_plot_df["EDR"], bins=40, color="#55A630", edgecolor="white")
        plt.xlabel("Expected Damage Ratio (EDR)")
        plt.ylabel("Count")
        plt.title("Distribution of Expected Damage Ratio")
        plt.grid(True, alpha=0.3)
        finish_plot(figures_dir / "core_edr_distribution.png")

        log_edr_vals = edr_plot_df.loc[edr_plot_df["EDR"] > 0, "EDR"]
        if not log_edr_vals.empty:
            plt.figure(figsize=(8, 6))
            plt.hist(np.log10(log_edr_vals), bins=60, color="#8E5572", edgecolor="white")
            plt.xlabel("log10(EDR)")
            plt.ylabel("Count")
            plt.title("Log-Transformed Expected Damage Ratio Distribution")
            plt.grid(True, alpha=0.3)
            finish_plot(figures_dir / "core_log_edr_distribution.png")

        top_classes = edr_df["HWB_CLASS"].dropna().value_counts().head(10).index
        box_df = edr_df[edr_df["HWB_CLASS"].isin(top_classes)].copy()
        if not box_df.empty:
            plt.figure(figsize=(12, 6))
            sns.boxplot(data=box_df, x="HWB_CLASS", y="EDR", color="#8FB8DE")
            plt.xlabel("HWB Class")
            plt.ylabel("Expected Damage Ratio (EDR)")
            plt.title("EDR by HAZUS Bridge Class")
            plt.xticks(rotation=45, ha="right")
            finish_plot(figures_dir / "core_edr_by_hazus_class.png")

    damage_cols = ["P_DS0", "P_DS1", "P_DS2", "P_DS3", "P_DS4"]
    mean_probs = edr_df[damage_cols].mean(numeric_only=True)
    if not mean_probs.empty:
        plt.figure(figsize=(8, 6))
        mean_probs.plot(kind="bar", color="#BC4749")
        plt.xlabel("Damage State")
        plt.ylabel("Average Probability")
        plt.title("Average Damage-State Probabilities")
        plt.grid(True, axis="y", alpha=0.3)
        finish_plot(figures_dir / "core_damage_state_probabilities.png")

    top_damage_classes = edr_df["HWB_CLASS"].dropna().value_counts().head(8).index
    class_damage = (
        edr_df[edr_df["HWB_CLASS"].isin(top_damage_classes)]
        .groupby("HWB_CLASS")[damage_cols]
        .mean()
    )
    if not class_damage.empty:
        ax = class_damage.plot(kind="bar", stacked=True, figsize=(10, 6), colormap="viridis")
        ax.set_xlabel("HWB Class")
        ax.set_ylabel("Average Probability")
        ax.set_title("Average Damage-State Probabilities by HAZUS Class")
        ax.grid(True, axis="y", alpha=0.3)
        plt.xticks(rotation=45, ha="right")
        finish_plot(figures_dir / "core_damage_state_by_hazus_class.png")

    svi_vals = svi_df["SVI"].dropna()
    if not svi_vals.empty:
        plt.figure(figsize=(8, 6))
        plt.hist(svi_vals, bins=40, color="#6A994E", edgecolor="white")
        plt.xlabel("SVI")
        plt.ylabel("Count")
        plt.title("Distribution of Seismic Vulnerability Index")
        plt.grid(True, alpha=0.3)
        finish_plot(figures_dir / "core_svi_distribution.png")

    svi_plot_df = svi_df.dropna(subset=["SVI", "EDR"]).copy()
    if not svi_plot_df.empty:
        plt.figure(figsize=(8, 6))
        plt.scatter(svi_plot_df["SVI"], svi_plot_df["EDR"], s=8, alpha=0.35)
        plt.xlabel("SVI")
        plt.ylabel("Expected Damage Ratio (EDR)")
        plt.title("SVI vs EDR")
        plt.grid(True, alpha=0.3)
        finish_plot(figures_dir / "core_svi_vs_edr.png")

    mean_svi_by_class = svi_df.groupby("HWB_CLASS")["SVI"].mean().sort_values(ascending=False)
    if not mean_svi_by_class.empty:
        plt.figure(figsize=(10, 6))
        mean_svi_by_class.plot(kind="bar", color="#A7C957")
        plt.xlabel("HWB Class")
        plt.ylabel("Mean SVI")
        plt.title("Average SVI by HAZUS Class")
        plt.grid(True, axis="y", alpha=0.3)
        finish_plot(figures_dir / "core_mean_svi_by_hazus_class.png")

    pga_svi_df = svi_df.dropna(subset=["pga", "SVI"]).copy()
    if not pga_svi_df.empty:
        plt.figure(figsize=(8, 6))
        plt.scatter(pga_svi_df["pga"], pga_svi_df["SVI"], s=8, alpha=0.35)
        plt.xlabel("PGA")
        plt.ylabel("SVI")
        plt.title("PGA vs SVI")
        plt.grid(True, alpha=0.3)
        finish_plot(figures_dir / "core_pga_vs_svi.png")

    if {"Actual_EDR", "Predicted_EDR"}.issubset(ml_df.columns):
        actual = ml_df["Actual_EDR"].dropna()
        predicted = ml_df["Predicted_EDR"].dropna()
        paired = ml_df.dropna(subset=["Actual_EDR", "Predicted_EDR"]).copy()

        if not paired.empty:
            plt.figure(figsize=(7, 6))
            plt.scatter(paired["Actual_EDR"], paired["Predicted_EDR"], s=14, alpha=0.45)
            lims = [
                min(paired["Actual_EDR"].min(), paired["Predicted_EDR"].min()),
                max(paired["Actual_EDR"].max(), paired["Predicted_EDR"].max()),
            ]
            plt.plot(lims, lims, color="black", linestyle="--", linewidth=1)
            best_model = paired["Best_Model"].mode().iloc[0] if "Best_Model" in paired.columns else "Best Model"
            plt.xlabel("Actual EDR")
            plt.ylabel("Predicted EDR")
            plt.title(f"Notebook ML Predictions ({best_model})")
            plt.grid(True, alpha=0.3)
            finish_plot(figures_dir / "core_ml_actual_vs_predicted.png")

            residual = paired["Actual_EDR"] - paired["Predicted_EDR"]
            plt.figure(figsize=(8, 6))
            sns.histplot(residual, bins=40, kde=True, color="#386641")
            plt.xlabel("Residual (Actual - Predicted)")
            plt.ylabel("Count")
            plt.title("Notebook ML Residual Distribution")
            plt.grid(True, axis="y", alpha=0.3)
            finish_plot(figures_dir / "core_ml_residuals.png")


if __name__ == "__main__":
    main()

"""
Damage State Classification
============================
Classifies bridges into HAZUS-aligned damage states (DS0-DS4) based on
NDVI change as a proxy for ground deformation / structural damage.

Damage State Thresholds (NDVI change):
    DS0 - No Damage:    ndvi_change > -0.02
    DS1 - Slight:       -0.05 < ndvi_change <= -0.02
    DS2 - Moderate:     -0.10 < ndvi_change <= -0.05
    DS3 - Extensive:    -0.15 < ndvi_change <= -0.10
    DS4 - Complete:     ndvi_change <= -0.15
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

# Damage state definitions
DS_ORDER = [
    "DS0 – No Damage",
    "DS1 – Slight",
    "DS2 – Moderate",
    "DS3 – Extensive",
    "DS4 – Complete",
]

DS_COLORS = {
    "DS0 – No Damage": "#2ca02c",
    "DS1 – Slight":    "#ffdd57",
    "DS2 – Moderate":  "#ff9f1c",
    "DS3 – Extensive": "#e63946",
    "DS4 – Complete":  "#6a040f",
}

# NDVI change thresholds
NDVI_THRESHOLDS = {
    "DS4 – Complete":  -0.15,
    "DS3 – Extensive": -0.10,
    "DS2 – Moderate":  -0.05,
    "DS1 – Slight":    -0.02,
}


def _classify_single(ndvi_change):
    """Classify a single NDVI change value into a damage state."""
    if pd.isna(ndvi_change):
        return np.nan
    if ndvi_change <= -0.15:
        return "DS4 – Complete"
    elif ndvi_change <= -0.10:
        return "DS3 – Extensive"
    elif ndvi_change <= -0.05:
        return "DS2 – Moderate"
    elif ndvi_change <= -0.02:
        return "DS1 – Slight"
    else:
        return "DS0 – No Damage"


def classify_damage_states(df, ndvi_col="ndvi_chan"):
    """
    Assign damage states to all bridges based on NDVI change.

    Parameters
    ----------
    df : DataFrame
        Must contain the NDVI change column.
    ndvi_col : str
        Name of the NDVI change column.

    Returns
    -------
    df : DataFrame
        Input DataFrame with 'damage_state' column added.
    """
    df = df.copy()
    df["damage_state"] = df[ndvi_col].apply(_classify_single)
    return df


def plot_damage_distribution(df, save_path=None):
    """
    Bar chart and histogram of damage state distribution.

    Parameters
    ----------
    df : DataFrame
        Must contain 'damage_state' and 'ndvi_chan' columns.
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Bar chart of counts
    counts = df["damage_state"].value_counts().reindex(DS_ORDER).fillna(0).astype(int)
    bars = axes[0].bar(
        range(len(DS_ORDER)), counts.values,
        color=[DS_COLORS[ds] for ds in DS_ORDER], edgecolor="black", linewidth=0.5,
    )
    for bar, count in zip(bars, counts.values):
        pct = count / len(df) * 100
        axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 50,
                     f"{count:,}\n({pct:.1f}%)", ha="center", va="bottom", fontsize=9)
    axes[0].set_xticks(range(len(DS_ORDER)))
    axes[0].set_xticklabels([ds.split(" – ")[1] for ds in DS_ORDER], fontsize=10)
    axes[0].set_ylabel("Number of Bridges")
    axes[0].set_title("Phase 1: NDVI-Based Damage State Classification", fontweight="bold")

    # Histogram colored by damage state
    ndvi_bins = np.linspace(df["ndvi_chan"].min() - 0.005, df["ndvi_chan"].max() + 0.005, 80)
    for ds in reversed(DS_ORDER):
        subset = df.loc[df["damage_state"] == ds, "ndvi_chan"]
        if len(subset) > 0:
            axes[1].hist(subset, bins=ndvi_bins, alpha=0.8, label=ds, color=DS_COLORS[ds])
    axes[1].set_xlabel("NDVI Change")
    axes[1].set_ylabel("Count")
    axes[1].set_title("NDVI Change Distribution by Damage State", fontweight="bold")
    axes[1].legend(fontsize=8)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
        print(f"Figure saved: {save_path}")
    plt.show()
    plt.close(fig)


def print_damage_summary(df):
    """Print a formatted summary table of damage classification results."""
    counts = df["damage_state"].value_counts().reindex(DS_ORDER).fillna(0).astype(int)
    total = len(df)

    print("=" * 60)
    print("PHASE 1: DAMAGE STATE CLASSIFICATION SUMMARY")
    print("=" * 60)
    print(f"{'Damage State':<22} {'Count':>8} {'Percent':>10}")
    print("-" * 42)
    for ds in DS_ORDER:
        c = counts[ds]
        print(f"  {ds:<20} {c:>8,} {c/total*100:>9.2f}%")
    print("-" * 42)
    print(f"  {'TOTAL':<20} {total:>8,} {'100.00%':>10}")
    damaged = total - counts[DS_ORDER[0]]
    print(f"\n  Bridges with ANY damage (≥DS1): {damaged:,} ({damaged/total*100:.1f}%)")

"""
Economic Disruption Module
==========================
Computes the Traffic Disruption Index (TDI) as a proxy for economic loss.

TDI = P(≥DS1) × ADT (Average Daily Traffic)

Two variants:
    - TDI_binary:   1{damage ≥ DS1} × ADT  (vehicles at risk)
    - TDI_weighted:  severity_weight × ADT   (damage-weighted loss proxy,
                     analogous to MDR × TIV in property cat modeling)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

from .damage_classification import DS_ORDER, DS_COLORS

# Severity weights (analogous to Mean Damage Ratios)
DS_SEVERITY_WEIGHT = {
    "DS0 – No Damage": 0.00,
    "DS1 – Slight":    0.02,
    "DS2 – Moderate":  0.10,
    "DS3 – Extensive": 0.40,
    "DS4 – Complete":  1.00,
}


def compute_tdi(df, adt_col="avg_daily_"):
    """
    Compute Traffic Disruption Index for each bridge.

    Parameters
    ----------
    df : DataFrame
        Must contain 'damage_state' and ADT column.
    adt_col : str
        Name of the Average Daily Traffic column.

    Returns
    -------
    df : DataFrame
        With 'severity_weight', 'is_damaged', 'TDI_binary', 'TDI_weighted' added.
    """
    df = df.copy()
    df["severity_weight"] = df["damage_state"].map(DS_SEVERITY_WEIGHT)
    df["is_damaged"] = (df["damage_state"] != "DS0 – No Damage").astype(int)
    df["TDI_binary"] = df["is_damaged"] * df[adt_col]
    df["TDI_weighted"] = df["severity_weight"] * df[adt_col]
    return df


def summarize_tdi(df, adt_col="avg_daily_"):
    """
    Print a formatted TDI summary table.
    """
    total_bridges = len(df)
    total_adt = df[adt_col].sum()
    at_risk_adt = df["TDI_binary"].sum()
    weighted_adt = df["TDI_weighted"].sum()

    print("=" * 72)
    print("PHASE 3: ECONOMIC DISRUPTION SUMMARY (Traffic Disruption Index)")
    print("=" * 72)
    print(f"  Total bridges:                               {total_bridges:>12,}")
    print(f"  Total portfolio ADT (vehicles/day):          {total_adt:>12,.0f}")
    print(f"  Vehicles at risk (≥DS1):                     {at_risk_adt:>12,.0f}  ({at_risk_adt/total_adt*100:.1f}%)")
    print(f"  Damage-weighted TDI:                         {weighted_adt:>12,.0f}  ({weighted_adt/total_adt*100:.1f}% effective)")

    print(f"\n{'State':<24} {'Bridges':>8} {'Sum ADT':>14} {'Wt. TDI':>14} {'% Total TDI':>14}")
    print("-" * 76)
    for ds in DS_ORDER:
        sub = df[df["damage_state"] == ds]
        n = len(sub)
        adt = sub[adt_col].sum()
        tdi = sub["TDI_weighted"].sum()
        pct = tdi / weighted_adt * 100 if weighted_adt > 0 else 0
        print(f"  {ds:<22} {n:>8,} {adt:>14,.0f} {tdi:>14,.0f} {pct:>13.1f}%")


def plot_tdi(df, save_path=None):
    """
    Two-panel figure: TDI by damage state + PGA vs TDI scatter.
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Left: stacked bar of weighted TDI per damage state
    tdi_by_ds = [
        df.loc[df["damage_state"] == ds, "TDI_weighted"].sum() / 1e6
        for ds in DS_ORDER
    ]
    colors = [DS_COLORS[ds] for ds in DS_ORDER]
    axes[0].bar(range(len(DS_ORDER)), tdi_by_ds, color=colors, edgecolor="black", linewidth=0.5)
    axes[0].set_xticks(range(len(DS_ORDER)))
    axes[0].set_xticklabels([ds.split(" – ")[1] for ds in DS_ORDER], fontsize=10)
    axes[0].set_ylabel("TDI (Millions of Vehicles/Day)")
    axes[0].set_title("Phase 3: TDI by Damage State", fontweight="bold")

    # Right: scatter PGA vs TDI_weighted
    for ds in DS_ORDER:
        sub = df[df["damage_state"] == ds]
        if len(sub) > 0:
            axes[1].scatter(
                sub["pga"], sub["TDI_weighted"] / 1e3,
                color=DS_COLORS[ds], alpha=0.4, s=15, label=ds,
            )
    axes[1].set_xlabel("PGA (g)")
    axes[1].set_ylabel("TDI (Thousands of Vehicles/Day)")
    axes[1].set_title("PGA vs Damage-Weighted TDI", fontweight="bold")
    axes[1].legend(fontsize=8, loc="upper left")

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
        print(f"Figure saved: {save_path}")
    plt.show()
    plt.close(fig)

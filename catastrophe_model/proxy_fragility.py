"""
Proxy Fragility Curves
======================
Derives empirical fragility curves from observed NDVI-based damage states
and PGA values. Fits lognormal CDFs to the empirical exceedance data.

Fragility curve: P(DS ≥ ds | PGA) = Φ(ln(PGA / θ) / β)
    where θ = median capacity, β = dispersion
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.optimize import curve_fit

from .damage_classification import DS_ORDER, DS_COLORS, NDVI_THRESHOLDS


def lognormal_cdf(pga, theta, beta):
    """
    Lognormal fragility function.

    Parameters
    ----------
    pga : float or array
        Peak Ground Acceleration (g).
    theta : float
        Median capacity (g).
    beta : float
        Log-standard deviation (dispersion).

    Returns
    -------
    float or array : Probability of exceedance.
    """
    return norm.cdf(np.log(pga / theta) / beta)


def compute_fragility_curves(df, pga_col="pga", ndvi_col="ndvi_chan", n_bins=25):
    """
    Compute empirical fragility data and fit lognormal curves.

    Parameters
    ----------
    df : DataFrame
        Must contain PGA and NDVI change columns.
    pga_col : str
        PGA column name.
    ndvi_col : str
        NDVI change column name.
    n_bins : int
        Number of PGA bins for empirical estimation.

    Returns
    -------
    empirical : dict
        {damage_state: DataFrame with 'pga_mid' and 'prob'} for each DS.
    fitted_params : dict
        {damage_state: {'theta': float, 'beta': float}} for each DS.
    """
    df_clean = df.dropna(subset=[pga_col, ndvi_col]).copy()
    pga_bins = np.linspace(df_clean[pga_col].min(), df_clean[pga_col].max(), n_bins + 1)
    df_clean["pga_bin"] = pd.cut(df_clean[pga_col], bins=pga_bins, include_lowest=True)

    # NDVI cutoffs for each damage state
    ds_cutoffs = {
        "DS1 – Slight":    -0.02,
        "DS2 – Moderate":  -0.05,
        "DS3 – Extensive": -0.10,
        "DS4 – Complete":  -0.15,
    }

    empirical = {}
    fitted_params = {}

    for ds, cutoff in ds_cutoffs.items():
        rows = []
        for interval, group in df_clean.groupby("pga_bin", observed=True):
            if len(group) >= 5:
                p = (group[ndvi_col] <= cutoff).mean()
                rows.append({"pga_mid": interval.mid, "prob": p})

        if not rows:
            continue

        emp_df = pd.DataFrame(rows)
        empirical[ds] = emp_df

        # Fit lognormal CDF
        try:
            popt, _ = curve_fit(
                lognormal_cdf,
                emp_df["pga_mid"].values,
                emp_df["prob"].values,
                p0=[0.5, 1.0],
                bounds=([0.001, 0.01], [10.0, 5.0]),
                maxfev=10000,
            )
            fitted_params[ds] = {"theta": popt[0], "beta": popt[1]}
        except RuntimeError:
            fitted_params[ds] = {"theta": np.nan, "beta": np.nan}

    return empirical, fitted_params


def plot_fragility_curves(empirical, fitted_params, save_path=None):
    """
    Plot empirical points and fitted lognormal fragility curves.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    pga_range = np.linspace(0.01, 2.0, 200)

    ds_plot_order = ["DS1 – Slight", "DS2 – Moderate", "DS3 – Extensive", "DS4 – Complete"]

    for ds in ds_plot_order:
        color = DS_COLORS[ds]

        # Plot empirical points
        if ds in empirical:
            emp = empirical[ds]
            ax.scatter(emp["pga_mid"], emp["prob"], color=color, s=30, zorder=5, alpha=0.7)

        # Plot fitted curve
        if ds in fitted_params and not np.isnan(fitted_params[ds]["theta"]):
            theta = fitted_params[ds]["theta"]
            beta = fitted_params[ds]["beta"]
            curve = lognormal_cdf(pga_range, theta, beta)
            ax.plot(pga_range, curve, color=color, linewidth=2,
                    label=f"{ds}  (θ={theta:.3f}g, β={beta:.2f})")

    ax.set_xlabel("Peak Ground Acceleration, PGA (g)", fontsize=12)
    ax.set_ylabel("P(DS ≥ ds | PGA)", fontsize=12)
    ax.set_title("Phase 2: Empirical Fragility Curves (NDVI-Based Proxy)", fontsize=14, fontweight="bold")
    ax.legend(fontsize=9, loc="lower right")
    ax.set_xlim(0, 2.0)
    ax.set_ylim(0, 1.0)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
        print(f"Figure saved: {save_path}")
    plt.show()
    plt.close(fig)


def print_fragility_summary(fitted_params):
    """Print fitted fragility curve parameters."""
    print("=" * 60)
    print("PHASE 2: FITTED FRAGILITY CURVE PARAMETERS")
    print("=" * 60)
    print(f"{'Damage State':<22} {'Median θ (g)':>14} {'Dispersion β':>14}")
    print("-" * 52)
    for ds in ["DS1 – Slight", "DS2 – Moderate", "DS3 – Extensive", "DS4 – Complete"]:
        if ds in fitted_params:
            p = fitted_params[ds]
            print(f"  {ds:<20} {p['theta']:>14.3f} {p['beta']:>14.2f}")

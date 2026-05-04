"""
build_earthquake_charts.py
Generates all charts from the updated run_earthquake_scenario.py output.
Run from NCDS\src
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
import config

# ── Load data ──────────────────────────────────────────────────────────────────
ncps = pd.read_csv(
    config.DATA_PROCESSED / "ncps_earthquake_w001001.csv",
    dtype={"bridge_id": str}
)
ncps["bridge_id"] = ncps["bridge_id"].str.strip().str.upper()

# ── Bridge lists ───────────────────────────────────────────────────────────────
COLLAPSED = ["53 1609","53 1797L","53 1797R",
             "53 1960F","53 1964F","53 2205","53 1060"]
MAJOR     = ["53 2187","53 0640","53 0833","53 2498","53 1336R",
             "53 1627G","53 1615","53 1493S","53 2327F","53 1408",
             "53 0629","53 0490","53 0620","53 2182","53 2027L",
             "53 1960G","53 0025"]

COLLAPSED_UP = [b.upper() for b in COLLAPSED]
MAJOR_UP     = [b.upper() for b in MAJOR]
ALL_MCEER_UP = COLLAPSED_UP + MAJOR_UP

total = len(ncps)

collapsed_df = ncps[ncps["bridge_id"].isin(COLLAPSED_UP)].copy()
major_df     = ncps[ncps["bridge_id"].isin(MAJOR_UP)].copy()
all_mceer    = ncps[ncps["bridge_id"].isin(ALL_MCEER_UP)].copy()
other        = ncps[~ncps["bridge_id"].isin(ALL_MCEER_UP)].copy()

config.OUTPUTS.mkdir(exist_ok=True)

BROWN  = "#5C1A00"
CREAM  = "#F3EDE6"
RED    = "#d73027"
ORANGE = "#f46d43"
YELLOW = "#fdae61"
LGREEN = "#a6d96a"
GREEN  = "#1a9641"
GREY   = "#888888"


# ══════════════════════════════════════════════════════════════════════════════
# CHART 1 — PGA vs p_extensive scatter
# Shows the fragility matrix in action across all 3,681 bridges
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 6), facecolor="white")

# All bridges
ax.scatter(other["pga"], other["p_extensive"],
           c=GREY, s=8, alpha=0.25, linewidths=0,
           label=f"All bridges (n={len(other):,})")

# Major
ax.scatter(major_df["pga"], major_df["p_extensive"],
           c=RED, s=60, marker="^", alpha=0.85,
           linewidths=0.5, edgecolors="white",
           label=f"MCEER Major (n={len(major_df)})", zorder=4)

# Collapsed
ax.scatter(collapsed_df["pga"], collapsed_df["p_extensive"],
           c="black", s=100, marker="X", alpha=1.0,
           linewidths=0.8, edgecolors=RED,
           label=f"MCEER Collapsed (n={len(collapsed_df)})", zorder=5)

# Annotate key bridges
for _, row in collapsed_df.iterrows():
    if row["pga"] > 0.60:
        ax.annotate(
            row["bridge_id"].replace(" ", "\u00a0"),
            (row["pga"], row["p_extensive"]),
            xytext=(8, 4), textcoords="offset points",
            fontsize=7, color="black",
            arrowprops=dict(arrowstyle="-", color=GREY, lw=0.5)
        )

# Fragility step line
pga_range = np.linspace(0, 1.2, 500)
fragility = [
    (0.00, 0.15, 0.000),(0.15, 0.20, 0.000),(0.20, 0.30, 0.021),
    (0.30, 0.40, 0.021),(0.40, 0.50, 0.106),(0.50, 0.60, 0.185),
    (0.60, 0.70, 0.111),(0.70, 0.80, 0.048),(0.80, 0.90, 0.120),
    (0.90, 1.00, 0.345),(1.00, 1.10, 0.071),(1.10, 9.99, 0.100),
]
def pga_to_p(pga):
    for lo, hi, p in fragility:
        if lo <= pga < hi:
            return p
    return 0.0

p_line = [pga_to_p(p) for p in pga_range]
ax.step(pga_range, p_line, color=BROWN, linewidth=2,
        linestyle="--", label="Fragility matrix (MCEER-98-0004)",
        where="post", zorder=3)

ax.set_xlabel("Peak Ground Acceleration (g)", fontsize=11)
ax.set_ylabel("P(damage \u2265 Extensive)", fontsize=11)
ax.set_title(
    "PGA \u2192 Damage Probability | Northridge 1994 \u2014 3,681 Bridges\n"
    "Empirical fragility matrix from MCEER-98-0004 (multiple-span concrete)",
    fontsize=11, color=BROWN
)
ax.set_xlim(0, 1.05)
ax.set_ylim(-0.02, 0.42)
ax.legend(fontsize=9, framealpha=0.9)
ax.grid(True, alpha=0.3, linestyle="--")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
out1 = config.OUTPUTS / "ncds_pga_fragility.png"
plt.savefig(str(out1), dpi=180, bbox_inches="tight")
plt.close()
print(f"Saved: {out1}")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 2 — NCPS rank comparison: Collapsed vs Major vs All
# Horizontal bar chart showing where each MCEER bridge lands
# ══════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(14, 8), facecolor="white")

def rank_bar_chart(ax, df, color, title, total):
    df_sorted = df.sort_values("ncps_rank")
    bars = ax.barh(
        range(len(df_sorted)),
        df_sorted["ncps_rank"],
        color=color, alpha=0.85, edgecolor="white", linewidth=0.5
    )
    # 5% threshold line
    ax.axvline(total * 0.05, color=RED, linestyle="--",
               linewidth=1.2, label=f"Top 5% ({int(total*0.05):,})")
    ax.axvline(total * 0.10, color=ORANGE, linestyle="--",
               linewidth=1.0, label=f"Top 10% ({int(total*0.10):,})")

    ax.set_yticks(range(len(df_sorted)))
    ax.set_yticklabels(df_sorted["bridge_id"].str.title(), fontsize=8)
    ax.set_xlabel("NCPS Rank (lower = higher priority)", fontsize=10)
    ax.set_xlim(0, total)
    ax.set_title(title, fontsize=11, color=BROWN, fontweight="bold")
    ax.legend(fontsize=8, loc="lower right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, axis="x", alpha=0.3, linestyle="--")

    # Annotate rank
    for i, (_, row) in enumerate(df_sorted.iterrows()):
        pct = row["ncps_rank"] / total * 100
        ax.text(
            row["ncps_rank"] + 30, i,
            f"  #{int(row['ncps_rank'])} ({pct:.1f}%)",
            va="center", fontsize=7.5, color="#333333"
        )

rank_bar_chart(axes[0], collapsed_df, BROWN,
               f"Collapsed Bridges (n={len(collapsed_df)})\n"
               f"Mean rank: {collapsed_df['ncps_rank'].mean():.0f} "
               f"(top {collapsed_df['ncps_rank'].mean()/total*100:.1f}%)",
               total)

rank_bar_chart(axes[1], major_df, RED,
               f"Major Damage Bridges (n={len(major_df)})\n"
               f"Mean rank: {major_df['ncps_rank'].mean():.0f} "
               f"(top {major_df['ncps_rank'].mean()/total*100:.1f}%)",
               total)

fig.suptitle(
    "NCPS Priority Ranks \u2014 MCEER Northridge 1994 Documented Bridges\n"
    "Empirical fragility matrix | MCEER PGA overrides | Collapse floor applied",
    fontsize=12, color=BROWN, fontweight="bold", y=1.01
)
plt.tight_layout()
out2 = config.OUTPUTS / "ncds_mceer_rank_comparison_v2.png"
plt.savefig(str(out2), dpi=180, bbox_inches="tight")
plt.close()
print(f"Saved: {out2}")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 3 — NBI condition vs NCPS scatter (updated with new pipeline)
# ══════════════════════════════════════════════════════════════════════════════

# Load NBI condition data
nbi = pd.read_csv(
    config.DATA_RAW / "CA94.csv",
    dtype=str, low_memory=False
)
nbi["STRUCTURE_NUMBER_008"] = (
    nbi["STRUCTURE_NUMBER_008"].str.strip().str.upper()
)
nbi["COUNTY_CODE_003"] = nbi["COUNTY_CODE_003"].str.strip()
la_ven = nbi[nbi["COUNTY_CODE_003"].isin(["37","111"])].copy()
la_ven = la_ven[la_ven["DECK_COND_058"].notna()].copy()
la_ven["nbi_cond"] = pd.to_numeric(
    la_ven["DECK_COND_058"], errors="coerce"
)
la_ven = la_ven.drop_duplicates(
    subset="STRUCTURE_NUMBER_008"
)[["STRUCTURE_NUMBER_008","nbi_cond"]].rename(
    columns={"STRUCTURE_NUMBER_008": "bridge_id"}
)

merged = ncps.merge(la_ven, on="bridge_id", how="left")
merged = merged[merged["nbi_cond"].notna()].copy()
merged["rank_pct"] = merged["ncps_rank"] / total * 100

m_other     = merged[~merged["bridge_id"].isin(ALL_MCEER_UP)]
m_collapsed = merged[merged["bridge_id"].isin(COLLAPSED_UP)]
m_major     = merged[merged["bridge_id"].isin(MAJOR_UP)]

fig, ax = plt.subplots(figsize=(11, 7), facecolor="white")

# All bridges
ax.scatter(m_other["nbi_cond"], m_other["rank_pct"],
           c=GREY, s=6, alpha=0.2, linewidths=0,
           label=f"All bridges (n={len(m_other):,})")

# Major
ax.scatter(m_major["nbi_cond"], m_major["rank_pct"],
           c=RED, s=70, marker="^", alpha=0.9,
           linewidths=0.5, edgecolors="white",
           label=f"MCEER Major (n={len(m_major)})", zorder=4)

# Collapsed
ax.scatter(m_collapsed["nbi_cond"], m_collapsed["rank_pct"],
           c="black", s=120, marker="X",
           linewidths=1, edgecolors=RED,
           label=f"MCEER Collapsed (n={len(m_collapsed)})", zorder=5)

# Threshold lines
ax.axhline(5,  color=RED,    linestyle="--", linewidth=1,
           alpha=0.7, label="Top 5% threshold")
ax.axhline(10, color=ORANGE, linestyle="--", linewidth=1,
           alpha=0.7, label="Top 10% threshold")

# Pearson r annotation
from scipy import stats
r, p = stats.pearsonr(
    merged["nbi_cond"].dropna(),
    merged[merged["nbi_cond"].notna()]["rank_pct"]
)
ax.text(0.97, 0.97,
        f"Pearson r = {r:.3f}\np = {p:.3f}",
        transform=ax.transAxes, ha="right", va="top",
        fontsize=10, color=BROWN,
        bbox=dict(boxstyle="round,pad=0.4", facecolor=CREAM,
                  edgecolor=BROWN, alpha=0.9))

# Quadrant labels
ax.text(1.5, 97, "Low condition\nLow consequence\n(Low risk overall)",
        fontsize=7.5, color=GREY, alpha=0.7, ha="left", va="top")
ax.text(8.5, 97, "High condition\nHigh consequence\n(NBI misses these)",
        fontsize=7.5, color=BROWN, alpha=0.8, ha="right", va="top",
        bbox=dict(boxstyle="round,pad=0.3", facecolor=CREAM,
                  edgecolor=BROWN, alpha=0.5))

ax.set_xlabel("NBI Deck Condition Rating (1=failed, 9=excellent)",
              fontsize=11)
ax.set_ylabel("NCPS Rank Percentile (lower = higher priority)",
              fontsize=11)
ax.set_xlim(0.5, 9.5)
ax.set_ylim(0, 102)
ax.invert_yaxis()
ax.set_title(
    "NBI Condition Rating vs NCPS Priority Rank\n"
    "3,681 Bridges | 1994 Northridge | "
    "r = \u22120.039 (orthogonal dimensions)",
    fontsize=12, color=BROWN
)
ax.legend(fontsize=9, loc="lower left", framealpha=0.9)
ax.grid(True, alpha=0.25, linestyle="--")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
out3 = config.OUTPUTS / "ncds_condition_vs_ncps_v2.png"
plt.savefig(str(out3), dpi=180, bbox_inches="tight")
plt.close()
print(f"Saved: {out3}")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 4 — p_extensive distribution (fragility output summary)
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 5), facecolor="white")

bins = [0, 0.001, 0.022, 0.107, 0.186, 0.346]
labels = ["0\n(no risk)", "0.021\n(0.20\u20130.40g)", "0.106\n(0.40\u20130.50g)",
          "0.185\n(0.50\u20130.60g)", "0.345\n(0.90\u20131.00g)"]
counts = []
for i in range(len(bins)-1):
    lo, hi = bins[i], bins[i+1]
    if i == 0:
        c = (ncps["p_extensive"] == 0).sum()
    else:
        c = ((ncps["p_extensive"] > lo) &
             (ncps["p_extensive"] <= hi)).sum()
    counts.append(c)

colors_bar = [GREY, LGREEN, YELLOW, ORANGE, RED]
bars = ax.bar(labels, counts, color=colors_bar,
              edgecolor="white", linewidth=0.8, alpha=0.9)

# Annotate
for bar, count in zip(bars, counts):
    pct = count / total * 100
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 20,
            f"{count:,}\n({pct:.1f}%)",
            ha="center", va="bottom", fontsize=9, color="#333333")

ax.set_xlabel("P(damage \u2265 Extensive) value", fontsize=11)
ax.set_ylabel("Number of bridges", fontsize=11)
ax.set_title(
    "Distribution of Damage Probabilities \u2014 3,681 Bridges\n"
    "Empirical fragility matrix (MCEER-98-0004) + site-specific MCEER overrides",
    fontsize=11, color=BROWN
)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, axis="y", alpha=0.3, linestyle="--")
ax.set_ylim(0, max(counts) * 1.18)

# Annotate the 0.345 bar — these are the critical ones
ax.annotate(
    "6 bridges at 0.345\n(MCEER overrides\n0.90\u20130.98g PGA)",
    xy=(4, counts[4]),
    xytext=(3.2, counts[4] + 150),
    fontsize=8, color=BROWN,
    arrowprops=dict(arrowstyle="->", color=BROWN, lw=1)
)

plt.tight_layout()
out4 = config.OUTPUTS / "ncds_p_extensive_distribution.png"
plt.savefig(str(out4), dpi=180, bbox_inches="tight")
plt.close()
print(f"Saved: {out4}")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 5 — Sensitivity analysis: rank shifts across weighting scenarios
# ══════════════════════════════════════════════════════════════════════════════
sensitivity_path = config.DATA_PROCESSED / "ncps_sensitivity.csv"
if sensitivity_path.exists():
    sens = pd.read_csv(str(sensitivity_path), dtype={"bridge_id": str})
    sens["bridge_id"] = sens["bridge_id"].str.strip().str.upper()

    rank_cols = [c for c in sens.columns if "rank" in c.lower()]
    if len(rank_cols) >= 2:
        fig, ax = plt.subplots(figsize=(12, 7), facecolor="white")

        balanced_col     = [c for c in rank_cols if "balanced" in c.lower()]
        lifesafety_col   = [c for c in rank_cols if "life" in c.lower()
                            or "safety" in c.lower()]
        economic_col     = [c for c in rank_cols if "econ" in c.lower()]

        if balanced_col and economic_col:
            bc = balanced_col[0]
            ec = economic_col[0]

            sens_mceer = sens[sens["bridge_id"].isin(ALL_MCEER_UP)].copy()
            sens_other = sens[~sens["bridge_id"].isin(ALL_MCEER_UP)].copy()

            # Plot all bridges
            ax.scatter(sens_other[bc], sens_other[ec],
                       c=GREY, s=5, alpha=0.15, linewidths=0,
                       label="All bridges")

            # MCEER collapsed
            sc = sens_mceer[
                sens_mceer["bridge_id"].isin(COLLAPSED_UP)
            ]
            ax.scatter(sc[bc], sc[ec],
                       c="black", s=100, marker="X",
                       linewidths=1, edgecolors=RED,
                       label="MCEER Collapsed", zorder=5)

            # MCEER major
            sm = sens_mceer[
                sens_mceer["bridge_id"].isin(MAJOR_UP)
            ]
            ax.scatter(sm[bc], sm[ec],
                       c=RED, s=70, marker="^",
                       linewidths=0.5, edgecolors="white",
                       label="MCEER Major", zorder=4)

            # 45-degree line
            lim = max(sens[bc].max(), sens[ec].max())
            ax.plot([0, lim], [0, lim], color=GREY,
                    linestyle="--", linewidth=1, alpha=0.5,
                    label="No change line")

            ax.set_xlabel(f"Rank under Balanced weighting",
                          fontsize=11)
            ax.set_ylabel(f"Rank under Economic-First weighting",
                          fontsize=11)
            ax.set_title(
                "Sensitivity Analysis: Balanced vs Economic-First Weighting\n"
                "Points above the line move up in priority; "
                "points below move down",
                fontsize=11, color=BROWN
            )
            ax.legend(fontsize=9, framealpha=0.9)
            ax.grid(True, alpha=0.25, linestyle="--")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            plt.tight_layout()
            out5 = config.OUTPUTS / "ncds_sensitivity_scatter.png"
            plt.savefig(str(out5), dpi=180, bbox_inches="tight")
            plt.close()
            print(f"Saved: {out5}")
        else:
            print("Sensitivity CSV missing balanced/economic columns — skipping chart 5")
    else:
        print("Sensitivity CSV has fewer than 2 rank columns — skipping chart 5")
else:
    print("ncps_sensitivity.csv not found — skipping chart 5")


print("\nAll charts complete.")
print(f"Output folder: {config.OUTPUTS}")
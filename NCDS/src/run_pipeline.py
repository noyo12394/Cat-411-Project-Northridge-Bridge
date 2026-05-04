"""
run_pipeline.py
───────────────
Single entry point for the full Network Criticality Priority Score
(NCPS) pipeline.

Run order:
    1. Load network + bridges (loads from pickle)
    2. Network metrics (loads from cache where available)
    3. Economic exposure (full 4,050 bridges)
    4. Emergency access (37 MCEER bridges — validation only)
    5. NCPS scoring (full 4,050 + Northridge validation table)

Usage:
    python run_pipeline.py               # full run
    python run_pipeline.py --skip-econ   # skip economic (use cache)
    python run_pipeline.py --skip-emergency  # skip emergency
    python run_pipeline.py --ncps-only   # just rerun scoring
"""
import argparse
import pickle
import time
from pathlib import Path
import pandas as pd
import numpy as np
import networkx as nx
import sys

sys.path.insert(0, str(Path(__file__).parent))
import config

from network_metrics   import (compile_network_scores,
                                compute_edge_betweenness,
                                compute_detour_cost,
                                compute_component_impact)
from economic_exposure import run_economic_exposure
from emergency_access  import run_emergency_access
from ncps_scorer       import compute_ncps, run_sensitivity


# ── Helpers ────────────────────────────────────────────────────────────────────

def banner(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def elapsed(t0):
    s = time.time() - t0
    return f"{s/60:.1f} min" if s > 60 else f"{s:.1f}s"


def strip_ids(df, col="bridge_id"):
    """Strip whitespace from a bridge ID column in place."""
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()
    return df


# ── Step 1: Load Network + Bridges ─────────────────────────────────────────────

def load_network_and_bridges():
    banner("STEP 1 — Load Network & Bridges")
    t0 = time.time()

    import geopandas as gpd

    # ── Graph ──
    graph_path = config.DATA_PROCESSED / "la_county_graph.pkl"
    if not graph_path.exists():
        raise FileNotFoundError(
            f"Graph not found: {graph_path}\n"
            f"Run network_builder.py first."
        )
    with open(graph_path, "rb") as f:
        G = pickle.load(f)
    print(f"  Graph loaded: {G.number_of_nodes():,} nodes, "
          f"{G.number_of_edges():,} edges")

    # ── Bridge edge map ──
    bridge_map_path = config.DATA_PROCESSED / "bridge_edge_map.pkl"
    if not bridge_map_path.exists():
        raise FileNotFoundError(
            f"Bridge edge map not found: {bridge_map_path}\n"
            f"Run notebook 02_bridge_matching first."
        )
    with open(bridge_map_path, "rb") as f:
        bridge_edge_map = pickle.load(f)

    # Strip whitespace from all bridge IDs
    bridge_edge_map = {
        str(k).strip(): v for k, v in bridge_edge_map.items()
    }
    print(f"  Bridge edge map loaded: {len(bridge_edge_map):,} bridges")

    # ── Bridges GeoDataFrame ──
    bridges_path = config.DATA_PROCESSED / "bridges_matched.gpkg"
    if not bridges_path.exists():
        raise FileNotFoundError(
            f"Matched bridges not found: {bridges_path}\n"
            f"Run notebook 02_bridge_matching first."
        )
    bridges_gdf = gpd.read_file(bridges_path)

    # Identify and strip the structure number column
    id_col = (
        "STRUCTURE_NUMBER_008"
        if "STRUCTURE_NUMBER_008" in bridges_gdf.columns
        else bridges_gdf.columns[0]
    )
    bridges_gdf[id_col] = bridges_gdf[id_col].astype(str).str.strip()
    print(f"  Bridges GeoDataFrame loaded: {len(bridges_gdf):,} rows")

    # ── Diagnostics: check MCEER coverage ──
    mceer_clean   = [b.strip() for b in config.MCEER_ALL_37]
    bridge_ids_in = set(bridges_gdf[id_col].values)
    matched       = [b for b in mceer_clean if b in bridge_ids_in]
    missing       = [b for b in mceer_clean if b not in bridge_ids_in]
    print(f"\n  MCEER bridge coverage:")
    print(f"    Matched in NBI: {len(matched)}/37")
    if missing:
        print(f"    Missing:        {missing}")

    print(f"\n  Done in {elapsed(t0)}")
    return G, bridge_edge_map, bridges_gdf


# ── Step 2: Network Metrics ─────────────────────────────────────────────────────

def load_or_compute_network_metrics(G, bridge_edge_map):
    banner("STEP 2 — Network Metrics")
    t0 = time.time()

    # ── Betweenness ──
    bt_path = config.DATA_PROCESSED / "betweenness.pkl"
    if bt_path.exists():
        print("  Betweenness: loading from cache...")
        with open(bt_path, "rb") as f:
            betweenness = pickle.load(f)
        betweenness = {str(k).strip(): v for k, v in betweenness.items()}
    else:
        print("  Betweenness: computing (k=500 sample)...")
        betweenness = compute_edge_betweenness(G, bridge_edge_map)
        with open(bt_path, "wb") as f:
            pickle.dump(betweenness, f)
    print(f"  Betweenness: {len(betweenness):,} bridges | "
          f"max={max(betweenness.values()):.4f}")

    # ── Detour cost ──
    dc_path = config.DATA_PROCESSED / "detour_cost.pkl"
    if dc_path.exists():
        print("  Detour cost: loading from cache...")
        with open(dc_path, "rb") as f:
            detour_cost = pickle.load(f)
        detour_cost = {str(k).strip(): v for k, v in detour_cost.items()}
    else:
        print("  Detour cost: computing...")
        detour_cost = compute_detour_cost(G, bridge_edge_map)
        with open(dc_path, "wb") as f:
            pickle.dump(detour_cost, f)
    severed = sum(1 for v in detour_cost.values() if v == float("inf"))
    finite  = [v for v in detour_cost.values() if v != float("inf")]
    print(f"  Detour cost: {len(detour_cost):,} bridges | "
          f"severed={severed:,} | median={np.median(finite):.2f}x")

    # ── Component impact ──
    ci_path = config.DATA_PROCESSED / "component_impact.pkl"
    if ci_path.exists():
        print("  Component impact: loading from cache...")
        with open(ci_path, "rb") as f:
            component_impact = pickle.load(f)
        component_impact = {
            str(k).strip(): v for k, v in component_impact.items()
        }
    else:
        print("  Component impact: computing...")
        component_impact = compute_component_impact(G, bridge_edge_map)
        with open(ci_path, "wb") as f:
            pickle.dump(component_impact, f)
    disconnecting = sum(
        1 for v in component_impact.values() if v["disconnects"]
    )
    print(f"  Component impact: {len(component_impact):,} bridges | "
          f"disconnecting={disconnecting:,}")

    # ── Compile ──
    network_scores = compile_network_scores(
        betweenness, detour_cost, component_impact
    )
    network_scores = strip_ids(network_scores)

    out_path = config.DATA_PROCESSED / "network_scores.csv"
    network_scores.to_csv(out_path, index=False)
    print(f"  Network scores saved: {out_path}")
    print(f"  Done in {elapsed(t0)}")
    return network_scores


# ── Step 3: Economic Exposure ───────────────────────────────────────────────────

def load_or_compute_economic_scores(G, bridge_edge_map, bridges_gdf):
    banner("STEP 3 — Economic Exposure")
    t0 = time.time()

    out_path = config.DATA_PROCESSED / "economic_scores.csv"
    if out_path.exists():
        print("  Loading from cache...")
        scores = pd.read_csv(out_path)
        scores = strip_ids(scores)
        print(f"  Loaded {len(scores):,} economic scores")
    else:
        print("  Computing economic exposure...")
        scores = run_economic_exposure(G, bridge_edge_map, bridges_gdf)
        scores = strip_ids(scores)

    print(f"  Done in {elapsed(t0)}")
    return scores


# ── Step 4: Emergency Access ────────────────────────────────────────────────────

def load_or_compute_emergency_scores(G, bridge_edge_map, bridges_gdf):
    banner("STEP 4 — Emergency Access (MCEER 37 validation)")
    t0 = time.time()

    out_path = config.DATA_PROCESSED / "emergency_scores_validation.csv"
    if out_path.exists():
        print("  Loading from cache...")
        scores = pd.read_csv(out_path)
        scores = strip_ids(scores)
        print(f"  Loaded {len(scores):,} emergency scores")
    else:
        print("  Computing emergency access impact...")
        scores = run_emergency_access(G, bridge_edge_map, bridges_gdf)
        if scores is not None and "bridge_id" in scores.columns:
            scores = strip_ids(scores)

    print(f"  Done in {elapsed(t0)}")
    return scores


# ── Step 5: NCPS Scoring ────────────────────────────────────────────────────────

def build_damage_probabilities(network_scores):
    """
    Build damage probability table.

    Priority order:
    1. Team HAZUS/ML output (damage_probabilities.csv) if it exists
    2. MCEER PGA values for the 37 documented bridges
    3. Betweenness-normalised proxy for all other bridges

    This means the 37 MCEER bridges get real seismic ground motion
    values as their damage probability, which is academically
    defensible for the Northridge validation.
    """
    damage_path = config.DATA_PROCESSED / "damage_probabilities.csv"

    if damage_path.exists():
        print("  Loading damage probabilities from team pipeline...")
        damage_df = pd.read_csv(damage_path)
        damage_df = strip_ids(damage_df)
        print(f"  Loaded {len(damage_df):,} damage probabilities")
        return damage_df

    print("  Damage probability file not found.")
    print("  Building hybrid proxy:")
    print("    - MCEER bridges: actual PGA values (0.25 — 0.98g)")
    print("    - All others:    betweenness-normalised proxy")

    # Start with betweenness proxy for all bridges
    damage_df = network_scores[
        ["bridge_id", "betweenness_norm"]
    ].copy()
    damage_df = damage_df.rename(
        columns={"betweenness_norm": "p_extensive"}
    )

    # Override MCEER bridges with actual PGA values
    mceer_pga_clean = {
        k.strip(): v for k, v in config.MCEER_PGA.items()
    }

    mceer_count = 0
    for idx, row in damage_df.iterrows():
        bid = row["bridge_id"]
        if bid in mceer_pga_clean:
            damage_df.at[idx, "p_extensive"] = mceer_pga_clean[bid]
            mceer_count += 1

    print(f"  MCEER bridges with PGA override: {mceer_count}/37")
    print(f"  Proxy bridges (betweenness):     "
          f"{len(damage_df) - mceer_count:,}")

    # Show PGA distribution for MCEER bridges
    mceer_rows = damage_df[
        damage_df["bridge_id"].isin(mceer_pga_clean.keys())
    ]
    if len(mceer_rows) > 0:
        print(f"  MCEER p_extensive range: "
              f"{mceer_rows['p_extensive'].min():.2f} — "
              f"{mceer_rows['p_extensive'].max():.2f}")

    return damage_df


def run_ncps_scoring(network_scores, economic_scores,
                     emergency_scores, bridges_gdf):
    banner("STEP 5 — NCPS Scoring")
    t0 = time.time()

    # ── Build damage probabilities ──
    damage_df = build_damage_probabilities(network_scores)

    # ── Ensure all IDs are stripped ──
    for df in [network_scores, economic_scores, damage_df]:
        strip_ids(df)
    if emergency_scores is not None:
        strip_ids(emergency_scores)

    # ── Run balanced NCPS ──
    print("\n  Running balanced scenario...")
    ncps_balanced = compute_ncps(
        damage_df,
        network_scores,
        economic_scores,
        emergency_scores,
        weights=config.NCPS_WEIGHTS["balanced"]
    )
    ncps_balanced = strip_ids(ncps_balanced)

    # Save
    main_out = config.DATA_PROCESSED / "ncps_results.csv"
    ncps_balanced.to_csv(main_out, index=False)
    print(f"\n  NCPS results saved: {main_out}")

    # ── Sensitivity analysis ──
    print("\n  Running sensitivity analysis...")
    sensitivity = run_sensitivity(
        damage_df, network_scores,
        economic_scores, emergency_scores
    )
    sens_out = config.DATA_PROCESSED / "ncps_sensitivity.csv"
    sensitivity["rank_comparison"].to_csv(sens_out, index=False)
    print(f"  Sensitivity results saved: {sens_out}")

    # ── Northridge validation table ──
    print("\n  Building Northridge validation table...")
    mceer_clean     = [b.strip() for b in config.MCEER_ALL_37]
    collapsed_clean = [b.strip() for b in config.MCEER_COLLAPSED]
    major_clean     = [b.strip() for b in config.MCEER_MAJOR_DAMAGE]
    moderate_clean  = [b.strip() for b in config.MCEER_MODERATE_DAMAGE]
    pga_clean       = {k.strip(): v for k, v in config.MCEER_PGA.items()}

    mceer_results = ncps_balanced[
        ncps_balanced["bridge_id"].isin(mceer_clean)
    ].copy()

    if len(mceer_results) > 0:
        mceer_results["damage_state"] = mceer_results["bridge_id"].apply(
            lambda x: (
                "Collapse" if x in collapsed_clean
                else "Major" if x in major_clean
                else "Moderate"
            )
        )
        mceer_results["pga"] = mceer_results["bridge_id"].map(pga_clean)

        # Sort by damage state then rank
        state_order = {"Collapse": 0, "Major": 1, "Moderate": 2}
        mceer_results["_sort"] = mceer_results["damage_state"].map(
            state_order
        )
        mceer_results = mceer_results.sort_values(
            ["_sort", "ncps_rank"]
        ).drop(columns="_sort")

    else:
        print("  WARNING: No MCEER bridges found in NCPS results.")
        print("  Sample NCPS IDs:",
              ncps_balanced["bridge_id"].head(5).tolist())
        print("  Sample MCEER IDs:", mceer_clean[:5])

    val_out = config.DATA_PROCESSED / "northridge_validation.csv"
    mceer_results.to_csv(val_out, index=False)
    print(f"  Validation table saved: {val_out} "
          f"({len(mceer_results)} bridges)")

    # ── Print results summary ──
    print("\n" + "="*60)
    print("NCPS RESULTS SUMMARY")
    print("="*60)
    print(f"\n  Total bridges scored: {len(ncps_balanced):,}")
    print(f"  NCPS range: "
          f"{ncps_balanced['ncps'].min():.4f} — "
          f"{ncps_balanced['ncps'].max():.4f}")

    print("\n  Top 10 bridges by NCPS:")
    top10_cols = ["bridge_id", "ncps_rank", "ncps",
                  "network_score", "economic_score"]
    available  = [c for c in top10_cols if c in ncps_balanced.columns]
    print(ncps_balanced[available].head(10).to_string(index=False))

    if len(mceer_results) > 0:
        print("\n  Northridge validation — MCEER bridges by NCPS rank:")
        val_cols  = ["bridge_id", "damage_state", "pga",
                     "ncps_rank", "ncps", "network_score",
                     "economic_score"]
        available = [c for c in val_cols if c in mceer_results.columns]
        print(mceer_results[available].to_string(index=False))

        # ── Validation statistics ──
        print("\n" + "="*60)
        print("VALIDATION STATISTICS")
        print("="*60)

        stats = mceer_results.groupby("damage_state").agg(
            count=("bridge_id", "count"),
            mean_rank=("ncps_rank", "mean"),
            median_rank=("ncps_rank", "median"),
            mean_ncps=("ncps", "mean"),
            mean_pga=("pga", "mean"),
        ).sort_values("mean_rank")

        print("\n  Mean NCPS rank by damage state "
              "(lower = higher priority = better):")
        print(stats.to_string())

        # Percentile context
        total = len(ncps_balanced)
        for state in ["Collapse", "Major", "Moderate"]:
            subset = mceer_results[
                mceer_results["damage_state"] == state
            ]
            if len(subset) == 0:
                continue
            mean_rank = subset["ncps_rank"].mean()
            pct = (mean_rank / total) * 100
            print(f"\n  {state} bridges avg rank: "
                  f"{mean_rank:.0f}/{total:,} "
                  f"(top {pct:.1f}% of network)")

        # Key validation question
        collapse_rank = mceer_results[
            mceer_results["damage_state"] == "Collapse"
        ]["ncps_rank"].mean()
        major_rank = mceer_results[
            mceer_results["damage_state"] == "Major"
        ]["ncps_rank"].mean()

        print(f"\n  Collapsed bridges rank higher than major damage: "
              f"{'YES ✓' if collapse_rank < major_rank else 'NO ✗'}")
        print(f"  (Collapse mean rank {collapse_rank:.0f} vs "
              f"Major mean rank {major_rank:.0f})")

    print(f"\n  Done in {elapsed(t0)}")
    return ncps_balanced, mceer_results


# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Run NCPS pipeline")
    parser.add_argument(
        "--skip-econ", action="store_true",
        help="Skip economic exposure (use cached results)"
    )
    parser.add_argument(
        "--skip-emergency", action="store_true",
        help="Skip emergency access (use cached results)"
    )
    parser.add_argument(
        "--ncps-only", action="store_true",
        help="Skip all computation, just rerun NCPS scoring"
    )
    args = parser.parse_args()

    pipeline_start = time.time()

    banner("NCPS PIPELINE — NORTHRIDGE VALIDATION STUDY")
    print(f"  Study area:  LA + Ventura County")
    print(f"  Bridges:     Full NCPS on 4,050 | "
          f"Emergency validation on {len(config.MCEER_ALL_37)}")
    print(f"  Outputs:     {config.DATA_PROCESSED}")

    # ── Step 1 ──
    G, bridge_edge_map, bridges_gdf = load_network_and_bridges()

    # ── Step 2 ──
    network_scores = load_or_compute_network_metrics(
        G, bridge_edge_map
    )

    # ── Step 3 ──
    if args.ncps_only:
        econ_path = config.DATA_PROCESSED / "economic_scores.csv"
        economic_scores = pd.read_csv(econ_path)
        economic_scores = strip_ids(economic_scores)
        print(f"\n  Economic scores loaded: "
              f"{len(economic_scores):,} bridges")
    else:
        economic_scores = load_or_compute_economic_scores(
            G, bridge_edge_map, bridges_gdf
        )

    # ── Step 4 ──
    if args.ncps_only or args.skip_emergency:
        emg_path = (config.DATA_PROCESSED
                    / "emergency_scores_validation.csv")
        if emg_path.exists():
            emergency_scores = pd.read_csv(emg_path)
            emergency_scores = strip_ids(emergency_scores)
            print(f"\n  Emergency scores loaded: "
                  f"{len(emergency_scores):,} bridges")
        else:
            print("\n  Emergency cache not found — computing...")
            emergency_scores = load_or_compute_emergency_scores(
                G, bridge_edge_map, bridges_gdf
            )
    else:
        emergency_scores = load_or_compute_emergency_scores(
            G, bridge_edge_map, bridges_gdf
        )

    # ── Step 5 ──
    ncps_results, validation_table = run_ncps_scoring(
        network_scores, economic_scores,
        emergency_scores, bridges_gdf
    )

    # ── Done ──
    total = elapsed(pipeline_start)
    banner(f"PIPELINE COMPLETE — total time: {total}")

    print("\n  Output files:")
    outputs = [
        "network_scores.csv",
        "economic_scores.csv",
        "emergency_scores_validation.csv",
        "ncps_results.csv",
        "ncps_sensitivity.csv",
        "northridge_validation.csv",
    ]
    for fname in outputs:
        p      = config.DATA_PROCESSED / fname
        status = "✓" if p.exists() else "✗ missing"
        print(f"    {status}  {fname}")

    return ncps_results, validation_table


if __name__ == "__main__":
    main()
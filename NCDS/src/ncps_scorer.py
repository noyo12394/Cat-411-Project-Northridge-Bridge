"""
Module 6: NCPS Composite Scorer

Combines damage probability with network, economic, and emergency
consequence scores into the final Network Criticality Priority Score.
Runs multiple weighting scenarios for sensitivity analysis.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import src.config as config


def compute_ncps(damage_probs_df, network_scores_df, economic_scores_df,
                 emergency_scores_df, weights=None):
    """
    Compute NCPS = P(damage >= Extensive) x [w1*Network + w2*Economic + w3*Emergency]

    Args:
        damage_probs_df: DataFrame with bridge_id and p_extensive (from team's HAZUS/ML)
        network_scores_df: output of network_metrics.compile_network_scores()
        economic_scores_df: output of economic_exposure.compile_economic_scores()
        emergency_scores_df: output of emergency_access.compile_emergency_scores()
        weights: dict {"network": float, "economic": float, "emergency": float}

    Returns:
        DataFrame with all scores and final NCPS ranking
    """
    if weights is None:
        weights = config.NCPS_WEIGHTS["balanced"]

    # Merge all scores on bridge_id
    df = damage_probs_df[["bridge_id", "p_extensive"]].copy()

    df = df.merge(
        network_scores_df[["bridge_id", "network_score"]],
        on="bridge_id", how="left"
    )
    df = df.merge(
        economic_scores_df[["bridge_id", "economic_score"]],
        on="bridge_id", how="left"
    )
    df = df.merge(
        emergency_scores_df[["bridge_id", "emergency_score"]],
        on="bridge_id", how="left"
    )

    # Fill missing scores with 0
    for col in ["network_score", "economic_score", "emergency_score"]:
        df[col] = df[col].fillna(0)

    # Compute weighted consequence index
    df["consequence_index"] = (
        weights["network"] * df["network_score"]
        + weights["economic"] * df["economic_score"]
        + weights["emergency"] * df["emergency_score"]
    )

    # NCPS = damage probability x consequence
    df["ncps"] = df["p_extensive"] * df["consequence_index"]

    # Rank (1 = highest priority)
    df["ncps_rank"] = df["ncps"].rank(ascending=False, method="min").astype(int)

    return df.sort_values("ncps_rank")


def run_sensitivity(damage_probs_df, network_scores_df, economic_scores_df,
                    emergency_scores_df):
    """
    Run NCPS under all weighting scenarios defined in config.
    Returns dict {scenario_name: scored_DataFrame}
    """
    results = {}
    for scenario_name, weights in config.NCPS_WEIGHTS.items():
        print(f"Running scenario: {scenario_name} {weights}")
        df = compute_ncps(
            damage_probs_df, network_scores_df,
            economic_scores_df, emergency_scores_df,
            weights=weights
        )
        results[scenario_name] = df

    # Compare rank shifts
    base = results["balanced"][["bridge_id", "ncps_rank"]].rename(columns={"ncps_rank": "rank_balanced"})
    for name in ["life_safety_first", "economic_first"]:
        other = results[name][["bridge_id", "ncps_rank"]].rename(columns={"ncps_rank": f"rank_{name}"})
        base = base.merge(other, on="bridge_id", how="left")

    base["rank_shift_safety"] = base["rank_balanced"] - base["rank_life_safety_first"]
    base["rank_shift_econ"] = base["rank_balanced"] - base["rank_economic_first"]

    print(f"\nRank shifts (balanced vs life-safety-first):")
    print(f"  Mean absolute shift: {base['rank_shift_safety'].abs().mean():.1f}")
    print(f"  Max shift: {base['rank_shift_safety'].abs().max()}")
    print(f"\nRank shifts (balanced vs economic-first):")
    print(f"  Mean absolute shift: {base['rank_shift_econ'].abs().mean():.1f}")
    print(f"  Max shift: {base['rank_shift_econ'].abs().max()}")

    results["rank_comparison"] = base
    return results


if __name__ == "__main__":
    print("Run via notebooks or import directly")

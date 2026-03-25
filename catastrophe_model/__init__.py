"""
Catastrophe Model Package
=========================
End-to-end catastrophe modeling pipeline for the 1994 Northridge Earthquake
using NDVI-based damage proxy and HAZUS methodology.

Components:
    1. damage_classification  - Assign damage states (DS0-DS4) from NDVI change
    2. proxy_fragility        - Derive empirical fragility curves (PGA → P(DS))
    3. economic_disruption    - Traffic Disruption Index (TDI) as loss proxy
    4. prioritization_map     - Emergency priority mapping for inspection
"""

from .damage_classification import classify_damage_states
from .proxy_fragility import compute_fragility_curves, lognormal_cdf
from .economic_disruption import compute_tdi, summarize_tdi
from .prioritization_map import create_priority_map, get_top_priority_bridges

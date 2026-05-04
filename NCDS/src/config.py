"""
Project configuration for Network Criticality Analysis.
All paths, parameters, and constants in one place.
"""
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_ROOT    = Path(__file__).parent.parent
DATA_RAW        = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED  = PROJECT_ROOT / "data" / "processed"
DATA_SHAPEFILES = PROJECT_ROOT / "data" / "shapefiles"
OUTPUTS         = PROJECT_ROOT / "outputs"

# ── Data Sources ───────────────────────────────────────────────────────────────
HAZUS_GDB       = PROJECT_ROOT / "data" / "National.gdb"
NBI_BRIDGES     = DATA_RAW / "CA94.csv"          # 1994 NBI — primary source
LODES_WAC       = PROJECT_ROOT / "data" / "ca_wac_S000_JT00_2023_fixed.csv"
NHFN_FREIGHT    = DATA_SHAPEFILES / "National_Highway_Freight_Network_(NHFN).shp"
HOSPITALS       = DATA_SHAPEFILES / "Hospitals.shp"

# ── Study Area ─────────────────────────────────────────────────────────────────
STUDY_AREA           = "Los Angeles County, California, USA"
STUDY_AREA_SECONDARY = "Ventura County, California, USA"
STUDY_STATE          = "CA"
STUDY_COUNTY_FIPS    = ["37", "111"]     # CA94 format — no leading zeros
STUDY_TRACT_PREFIXES = ("06037", "06111")
NETWORK_TYPE         = "drive"

# ── Northridge Earthquake Constants ────────────────────────────────────────────
NORTHRIDGE_EPICENTER_LAT =  34.213
NORTHRIDGE_EPICENTER_LON = -118.537
NORTHRIDGE_RADIUS_KM     =  50

NORTHRIDGE_BOUNDS = {
    "min_lat": 33.9,
    "max_lat": 34.6,
    "min_lon": -118.9,
    "max_lon": -117.8,
}

NORTHRIDGE_CORRIDORS = [
    "I-5", "SR-118", "SR-14", "I-10",
    "US-101", "I-210", "I-405",
    "SR-115", "SR-112", "SR-116", "SR-2",
]

# ── MCEER 37 Documented Damaged Bridges ────────────────────────────────────────
MCEER_COLLAPSED = [
    "53 1609",   "53 1960F",  "53 1964F",
    "53 1797L",  "53 1797R",  "53 2205",
    "53 1060",   "53 1960H",  "53 1960I",
    "53 1671L",  "53 1671T",
]

MCEER_MAJOR_DAMAGE = [
    "53 0059",   "53 0490",   "53 0620",
    "53 0629",   "53 0640",   "53 1609B",
    "53 1408",   "53 1627G",  "53 1615",
    "53 1493S",  "53 1336R",  "53 2327F",
    "53 2498",   "53 1960G",  "53 9910G",
    "53 2027L",  "53 2182",   "53 2920G",
    "53 0025",   "53 2187",   "53 1491",
    "53 2324",   "53 0833",
]

MCEER_MODERATE_DAMAGE = [
    "53 0847",   "53 0764",   "53 0312",
]

MCEER_ALL_37 = MCEER_COLLAPSED + MCEER_MAJOR_DAMAGE + MCEER_MODERATE_DAMAGE

MCEER_PGA = {
    "53 1609":  0.35, "53 1960F": 0.95, "53 1964F": 0.95,
    "53 1797L": 0.90, "53 1797R": 0.90, "53 2205":  0.35,
    "53 1060":  0.50, "53 1960H": 0.95, "53 1960I": 0.95,
    "53 1671L": 0.90, "53 1671T": 0.90, "53 0059":  0.25,
    "53 0490":  0.90, "53 0620":  0.90, "53 0629":  0.90,
    "53 0640":  0.90, "53 1609B": 0.90, "53 1408":  0.50,
    "53 1627G": 0.90, "53 1615":  0.90, "53 1493S": 0.90,
    "53 1336R": 0.90, "53 2327F": 0.90, "53 2498":  0.90,
    "53 1960G": 0.90, "53 9910G": 0.35, "53 2027L": 0.25,
    "53 2182":  0.25, "53 2920G": 0.35, "53 0025":  0.25,
    "53 2187":  0.98, "53 1491":  0.90, "53 2324":  0.25,
    "53 0833":  0.90, "53 0847":  0.25, "53 0764":  0.25,
    "53 0312":  0.25,
}

# ── Bridge Matching ────────────────────────────────────────────────────────────
BRIDGE_SNAP_TOLERANCE_M = 50

# ── Network Metrics ────────────────────────────────────────────────────────────
BETWEENNESS_SAMPLE_K = 500
DETOUR_OD_SAMPLE     = 200

# ── Economic Exposure ──────────────────────────────────────────────────────────
ECONOMIC_CATCHMENT_M = 5000
FREIGHT_TIER         = None

# Economic score weights
ECONOMIC_WEIGHTS = {
    "jobs":    0.50,
    "aadt":    0.20,
    "freight": 0.30,
}

# ── Emergency Access ───────────────────────────────────────────────────────────
HOSPITAL_THRESHOLD_MIN      = 2
FIRE_STATION_THRESHOLD_MIN  = 1
SHELTER_THRESHOLD_MIN       = 5
CRITICAL_FACILITY_TYPES     = ["hospital", "fire_station", "police_station"]

FACILITY_BOUNDS = {
    "min_lat": 33.7,
    "max_lat": 34.9,
    "min_lon": -119.0,
    "max_lon": -117.6,
}

# ── NCPS Weights ───────────────────────────────────────────────────────────────
NCPS_WEIGHTS = {
    "balanced":          {"network": 0.40, "economic": 0.30, "emergency": 0.30},
    "life_safety_first": {"network": 0.25, "economic": 0.15, "emergency": 0.60},
    "economic_first":    {"network": 0.25, "economic": 0.55, "emergency": 0.20},
}

# ── Damage Probability ─────────────────────────────────────────────────────────
DAMAGE_THRESHOLD = "extensive"
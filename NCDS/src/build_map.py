"""
build_map.py
NCDS consequence map — updated to use run_earthquake_scenario.py output.
Loads ncps_earthquake_w001001.csv which contains empirically-calibrated
damage probabilities and MCEER PGA overrides.
Run from NCDS\src
"""
import folium
import pandas as pd
import geopandas as gpd
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
import config

print("Loading data...")

# ── Load earthquake pipeline output (empirical fragility + overrides) ──────────
eq_results = pd.read_csv(
    config.DATA_PROCESSED / "ncps_earthquake_w001001.csv",
    dtype={"bridge_id": str}
)
eq_results["bridge_id"] = (
    eq_results["bridge_id"].str.strip().str.upper()
)

# ── Load supplementary scores not in earthquake output ─────────────────────────
network  = pd.read_csv(config.DATA_PROCESSED / "network_scores.csv")
economic = pd.read_csv(config.DATA_PROCESSED / "economic_scores.csv")
for df in [network, economic]:
    df["bridge_id"] = df["bridge_id"].astype(str).str.strip().str.upper()

# ── Load bridge geometries ─────────────────────────────────────────────────────
bridges = gpd.read_file(config.DATA_PROCESSED / "bridges_matched.gpkg")
bridges["STRUCTURE_NUMBER_008"] = (
    bridges["STRUCTURE_NUMBER_008"]
    .astype(str).str.strip().str.upper()
)
bridges = bridges.rename(columns={"STRUCTURE_NUMBER_008": "bridge_id"})

# ── Merge everything onto bridges ──────────────────────────────────────────────
bridges = bridges.merge(eq_results, on="bridge_id", how="left")
bridges = bridges.merge(
    network[["bridge_id", "detour_severed", "disconnects_network"]],
    on="bridge_id", how="left"
)
bridges = bridges.merge(
    economic[["bridge_id", "jobs_in_catchment",
              "aadt", "on_freight_corridor"]],
    on="bridge_id", how="left"
)

# ── Coordinates: DMS conversion from 1994 NBI ──────────────────────────────────
print("Loading 1994 NBI coordinates...")

def nbi_to_decimal(raw_str):
    """Convert NBI DMS format DDMMSSFF to decimal degrees."""
    try:
        val = int(float(str(raw_str).strip()))
        degrees = val // 1000000
        minutes = (val % 1000000) // 10000
        seconds = (val % 10000) / 100
        return degrees + minutes / 60 + seconds / 3600
    except Exception:
        return None

nbi = pd.read_csv(
    config.DATA_RAW / "CA94.csv",
    dtype=str, low_memory=False
)
nbi["STRUCTURE_NUMBER_008"] = (
    nbi["STRUCTURE_NUMBER_008"].str.strip().str.upper()
)
nbi["COUNTY_CODE_003"] = nbi["COUNTY_CODE_003"].str.strip()

la_ven = nbi[nbi["COUNTY_CODE_003"].isin(["37", "111"])].copy()
la_ven = la_ven[la_ven["DECK_COND_058"].notna()].copy()
la_ven["lat_nbi"] = la_ven["LAT_016"].apply(nbi_to_decimal)
la_ven["lon_nbi"] = la_ven["LONG_017"].apply(
    lambda x: -nbi_to_decimal(x) if nbi_to_decimal(x) else None
)
la_ven_coords = la_ven.drop_duplicates(
    subset="STRUCTURE_NUMBER_008"
)[["STRUCTURE_NUMBER_008", "lat_nbi", "lon_nbi"]].rename(
    columns={"STRUCTURE_NUMBER_008": "bridge_id"}
)

bridges = bridges.merge(la_ven_coords, on="bridge_id", how="left")
bridges = bridges.to_crs(epsg=4326)
bridges["lat"] = bridges["lat_nbi"].fillna(bridges.geometry.y)
bridges["lon"] = bridges["lon_nbi"].fillna(bridges.geometry.x)

# ── MCEER coordinate overrides for accurate placement ─────────────────────────
MCEER_COORDS = {
    "53 1609":  (34.0367, -118.3717),
    "53 1797L": (34.2100, -118.5400),
    "53 1797R": (34.2100, -118.5390),
    "53 1960F": (34.3133, -118.4833),
    "53 1964F": (34.3130, -118.4830),
    "53 2205":  (34.2787, -118.4717),
    "53 1060":  (34.1617, -118.3717),
    "53 2187":  (34.1367, -118.7400),
    "53 0640":  (33.9567, -118.1117),
    "53 0833":  (33.9633, -118.1683),
    "53 2498":  (34.2800, -118.4717),
    "53 1336R": (34.1620, -118.3720),
    "53 1627G": (34.0200, -118.4300),
    "53 1615":  (34.0183, -118.4183),
    "53 1493S": (34.1617, -118.3710),
    "53 2327F": (34.2800, -118.4710),
    "53 1408":  (34.1833, -118.4500),
    "53 0629":  (34.0200, -118.4283),
    "53 0490":  (34.0217, -118.4300),
    "53 0620":  (34.0217, -118.4317),
    "53 2182":  (34.2433, -118.5400),
    "53 2027L": (34.3900, -118.5333),
    "53 1960G": (34.3133, -118.4835),
    "53 0025":  (34.1617, -118.3715),
}

overrides = 0
for bid, (lat, lon) in MCEER_COORDS.items():
    mask = bridges["bridge_id"] == bid
    if mask.any():
        bridges.loc[mask, "lat"] = lat
        bridges.loc[mask, "lon"] = lon
        overrides += 1
print(f"MCEER coordinate overrides: {overrides}")

# ── Filter to valid LA+Ventura bounds ──────────────────────────────────────────
bridges = bridges[
    bridges["lat"].between(33.0, 35.5) &
    bridges["lon"].between(-120.5, -116.5)
].copy()

total = len(bridges)
print(f"Bridges after filtering: {total:,}")

# ── MCEER lists ────────────────────────────────────────────────────────────────
COLLAPSED = [b.upper() for b in [
    "53 1609","53 1797L","53 1797R",
    "53 1960F","53 1964F","53 2205","53 1060"
]]
MAJOR = [b.upper() for b in [
    "53 2187","53 0640","53 0833","53 2498","53 1336R",
    "53 1627G","53 1615","53 1493S","53 2327F","53 1408",
    "53 0629","53 0490","53 0620","53 2182","53 2027L",
    "53 1960G","53 0025"
]]
MODERATE = [b.upper() for b in getattr(config, "MCEER_MODERATE_DAMAGE", [])]
ALL_MCEER = COLLAPSED + MAJOR + MODERATE


def damage_state(bid):
    if bid in COLLAPSED: return "Collapse"
    if bid in MAJOR:     return "Major"
    if bid in MODERATE:  return "Moderate"
    return None


def ncps_color(rank, total):
    if pd.isna(rank): return "#888888"
    pct = rank / total
    if pct <= 0.05:   return "#d73027"
    elif pct <= 0.10: return "#f46d43"
    elif pct <= 0.20: return "#fdae61"
    elif pct <= 0.40: return "#a6d96a"
    else:             return "#1a9641"


# ── Build map ──────────────────────────────────────────────────────────────────
print("Building map...")

m = folium.Map(
    location=[34.15, -118.35],
    zoom_start=10,
    tiles=None
)

# Esri satellite + labels
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/"
          "World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri World Imagery",
    name="Satellite",
    overlay=False,
    control=True
).add_to(m)

folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/"
          "Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
    attr="Esri Labels",
    name="Labels",
    overlay=True,
    control=True,
    opacity=0.8
).add_to(m)

# ── Layer groups ───────────────────────────────────────────────────────────────
layer_all       = folium.FeatureGroup(
    name="All Bridges (NCPS rank)", show=True)
layer_top5      = folium.FeatureGroup(
    name="Top 5% NCPS — Critical", show=True)
layer_severed   = folium.FeatureGroup(
    name="Severed Bridges (No Detour)", show=False)
layer_freight   = folium.FeatureGroup(
    name="Freight Corridor Bridges", show=False)
layer_mceer     = folium.FeatureGroup(
    name="MCEER Damaged Bridges 1994", show=True)
layer_epicentre = folium.FeatureGroup(
    name="Northridge Epicentre", show=True)

# ── Plot all bridges ───────────────────────────────────────────────────────────
print("  Plotting all bridges...")
for _, row in bridges.iterrows():
    lat = row["lat"]
    lon = row["lon"]
    if pd.isna(lat) or pd.isna(lon):
        continue

    bid       = row["bridge_id"]
    rank      = row.get("ncps_rank", np.nan)
    ncps_val  = row.get("ncps", 0) or 0
    net_score = row.get("network_score", 0) or 0
    eco_score = row.get("economic_score", 0) or 0
    pga_val   = row.get("pga", 0) or 0
    p_ext     = row.get("p_extensive", 0) or 0
    jobs      = row.get("jobs_in_catchment", 0) or 0
    aadt      = row.get("aadt", 0) or 0
    severed   = bool(row.get("detour_severed", False))
    freight   = bool(row.get("on_freight_corridor", False))
    name      = str(row.get("FEATURES_DESC_006A", "")).strip()
    pct       = (rank / total * 100) if not pd.isna(rank) else 0
    color     = ncps_color(rank, total)
    radius    = 6 if pct <= 5 else 3

    popup_html = f"""
    <b style="font-size:13px;">{bid}</b><br>
    <i>{name}</i><br>
    <hr style="margin:4px 0;">
    <b>NCPS Rank:</b> {int(rank) if not pd.isna(rank) else 'N/A'}
        / {total:,} &nbsp;(top {pct:.1f}%)<br>
    <b>NCPS Score:</b> {ncps_val:.4f}<br>
    <b>P(extensive):</b> {p_ext:.3f}
        &nbsp;<i>(empirical fragility)</i><br>
    <b>PGA 1994:</b> {pga_val:.3f}g<br>
    <hr style="margin:4px 0;">
    <b>Network Score:</b> {net_score:.3f}<br>
    <b>Economic Score:</b> {eco_score:.3f}<br>
    <b>Jobs (5km):</b> {int(jobs):,}<br>
    <b>AADT:</b> {int(aadt):,}<br>
    <b>Severed:</b> {'&#x2714; Yes' if severed else 'No'}<br>
    <b>Freight corridor:</b> {'&#x2714; Yes' if freight else 'No'}
    """

    folium.CircleMarker(
        location=[lat, lon],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.75,
        weight=0.5,
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"{bid} | Rank "
                f"{int(rank) if not pd.isna(rank) else 'N/A'}"
    ).add_to(layer_all)

    if not pd.isna(rank) and rank / total <= 0.05:
        folium.CircleMarker(
            location=[lat, lon],
            radius=7,
            color="#d73027",
            fill=True,
            fill_color="#d73027",
            fill_opacity=0.85,
            weight=1,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{bid} | Rank {int(rank)}"
        ).add_to(layer_top5)

    if severed:
        folium.CircleMarker(
            location=[lat, lon],
            radius=4,
            color="#7b2d8b",
            fill=True,
            fill_color="#7b2d8b",
            fill_opacity=0.7,
            weight=0.5,
            tooltip=f"{bid} | No detour"
        ).add_to(layer_severed)

    if freight:
        folium.CircleMarker(
            location=[lat, lon],
            radius=4,
            color="#0571b0",
            fill=True,
            fill_color="#0571b0",
            fill_opacity=0.7,
            weight=0.5,
            tooltip=f"{bid} | Freight corridor"
        ).add_to(layer_freight)

# ── Plot MCEER bridges ─────────────────────────────────────────────────────────
print("  Plotting MCEER bridges...")
mceer_colors = {
    "Collapse": "#000000",
    "Major":    "#d73027",
    "Moderate": "#fc8d59",
}

for _, row in bridges[bridges["bridge_id"].isin(ALL_MCEER)].iterrows():
    lat = row["lat"]
    lon = row["lon"]
    if pd.isna(lat) or pd.isna(lon):
        continue

    bid    = row["bridge_id"]
    state  = damage_state(bid) or "Unknown"
    rank   = row.get("ncps_rank", np.nan)
    pga    = row.get("pga", 0) or 0
    p_ext  = row.get("p_extensive", 0) or 0
    ncps_v = row.get("ncps", 0) or 0
    name   = str(row.get("FEATURES_DESC_006A", "")).strip()
    color  = mceer_colors.get(state, "#888888")
    pct    = (rank / total * 100) if not pd.isna(rank) else 0

    popup_html = f"""
    <b style="font-size:13px;color:{'#000' if state=='Collapse' else '#d73027'};">
    &#9888; MCEER {state.upper()}</b><br>
    <b>{bid}</b> &mdash; {name}<br>
    <hr style="margin:4px 0;">
    <b>Damage State:</b> {state}<br>
    <b>Site PGA:</b> {pga:.3f}g
        &nbsp;<i>(MCEER-98-0004 override)</i><br>
    <b>P(extensive):</b> {p_ext:.3f}<br>
    <b>NBI Condition 1994:</b> 7&ndash;8/9 &mdash; rated Good<br>
    <hr style="margin:4px 0;">
    <b>NCPS Rank:</b> {int(rank) if not pd.isna(rank) else 'N/A'}
        / {total:,} &nbsp;(top {pct:.1f}%)<br>
    <b>NCPS Score:</b> {ncps_v:.4f}<br>
    <b>Network Score:</b> {row.get('network_score', 0):.3f}<br>
    <b>Economic Score:</b> {row.get('economic_score', 0):.3f}
    """

    # Outer ring
    folium.CircleMarker(
        location=[lat, lon],
        radius=16,
        color=color,
        fill=False,
        weight=3,
        popup=folium.Popup(popup_html, max_width=320),
        tooltip=f"MCEER {state}: {bid}"
    ).add_to(layer_mceer)

    # Inner dot
    folium.CircleMarker(
        location=[lat, lon],
        radius=8,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.95,
        weight=2,
        popup=folium.Popup(popup_html, max_width=320),
        tooltip=f"MCEER {state}: {bid}"
    ).add_to(layer_mceer)

    # Label for collapsed bridges
    if state == "Collapse":
        folium.Marker(
            location=[lat + 0.004, lon],
            icon=folium.DivIcon(
                html=f'<div style="'
                     f'font-size:9px;font-weight:bold;'
                     f'color:#000;white-space:nowrap;'
                     f'background:rgba(255,255,255,0.92);'
                     f'padding:2px 5px;border-radius:3px;'
                     f'border:1px solid #000;'
                     f'box-shadow:1px 1px 3px rgba(0,0,0,0.3);">'
                     f'{bid}</div>',
                icon_size=(90, 22),
                icon_anchor=(45, 22)
            )
        ).add_to(layer_mceer)

# ── Epicentre ──────────────────────────────────────────────────────────────────
print("  Adding epicentre...")
folium.Marker(
    location=[config.NORTHRIDGE_EPICENTER_LAT,
              config.NORTHRIDGE_EPICENTER_LON],
    popup=folium.Popup(
        "<b>Northridge Earthquake Epicentre</b><br>"
        "January 17, 1994 &mdash; Mw 6.7<br>"
        "34.213&deg;N, 118.537&deg;W<br>"
        "Depth: 18.4 km<br>"
        "Peak ground acceleration: 0.87g<br>"
        "<i>Source: USGS ShakeMap</i>",
        max_width=220
    ),
    tooltip="Northridge Epicentre (Mw 6.7, Jan 17 1994)",
    icon=folium.Icon(color="red", icon="star", prefix="fa")
).add_to(layer_epicentre)

folium.Circle(
    location=[config.NORTHRIDGE_EPICENTER_LAT,
              config.NORTHRIDGE_EPICENTER_LON],
    radius=config.NORTHRIDGE_RADIUS_KM * 1000,
    color="#d73027",
    fill=True,
    fill_color="#d73027",
    fill_opacity=0.04,
    weight=1.5,
    dash_array="6 4",
    tooltip="50km analysis radius"
).add_to(layer_epicentre)

# ── Legend ─────────────────────────────────────────────────────────────────────
legend_html = """
<div style="
    position:fixed;bottom:30px;left:30px;z-index:1000;
    background:rgba(255,255,255,0.96);
    padding:15px 18px;border-radius:8px;
    border:2px solid #ccc;font-family:Arial,sans-serif;
    font-size:12px;box-shadow:3px 3px 8px rgba(0,0,0,0.25);
    min-width:240px;line-height:1.9;">
<div style="font-size:13px;font-weight:bold;
     color:#5C1A00;margin-bottom:6px;">
NCPS Priority Rank
</div>
<span style="color:#d73027;font-size:16px;">&#9679;</span>
    Top 5% &mdash; Critical<br>
<span style="color:#f46d43;font-size:16px;">&#9679;</span>
    Top 6&ndash;10%<br>
<span style="color:#fdae61;font-size:16px;">&#9679;</span>
    Top 11&ndash;20%<br>
<span style="color:#a6d96a;font-size:16px;">&#9679;</span>
    Top 21&ndash;40%<br>
<span style="color:#1a9641;font-size:16px;">&#9679;</span>
    Bottom 60%<br>
<hr style="margin:8px 0;">
<div style="font-size:13px;font-weight:bold;
     color:#5C1A00;margin-bottom:6px;">
MCEER 1994 Documented Damage
</div>
<span style="color:#000;font-size:16px;">&#8857;</span>
    Collapse<br>
<span style="color:#d73027;font-size:16px;">&#8857;</span>
    Major Damage<br>
<span style="color:#fc8d59;font-size:16px;">&#8857;</span>
    Moderate Damage<br>
<hr style="margin:8px 0;">
<span style="color:#d73027;">&#9733;</span>
    Northridge Epicentre (Mw 6.7)<br>
<span style="color:#d73027;">&#8722; &#8722;</span>
    50 km analysis radius<br>
<hr style="margin:8px 0;border-color:#eee;">
<div style="font-size:10px;color:#666;line-height:1.5;">
    NCDS &mdash; Sydane Morrison<br>
    Lehigh University &nbsp;|&nbsp; CAT 411 &nbsp;|&nbsp; 2026<br>
    PGA: USGS Northridge ShakeMap + MCEER site overrides<br>
    Fragility: MCEER-98-0004 empirical matrix
</div>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# ── Title ──────────────────────────────────────────────────────────────────────
title_html = """
<div style="
    position:fixed;top:15px;left:50%;
    transform:translateX(-50%);z-index:1000;
    background:rgba(255,255,255,0.96);
    padding:10px 22px;border-radius:8px;
    border:2px solid #8B4513;font-family:Arial,sans-serif;
    font-size:14px;font-weight:bold;text-align:center;
    box-shadow:3px 3px 8px rgba(0,0,0,0.2);color:#4a2c0a;">
    Network Criticality Priority Score (NCPS)<br>
    <span style="font-size:11px;font-weight:normal;">
    LA + Ventura County &nbsp;&mdash;&nbsp; 3,681 Bridges
    &nbsp;&mdash;&nbsp; Northridge 1994 Validation<br>
    Empirical fragility matrix (MCEER-98-0004)
    &nbsp;|&nbsp; Site-specific PGA overrides
    </span>
</div>
"""
m.get_root().html.add_child(folium.Element(title_html))

# ── Assemble and save ──────────────────────────────────────────────────────────
layer_all.add_to(m)
layer_top5.add_to(m)
layer_severed.add_to(m)
layer_freight.add_to(m)
layer_mceer.add_to(m)
layer_epicentre.add_to(m)
folium.LayerControl(collapsed=False).add_to(m)

config.OUTPUTS.mkdir(exist_ok=True)
out_path = config.OUTPUTS / "ncds_consequence_map.html"
m.save(str(out_path))

print(f"\nMap saved: {out_path}")
print(f"\nSummary:")
print(f"  Total bridges:    {total:,}")
top5 = len(bridges[
    bridges["ncps_rank"].notna() &
    (bridges["ncps_rank"] / total <= 0.05)
])
print(f"  Top 5% critical:  {top5:,}")
print(f"  Severed bridges:  "
      f"{int(bridges['detour_severed'].sum()):,}")
print(f"  MCEER on map:     "
      f"{int(bridges['bridge_id'].isin(ALL_MCEER).sum()):,}")
print(f"\nOpen in browser: {out_path}")
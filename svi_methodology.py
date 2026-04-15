from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import norm


REFERENCE_YEAR = 2025
DEFAULT_FRAGILITY_MEDIAN_METHOD = "linear"

SVI_WEIGHTS = {
    "score_year_built": 0.20,
    "score_condition": 0.20,
    "score_skew": 0.15,
    "score_continuity": 0.15,
    "score_material": 0.10,
    "score_max_span": 0.10,
    "score_num_spans": 0.10,
}

FRAGILITY_MU_BOUNDS = {
    "slight": (0.25, 0.80),
    "moderate": (0.35, 1.00),
    "extensive": (0.45, 1.20),
    "complete": (0.70, 1.70),
}

FRAGILITY_DAMAGE_WEIGHTS = {
    "P_DS0": 0.00,
    "P_DS1": 0.03,
    "P_DS2": 0.08,
    "P_DS3": 0.25,
    "P_DS4": 1.00,
}

FRAGILITY_DISPERSION_BETA0 = 0.60
FRAGILITY_DISPERSION_SLOPE = 0.20

CONTINUOUS_KIND_CODES = {"2", "4", "6"}
CONCRETE_KIND_CODES = {"1", "2", "5", "6"}
STEEL_KIND_CODES = {"3", "4"}
WOOD_KIND_CODES = {"7"}


def clean_int_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def clean_float_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def extract_year(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.extract(r"(\d{4})")[0]
        .pipe(pd.to_numeric, errors="coerce")
    )


def clean_kind_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().replace({"": np.nan, "nan": np.nan, "None": np.nan})


def year_built_score(series: pd.Series) -> pd.Series:
    years = clean_int_series(series)
    scores = pd.Series(np.nan, index=years.index, dtype=float)
    scores.loc[years < 1971] = 1.00
    scores.loc[(years >= 1971) & (years <= 1989)] = 0.70
    scores.loc[years > 1989] = 0.40
    return scores


def condition_score(series: pd.Series) -> pd.Series:
    condition = clean_float_series(series)
    return ((9.0 - condition) / 9.0).clip(lower=0.0, upper=1.0)


def skew_score(series: pd.Series) -> pd.Series:
    skew = clean_float_series(series).clip(lower=0.0)
    return (skew / 30.0).clip(upper=1.0)


def continuity_score(kind_series: pd.Series) -> pd.Series:
    kinds = clean_kind_series(kind_series)
    scores = pd.Series(np.nan, index=kinds.index, dtype=float)
    scores.loc[kinds.isin(CONTINUOUS_KIND_CODES)] = 0.00
    scores.loc[kinds.notna() & ~kinds.isin(CONTINUOUS_KIND_CODES)] = 1.00
    return scores


def material_score(kind_series: pd.Series) -> pd.Series:
    kinds = clean_kind_series(kind_series)
    scores = pd.Series(np.nan, index=kinds.index, dtype=float)
    scores.loc[kinds.isin(WOOD_KIND_CODES)] = 1.00
    scores.loc[kinds.isin(CONCRETE_KIND_CODES)] = 0.85
    scores.loc[kinds.isin(STEEL_KIND_CODES)] = 0.50
    return scores


def max_span_score(series: pd.Series) -> pd.Series:
    spans = clean_float_series(series).clip(lower=0.0)
    return (spans / 250.0).clip(upper=1.0)


def num_spans_score(series: pd.Series) -> pd.Series:
    spans = clean_int_series(series)
    scores = pd.Series(np.nan, index=spans.index, dtype=float)
    scores.loc[spans == 1] = 0.00
    scores.loc[spans.isin([2, 3])] = 0.25
    scores.loc[(spans >= 4) & (spans <= 6)] = 0.50
    scores.loc[spans > 6] = 0.85
    return scores


def reconstruction_multiplier(series: pd.Series) -> pd.Series:
    years = clean_int_series(series)
    multiplier = pd.Series(1.00, index=years.index, dtype=float)
    valid = years.notna()
    multiplier.loc[valid & (years >= 1971) & (years <= 1989)] = 0.95
    multiplier.loc[valid & (years > 1989)] = 0.90
    return multiplier


def prepare_svi_inputs(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    if "year" not in result.columns and "YEAR_BUILT_027" in result.columns:
        result["year"] = clean_int_series(result["YEAR_BUILT_027"])
    if "yr_recon" not in result.columns and "YEAR_RECONSTRUCTED_106" in result.columns:
        result["yr_recon"] = extract_year(result["YEAR_RECONSTRUCTED_106"])
    if "spans" not in result.columns and "MAIN_UNIT_SPANS_045" in result.columns:
        result["spans"] = clean_int_series(result["MAIN_UNIT_SPANS_045"])
    if "max_span" not in result.columns and "MAX_SPAN_LEN_MT_048" in result.columns:
        result["max_span"] = clean_float_series(result["MAX_SPAN_LEN_MT_048"]).clip(lower=0.0)
    if "skew" not in result.columns and "DEGREES_SKEW_034" in result.columns:
        result["skew"] = clean_float_series(result["DEGREES_SKEW_034"]).clip(lower=0.0)

    if "cond" not in result.columns:
        if "SUBSTRUCTURE_COND_060" in result.columns:
            result["cond"] = clean_float_series(result["SUBSTRUCTURE_COND_060"])
        elif "LOWEST_RATING" in result.columns:
            result["cond"] = clean_float_series(result["LOWEST_RATING"])
        else:
            result["cond"] = np.nan

    if "kind" not in result.columns and "STRUCTURE_KIND_043A" in result.columns:
        result["kind"] = clean_kind_series(result["STRUCTURE_KIND_043A"])
    if "type" not in result.columns and "STRUCTURE_TYPE_043B" in result.columns:
        result["type"] = clean_kind_series(result["STRUCTURE_TYPE_043B"])

    return result


def compute_svi_scores(df: pd.DataFrame) -> pd.DataFrame:
    result = prepare_svi_inputs(df)

    result["score_year_built"] = year_built_score(result["year"])
    result["score_condition"] = condition_score(result["cond"])
    result["score_skew"] = skew_score(result["skew"])
    result["score_continuity"] = continuity_score(result["kind"])
    result["score_material"] = material_score(result["kind"])
    result["score_max_span"] = max_span_score(result["max_span"])
    result["score_num_spans"] = num_spans_score(result["spans"])
    result["YR_MULTIPLIER"] = reconstruction_multiplier(result["yr_recon"])

    filled_components = {}
    for col in SVI_WEIGHTS:
        series = result[col]
        median = series.dropna().median() if series.notna().any() else 0.0
        filled_components[col] = series.fillna(median)

    result["SVI_RAW"] = sum(filled_components[col] * weight for col, weight in SVI_WEIGHTS.items())
    result["SVI"] = (result["SVI_RAW"] * result["YR_MULTIPLIER"]).clip(lower=0.0, upper=1.0)

    # Backward-compatible aliases used in existing notebooks and figures.
    result["score_year"] = result["score_year_built"]
    result["score_recon"] = result["YR_MULTIPLIER"]
    result["score_spans"] = result["score_num_spans"]
    result["score_max_span"] = result["score_max_span"]
    result["score_cond"] = result["score_condition"]

    return result


def fragility_median_from_svi(svi: pd.Series | np.ndarray | float, damage_state: str, method: str = DEFAULT_FRAGILITY_MEDIAN_METHOD):
    mu_min, mu_max = FRAGILITY_MU_BOUNDS[damage_state]
    svi_values = np.clip(pd.to_numeric(svi, errors="coerce"), 0.0, 1.0)
    if method == "linear":
        return mu_min + svi_values * (mu_max - mu_min)
    if method == "exponential":
        return mu_max * ((mu_min / mu_max) ** (1.0 - svi_values))
    raise ValueError(f"Unsupported fragility median method: {method}")


def fragility_dispersion_from_svi(svi: pd.Series | np.ndarray | float) -> pd.Series | np.ndarray | float:
    svi_values = np.clip(pd.to_numeric(svi, errors="coerce"), 0.0, 1.0)
    return FRAGILITY_DISPERSION_BETA0 + FRAGILITY_DISPERSION_SLOPE * svi_values


def compute_fragility_parameters(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for method_name in ("linear", "exponential"):
        suffix = method_name.upper()
        for damage_state, prefix in [
            ("slight", "MU_DS1"),
            ("moderate", "MU_DS2"),
            ("extensive", "MU_DS3"),
            ("complete", "MU_DS4"),
        ]:
            result[f"{prefix}_{suffix}"] = fragility_median_from_svi(result["SVI"], damage_state, method=method_name)
    result["BETA_SVI"] = fragility_dispersion_from_svi(result["SVI"])
    return result


def exceedance_probability(pga: float, theta: float, beta: float) -> float:
    if pd.isna(pga) or pd.isna(theta) or pd.isna(beta) or pga <= 0 or theta <= 0 or beta <= 0:
        return 0.0
    return float(norm.cdf(np.log(pga / theta) / beta))


def compute_damage_probs_row(row: pd.Series, median_method: str = DEFAULT_FRAGILITY_MEDIAN_METHOD) -> pd.Series:
    pga = pd.to_numeric(row.get("pga"), errors="coerce")
    svi = pd.to_numeric(row.get("SVI"), errors="coerce")
    if pd.isna(pga) or pga <= 0 or pd.isna(svi):
        return pd.Series([1.0, 0.0, 0.0, 0.0, 0.0], index=["P_DS0", "P_DS1", "P_DS2", "P_DS3", "P_DS4"])

    mu1 = fragility_median_from_svi(svi, "slight", method=median_method)
    mu2 = fragility_median_from_svi(svi, "moderate", method=median_method)
    mu3 = fragility_median_from_svi(svi, "extensive", method=median_method)
    mu4 = fragility_median_from_svi(svi, "complete", method=median_method)
    beta = fragility_dispersion_from_svi(svi)

    pe1 = exceedance_probability(pga, mu1, beta)
    pe2 = exceedance_probability(pga, mu2, beta)
    pe3 = exceedance_probability(pga, mu3, beta)
    pe4 = exceedance_probability(pga, mu4, beta)

    p_ds0 = max(0.0, 1.0 - pe1)
    p_ds1 = max(0.0, pe1 - pe2)
    p_ds2 = max(0.0, pe2 - pe3)
    p_ds3 = max(0.0, pe3 - pe4)
    p_ds4 = max(0.0, pe4)

    total = p_ds0 + p_ds1 + p_ds2 + p_ds3 + p_ds4
    if total <= 0:
        return pd.Series([1.0, 0.0, 0.0, 0.0, 0.0], index=["P_DS0", "P_DS1", "P_DS2", "P_DS3", "P_DS4"])

    return pd.Series(
        [p_ds0 / total, p_ds1 / total, p_ds2 / total, p_ds3 / total, p_ds4 / total],
        index=["P_DS0", "P_DS1", "P_DS2", "P_DS3", "P_DS4"],
    )


def compute_damage_probabilities(df: pd.DataFrame, median_method: str = DEFAULT_FRAGILITY_MEDIAN_METHOD) -> pd.DataFrame:
    result = compute_fragility_parameters(compute_svi_scores(df))
    result[["P_DS0", "P_DS1", "P_DS2", "P_DS3", "P_DS4"]] = result.apply(
        compute_damage_probs_row,
        axis=1,
        median_method=median_method,
    )
    result["P_SUM"] = result[["P_DS0", "P_DS1", "P_DS2", "P_DS3", "P_DS4"]].sum(axis=1)
    result["EDR"] = sum(result[col] * FRAGILITY_DAMAGE_WEIGHTS[col] for col in FRAGILITY_DAMAGE_WEIGHTS)
    result["Fragility_Median_Method"] = median_method
    return result


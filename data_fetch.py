from eurostat import get_data_df
import pandas as pd
from functools import lru_cache


# ---------------------------------------------------------------------------
# Reusable helpers
# ---------------------------------------------------------------------------

def _melt_annual(df, value_name, start_year=2000):
    id_cols = [c for c in df.columns if not _is_year_col(c)]
    year_cols = [c for c in df.columns if _is_year_col(c)]
    df_long = df.melt(id_vars=id_cols, value_vars=year_cols,
                      var_name="year", value_name=value_name)
    df_long["year"] = pd.to_datetime(df_long["year"], format="%Y")
    df_long = df_long[df_long["year"] >= str(start_year)]
    df_long = df_long.dropna(subset=[value_name])
    return df_long.sort_values("year").reset_index(drop=True)


def _melt_monthly(df, value_name, start_year=2000):
    id_cols = [c for c in df.columns if not _is_month_col(c)]
    month_cols = [c for c in df.columns if _is_month_col(c)]
    df_long = df.melt(id_vars=id_cols, value_vars=month_cols,
                      var_name="date", value_name=value_name)
    df_long["date"] = pd.to_datetime(df_long["date"], format="%Y-%m")
    df_long = df_long[df_long["date"] >= str(start_year)]
    df_long = df_long.dropna(subset=[value_name])
    return df_long.sort_values("date").reset_index(drop=True)


def _is_year_col(col):
    try:
        y = int(str(col).strip())
        return 1950 <= y <= 2100
    except ValueError:
        return False


def _is_month_col(col):
    import re
    return bool(re.match(r"^\d{4}-\d{2}$", str(col).strip()))


def _geo_col(df):
    for c in df.columns:
        if "geo" in c.lower():
            return c
    raise KeyError("No geo column found in dataframe")


# ---------------------------------------------------------------------------
# Economy
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def fetch_greece_unemployment():
    df = get_data_df("une_rt_m")
    geo = _geo_col(df)
    df = df[(df[geo] == "EL") & (df["s_adj"] == "SA") & (df["age"] == "TOTAL") & (df["sex"] == "T")]
    return _melt_monthly(df, "unemployment_rate")[["date", "unemployment_rate"]]


@lru_cache(maxsize=1)
def fetch_greece_gdp():
    df = get_data_df("nama_10_gdp")
    geo = _geo_col(df)
    df = df[(df[geo] == "EL") & (df["unit"] == "CP_MEUR") & (df["na_item"] == "B1GQ")]
    return _melt_annual(df, "gdp")[["year", "gdp"]]


@lru_cache(maxsize=1)
def fetch_greece_inflation():
    df = get_data_df("prc_hicp_manr")
    geo = _geo_col(df)
    df = df[(df[geo] == "EL") & (df["coicop"] == "CP00") & (df["unit"] == "RCH_A")]
    return _melt_monthly(df, "inflation_rate", start_year=2015)[["date", "inflation_rate"]]


@lru_cache(maxsize=1)
def fetch_greece_gov_debt():
    df = get_data_df("gov_10dd_edpt1")
    geo = _geo_col(df)
    df = df[(df[geo] == "EL") & (df["sector"] == "S13") & (df["na_item"] == "GD") & (df["unit"] == "PC_GDP")]
    return _melt_annual(df, "gov_debt")[["year", "gov_debt"]]


@lru_cache(maxsize=1)
def fetch_greece_deficit():
    df = get_data_df("gov_10dd_edpt1")
    geo = _geo_col(df)
    df = df[(df[geo] == "EL") & (df["sector"] == "S13") & (df["na_item"] == "B9") & (df["unit"] == "PC_GDP")]
    return _melt_annual(df, "deficit")[["year", "deficit"]]


@lru_cache(maxsize=1)
def fetch_greece_real_gdp_growth():
    df = get_data_df("nama_10_gdp")
    geo = _geo_col(df)
    df = df[(df[geo] == "EL") & (df["unit"] == "CLV10_MEUR") & (df["na_item"] == "B1GQ")]
    df_long = _melt_annual(df, "gdp")
    df_long["growth"] = df_long["gdp"].pct_change() * 100
    return df_long.dropna(subset=["growth"])[["year", "growth"]]


# ---------------------------------------------------------------------------
# Labour
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def fetch_greece_youth_unemployment():
    df = get_data_df("une_rt_a")
    geo = _geo_col(df)
    df = df[(df[geo] == "EL") & (df["age"] == "Y15-24") & (df["sex"] == "T")]
    return _melt_annual(df, "unemployment")[["year", "unemployment"]]


@lru_cache(maxsize=1)
def fetch_greece_employment_rate():
    """Employment rate 20-64 (%). indic_em=EMP_LFS."""
    df = get_data_df("lfsi_emp_a")
    geo = _geo_col(df)
    df = df[(df[geo] == "EL") & (df["indic_em"] == "EMP_LFS") & (df["age"] == "Y20-64") & (df["sex"] == "T") & (df["unit"] == "PC_POP")]
    return _melt_annual(df, "employment_rate")[["year", "employment_rate"]]


@lru_cache(maxsize=1)
def fetch_greece_neet_rate():
    """NEET rate 15-29 (%). training=NO_FE_NO_NFE, wstatus=NEMP."""
    df = get_data_df("edat_lfse_20")
    geo = _geo_col(df)
    df = df[(df[geo] == "EL") & (df["sex"] == "T") & (df["age"] == "Y15-29") & (df["training"] == "NO_FE_NO_NFE") & (df["wstatus"] == "NEMP") & (df["unit"] == "PC")]
    return _melt_annual(df, "neet_rate")[["year", "neet_rate"]]


# ---------------------------------------------------------------------------
# Society & Demographics
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def fetch_greece_poverty_rate():
    df = get_data_df("ilc_li02")
    geo = _geo_col(df)
    df = df[(df[geo] == "EL") & (df["age"] == "TOTAL") & (df["sex"] == "T")]
    return _melt_annual(df, "at_risk_of_poverty_rate")[["year", "at_risk_of_poverty_rate"]]


@lru_cache(maxsize=1)
def fetch_greece_fertility_rate():
    df = get_data_df("demo_frate")
    geo = _geo_col(df)
    df = df[(df[geo] == "EL")]
    return _melt_annual(df, "fertility")[["year", "fertility"]]


@lru_cache(maxsize=1)
def fetch_greece_population_change():
    df = get_data_df("demo_gind")
    geo = _geo_col(df)
    df = df[(df[geo] == "EL") & (df["indic_de"] == "NATGROW")]
    return _melt_annual(df, "population_change")[["year", "population_change"]]


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def fetch_greece_renewables_share():
    """Share of renewables in gross final energy consumption (%). nrg_bal=REN, unit=PC."""
    df = get_data_df("nrg_ind_ren")
    geo = _geo_col(df)
    df = df[(df[geo] == "EL") & (df["nrg_bal"] == "REN") & (df["unit"] == "PC")]
    return _melt_annual(df, "renewables_share")[["year", "renewables_share"]]


# ---------------------------------------------------------------------------
# Crime
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def fetch_greece_crime_by_category():
    """Offences by key category — homicide, robbery, theft, drug offences (NR)."""
    df = get_data_df("crim_off_cat")
    geo = _geo_col(df)
    cats = {
        "ICCS0101": "Homicide",
        "ICCS0401": "Robbery",
        "ICCS0501": "Theft",
        "ICCS0601": "Drug offences",
    }
    df = df[(df[geo] == "EL") & (df["iccs"].isin(cats.keys())) & (df["unit"] == "NR")]
    df_long = _melt_annual(df, "offences")
    df_long["category"] = df_long["iccs"].map(cats)
    return df_long[["year", "category", "offences"]]


@lru_cache(maxsize=1)
def fetch_greece_prison_population():
    """Prison population count (crim_pris_pop, unit=NR)."""
    df = get_data_df("crim_pris_pop")
    geo = _geo_col(df)
    df = df[(df[geo] == "EL") & (df["unit"] == "NR")]
    df_long = _melt_annual(df, "prison_population")
    return df_long.groupby("year", as_index=False)["prison_population"].sum()[["year", "prison_population"]]


# ---------------------------------------------------------------------------
# Migration & Expats
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def fetch_greece_asylum_applications():
    """First-time asylum applications. Column=applicant, value=FRST."""
    df = get_data_df("migr_asyappctza")
    geo = _geo_col(df)
    df = df[(df[geo] == "EL") & (df["applicant"] == "FRST") & (df["citizen"] == "TOTAL") & (df["sex"] == "T") & (df["age"] == "TOTAL")]
    return _melt_annual(df, "asylum_applications")[["year", "asylum_applications"]]


@lru_cache(maxsize=1)
def fetch_greece_foreign_population_share():
    """Foreign residents as % of total population (TOTAL minus NAT from migr_pop1ctz)."""
    df = get_data_df("migr_pop1ctz")
    geo = _geo_col(df)
    base = df[(df[geo] == "EL") & (df["sex"] == "T") & (df["age"] == "TOTAL") & (df["unit"] == "NR")]
    total = _melt_annual(base[base["citizen"] == "TOTAL"], "total_pop")
    nat   = _melt_annual(base[base["citizen"] == "NAT"],   "nat_pop")
    merged = total[["year", "total_pop"]].merge(nat[["year", "nat_pop"]], on="year")
    merged["share"] = (merged["total_pop"] - merged["nat_pop"]) / merged["total_pop"] * 100
    return merged[["year", "share"]]

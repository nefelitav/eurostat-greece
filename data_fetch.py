from eurostat import get_data_df
import pandas as pd
from functools import lru_cache

@lru_cache(maxsize=1)
def fetch_greece_unemployment():
    df = get_data_df('une_rt_m')
    df = df[df['geo\\TIME_PERIOD'] == 'EL']
    df = df[(df['s_adj'] == 'SA') & (df['age'] == 'TOTAL') & (df['sex'] == 'T')]
    date_cols = df.columns[6:]
    df_long = df.melt(id_vars=['freq', 's_adj', 'age', 'unit', 'sex', 'geo\\TIME_PERIOD'],
                      value_vars=date_cols,
                      var_name='date',
                      value_name='unemployment_rate')
    df_long['date'] = pd.to_datetime(df_long['date'], format='%Y-%m')
    df_long = df_long[df_long['date'] >= '2000-01-01'].dropna(subset=['unemployment_rate'])
    df_long = df_long.sort_values('date').reset_index(drop=True)
    return df_long[['date', 'unemployment_rate']]

@lru_cache(maxsize=1)
def fetch_greece_gdp():
    df = get_data_df('nama_10_gdp')

    df = df[df['geo\\TIME_PERIOD'] == 'EL']

    year_cols = df.columns[5:]

    df_long = df.melt(id_vars=['freq', 'unit', 'na_item', 'geo\\TIME_PERIOD'],
                      value_vars=year_cols,
                      var_name='year',
                      value_name='gdp')

    df_long['year'] = pd.to_datetime(df_long['year'], format='%Y')

    df_long = df_long[df_long['year'] >= '2000-01-01'].dropna(subset=['gdp'])

    df_long = df_long.sort_values('year')

    df_long = df_long.reset_index(drop=True)

    return df_long[['year', 'gdp']]

@lru_cache(maxsize=1)
def fetch_greece_inflation():
    df = get_data_df('prc_hicp_manr')

    df = df[(df['geo\\TIME_PERIOD'] == 'EL') & (df['coicop'] == 'CP00') & (df['unit'] == 'RCH_A')]

    date_cols = df.columns[5:]

    df_long = df.melt(id_vars=['freq', 'unit', 'coicop', 'geo\\TIME_PERIOD'],
                      value_vars=date_cols,
                      var_name='date',
                      value_name='inflation_rate')

    df_long['date'] = pd.to_datetime(df_long['date'], format='%Y-%m')

    df_long = df_long[df_long['date'] >= '2015-01-01'].dropna(subset=['inflation_rate'])

    df_long = df_long.sort_values('date').reset_index(drop=True)

    return df_long[['date', 'inflation_rate']]

@lru_cache(maxsize=1)
def fetch_greece_wages():
    df = get_data_df('nama_10_a10')
    df = df[df['geo\\TIME_PERIOD'] == 'EL']
    if 'na_item' in df.columns:
        df = df[df['na_item'] == 'B1G']
    date_cols = df.columns[5:]
    df_long = df.melt(id_vars=df.columns[:5], value_vars=date_cols, var_name='year', value_name='wages')
    df_long['year'] = pd.to_datetime(df_long['year'], format='%Y')
    df_long = df_long.dropna(subset=['wages'])
    return df_long[['year', 'wages']]

@lru_cache(maxsize=1)
def fetch_greece_gov_debt():
    df = get_data_df('gov_10dd_edpt1')
    df = df[df['geo\\TIME_PERIOD'] == 'EL']
    date_cols = df.columns[5:]
    df_long = df.melt(id_vars=df.columns[:5], value_vars=date_cols, var_name='year', value_name='gov_debt')
    df_long['year'] = pd.to_datetime(df_long['year'], format='%Y')
    df_long = df_long.dropna(subset=['gov_debt'])
    return df_long[['year', 'gov_debt']]

@lru_cache(maxsize=1)
def fetch_greece_deficit():
    df = get_data_df("gov_10dd_edpt1")

    df = df[
        (df["geo\\TIME_PERIOD"] == "EL") &
        (df["sector"] == "S13") &
        (df["na_item"] == "B9") &
        (df["unit"] == "PC_GDP")
    ]

    year_cols = df.columns[6:]

    df_long = df.melt(
        id_vars=["freq", "unit", "sector", "na_item", "geo\\TIME_PERIOD"],
        value_vars=year_cols,
        var_name="year",
        value_name="deficit"
    )

    df_long["year"] = pd.to_datetime(df_long["year"], format="%Y")
    df_long = df_long.dropna(subset=["deficit"])
    df_long = df_long.sort_values("year").reset_index(drop=True)

    return df_long[["year", "deficit"]]

@lru_cache(maxsize=1)
def fetch_greece_youth_unemployment():
    df = get_data_df("une_rt_a")

    df = df[
        (df["geo\\TIME_PERIOD"] == "EL") &
        (df["age"] == "Y15-24") &
        (df["sex"] == "T")
    ]

    year_cols = df.columns[6:]
    df_long = df.melt(
        id_vars=df.columns[:6],
        value_vars=year_cols,
        var_name="year",
        value_name="unemployment"
    )

    df_long["year"] = pd.to_datetime(df_long["year"], format="%Y")
    df_long = df_long.dropna(subset=["unemployment"])

    return df_long[["year", "unemployment"]]

@lru_cache(maxsize=1)
def fetch_greece_real_gdp_growth():
    df = get_data_df("nama_10_gdp")

    df = df[
        (df["geo\\TIME_PERIOD"] == "EL") &
        (df["unit"] == "CLV10_MEUR") &
        (df["na_item"] == "B1GQ")
    ]

    year_cols = df.columns[5:]
    df_long = df.melt(
        id_vars=df.columns[:5],
        value_vars=year_cols,
        var_name="year",
        value_name="gdp"
    )

    df_long["year"] = pd.to_datetime(df_long["year"], format="%Y")
    df_long = df_long.sort_values("year")
    df_long["growth"] = df_long["gdp"].pct_change() * 100

    return df_long.dropna(subset=["growth"])[["year", "growth"]]

@lru_cache(maxsize=1)
def fetch_greece_productivity():
    df = get_data_df('nama_10_lp_ulc')

    df = df[df['geo\\TIME_PERIOD'] == 'EL']

    year_cols = df.columns[4:]

    df_long = df.melt(
        id_vars=df.columns[:4],
        value_vars=year_cols,
        var_name='year',
        value_name='productivity'
    )

    df_long['year'] = pd.to_numeric(df_long['year'], errors='coerce')
    df_long = df_long.dropna(subset=['productivity'])

    return df_long[['year', 'productivity']]

@lru_cache(maxsize=1)
def fetch_greece_poverty_rate():
    df = get_data_df("ilc_li02")

    df_filtered = df[(df['geo\\TIME_PERIOD'] == 'EL') & (df['age'] == 'Y_LT18') & (df['sex'] == 'T')]

    df_melted = df_filtered.melt(id_vars=['freq', 'unit', 'indic_il', 'sex', 'age', r'geo\TIME_PERIOD'],
                                 value_vars=[str(y) for y in range(1995, 2026)],
                                 var_name='year',
                                 value_name='value')

    df_melted['year'] = df_melted['year'].astype(int)

    return df_melted[["year", "value"]].rename(columns={"value": "at_risk_of_poverty_rate"}).dropna()

@lru_cache(maxsize=1)
def fetch_greece_fertility_rate():
    df = get_data_df("demo_frate")

    df = df[df["geo\\TIME_PERIOD"] == "EL"]

    years = df.columns[3:]
    df = df.melt(
        id_vars=df.columns[:3],
        value_vars=years,
        var_name="year",
        value_name="fertility"
    )

    df["year"] = pd.to_datetime(df["year"], format="%Y")
    return df[["year", "fertility"]].dropna()

@lru_cache(maxsize=1)
def fetch_greece_population_change():
    df = get_data_df("demo_gind")

    df = df[df["geo\\TIME_PERIOD"] == "EL"]

    years = df.columns[4:]
    df = df.melt(
        id_vars=df.columns[:4],
        value_vars=years,
        var_name="year",
        value_name="population_change"
    )

    df["year"] = pd.to_datetime(df["year"], format="%Y")
    return df[["year", "population_change"]].dropna()

@lru_cache(maxsize=1)
def fetch_greece_energy_dependency():
    df = get_data_df("some_code_for_energy_dependency")

    df = df.rename(columns={"geo\\TIME_PERIOD": "geo_time_period"})  # Rename so it doesn't conflict

    years = [col for col in df.columns if col.isdigit()]

    df_long = df.melt(
        id_vars=[col for col in df.columns if col not in years],
        value_vars=years,
        var_name="year",
        value_name="energy_dependency"
    )

    df_long["year"] = pd.to_datetime(df_long["year"], format="%Y")

    return df_long[["year", "energy_dependency"]].dropna()

@lru_cache(maxsize=1)
def fetch_greece_greenhouse_gas_emissions():
    df = get_data_df("env_air_gge")

    print("Columns before melt:", df.columns)

    id_vars = df.columns[:6]
    value_vars = df.columns[6:]

    df_melted = df.melt(
        id_vars=id_vars,
        value_vars=value_vars,
        var_name="year",
        value_name="ghg_emissions"
    )

    print("Columns after melt:", df_melted.columns)

    df_melted["year"] = pd.to_datetime(df_melted["year"], format="%Y")

    df_melted = df_melted[df_melted["geo\\TIME_PERIOD"] == "EL"]

    return df_melted[["year", "ghg_emissions"]].dropna()

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_timeseries(df, y, title, ylabel):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df["year"], df[y], marker="o")
    ax.set_title(title)
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    ax.grid(True)
    fig.tight_layout()
    return fig

def plot_gdp(df):
    return plot_timeseries(
        df,
        y="gdp",
        title="Greece Annual GDP",
        ylabel="Million EUR"
    )


def plot_wages(df):
    return plot_timeseries(
        df,
        y="wages",
        title="Greece Wages and Earnings",
        ylabel="EUR"
    )


def plot_gov_debt(df):
    return plot_timeseries(
        df,
        y="gov_debt",
        title="Greece Government Debt",
        ylabel="% of GDP"
    )


def plot_deficit(df):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axhline(0, linewidth=1)
    ax.plot(df["year"], df["deficit"], marker="o")
    ax.set_title("Greece Government Deficit / Surplus")
    ax.set_xlabel("Year")
    ax.set_ylabel("% of GDP")
    ax.grid(True)
    fig.tight_layout()
    return fig


def plot_gdp_growth(df):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axhline(0, linewidth=1)
    ax.plot(df["year"], df["growth"], marker="o")
    ax.set_title("Greece Real GDP Growth (YoY)")
    ax.set_xlabel("Year")
    ax.set_ylabel("%")
    ax.grid(True)
    fig.tight_layout()
    return fig


def plot_youth_unemployment(df):
    return plot_timeseries(
        df,
        y="unemployment",
        title="Greece Youth Unemployment (15–24)",
        ylabel="%"
    )

def plot_unemployment(df):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["date"], df["unemployment_rate"], marker="o")
    ax.set_title("Greece Monthly Unemployment Rate (SA)")
    ax.set_xlabel("Date")
    ax.set_ylabel("%")
    ax.grid(True)

    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    fig.tight_layout()
    return fig


def plot_inflation(df):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["date"], df["inflation_rate"], marker="o")
    ax.set_title("Greece Inflation Rate (HICP)")
    ax.set_xlabel("Date")
    ax.set_ylabel("%")
    ax.grid(True)
    fig.tight_layout()
    return fig

def plot_productivity(df):
    return plot_timeseries(
        df,
        y="productivity",
        title="Greece Productivity",
        ylabel="Index (2015=100)"
    )

def plot_at_risk_of_poverty(df):
    return plot_timeseries(
        df,
        y="at_risk_of_poverty_rate",
        title="Greece At-risk-of-poverty Rate",
        ylabel="%"
    )

def plot_fertility_rate(df):
    return plot_timeseries(
        df,
        y="fertility_rate",
        title="Greece Fertility Rate",
        ylabel="Births per Woman"
    )

def plot_population_change(df):
    return plot_timeseries(
        df,
        y="population_change",
        title="Greece Population Change",
        ylabel="Number of People"
    )

def plot_energy_dependency(df):
    return plot_timeseries(
        df,
        y="energy_dependency",
        title="Greece Energy Dependency",
        ylabel="%"
    )

def plot_greenhouse_gas_emissions(df):
    return plot_timeseries(
        df,
        y="ghg_emissions",
        title="Greece Greenhouse Gas Emissions",
        ylabel="Million Tonnes CO2 eq."
    )

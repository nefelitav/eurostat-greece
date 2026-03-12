import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

# ---------------------------------------------------------------------------
# Palette / style constants
# ---------------------------------------------------------------------------
_BLUE    = "#1a73e8"
_RED     = "#e53935"
_GREEN   = "#43a047"
_ORANGE  = "#fb8c00"
_PURPLE  = "#8e24aa"
_TEAL    = "#00897b"
_GREY    = "#757575"

_CATEGORY_COLORS = [_BLUE, _RED, _GREEN, _ORANGE, _PURPLE, _TEAL, _GREY]

# ---------------------------------------------------------------------------
# Reusable base helpers
# ---------------------------------------------------------------------------

def _base_fig(figsize=(9, 4)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return fig, ax


def _year_axis(ax):
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")


def _annotate_latest(ax, x, y, fmt="{:.1f}"):
    """Annotate the last data point with its value."""
    ax.annotate(
        fmt.format(y),
        xy=(x, y),
        xytext=(6, 4),
        textcoords="offset points",
        fontsize=8,
        color=_GREY,
    )


def _delta_badge(ax, series, unit=""):
    """Add a small Δ change annotation in the top-left corner of the axes."""
    if len(series) < 2:
        return
    latest = series.iloc[-1]
    prev   = series.iloc[-2]
    delta  = latest - prev
    color  = _GREEN if delta <= 0 else _RED   # lower is better default; callers override
    sign   = "+" if delta > 0 else ""
    ax.text(
        0.02, 0.95,
        f"Latest: {latest:.1f}{unit}  ({sign}{delta:.1f}{unit} vs prev yr)",
        transform=ax.transAxes,
        fontsize=8,
        verticalalignment="top",
        color=color,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=color, alpha=0.8),
    )


def plot_line(df, x_col, y_col, title, ylabel, color=_BLUE,
              zero_line=False, lower_is_better=True, unit="",
              figsize=(9, 4)):
    """Generic reusable line plot with delta badge and latest-point annotation."""
    fig, ax = _base_fig(figsize)
    ax.plot(df[x_col], df[y_col], color=color, linewidth=2, marker="o", markersize=3)
    if zero_line:
        ax.axhline(0, color=_GREY, linewidth=0.8, linestyle="--")
    _year_axis(ax)
    ax.set_title(title, fontsize=11, fontweight="bold", pad=10)
    ax.set_xlabel("")
    ax.set_ylabel(ylabel, fontsize=9)
    if len(df) > 0:
        _annotate_latest(ax, df[x_col].iloc[-1], df[y_col].iloc[-1])
        badge_series = df[y_col]
        # flip colour logic for indicators where higher is better
        _delta_badge_directional(ax, badge_series, unit, lower_is_better)
    fig.tight_layout()
    return fig


def _delta_badge_directional(ax, series, unit, lower_is_better):
    if len(series) < 2:
        return
    latest = series.iloc[-1]
    prev   = series.iloc[-2]
    delta  = latest - prev
    if lower_is_better:
        color = _GREEN if delta < 0 else _RED
    else:
        color = _GREEN if delta > 0 else _RED
    sign = "+" if delta > 0 else ""
    ax.text(
        0.02, 0.95,
        f"Latest: {latest:.1f}{unit}  ({sign}{delta:.1f}{unit} vs prev)",
        transform=ax.transAxes,
        fontsize=8,
        verticalalignment="top",
        color=color,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=color, alpha=0.8),
    )


def plot_bar(df, x_col, y_col, title, ylabel, color=_BLUE,
             zero_line=False, lower_is_better=True, unit="",
             figsize=(9, 4)):
    """Generic reusable bar chart (useful for annual totals)."""
    fig, ax = _base_fig(figsize)
    xs = [t.year if hasattr(t, "year") else int(t) for t in df[x_col]]
    ax.bar(xs, df[y_col], color=color, alpha=0.8)
    if zero_line:
        ax.axhline(0, color=_GREY, linewidth=0.8)
    ax.set_title(title, fontsize=11, fontweight="bold", pad=10)
    ax.set_ylabel(ylabel, fontsize=9)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    if len(df) > 0:
        _delta_badge_directional(ax, df[y_col], unit, lower_is_better)
    fig.tight_layout()
    return fig


def plot_multi_line(df, x_col, category_col, y_col, title, ylabel, figsize=(9, 4)):
    """Reusable multi-line chart for category-broken-down series."""
    fig, ax = _base_fig(figsize)
    for i, (cat, grp) in enumerate(df.groupby(category_col)):
        grp = grp.sort_values(x_col)
        color = _CATEGORY_COLORS[i % len(_CATEGORY_COLORS)]
        ax.plot(grp[x_col], grp[y_col], label=cat, color=color, linewidth=2, marker="o", markersize=3)
    _year_axis(ax)
    ax.set_title(title, fontsize=11, fontweight="bold", pad=10)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.legend(fontsize=8, framealpha=0.7)
    fig.tight_layout()
    return fig

# ---------------------------------------------------------------------------
# Economy
# ---------------------------------------------------------------------------

def plot_gdp(df):
    return plot_line(df, "year", "gdp",
                     title="Greece Annual GDP (Current Prices)",
                     ylabel="Million EUR",
                     color=_BLUE, lower_is_better=False, unit=" M€")

def plot_gdp_growth(df):
    return plot_line(df, "year", "growth",
                     title="Greece Real GDP Growth (YoY)",
                     ylabel="%", color=_TEAL,
                     zero_line=True, lower_is_better=False, unit="%")

def plot_gov_debt(df):
    return plot_line(df, "year", "gov_debt",
                     title="Greece Government Debt (% of GDP)",
                     ylabel="% of GDP", color=_RED,
                     lower_is_better=True, unit="%")

def plot_deficit(df):
    return plot_line(df, "year", "deficit",
                     title="Greece Government Deficit / Surplus (% of GDP)",
                     ylabel="% of GDP", color=_ORANGE,
                     zero_line=True, lower_is_better=False, unit="%")

def plot_inflation(df):
    fig, ax = _base_fig((9, 4))
    ax.plot(df["date"], df["inflation_rate"], color=_ORANGE, linewidth=2, marker="o", markersize=2)
    ax.axhline(0, color=_GREY, linewidth=0.8, linestyle="--")
    ax.axhline(2, color=_GREEN, linewidth=0.8, linestyle=":", label="ECB target 2%")
    ax.set_title("Greece Inflation Rate (HICP)", fontsize=11, fontweight="bold", pad=10)
    ax.set_ylabel("%", fontsize=9)
    ax.legend(fontsize=8)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    _delta_badge_directional(ax, df["inflation_rate"], "%", lower_is_better=True)
    fig.tight_layout()
    return fig

def plot_wages(df):
    return plot_line(df, "year", "wages",
                     title="Greece Labour Cost Index (Real, 2016=100)",
                     ylabel="Index (2016=100)", color=_GREEN,
                     lower_is_better=False)

# ---------------------------------------------------------------------------
# Labour
# ---------------------------------------------------------------------------

def plot_unemployment(df):
    fig, ax = _base_fig((10, 4))
    ax.plot(df["date"], df["unemployment_rate"], color=_RED, linewidth=2, marker="o", markersize=2)
    ax.set_title("Greece Monthly Unemployment Rate (SA)", fontsize=11, fontweight="bold", pad=10)
    ax.set_ylabel("%", fontsize=9)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    _delta_badge_directional(ax, df["unemployment_rate"], "%", lower_is_better=True)
    fig.tight_layout()
    return fig

def plot_youth_unemployment(df):
    return plot_line(df, "year", "unemployment",
                     title="Greece Youth Unemployment Rate (15–24)",
                     ylabel="%", color=_RED,
                     lower_is_better=True, unit="%")

def plot_employment_rate(df):
    return plot_line(df, "year", "employment_rate",
                     title="Greece Employment Rate (20–64)",
                     ylabel="%", color=_GREEN,
                     lower_is_better=False, unit="%")

def plot_neet_rate(df):
    return plot_line(df, "year", "neet_rate",
                     title="Greece NEET Rate (15–29)",
                     ylabel="%", color=_ORANGE,
                     lower_is_better=True, unit="%")

def plot_productivity(df):
    return plot_line(df, "year", "productivity",
                     title="Greece Labour Productivity (Index 2010=100)",
                     ylabel="Index", color=_TEAL,
                     lower_is_better=False)

# ---------------------------------------------------------------------------
# Society & Demographics
# ---------------------------------------------------------------------------

def plot_at_risk_of_poverty(df):
    return plot_line(df, "year", "at_risk_of_poverty_rate",
                     title="Greece At-risk-of-poverty Rate (All Ages)",
                     ylabel="%", color=_RED,
                     lower_is_better=True, unit="%")

def plot_fertility_rate(df):
    return plot_line(df, "year", "fertility",
                     title="Greece Fertility Rate",
                     ylabel="Births per Woman", color=_PURPLE,
                     lower_is_better=False)

def plot_population_change(df):
    return plot_line(df, "year", "population_change",
                     title="Greece Natural Population Change",
                     ylabel="Persons", color=_GREY,
                     zero_line=True, lower_is_better=False)

def plot_old_age_dependency(df):
    return plot_line(df, "year", "old_age_dependency",
                     title="Greece Old-Age Dependency Ratio",
                     ylabel="Per 100 working-age", color=_PURPLE,
                     lower_is_better=True)

# ---------------------------------------------------------------------------
# Environment & Energy
# ---------------------------------------------------------------------------

def plot_energy_dependency(df):
    return plot_line(df, "year", "energy_dependency",
                     title="Greece Energy Import Dependency",
                     ylabel="%", color=_ORANGE,
                     lower_is_better=True, unit="%")

def plot_greenhouse_gas_emissions(df):
    return plot_line(df, "year", "ghg_emissions",
                     title="Greece Greenhouse Gas Emissions",
                     ylabel="Thousand tonnes CO₂ eq.", color=_GREY,
                     lower_is_better=True)

def plot_renewables_share(df):
    return plot_line(df, "year", "renewables_share",
                     title="Greece Renewables Share in Final Energy Consumption",
                     ylabel="%", color=_GREEN,
                     lower_is_better=False, unit="%")

# ---------------------------------------------------------------------------
# Crime
# ---------------------------------------------------------------------------

def plot_crime_offences(df):
    return plot_bar(df, "year", "offences",
                    title="Greece Total Recorded Criminal Offences",
                    ylabel="Number of offences", color=_RED,
                    lower_is_better=True)

def plot_crime_by_category(df):
    return plot_multi_line(df, "year", "category", "offences",
                           title="Greece Recorded Offences by Category",
                           ylabel="Number of offences")

def plot_prison_population(df):
    return plot_bar(df, "year", "prison_population",
                    title="Greece Prison Population",
                    ylabel="Number of inmates", color=_ORANGE,
                    lower_is_better=True)

# ---------------------------------------------------------------------------
# Migration & Expats
# ---------------------------------------------------------------------------

def plot_foreign_population(df):
    return plot_bar(df, "year", "foreign_population",
                    title="Greece Foreign Residents (stock)",
                    ylabel="Number of persons", color=_BLUE,
                    lower_is_better=False)

def plot_foreign_population_share(df):
    return plot_line(df, "year", "share",
                     title="Greece Foreign Residents as Share of Population",
                     ylabel="%", color=_BLUE,
                     lower_is_better=False, unit="%")

def plot_immigration_flows(df):
    return plot_bar(df, "year", "immigration",
                    title="Greece Annual Immigration Inflows (Foreign Citizens)",
                    ylabel="Number of persons", color=_TEAL,
                    lower_is_better=False)

def plot_emigration_flows(df):
    return plot_bar(df, "year", "emigration",
                    title="Greece Annual Emigration Outflows (Greek Citizens)",
                    ylabel="Number of persons", color=_ORANGE,
                    lower_is_better=True)

def plot_asylum_applications(df):
    return plot_bar(df, "year", "asylum_applications",
                    title="Greece First-time Asylum Applications",
                    ylabel="Number of applications", color=_PURPLE,
                    lower_is_better=False)

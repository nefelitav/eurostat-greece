from flask import Flask, render_template_string, Response
from flask_caching import Cache
import io
import matplotlib.pyplot as plt

from data_fetch import (
    fetch_greece_unemployment,
    fetch_greece_gdp,
    fetch_greece_inflation,
    fetch_greece_wages,
    fetch_greece_gov_debt,
    fetch_greece_deficit,
    fetch_greece_youth_unemployment,
    fetch_greece_real_gdp_growth,
    fetch_greece_productivity,
    fetch_greece_poverty_rate,
    fetch_greece_fertility_rate,
    fetch_greece_population_change,
    fetch_greece_energy_dependency,
    fetch_greece_greenhouse_gas_emissions,
)

from plotting import (
    plot_unemployment,
    plot_gdp,
    plot_inflation,
    plot_wages,
    plot_gov_debt,
    plot_deficit,
    plot_youth_unemployment,
    plot_gdp_growth,
    plot_productivity,
    plot_at_risk_of_poverty,
    plot_fertility_rate,
    plot_population_change,
    plot_energy_dependency,
    plot_greenhouse_gas_emissions,
)

app = Flask(__name__)

cache = Cache(app, config={
    "CACHE_TYPE": "simple",
    "CACHE_DEFAULT_TIMEOUT": 3600
})

@cache.cached()
def unemployment_data(): return fetch_greece_unemployment()

@cache.cached()
def gdp_data(): return fetch_greece_gdp()

@cache.cached()
def inflation_data(): return fetch_greece_inflation()

@cache.cached()
def wages_data(): return fetch_greece_wages()

@cache.cached()
def gov_debt_data(): return fetch_greece_gov_debt()

@cache.cached()
def deficit_data(): return fetch_greece_deficit()

@cache.cached()
def youth_unemployment_data(): return fetch_greece_youth_unemployment()

@cache.cached()
def gdp_growth_data(): return fetch_greece_real_gdp_growth()

@cache.cached()
def productivity_data(): return fetch_greece_productivity()

@cache.cached()
def at_risk_of_poverty_data(): return fetch_greece_poverty_rate()

@cache.cached()
def fertility_rate_data(): return fetch_greece_fertility_rate()

@cache.cached()
def population_change_data(): return fetch_greece_population_change()

@cache.cached()
def energy_dependency_data(): return fetch_greece_energy_dependency()

@cache.cached()
def greenhouse_gas_emissions_data(): return fetch_greece_greenhouse_gas_emissions()

def fig_to_png(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return Response(buf.getvalue(), mimetype="image/png")

@app.route("/")
def index():
    return render_template_string("""
    <style>
        h1 {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-weight: 300;
            font-size: 1.5rem;
            color: #222;
            text-align: center;
            margin: 1rem 0;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }

        img { width: 100%; border: 1px solid #ccc; }
    </style>

    <h1>Eurostat Dashboard 🇬🇷</h1>

    <div class="grid">
       <img src="/gdp.png" alt="GDP">
       <img src="/gdp_growth.png" alt="GDP Growth">
       <img src="/gov_debt.png" alt="Government Debt">

       <img src="/inflation.png" alt="Inflation">
       <img src="/wages.png" alt="Wages">
       <img src="/deficit.png" alt="Deficit">

       <img src="/unemployment.png" alt="Unemployment">
       <img src="/youth_unemployment.png" alt="Youth Unemployment">
       <img src="/productivity.png" alt="Productivity">

       <img src="/population_change.png" alt="Population Change">
       <img src="/at_risk_of_poverty.png" alt="At Risk of Poverty Rate">
       <img src="/greenhouse_gas_emissions.png" alt="Greenhouse Gas Emissions">
    </div>
    """)

@app.route("/unemployment.png")
def unemployment_png():
    return fig_to_png(plot_unemployment(unemployment_data()))

@app.route("/gdp.png")
def gdp_png():
    return fig_to_png(plot_gdp(gdp_data()))

@app.route("/inflation.png")
def inflation_png():
    return fig_to_png(plot_inflation(inflation_data()))

@app.route("/wages.png")
def wages_png():
    return fig_to_png(plot_wages(wages_data()))

@app.route("/gov_debt.png")
def gov_debt_png():
    return fig_to_png(plot_gov_debt(gov_debt_data()))

@app.route("/deficit.png")
def deficit_png():
    return fig_to_png(plot_deficit(deficit_data()))

@app.route("/youth_unemployment.png")
def youth_unemployment_png():
    return fig_to_png(plot_youth_unemployment(youth_unemployment_data()))

@app.route("/gdp_growth.png")
def gdp_growth_png():
    return fig_to_png(plot_gdp_growth(gdp_growth_data()))

@app.route("/productivity.png")
def productivity_png():
    return fig_to_png(plot_productivity(productivity_data()))

@app.route("/at_risk_of_poverty.png")
def at_risk_of_poverty_png():
    return fig_to_png(plot_at_risk_of_poverty(at_risk_of_poverty_data()))

@app.route("/fertility_rate.png")
def fertility_rate_png():
    return fig_to_png(plot_fertility_rate(fertility_rate_data()))

@app.route("/population_change.png")
def population_change_png():
    return fig_to_png(plot_population_change(population_change_data()))

@app.route("/energy_dependency.png")
def energy_dependency_png():
    return fig_to_png(plot_energy_dependency(energy_dependency_data()))

@app.route("/greenhouse_gas_emissions.png")
def greenhouse_gas_emissions_png():
    return fig_to_png(plot_greenhouse_gas_emissions(greenhouse_gas_emissions_data()))

if __name__ == "__main__":
    app.run(debug=True)

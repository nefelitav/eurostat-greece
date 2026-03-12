from flask import Flask, render_template_string, Response, jsonify
from flask_caching import Cache
import io
import threading
import matplotlib.pyplot as plt

from data_fetch import (
    fetch_greece_unemployment,
    fetch_greece_gdp,
    fetch_greece_inflation,
    fetch_greece_gov_debt,
    fetch_greece_deficit,
    fetch_greece_real_gdp_growth,
    fetch_greece_youth_unemployment,
    fetch_greece_employment_rate,
    fetch_greece_neet_rate,
    fetch_greece_poverty_rate,
    fetch_greece_fertility_rate,
    fetch_greece_population_change,
    fetch_greece_renewables_share,
    fetch_greece_crime_by_category,
    fetch_greece_prison_population,
    fetch_greece_asylum_applications,
    fetch_greece_foreign_population_share,
)

from plotting import (
    plot_unemployment,
    plot_gdp,
    plot_inflation,
    plot_gov_debt,
    plot_deficit,
    plot_gdp_growth,
    plot_youth_unemployment,
    plot_employment_rate,
    plot_neet_rate,
    plot_at_risk_of_poverty,
    plot_fertility_rate,
    plot_population_change,
    plot_renewables_share,
    plot_crime_by_category,
    plot_prison_population,
    plot_asylum_applications,
    plot_foreign_population_share,
)

app = Flask(__name__)
cache = Cache(app, config={"CACHE_TYPE": "simple", "CACHE_DEFAULT_TIMEOUT": 3600})

# Set of chart slugs whose data has been fetched and is ready to render
_ready: set = set()
_ready_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Background preload
# ---------------------------------------------------------------------------

# Maps route slug -> fetcher function
_FETCHERS = {
    "gdp":                    fetch_greece_gdp,
    "gdp_growth":             fetch_greece_real_gdp_growth,
    "inflation":              fetch_greece_inflation,
    "gov_debt":               fetch_greece_gov_debt,
    "deficit":                fetch_greece_deficit,
    "unemployment":           fetch_greece_unemployment,
    "youth_unemployment":     fetch_greece_youth_unemployment,
    "employment_rate":        fetch_greece_employment_rate,
    "neet_rate":              fetch_greece_neet_rate,
    "at_risk_of_poverty":     fetch_greece_poverty_rate,
    "fertility_rate":         fetch_greece_fertility_rate,
    "population_change":      fetch_greece_population_change,
    "renewables_share":       fetch_greece_renewables_share,
    "crime_by_category":      fetch_greece_crime_by_category,
    "prison_population":      fetch_greece_prison_population,
    "foreign_population_share": fetch_greece_foreign_population_share,
    "asylum_applications":    fetch_greece_asylum_applications,
}

def _preload():
    for slug, fn in _FETCHERS.items():
        try:
            fn()
            with _ready_lock:
                _ready.add(slug)
            print(f"[preload] ✓ {slug}")
        except Exception as e:
            print(f"[preload] ✗ {slug}: {e}")

threading.Thread(target=_preload, daemon=True).start()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fig_to_png(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120)
    plt.close(fig)
    buf.seek(0)
    return Response(buf.getvalue(), mimetype="image/png")


def _placeholder_png(label="Loading…"):
    import matplotlib
    matplotlib.use("Agg")
    fig, ax = plt.subplots(figsize=(6, 3))
    fig.patch.set_facecolor("#f5f5f5")
    ax.set_facecolor("#f5f5f5")
    ax.text(0.5, 0.55, "⏳", fontsize=36, ha="center", va="center", transform=ax.transAxes)
    ax.text(0.5, 0.28, label, fontsize=11, ha="center", va="center", color="#999", transform=ax.transAxes)
    ax.axis("off")
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=80)
    plt.close(fig)
    buf.seek(0)
    return Response(buf.getvalue(), mimetype="image/png", headers={"Cache-Control": "no-store"})


def safe_chart(slug, data_fn, plot_fn):
    with _ready_lock:
        is_ready = slug in _ready
    if not is_ready:
        return _placeholder_png("Fetching data…")
    try:
        df = data_fn()
        if df is None or len(df) == 0:
            return _placeholder_png("No data available")
        return fig_to_png(plot_fn(df))
    except Exception as e:
        print(f"[chart] {slug}: {e}")
        return _placeholder_png("Data unavailable")


@app.route("/status.json")
def status_json():
    with _ready_lock:
        ready_list = sorted(_ready)
    total = len(_FETCHERS)
    return jsonify({"ready": ready_list, "total": total, "done": len(ready_list) == total})

# ---------------------------------------------------------------------------
# Dashboard HTML
# ---------------------------------------------------------------------------

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Greece Statistics Dashboard</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    #load-banner {
      background: #fff8e1; border-bottom: 1px solid #ffe082;
      text-align: center; padding: .5rem 1rem;
      font-size: .82rem; color: #795548;
    }

    @keyframes shimmer {
      0%   { background-position: -800px 0; }
      100% { background-position:  800px 0; }
    }
    .skeleton {
      background: linear-gradient(90deg, #e8e8e8 25%, #f5f5f5 50%, #e8e8e8 75%);
      background-size: 800px 100%; animation: shimmer 1.4s infinite linear;
      border-radius: 4px; min-height: 220px; width: 100%; display: block;
    }
    .card img        { display: none; width: 100%; }
    .card img.loaded { display: block; }

    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: #f0f2f5; color: #1a1a2e;
    }
    header {
      background: linear-gradient(135deg, #003476 0%, #0d5cad 100%);
      color: white; padding: 1.4rem 2rem;
      display: flex; align-items: center; gap: 1rem;
      position: sticky; top: 0; z-index: 100;
      box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    }
    header .flag { font-size: 2rem; }
    header h1    { font-size: 1.3rem; font-weight: 600; }
    header p     { font-size: 0.78rem; opacity: .8; margin-top: 2px; }
    nav {
      background: white; border-bottom: 2px solid #e0e0e0;
      padding: 0 2rem; display: flex; overflow-x: auto;
    }
    nav a {
      display: inline-block; padding: .65rem 1.1rem;
      font-size: .82rem; font-weight: 500; color: #555;
      text-decoration: none; border-bottom: 3px solid transparent;
      white-space: nowrap; transition: color .15s, border-color .15s;
    }
    nav a:hover  { color: #003476; }
    nav a.active { color: #003476; border-bottom-color: #003476; }
    main { max-width: 1400px; margin: 0 auto; padding: 2rem 1.5rem 4rem; }
    .section { margin-bottom: 3rem; scroll-margin-top: 80px; }
    .section-header {
      display: flex; align-items: center; gap: .6rem;
      margin-bottom: 1rem; padding-bottom: .5rem;
      border-bottom: 2px solid #003476;
    }
    .section-header .icon { font-size: 1.3rem; }
    .section-header h2   { font-size: 1rem; font-weight: 700; color: #003476; text-transform: uppercase; letter-spacing: .6px; }
    .section-header p    { font-size: .78rem; color: #666; margin-left: auto; font-style: italic; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr)); gap: 1.25rem; }
    .card {
      background: white; border-radius: 10px;
      box-shadow: 0 1px 4px rgba(0,0,0,.08); overflow: hidden;
      transition: box-shadow .2s;
    }
    .card:hover { box-shadow: 0 4px 16px rgba(0,0,0,.14); }
    .card-footer { padding: .45rem .75rem; font-size: .72rem; color: #888; background: #fafafa; border-top: 1px solid #f0f0f0; }
    footer { text-align: center; padding: 1.5rem; font-size: .75rem; color: #999; border-top: 1px solid #e0e0e0; background: white; }
  </style>
</head>
<body>

<div id="load-banner">
  ⏳ Fetching data from Eurostat in the background — charts will appear as they load.
  <span id="load-counter"></span>
</div>

<header>
  <span class="flag">🇬🇷</span>
  <div>
    <h1>Greece Statistics Dashboard</h1>
    <p>Data sourced from Eurostat · Charts cached for 1 hour</p>
  </div>
</header>

<nav>
  <a href="#economy" class="active">💶 Economy</a>
  <a href="#labour">👷 Labour</a>
  <a href="#society">👨‍👩‍👧 Society</a>
  <a href="#environment">🌿 Environment</a>
  <a href="#crime">🚔 Crime</a>
  <a href="#migration">🌍 Migration</a>
</nav>

<main>

  <section class="section" id="economy">
    <div class="section-header"><span class="icon">💶</span><h2>Economy</h2><p>nama_10_gdp · gov_10dd_edpt1 · prc_hicp_manr</p></div>
    <div class="grid">
      <div class="card"><img data-src="/gdp.png" data-slug="gdp" alt="GDP"><div class="skeleton"></div><div class="card-footer">nama_10_gdp · CP_MEUR · B1GQ</div></div>
      <div class="card"><img data-src="/gdp_growth.png" data-slug="gdp_growth" alt="GDP Growth"><div class="skeleton"></div><div class="card-footer">nama_10_gdp · CLV10_MEUR · year-on-year % change</div></div>
      <div class="card"><img data-src="/inflation.png" data-slug="inflation" alt="Inflation"><div class="skeleton"></div><div class="card-footer">prc_hicp_manr · CP00 · monthly HICP</div></div>
      <div class="card"><img data-src="/gov_debt.png" data-slug="gov_debt" alt="Government Debt"><div class="skeleton"></div><div class="card-footer">gov_10dd_edpt1 · S13 · GD · % of GDP</div></div>
      <div class="card"><img data-src="/deficit.png" data-slug="deficit" alt="Deficit"><div class="skeleton"></div><div class="card-footer">gov_10dd_edpt1 · S13 · B9 · % of GDP</div></div>
    </div>
  </section>

  <section class="section" id="labour">
    <div class="section-header"><span class="icon">👷</span><h2>Labour Market</h2><p>une_rt_m · une_rt_a · lfsi_emp_a · edat_lfse_20</p></div>
    <div class="grid">
      <div class="card"><img data-src="/unemployment.png" data-slug="unemployment" alt="Unemployment"><div class="skeleton"></div><div class="card-footer">une_rt_m · seasonally adjusted · monthly</div></div>
      <div class="card"><img data-src="/youth_unemployment.png" data-slug="youth_unemployment" alt="Youth Unemployment"><div class="skeleton"></div><div class="card-footer">une_rt_a · 15–24 · annual</div></div>
      <div class="card"><img data-src="/employment_rate.png" data-slug="employment_rate" alt="Employment Rate"><div class="skeleton"></div><div class="card-footer">lfsi_emp_a · EMP_LFS · 20–64 · % of population</div></div>
      <div class="card"><img data-src="/neet_rate.png" data-slug="neet_rate" alt="NEET Rate"><div class="skeleton"></div><div class="card-footer">edat_lfse_20 · 15–29 · not in education, employment or training</div></div>
    </div>
  </section>

  <section class="section" id="society">
    <div class="section-header"><span class="icon">👨‍👩‍👧</span><h2>Society &amp; Demographics</h2><p>ilc_li02 · demo_frate · demo_gind</p></div>
    <div class="grid">
      <div class="card"><img data-src="/at_risk_of_poverty.png" data-slug="at_risk_of_poverty" alt="Poverty Rate"><div class="skeleton"></div><div class="card-footer">ilc_li02 · all ages · at-risk-of-poverty threshold</div></div>
      <div class="card"><img data-src="/fertility_rate.png" data-slug="fertility_rate" alt="Fertility Rate"><div class="skeleton"></div><div class="card-footer">demo_frate · total fertility rate</div></div>
      <div class="card"><img data-src="/population_change.png" data-slug="population_change" alt="Population Change"><div class="skeleton"></div><div class="card-footer">demo_gind · natural population growth</div></div>
    </div>
  </section>

  <section class="section" id="environment">
    <div class="section-header"><span class="icon">🌿</span><h2>Environment</h2><p>nrg_ind_ren</p></div>
    <div class="grid">
      <div class="card"><img data-src="/renewables_share.png" data-slug="renewables_share" alt="Renewables Share"><div class="skeleton"></div><div class="card-footer">nrg_ind_ren · REN · % of gross final energy consumption</div></div>
    </div>
  </section>

  <section class="section" id="crime">
    <div class="section-header"><span class="icon">🚔</span><h2>Crime</h2><p>crim_off_cat · crim_pris_pop</p></div>
    <div class="grid">
      <div class="card"><img data-src="/crime_by_category.png" data-slug="crime_by_category" alt="Offences by Category"><div class="skeleton"></div><div class="card-footer">crim_off_cat · homicide / robbery / theft / drug offences · NR</div></div>
      <div class="card"><img data-src="/prison_population.png" data-slug="prison_population" alt="Prison Population"><div class="skeleton"></div><div class="card-footer">crim_pris_pop · total prison population · NR</div></div>
    </div>
  </section>

  <section class="section" id="migration">
    <div class="section-header"><span class="icon">🌍</span><h2>Migration &amp; Expats</h2><p>migr_pop1ctz · migr_asyappctza</p></div>
    <div class="grid">
      <div class="card"><img data-src="/foreign_population_share.png" data-slug="foreign_population_share" alt="Foreign Share"><div class="skeleton"></div><div class="card-footer">migr_pop1ctz · foreign residents as % of total population</div></div>
      <div class="card"><img data-src="/asylum_applications.png" data-slug="asylum_applications" alt="Asylum Applications"><div class="skeleton"></div><div class="card-footer">migr_asyappctza · first-time applications · applicant=FRST</div></div>
    </div>
  </section>

</main>

<footer>
  Data source: <strong>Eurostat</strong> &nbsp;·&nbsp; All indicators refer to Greece (EL) &nbsp;·&nbsp; Flask + Matplotlib
</footer>

<script>
  // ── Scroll-spy nav ────────────────────────────────────────────
  const sections = document.querySelectorAll('.section');
  const navLinks = document.querySelectorAll('nav a');
  new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        navLinks.forEach(a => a.classList.remove('active'));
        const lnk = document.querySelector('nav a[href="#' + e.target.id + '"]');
        if (lnk) lnk.classList.add('active');
      }
    });
  }, { threshold: 0.25 }).observe && sections.forEach(s =>
    new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        navLinks.forEach(a => a.classList.remove('active'));
        const lnk = document.querySelector('nav a[href="#' + e.target.id + '"]');
        if (lnk) lnk.classList.add('active');
      });
    }, { threshold: 0.25 }).observe(s)
  );

  // ── Status-driven chart loader ────────────────────────────────
  // Each <img data-src="…" data-slug="…"> is shown only once its slug
  // appears in /status.json. We poll that endpoint instead of probing
  // image dimensions (which was unreliable).

  const allImgs = Array.from(document.querySelectorAll('img[data-src]'));
  const total   = allImgs.length;
  let   loaded  = 0;
  const pending = new Map(allImgs.map(img => [img.dataset.slug, img]));

  const banner  = document.getElementById('load-banner');
  const counter = document.getElementById('load-counter');

  function markLoaded(img) {
    img.src = img.dataset.src + '?t=' + Date.now();
    img.onload = () => {
      img.classList.add('loaded');
      // hide the skeleton sibling
      const sk = img.nextElementSibling;
      if (sk && sk.classList.contains('skeleton')) sk.style.display = 'none';
      loaded++;
      counter.textContent = ' (' + loaded + ' / ' + total + ' ready)';
      if (loaded === total) {
        banner.style.background  = '#e8f5e9';
        banner.style.borderColor = '#a5d6a7';
        banner.style.color       = '#2e7d32';
        banner.innerHTML = '✅ All ' + total + ' charts loaded.';
      }
    };
  }

  function poll() {
    if (pending.size === 0) return;          // all done
    fetch('/status.json')
      .then(r => r.json())
      .then(data => {
        data.ready.forEach(slug => {
          if (pending.has(slug)) {
            markLoaded(pending.get(slug));
            pending.delete(slug);
          }
        });
        if (pending.size > 0) setTimeout(poll, 2000);
      })
      .catch(() => setTimeout(poll, 3000));  // retry on network error
  }

  counter.textContent = ' (0 / ' + total + ' ready)';
  poll();
</script>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(DASHBOARD_HTML)

# Economy
@app.route("/gdp.png")
def gdp_png():              return safe_chart("gdp", fetch_greece_gdp, plot_gdp)

@app.route("/gdp_growth.png")
def gdp_growth_png():       return safe_chart("gdp_growth", fetch_greece_real_gdp_growth, plot_gdp_growth)

@app.route("/inflation.png")
def inflation_png():        return safe_chart("inflation", fetch_greece_inflation, plot_inflation)

@app.route("/gov_debt.png")
def gov_debt_png():         return safe_chart("gov_debt", fetch_greece_gov_debt, plot_gov_debt)

@app.route("/deficit.png")
def deficit_png():          return safe_chart("deficit", fetch_greece_deficit, plot_deficit)

# Labour
@app.route("/unemployment.png")
def unemployment_png():         return safe_chart("unemployment", fetch_greece_unemployment, plot_unemployment)

@app.route("/youth_unemployment.png")
def youth_unemployment_png():   return safe_chart("youth_unemployment", fetch_greece_youth_unemployment, plot_youth_unemployment)

@app.route("/employment_rate.png")
def employment_rate_png():      return safe_chart("employment_rate", fetch_greece_employment_rate, plot_employment_rate)

@app.route("/neet_rate.png")
def neet_rate_png():            return safe_chart("neet_rate", fetch_greece_neet_rate, plot_neet_rate)

# Society
@app.route("/at_risk_of_poverty.png")
def at_risk_of_poverty_png():   return safe_chart("at_risk_of_poverty", fetch_greece_poverty_rate, plot_at_risk_of_poverty)

@app.route("/fertility_rate.png")
def fertility_rate_png():       return safe_chart("fertility_rate", fetch_greece_fertility_rate, plot_fertility_rate)

@app.route("/population_change.png")
def population_change_png():    return safe_chart("population_change", fetch_greece_population_change, plot_population_change)

# Environment
@app.route("/renewables_share.png")
def renewables_share_png():     return safe_chart("renewables_share", fetch_greece_renewables_share, plot_renewables_share)

# Crime
@app.route("/crime_by_category.png")
def crime_by_category_png():    return safe_chart("crime_by_category", fetch_greece_crime_by_category, plot_crime_by_category)

@app.route("/prison_population.png")
def prison_population_png():    return safe_chart("prison_population", fetch_greece_prison_population, plot_prison_population)

# Migration
@app.route("/foreign_population_share.png")
def foreign_pop_share_png():    return safe_chart("foreign_population_share", fetch_greece_foreign_population_share, plot_foreign_population_share)

@app.route("/asylum_applications.png")
def asylum_applications_png():  return safe_chart("asylum_applications", fetch_greece_asylum_applications, plot_asylum_applications)

if __name__ == "__main__":
    app.run(debug=False, port=5001, use_reloader=False)

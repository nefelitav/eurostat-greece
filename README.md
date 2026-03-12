# Greece Statistics Dashboard 🇬🇷

A Flask + Matplotlib dashboard that pulls **live data from Eurostat** and renders it as a clean, sectioned web page with trend annotations for every indicator.

![img.png](img.png)

---

## Indicators covered

| Section | Indicator | Eurostat dataset |
|---|---|---|
| **💶 Economy** | Annual GDP (current prices) | `nama_10_gdp` |
| | Real GDP growth (YoY %) | `nama_10_gdp` |
| | Inflation rate (HICP) | `prc_hicp_manr` |
| | Mean gross wages | `earn_eses_agt` |
| | Government debt (% GDP) | `gov_10dd_edpt1` |
| | Government deficit / surplus (% GDP) | `gov_10dd_edpt1` |
| **👷 Labour** | Monthly unemployment rate (SA) | `une_rt_m` |
| | Youth unemployment (15–24) | `une_rt_a` |
| | Employment rate (20–64) | `lfsi_emp_a` |
| | NEET rate (15–29) | `edat_lfse_20` |
| | Labour productivity (index 2010=100) | `nama_10_lp_ulc` |
| **👨‍👩‍👧 Society** | At-risk-of-poverty rate | `ilc_li02` |
| | Fertility rate | `demo_frate` |
| | Natural population change | `demo_gind` |
| **🌿 Environment** | Greenhouse gas emissions | `env_air_gge` |
| | Energy import dependency | `nrg_ind_id` |
| | Renewables share in final energy | `nrg_ind_ren` |
| **🚔 Crime** | Total recorded criminal offences | `crim_off_cat` |
| | Offences by category (homicide, robbery, theft, drugs) | `crim_off_cat` |
| | Prison population | `crim_pris_pop` |
| **🌍 Migration & Expats** | Foreign residents (stock) | `migr_pop1ctz` |
| | Foreign residents as % of population | `migr_pop1ctz` |
| | Annual immigration inflows | `migr_imm1ctz` |
| | Annual emigration outflows (brain drain) | `migr_emi1ctz` |
| | First-time asylum applications | `migr_asyappctza` |

---

## Features

- **Grouped sections** — sticky header nav jumps directly to Economy, Labour, Society, Environment, Crime, or Migration
- **Delta badge on every chart** — shows the latest value and change vs the previous period in green/red
- **Reusable helpers** in `data_fetch.py` (`_melt_annual`, `_melt_monthly`, `_geo_col`) and `plotting.py` (`plot_line`, `plot_bar`, `plot_multi_line`) — adding a new indicator is ~5 lines
- **1-hour server-side caching** via Flask-Caching — Eurostat is only queried once per restart
- Each card shows the **Eurostat dataset code** so you can verify the source at a glance

---

## Run locally

**Step 1 — create and activate a virtual environment** (one-time setup):
```bash
cd eurostat-greece
python3 -m venv .venv
source .venv/bin/activate
```

**Step 2 — install dependencies:**
```bash
pip install flask flask-caching matplotlib pandas eurostat
```

**Step 3 — start the server:**
```bash
FLASK_DEBUG=0 python3 main.py
```

Then open **[http://127.0.0.1:5001](http://127.0.0.1:5001)** in your browser.

> **Note on macOS:** port 5000 is taken by AirPlay Receiver — the app intentionally runs on **port 5001**.

> **First load:** the page appears instantly with skeleton placeholders. Charts pop in one by one as Eurostat data downloads in the background (~30–90 s total for all 25 charts). After that everything is cached for 1 hour and reloads instantly.

### Subsequent runs (venv already set up)
```bash
source .venv/bin/activate
FLASK_DEBUG=0 python3 main.py
```

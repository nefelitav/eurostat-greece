# Greece Statistics Dashboard 🇬🇷

A Flask + Matplotlib dashboard that pulls **live data from Eurostat** and renders it as a web page.

![Dashboard screenshot 1](img.png)
![Dashboard screenshot 2](img_1.png)
![Dashboard screenshot 3](img_2.png)
![Dashboard screenshot 4](img_3.png)

---

## Indicators covered

| Section | Indicator | Eurostat dataset |
|---|---|---|
| **💶 Economy** | Annual GDP (current prices) | `nama_10_gdp` |
| | Real GDP growth (YoY %) | `nama_10_gdp` |
| | Inflation rate (HICP) | `prc_hicp_manr` |
| | Government debt (% of GDP) | `gov_10dd_edpt1` |
| | Government deficit / surplus (% of GDP) | `gov_10dd_edpt1` |
| **👷 Labour** | Monthly unemployment rate (SA) | `une_rt_m` |
| | Youth unemployment rate (15–24) | `une_rt_a` |
| | Employment rate (20–64) | `lfsi_emp_a` |
| | NEET rate (15–29) | `edat_lfse_20` |
| **👨‍👩‍👧 Society** | At-risk-of-poverty rate | `ilc_li02` |
| | Fertility rate | `demo_frate` |
| | Natural population change | `demo_gind` |
| **🌿 Environment** | Renewables share in final energy | `nrg_ind_ren` |
| **🚔 Crime** | Offences by category (homicide, robbery, theft, drugs) | `crim_off_cat` |
| | Prison population | `crim_pris_pop` |
| **🌍 Migration** | Foreign residents as % of population | `migr_pop1ctz` |
| | First-time asylum applications | `migr_asyappctza` |

---


## Run locally

**First time: create a virtual environment and install dependencies:**
```bash
cd eurostat-greece
python3 -m venv .venv
source .venv/bin/activate
pip install flask flask-caching matplotlib pandas eurostat
```

**Start the server:**
```bash
FLASK_DEBUG=0 python3 main.py
```

Open **[http://127.0.0.1:5001](http://127.0.0.1:5001)** in your browser.

> Charts load in the background (~1–2 min on first run). After that everything is instant from the cache.

**Subsequent runs:**
```bash
source .venv/bin/activate
FLASK_DEBUG=0 python3 main.py
```

# Zalando SE — ESG Performance Dashboard (SAM 503 · Lab 4)

Interactive Streamlit dashboard tracking Zalando's carbon, energy, water, waste, social and governance
performance over **FY2016–FY2025**, built for sustainability analysts who brief the Sustainability Director
and the Board.

## Student inputs (Lab 4 brief)
| Item | Input |
|---|---|
| Company | Zalando SE (Berlin; incl. ABOUT YOU from 11 Jul 2025) |
| Industry | Online fashion & lifestyle retail (NACE G) |
| Audience | Sustainability analysts monitoring and reporting ESG metrics |
| Purpose | Inform the Sustainability Director → Board on findings, risks and progress |
| Time horizon | 10 years (FY2016–FY2025) + target pathway to 2033 |
| Key questions | On track for SBTs? Growth decoupled from emissions? Hotspots? Circular operations? Safe & fair workplace? Data reliable? |
| Environmental | Scope 1, 2 (MB/LB), 3 by category; GHG intensity; energy & mix; renewable share; water; waste & disposal routes |
| Social | Headcount, women in workforce/top mgmt, pay gap (unadjusted/adjusted), turnover, accident rates |
| Governance | Board size & independence, women on board, pay ratio, ESG in exec pay, corruption incidents, assurance |
| Targets | SBT near-term 2033 (S1+2 −55%, S3 cat.1+4 −33% vs 2022), net-zero 2040/2050, RE100, supplier SBTs |
| Visuals | KPI cards, line/bar trends with methodology-break band, category bars, target progress bars, pathway |

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run in Google Colab
Open `notebooks/zalando_esg_exploration.ipynb` (data exploration) — the last cell launches the app via a tunnel.

## Deploy (Streamlit Community Cloud)
1. Push this folder to a public GitHub repo (e.g. `sam_503_esg-lab`).
2. Go to share.streamlit.io → **New app** → pick the repo, branch `main`, file `app.py` → **Deploy**.

## Repository structure
```
app.py                      Streamlit dashboard
requirements.txt
.streamlit/config.toml      theme
data/zalando_timeseries.csv          10-year series (GHG, energy, waste, water, financials, people)
data/zalando_scope3_categories.csv   Scope 3 by GHG Protocol category, 2024–2025
data/zalando_energy_mix.csv          energy by source, 2024–2025
data/zalando_waste.csv               waste by treatment route, 2024–2025
data/zalando_targets.csv             SBT and other targets with 2025 progress
data/zalando_social_governance.csv   S & G KPIs, 2024–2025
notebooks/zalando_esg_exploration.ipynb
```

## Important data caveats
- **Methodology break:** FY2017–2023 GHG figures come from Sustainability Progress Reports (legacy method,
  operational control). FY2024–2025 come from the ESRS sustainability statement in AR2025 (financial +
  operational control) and include a **−39.3% Scope 3 restatement** for 2024. Do not read the 2023→2024 drop
  as a real reduction.
- **SBT boundary ≠ ESRS boundary:** targets use operational control and exclude ABOUT YOU.
- FY2016 has no published GHG inventory. Revenue/EBIT/employees FY2016–2023 were transcribed from annual
  reports — verify before external use.

## Sources
- Zalando SE Annual Report 2025 (sustainability statement with KPMG limited assurance).
- Zalando SE Sustainability Progress Reports 2020, 2022, 2023 — corporate.zalando.com.

# Data sources — live check + refresh notes (branch `refresh-mn-wa-ca-or-ny`)

Focus states for this refresh: MN, WA, CA, OR, NY. Where the upstream file is
national, all states were extended (same effort, keeps state-comparison charts coherent).

## Refreshed in this branch

### 1. `raw/us_emissions_2000_2018.csv` → 1990–2022 (was 1990–2018)

- Old source (per `src/constants/source-citations.js`): WRI Climate Watch U.S.
  States GHG 1990–2018, Mar 2021,
  `https://datasets.wri.org/dataset/climate-watch-states-greenhouse-gas-emissions`
  — **STALE and effectively dead: that URL returns HTTP 404.**
- New source: EPA *Inventory of U.S. GHG Emissions and Sinks by State 1990–2022*,
  consolidated workbook `AllStateGHGData90-22_v082924.xlsx` (1990–2022, posted Sep 2024):
  `https://www.epa.gov/system/files/other-files/2024-09/allstateghgdata90-22_v082924.zip`
  (report page: `https://www.epa.gov/ghgemissions/methodology-report-inventory-us-greenhouse-gas-emissions-and-sinks-state-1990-2022`).
  EPA publishes the national Inventory each April with a ~2-year lag; the state
  disaggregation follows later in the year. Facility-level cross-check: EPA FLIGHT
  (`https://ghgdata.epa.gov/ghgp/main.do`), current through last completed calendar year.
- Method: kept all 1990–2018 WRI rows byte-identical, appended EPA-mapped 2019–2022
  rows (208 rows = 52 states + DC + national total × 4 years) in the same schema.
  Non-CO2 rows in the EPA workbook are already Tg CO2e. Column mapping:
  `emission_sub_{electric,residential,commercial}` = end-use fuel-combustion CO2;
  `emission_sub_industrial` = Industry fuel-combustion CO2 + non-energy use + mobile
  combustion; `emission_sub_transportation` = Transportation fuel-combustion CO2 +
  mobile combustion + non-energy use; `emission_sub_fugitive` = coal mining, oil/gas
  systems, abandoned wells/mines; `emission_by_waste` = landfills, wastewater,
  composting, digestion, waste incineration; `emission_by_agriculture` = Agriculture
  total minus farm fuel-combustion CO2; `emission_by_industrial` = Industry remainder
  (partition); `emission_by_energy` = all non-LULUCF CO2; gas totals summed;
  `emission_by_forestry` = LULUCF net total. `state_gdp`, `population`,
  `total_energy_use`, `emission_by_bunker_fuel` are blank for 2019–2022 (not in the
  EPA state file; frontend does not consume them).
- **Methodology break at 2018→2019 — FIXED by overlap-ratio splicing**
  (WRI/SIT basis 1990–2018 vs official EPA state disaggregation 2019–2022).
  Pre-fix overlap-year (2018) deltas, EPA-mapped vs WRI:

  | state | electric | residential | commercial | industrial | transport |
  |---|---|---|---|---|---|
  | CA | −0.1% | −1.4% | −5.0% | −1.0% | −13.0% |
  | MN | +1.5% | −2.4% | −3.9% | −18.3% | +3.7% |
  | WA | +0.7% | −4.9% | −5.0% | −5.2% | −19.6% |
  | OR | +0.2% | −7.9% | −5.3% | −6.0% | −1.5% |
  | NY | −0.5% | −4.1% | −3.5% | −6.1% | −0.8% |

  Fix (`data/scripts/splice_emissions_2018_2019.py`, run:
  `python scripts/splice_emissions_2018_2019.py <AllStateGHGData90-22 workbook>
  raw/us_emissions_2000_2018.csv splice_factors_2018.csv`, then regenerate
  `final/emissions/emissions.json` via `get_emissions.py`): standard
  single-overlap-year ratio splicing — 2018 is the only shared year (WRI ends
  2018; the EPA workbook covers 1990–2022, so no 2018–2019 mean is possible).
  Per state × column, `r = EPA_basis(2018) / WRI(2018)`; every pre-2019 value
  is multiplied by `r` (rounded to 7dp, the finest WRI precision).
  `EPA_basis(2018)` is recomputed from the workbook with the same mapping as
  the 2019–2022 append — and that mapping is trusted only because it
  reproduces **every** appended 2019–2022 state row (51 geos × 4 yrs × 17
  columns) to a max abs err of 5e-5. Post-2019 state rows are never touched.
  Usability rule: both sides nonzero with the same sign, else the series is
  left untouched and flagged — never fabricated.
- Splice factors (EPA2018/WRI2018; full 884-row table in
  `data/splice_factors_2018.csv`, focus states below):

  | state | electric | residential | commercial | industrial_sub | transport | fugitive | waste | agri | industrial_by |
  |---|---|---|---|---|---|---|---|---|---|
  | CA | 0.9987 | 0.9864 | 0.9495 | 0.9896 | 0.8700 | 2.5631 | 0.8332 | 1.0870 | 0.2810 |
  | MN | 1.0149 | 0.9770 | 0.9600 | 0.8170 | 1.0372 | — (WRI 0) | 1.0099 | 1.0245 | 4.1639 |
  | WA | 1.0071 | 0.9503 | 0.9511 | 0.9481 | 0.8042 | — (WRI 0) | 1.2797 | 1.1611 | 0.3129 |
  | OR | 1.0021 | 0.9220 | 0.9469 | 0.9397 | 0.9845 | 148.8801 | 1.4745 | 1.0827 | 0.2869 |
  | NY | 0.9954 | 0.9586 | 0.9652 | 0.9393 | 0.9919 | 6.6393 | 0.6352 | 1.0696 | 0.3445 |

  (OR fugitive: valid overlap, both sides small-positive — WRI 0.0043 vs EPA
  0.64; the flat WRI shape is preserved, only rebased. MN `industrial_by`
  4.16: small-partition residual, same-sign, kept.)
- Result: 838 state-series spliced; the old level breaks are gone —
  CA transport −12.2% → +0.9%, WA transport −17.6% → +2.4%,
  MN industrial-sub −15.9% → +3.0% (2018→2019, spliced basis).
- Left untouched (29 state-series, all flagged in `splice_factors_2018.csv`):
  - `emission_sub_fugitive` with WRI 2018 = 0 (SIT reported no fugitive):
    CT, DE, GA, HI, ID, IA, ME, MA, **MN**, NH, NJ, NC, RI, SC, VT, **WA**,
    WI + DC (also DC `emission_by_agriculture` and `emission_sub_electric`,
    both ~0 — DC has no power plants). Residual effect: a small known step
    where fugitive appears in 2019 (MN +1.35 on a ~60 bucket ≈ +2.2pp of the
    2018→2019 move; WA +0.81 on ~26 ≈ +3.1pp) — documented noise, not
    fabricated history.
  - `emission_by_forestry` sign flips (sink↔source classification differs):
    AZ, HI, NV, SD, UT. `emission_by_industrial` sign flips (near-zero
    partition residuals): ID, NE, ND, SD.
  - `emission_by_bunker_fuel`, `state_gdp`, `population`, `total_energy_use`:
    no EPA mapping — untouched all years (still WRI pre-2019, blank 2019+).
- Remaining 2018→2019 moves are EPA-own-series interannual changes on one
  methodology, within each series' historical volatility — e.g. electric:
  CA −7.6% (EPA YoY history: −17.4%, −9.7%, +8.2%), NY −12.2% (−20.3%,
  +10.8%), MN −14.5% (coal retirements; then −16.0%), OR +25.8% and WA +35.0%
  (small hydro-dominated bases ~8–10 MMT; 2019 was a low-water year, and both
  snap back in 2020: −15.5%, −19.7%). Frontend-bucket spot check:

  | state | dirty_power | buildings | transportation | dumps/farms/industrial/other |
  |---|---|---|---|---|
  | CA | −7.6% | +7.9% | +0.9% | −0.2% |
  | MN | −14.5% | +3.3% | −0.1% | −2.4% |
  | WA | +35.0% | +5.7% | +2.4% | +4.6% (∼3.1pp is the flagged fugitive gap) |
  | OR | +25.8% | +9.6% | −3.2% | +0.6% |
  | NY | −12.2% | −0.9% | +1.2% | −3.1% |
- **National-row repair (same commit).** The EPA workbook's `National` geo
  carries only LULUCF rows, so the 2019–2022 append had left every
  `United States` sector/total at **0** — while the frontend's US views read
  `data["united_states"]` (`src/components/getLatestEmissions.js`), i.e. the
  About-page US chart showed 0 for recent years. The national row is now the
  column-wise sum of the states for **every** year (exactly what it was in
  the WRI era, verified to 4dp). Post-2019 *state* values stay byte-identical;
  only the national row changed there (0 → sums). National LULUCF is likewise
  the sum of state LULUCF — note it differs from EPA's headline national
  LULUCF total (state-level LULUCF does not sum to the national inventory).
- About-page citation follow-up (below) is done: `src/constants/
  source-citations.js` now cites the EPA Inventory (Sep 2024) for emissions
  and EIA Historical State Data + SEDS (Oct 2025) for generation, with the
  WRI series kept only as a historical-provenance note.

### 2. `raw/us_electric_generation_2001_20.csv` → 2001–2024 (was 2001–2020)

- Old source: EIA Open Data API v1 (`https://www.eia.gov/opendata/v1/qb.php?category=1`),
  Apr 2022 — **STALE: API v1 is retired** (replaced by keyed API v2).
- New sources (both live, no key needed):
  - `annual_generation_state.xls` — "1990–2024 Net Generation by State by Type of
    Producer by Energy Source (EIA-906/920/923)", final 2024 data released Oct 16, 2025:
    `https://www.eia.gov/electricity/data/state/annual_generation_state.xls`
    (index: `https://www.eia.gov/electricity/data/state/`).
  - SEDS consumption in physical units, `use_all_phy.csv` — 1960–2024 final, released
    Jun 2026: `https://www.eia.gov/state/seds/sep_use/total/csv/use_all_phy.csv`
    — small-scale PV (GWh) = `SOTGP` − `SOEGP` (million kWh == GWh numerically).
- Method: kept 2001–2020 rows byte-identical, appended 2021–2024 (204 rows =
  51 states × 4 years). `all_solar` = utility solar + small-scale PV;
  `other_renewables` = wind + utility solar + geothermal + other biomass + wood
  (replicates the file's own construction, verified on 2020 rows);
  `petro_coke` = 0 for new years (no coke split in the annual file; all five focus
  states had 0 coke in 2019–2020); `utility_scale_photovoltaic/_thermal` blank
  (no thermal/PV split in the annual file).
- Validation: 2020 overlap EIA-file vs raw matches exactly for coal, gas, petroleum,
  nuclear, hydro, wind, utility solar (e.g. CA gas 92046.68 GWh); SEDS small-scale
  within ~1% of the API-v1 values (CA 17620 vs 17407 GWh — SEDS includes a small
  solar-thermal share). EIA has since revised some 2020 figures by a few GWh
  (e.g. wood fuels); old rows were intentionally left untouched.

## Checked, not refreshed (stale — follow-ups)

### 3. `raw/power_plants_and_communities.csv` — data year 2019, STALE
- Upstream is live: EPA eGRID2023 (data year 2023, released Jan 15 2025),
  `https://www.epa.gov/egrid` (detailed data: `https://www.epa.gov/egrid/detailed-data`);
  EJScreen community data (`https://www.epa.gov/ejscreen`) also live
  (raw file carries 2018-vintage ACS/EJScreen columns).
- Not refreshed here: the raw file is a renamed eGRID-plant-file × EJScreen join and
  the join cannot be reproduced from either download alone; row-splicing 2023 plants
  into a 2019 schema risks column drift. eGRID plant file + EJScreen re-join is the
  natural next PR.

### 4. `raw/state_renewable_gen_targets.csv` — derived file, no direct upstream
- DSIRE (`https://www.dsireusa.org/`, N.C. Clean Energy Technology Center, live) has
  no CSV equivalent: the raw file is project-computed ("renewable GWh needed" per
  state, added Apr 2022). Refresh = recompute by documented method, out of scope here.

### 5. `raw/buildings_data.csv` — 2021 vintage, STALE
- Microsoft USBuildingFootprints live: `https://github.com/microsoft/USBuildingFootprints`.
- NREL inputs were the 2021 ResStock/ComStock end-use-load-profile releases
  (`https://data.openei.org/s3_viewer?bucket=oedi-data-lake&prefix=nrel-pds-building-stock%2Fend-use-load-profiles-for-us-building-stock%2F2021%2F...`);
  current releases are ResStock 2024.2 / ComStock 2024 (multi-TB, not re-derivable here).
  Unchanged.

### 6. `raw/vehicles_data.csv` — 2017 FHWA + ~2019 EV, STALE
- FHWA Highway Statistics Table MV-1 is live; latest is 2024 (Jan 2026):
  `https://www.fhwa.dot.gov/policyinformation/statistics/2024/mv1.cfm`.
- `EV_Registration` has no FHWA equivalent; closest live series is DOE AFDC
  "Electric Vehicle Registrations by State" (Experian-sourced, latest Dec-2023 vintage,
  updated Sep 2024): `https://afdc.energy.gov/data/10962`.
  Full MV-1 + AFDC rebuild is the natural next PR; untouched here.

## Pipeline compatibility
- `data/scripts/utils.py`: `DataFrame.applymap` → `.map` (applymap was removed in
  pandas 3.x; repo pins pandas 1.1.3 from the Docker era) and sorted state order so
  regenerated JSON is deterministic. Nothing else in the scripts changed.
- Verified: `get_emissions.py` + `get_generation.py` exit 0. After the
  2018-overlap splice + national repair: all 2019–2022 *state* emission JSON
  entries are byte-identical to the pre-splice refresh (only pre-2019 entries
  rescaled and the `united_states` entries repaired from 0 to state sums);
  CSV CRLF preserved without BOM (matching the checked-in file),
  non-spliced columns (`state_gdp`, `population`,
  `total_energy_use`, `emission_by_bunker_fuel`) cell-identical. Generation
  JSON untouched by this fix (all 1020 pre-existing entries still
  byte-identical to `main`).
- NOTE for Windows shells: redirect with `>` writes UTF-16; write the JSON via
  `python -c` + `subprocess` (UTF-8) as done for this refresh.

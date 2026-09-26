"""Refresh raw/state_renewable_gen_targets.csv against the latest generation year.

Usage:
    python scripts/refresh_target_generation.py <us_electric_generation.csv> \
        <targets.csv> <out.csv>

What the file means (upstream PR chihacknight/decarbonize-my-state#61): each
row is the solar / wind generation a state needs to decarbonize by 2050 —
enough clean electricity to cover (a) all generation currently produced from
fossil fuels, plus the added electric load of (b) electrifying all road
vehicles and (c) electrifying fossil-fueled building equipment.
`current_*`/`perc_*` measure progress toward that fixed target.

REVERSE-ENGINEERED DERIVATION (documented Sep 2026)
--------------------------------------------------
The Apr-2022 file (commit 66bda971) carried the inputs, later dropped:

    total_rnw_gen_needed = rnw_generation_fossil_fuels      # 2020 fossil GWh
                         + rnw_generation_transportation  # electrified-vehicle load
                         + rnw_generation_buildings       # electrified-buildings load

The fossil column reproduces this repo's own 2020 generation data exactly
(coal + natural_gas + other_gas + petro_liquids + petro_coke; max deviation
<0.01% across all 49 covered states). The transportation (~6-10 MWh/registered
vehicle) and buildings (~2-21 MWh/building) columns were computed in a
spreadsheet that was never committed; their exact coefficients are
unrecoverable, so they are carried forward as fixed scenario load.

The May-2022 file (commit f5fcd2e2) dropped the input columns and the ~5%
"other renewables" share: solar + wind ≈ 0.945 × needed for 49 states — a
2021-vintage recompute of the same model. Alaska and Hawaii were added by
hand ("whatever their current electric load from fossil fuels was for 2021",
PR #89) with a fixed 57.9/42.1 solar/wind split. Every state's solar share of
(solar+wind) is stable across both vintages (median drift 0.2 points), so
the split encodes per-state resource judgment we preserve verbatim.

Recompute rule (this refresh)
-----------------------------
Only the fossil component is re-based to the latest year; the electrified
transport/buildings loads stay at their Apr-2022 scenario values (they are
future demand, not generation history):

    needed_now = needed_2022 - fossil_2020 + fossil_latest
    total_gen_by_solar = needed_now × solar_share_state
    total_gen_by_wind  = needed_now × (1 - solar_share_state)

where solar_share_state is the state's May-2022 solar share of (solar+wind).
For AK/HI (needed ≈ fossil load only), needed_now = fossil_latest and the
solar share is the needed-weighted national average of the other 49 states
(0.513), since their original 0.579 split was an unexplained constant.

`current_*` = latest-year all_solar / wind (GWh).
`perc_*_target` = current/target*100, integer-rounded.
"""

import sys

import pandas as pd

FOSSIL_COLS = ["coal", "natural_gas", "other_gas", "petro_liquids", "petro_coke"]
BASELINE_YEAR = 2020  # vintage of the original total_rnw_gen_needed fossil input
# Solar+wind covered 94.5% of total_rnw_gen_needed in the May-2022 file
# (the ~5% "other renewables" share was dropped when the column was removed).
SOLAR_WIND_SHARE_OF_NEED = 0.945

# April-2022 total_rnw_gen_needed (GWh), commit 66bda971. This is the scenario
# size: fossil generation to replace + electrified transport + buildings.
NEEDED_2022 = {
    "AL": 132042.96, "AZ": 126944.01, "AR": 67135.58, "CA": 428592.58,
    "CO": 117713.46, "CT": 66499.63, "DC": 5696.27, "DE": 16093.38,
    "FL": 356889.47, "GA": 193209.26, "ID": 27917.91, "IL": 208912.78,
    "IN": 174905.71, "IA": 66265.99, "KS": 55494.04, "KY": 113779.60,
    "LA": 115268.67, "ME": 23733.34, "MD": 83271.97, "MA": 95958.16,
    "MI": 202578.14, "MN": 114487.92, "MS": 90265.40, "MO": 141008.74,
    "MT": 25618.47, "NE": 48003.57, "NV": 56752.59, "NH": 22892.47,
    "NJ": 126610.90, "NM": 52092.37, "NY": 261989.41, "NC": 176657.64,
    "ND": 38486.77, "OH": 242528.16, "OK": 98786.82, "OR": 70792.02,
    "PA": 292321.18, "RI": 19828.27, "SC": 88821.60, "SD": 16294.75,
    "TN": 107693.98, "TX": 590942.55, "UT": 73417.42, "VT": 10271.46,
    "VA": 165286.26, "WA": 107633.38, "WV": 74555.49, "WI": 133362.36,
    "WY": 45815.98,
}
# States added May-2022 whose original target was fossil-load-only (PR #89).
FOSSIL_ONLY_STATES = ["AK", "HI"]


if __name__ == "__main__":
    gen_path, tgt_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

    gen = pd.read_csv(gen_path)
    fossil_by_year = gen.set_index(["state", "year"])[FOSSIL_COLS].sum(axis=1)
    baseline_year = max(y for y in gen["year"].unique() if y <= BASELINE_YEAR)
    latest_year = int(gen["year"].max())
    fossil_base = fossil_by_year.xs(baseline_year, level="year")
    latest = gen[gen["year"] == latest_year].set_index("state")
    fossil_latest = latest[FOSSIL_COLS].sum(axis=1)

    tgt = pd.read_csv(tgt_path)
    tgt = tgt.drop(columns=[c for c in tgt.columns if c.startswith("Unnamed")])

    # --- recompute targets -------------------------------------------------
    needed_2022 = pd.Series(NEEDED_2022)
    needed_now = needed_2022 - fossil_base + fossil_latest
    # AK/HI: target proxies the full fossil load (no transport/buildings addon)
    for st in FOSSIL_ONLY_STATES:
        needed_now[st] = fossil_latest[st]

    # solar share of (solar+wind): preserve each state's existing split.
    tg = tgt.set_index("state")
    solar_share = tg["total_gen_by_solar"] / (tg["total_gen_by_solar"] + tg["total_gen_by_wind"])
    national_solar_share = (
        (needed_now * solar_share).drop(FOSSIL_ONLY_STATES, errors="ignore").sum()
        / needed_now.drop(FOSSIL_ONLY_STATES, errors="ignore").sum()
    )
    for st in FOSSIL_ONLY_STATES:
        solar_share[st] = national_solar_share

    tgt["total_gen_by_solar"] = (
        tgt["state"].map(needed_now * solar_share).round(0).astype("Int64")
    )
    tgt["total_gen_by_wind"] = (
        tgt["state"].map(needed_now * (1 - solar_share)).round(0).astype("Int64")
    )

    # --- refresh the "current" side ----------------------------------------
    tgt["current_solar"] = (
        tgt["state"].map(latest["all_solar"]).round(0).astype("Int64")
    )
    tgt["current_wind"] = (
        tgt["state"].map(latest["wind"]).round(0).astype("Int64")
    )
    tgt["perc_solar_target"] = (
        (tgt["current_solar"] / tgt["total_gen_by_solar"] * 100)
        .round(0).astype("Int64")
    )
    tgt["perc_wind_target"] = (
        (tgt["current_wind"] / tgt["total_gen_by_wind"] * 100)
        .round(0).astype("Int64")
    )

    tgt.to_csv(out_path, index=False)
    print(
        f"wrote {out_path}: {len(tgt)} rows, current basis {latest_year}, "
        f"target fossil basis {baseline_year}->{latest_year}"
    )

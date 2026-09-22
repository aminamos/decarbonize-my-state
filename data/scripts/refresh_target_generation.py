"""Refresh current_* / perc_* columns in raw/state_renewable_gen_targets.csv.

Usage:
    python scripts/refresh_target_generation.py <us_electric_generation.csv> \
        <targets.csv> <out.csv>

Method: `current_solar`/`current_wind` are the state's latest-year all_solar /
wind generation (GWh) — the original file matches the 2021 generation data to
within ~2% (it was built Apr 2022 against then-preliminary EIA API v1 values).
`perc_*_target` = current/target*100, rounded to the nearest integer (verified
against the original file).

`total_gen_by_solar` / `total_gen_by_wind` are fixed scenario targets whose
original derivation is undocumented (added Apr 2022; see DATA_SOURCES.md).
They are carried through unchanged — the file measures progress toward a
fixed target, so only the "current" side needs refreshing.
"""

import sys

import pandas as pd


if __name__ == "__main__":
    gen_path, tgt_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

    gen = pd.read_csv(gen_path)
    latest = gen[gen["year"] == gen["year"].max()].set_index("state")
    tgt = pd.read_csv(tgt_path)
    if "Unnamed: 7" in tgt.columns:
        tgt = tgt.drop(columns=["Unnamed: 7"])

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
    print(f"wrote {out_path}: {len(tgt)} rows, basis year {int(gen['year'].max())}")

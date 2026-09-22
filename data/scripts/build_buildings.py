"""Rebuild raw/buildings_data.csv from current upstream sources.

Usage:
    python scripts/build_buildings.py <microsoft_footprints.csv> \
        <resstock_baseline.parquet-or-url> <comstock_agg_dir> <out.csv>

Inputs:
    microsoft_footprints.csv  unchanged repo input (Microsoft
        USBuildingFootprints, 2018-2021 era — still the latest release)
    resstock baseline         ResStock 2024.2 amy2018_release_2
        metadata/baseline.parquet (oedi-data-lake S3). A URL works if pyarrow
        + fsspec are installed — only the needed columns are fetched.
    comstock_agg_dir          directory of ComStock 2024 amy2018_release_2
        per-state `*_baseline_agg_basic.csv.gz` files from
        metadata_and_annual_results_aggregates/by_state/basic/csv/

Method (matches the 2021 derivation in summarize_buidlings.py, with NREL
`weight` used instead of raw sample-row counts since the 2024 files carry
explicit building weights):
    res-count            = sum(weight) per state (ResStock)
    com-count            = sum(weight) per state (ComStock baseline)
    *-non-ele-heating    = weight where in.heating_fuel != Electricity
    *-non-ele-water-heating = weight where water-heater fuel != Electricity
    res-non-ele-range    = weight where in.cooking_range not like "Electric*"
    pct*                 = share of that stock's weighted buildings
    pctRes / pctCom      = res / com share of NREL-weighted buildings
    weightedRes          = (5*heat + 2*water + 1*range) / 8
    weightedCom          = (5*heat + 2*water) / 7
    weightedFossilBuildingsPct = pctRes*weightedRes + pctCom*weightedCom
    weightedEleBuildingsPct    = 100 - weightedFossilBuildingsPct
    (end-use weights 5:2:1 res / 5:2 com reverse-engineered from the 2021 file)

AK/HI have no NREL coverage -> zeroed (same as 2021 file). `united_states`
keeps the Microsoft total with zeroed NREL columns, as before.
"""

import glob
import os
import sys

import pandas as pd

STATE_NAMES = {
    "AL": "Alabama", "AR": "Arkansas", "AZ": "Arizona", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DC": "District of Columbia",
    "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "IA": "Iowa",
    "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "MA": "Massachusetts",
    "MD": "Maryland", "ME": "Maine", "MI": "Michigan", "MN": "Minnesota",
    "MO": "Missouri", "MS": "Mississippi", "MT": "Montana",
    "NC": "North Carolina", "ND": "North Dakota", "NE": "Nebraska",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
    "NV": "Nevada", "NY": "New York", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island",
    "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee",
    "TX": "Texas", "UT": "Utah", "VA": "Virginia", "VT": "Vermont",
    "WA": "Washington", "WI": "Wisconsin", "WV": "West Virginia",
    "WY": "Wyoming",
}

RES_COLS = [
    "in.state", "in.heating_fuel", "in.water_heater_fuel",
    "in.cooking_range", "weight",
]


def resstock_counts(parquet_or_url):
    df = pd.read_parquet(parquet_or_url, columns=RES_COLS)
    g = df.groupby("in.state")
    out = pd.DataFrame({"res-count": g["weight"].sum()})
    out["res-non-ele-heating"] = df[df["in.heating_fuel"] != "Electricity"] \
        .groupby("in.state")["weight"].sum()
    out["res-non-ele-water-heating"] = (
        df[df["in.water_heater_fuel"] != "Electricity"]
        .groupby("in.state")["weight"].sum()
    )
    non_el_range = df[
        ~df["in.cooking_range"].astype(str).str.contains("Electric")
    ]
    out["res-non-ele-range"] = non_el_range.groupby("in.state")["weight"].sum()
    out = out.fillna(0)
    out.index = out.index.map(STATE_NAMES)
    out.index.name = "geoid"
    return out.reset_index()


def comstock_counts(agg_dir):
    rows = []
    for path in sorted(glob.glob(os.path.join(agg_dir, "*_baseline_agg_basic.csv*"))):
        df = pd.read_csv(path, low_memory=False)
        df = df[df["in.upgrade_name"] == "Baseline"]
        name = df["in.state_name"].dropna().iloc[0]
        total = df["weight"].sum()
        rows.append({
            "geoid": name,
            "com-count": total,
            "com-non-ele-heating": df.loc[
                df["in.heating_fuel"] != "Electricity", "weight"].sum(),
            "com-non-ele-water-heating": df.loc[
                df["in.service_water_heating_fuel"] != "Electricity",
                "weight"].sum(),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    ms_path, res_src, com_dir, out_path = (
        sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4],
    )

    res = resstock_counts(res_src)
    com = comstock_counts(com_dir)
    merged = res.merge(com, on="geoid", how="outer").fillna(0)

    for prefix in ("res", "com"):
        merged[f"pct-{prefix}-non-ele-heating"] = (
            merged[f"{prefix}-non-ele-heating"] / merged[f"{prefix}-count"] * 100
        )
        merged[f"pct-{prefix}-non-ele-water-heating"] = (
            merged[f"{prefix}-non-ele-water-heating"]
            / merged[f"{prefix}-count"] * 100
        )
    merged["pct-res-non-ele-range"] = (
        merged["res-non-ele-range"] / merged["res-count"] * 100
    )

    ms = pd.read_csv(ms_path)
    ms["Microsoft Footprint Count"] = (
        ms["Microsoft Footprint Count"].str.replace(",", "").astype("int64")
    )
    out = ms[["State", "Microsoft Footprint Count"]].merge(
        merged, left_on="State", right_on="geoid", how="left"
    ).drop(columns=["geoid"])

    out["pctRes"] = out["res-count"] / (out["res-count"] + out["com-count"])
    out["pctCom"] = out["com-count"] / (out["res-count"] + out["com-count"])
    out["weightedRes"] = (
        5 * out["pct-res-non-ele-heating"]
        + 2 * out["pct-res-non-ele-water-heating"]
        + out["pct-res-non-ele-range"]
    ) / 8
    out["weightedCom"] = (
        5 * out["pct-com-non-ele-heating"]
        + 2 * out["pct-com-non-ele-water-heating"]
    ) / 7
    out["weightedFossilBuildingsPct"] = (
        out["pctRes"] * out["weightedRes"] + out["pctCom"] * out["weightedCom"]
    )
    out["weightedEleBuildingsPct"] = 100 - out["weightedFossilBuildingsPct"]

    out = out.rename(columns={
        "State": "state",
        "res-count": "nrelRes", "com-count": "nrelCom",
        "Microsoft Footprint Count": "buildings",
        "pct-res-non-ele-heating": "pctResNonElHeating",
        "pct-com-non-ele-heating": "pctComNonElHeating",
        "pct-res-non-ele-water-heating": "pctResNonElWaterHeating",
        "pct-com-non-ele-water-heating": "pctComNonElWaterHeating",
        "pct-res-non-ele-range": "pctResNonElRange",
        "res-non-ele-heating": "resNonElHeating",
        "com-non-ele-heating": "comNonElHeating",
        "res-non-ele-water-heating": "resNonElWaterHeating",
        "com-non-ele-water-heating": "comNonElWaterHeating",
        "res-non-ele-range": "resNonElRange",
    })
    out["state"] = out["state"].str.replace(" ", "_").str.lower()

    # States missing either NREL dataset (AK, HI) keep zeroed NREL columns,
    # matching the 2021 file.
    nrel_cols = [c for c in out.columns if c != "state" and c != "buildings"]
    uncovered = (out["nrelRes"].isna()) | (out["nrelCom"].isna())
    out.loc[uncovered, nrel_cols] = 0
    out[nrel_cols] = out[nrel_cols].fillna(0)

    us = {c: 0 for c in out.columns}
    us["state"] = "united_states"
    us["buildings"] = int(out["buildings"].sum())
    out = pd.concat([out, pd.DataFrame([us])], ignore_index=True)
    out.loc[out["state"] == "united_states", "weightedEleBuildingsPct"] = 0

    out["pctRes"] = out["pctRes"].round(4)
    out["pctCom"] = out["pctCom"].round(4)
    pct_cols = [c for c in out.columns if c.startswith(("pct", "weighted"))]
    out[pct_cols] = out[pct_cols].round(2)
    for c in ("buildings", "nrelRes", "nrelCom", "resNonElHeating",
              "comNonElHeating", "resNonElWaterHeating", "comNonElWaterHeating",
              "resNonElRange"):
        out[c] = out[c].round(0).astype("int64")
    out.to_csv(out_path, index=False)
    print(f"wrote {out_path}: {len(out)} rows")

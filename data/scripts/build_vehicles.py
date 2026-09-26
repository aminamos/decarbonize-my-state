"""Rebuild raw/vehicles_data.csv from current upstream sources.

Usage:
    python scripts/build_vehicles.py <mv1.html> <afdc_ev.xlsx> <out.csv>

Inputs:
    mv1.html     FHWA Highway Statistics Table MV-1 saved page
                 (e.g. https://www.fhwa.dot.gov/policyinformation/statistics/2024/mv1.cfm)
    afdc_ev.xlsx DOE AFDC "Electric Vehicle Registrations by State" workbook
                 (https://afdc.energy.gov/data/10962)

Output schema matches the original 2017 file:
    state, Cars_{Private,Public,All}, Buses_{...}, Trucks_{...},
    Motorcycles_{...}, MotorVehicles_{Private,Public,All}, EV_Registration

MV-1 column mapping: PRIVATE AND COMMERCIAL -> *_Private, PUBLICLY OWNED ->
*_Public, TOTAL -> *_All. The trailing "Total" row is written as
`united_states`; its EV count is the sum of state EVs.
"""

import re
import sys

import pandas as pd

CLASSES = [
    ("AUTOMOBILES", "Cars"),
    ("BUSES", "Buses"),
    ("TRUCKS", "Trucks"),
    ("MOTORCYCLES", "Motorcycles"),
    ("ALL MOTOR VEHICLES", "MotorVehicles"),
]
SPLITS = {
    "PRIVATE AND COMMERCIAL (INCLUDING TAXICABS)": "Private",
    "PRIVATE AND COMMERCIAL": "Private",
    "PUBLICLY OWNED": "Public",
    "TOTAL": "All",
}


def parse_mv1(path):
    table = pd.read_html(path)[0]
    out = pd.DataFrame()
    out["state"] = (
        table[("STATE", "STATE")]
        .astype(str)
        .str.replace(r"\s*\(\d+\)\s*$", "", regex=True)
        .replace({"Dist. of Col.": "District of Columbia"})
    )
    for src, dst in CLASSES:
        for split_src, split_dst in SPLITS.items():
            key = (src, split_src)
            if key not in table.columns:
                continue
            col = pd.to_numeric(table[key].astype(str).str.replace(",", ""), errors="coerce")
            out[f"{dst}_{split_dst}"] = col
    return out


def parse_afdc(path):
    df = pd.read_excel(path, sheet_name=0, header=None)
    df.columns = ["blank", "state", "ev", "c3", "c4"]
    df = df[["state", "ev"]].dropna()
    df["state"] = df["state"].astype(str).str.strip()
    df = df[df["state"].str.match(r"^[A-Za-z]") & df["ev"].astype(str).str.match(r"^\d")]
    df["ev"] = df["ev"].astype(int)
    return df


def slug(state):
    return state.strip().lower().replace(" ", "_")


if __name__ == "__main__":
    mv1_path, afdc_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

    mv1 = parse_mv1(mv1_path)
    total_row = mv1[mv1["state"] == "Total"]
    mv1 = mv1[mv1["state"] != "Total"]

    ev = parse_afdc(afdc_path)
    ev_us = ev[ev["state"].str.contains("United States|Total", case=False)]
    ev = ev[~ev["state"].str.contains("United States|Total", case=False)]

    merged = mv1.merge(ev, on="state", how="left").rename(columns={"ev": "EV_Registration"})

    us = total_row.copy()
    us["state"] = "United States"
    us["EV_Registration"] = int(ev_us["ev"].iloc[0]) if len(ev_us) else int(ev["ev"].sum())
    merged = pd.concat([merged, us], ignore_index=True)

    merged["state"] = merged["state"].map(slug)
    merged = merged.sort_values("state").reset_index(drop=True)

    value_cols = [c for c in merged.columns if c != "state"]
    merged[value_cols] = merged[value_cols].astype("Int64")

    merged.to_csv(out_path, index=False)
    print(f"wrote {out_path}: {len(merged)} rows")

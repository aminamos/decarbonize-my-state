"""Rebuild raw/power_plants_and_communities.csv from current upstream sources.

Usage:
    python scripts/build_power_plants.py <egrid20XX_data.xlsx> \
        <ppnc_uniform_buffers.csv> <out.csv>

Inputs:
    eGRID workbook   e.g. egrid2023_data_rev2.xlsx
                     (https://www.epa.gov/egrid/detailed-data)
    uniform buffers  EPA Power Plants and Neighboring Communities "Uniform
                     Buffers" CSV (https://www.epa.gov/power-sector/power-
                     plants-and-neighboring-communities-mapping-tool)

The plant roster is every eGRID plant with positive annual heat input from
combustion (PLHTIAN > 0) — this reproduces the population of the original
file (the EPA Power Plants & Neighboring Communities download) to within a
few plants. Plant columns come from the eGRID plant sheet verbatim; the
community/demographic block is left-joined from the PPNC uniform-buffer file
on ORISPL (a different, newer vintage — see DATA_SOURCES.md). Columns the
site consumes keep the original file's names so get_power_plants.py is
unchanged.

Numbers are thousands-grouped like the original CSV export (e.g. "8,290,060").
"""

import sys

import pandas as pd

RENAME = {
    "Plant file sequence number": "eGRID Plant file sequence number",
    "Plant state abbreviation": "state",
    "Plant name": "plant_name",
    "Utility name": "utility_name",
    "Plant county name": "county",
    "Plant nameplate capacity (MW)": "capacity_mw",
    "Plant latitude": "Latitude",
    "Plant longitude": "Longitude",
    "Plant primary fuel category": "fossil_fuel_category",
}

COMMUNITY_FIRST = "Flag for Overlapping with Tribes"


def fmt(v):
    """Comma-group large numbers like the original eGRID-derived CSV."""
    if v is None or (isinstance(v, float) and pd.isna(v)) or v == "":
        return ""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    if abs(f) >= 1000:
        s = f"{f:,.6f}".rstrip("0").rstrip(".")
        return s
    s = ("%f" % f).rstrip("0").rstrip(".")
    return s if s else "0"


if __name__ == "__main__":
    egrid_path, ppnc_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

    xl = pd.ExcelFile(egrid_path)
    plant_sheet = [s for s in xl.sheet_names if s.startswith("PLNT")][0]
    df = pd.read_excel(xl, sheet_name=plant_sheet, skiprows=[1], dtype=object)

    hti = pd.to_numeric(
        df["Plant annual heat input from combustion (MMBtu)"], errors="coerce"
    ).fillna(0)
    df = df[hti > 0].copy()

    df = df.rename(columns=RENAME)
    df.insert(0, "Plant sequence number", range(1, len(df) + 1))

    ppnc = pd.read_csv(ppnc_path, encoding="latin-1", dtype=str)
    community_cols = list(
        ppnc.columns[list(ppnc.columns).index(COMMUNITY_FIRST):-1]
    )
    ppnc = ppnc[["ORISPL"] + community_cols].copy()
    ppnc["ORISPL"] = ppnc["ORISPL"].str.strip()

    df["__oris"] = df["DOE/EIA ORIS plant or facility code"].astype(str).str.strip()
    df = df.merge(ppnc, left_on="__oris", right_on="ORISPL", how="left")
    df = df.drop(columns=["__oris", "ORISPL"])

    for col in df.columns:
        df[col] = df[col].map(fmt)

    df.to_csv(out_path, index=False)
    n_com = df["Total Population"].ne("").sum() if "Total Population" in df else 0
    print(f"wrote {out_path}: {len(df)} plants, {n_com} with community stats")

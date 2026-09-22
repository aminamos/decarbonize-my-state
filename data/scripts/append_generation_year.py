"""Append a new data year to raw/us_electric_generation_2001_20.csv.

Usage:
    python scripts/append_generation_year.py <annual_generation_state.xlsx> \
        <small_scale_solar_YEAR.xlsx> <year> <raw.csv> <out.csv>

Inputs:
    annual_generation_state.xlsx  EIA "Net Generation by State by Type of
        Producer by Energy Source" (https://www.eia.gov/electricity/data/state/)
    small_scale_solar_YEAR.xlsx   EIA-861M "Estimated Small Scale Solar PV
        Capacity and Generation" for the target year (archived copy —
        https://www.eia.gov/electricity/data/eia861m/, archive/xls/)
    year                          the year to append (must exist in the file)

Column mapping replicates the 2021-2024 append (see DATA_SOURCES.md):
    all_fuels=Total, coal, natural_gas=Natural Gas, other_gas=Other Gases,
    petro_liquids=Petroleum, petro_coke=0 (no coke split in the annual file),
    nuclear, hydro_electric=Hydroelectric Conventional,
    hydro_electric_storage=Pumped Storage,
    utility_scale_solar=Solar Thermal and Photovoltaic,
    small_scale_photovoltaic=861M state monthly-generation sum (NM -> blank),
    all_solar=utility+small_scale,
    other_renewables=wind+utility_scale_solar+geothermal+other_biomass+wood,
    wind, geothermal=Geothermal, other_biomass=Other Biomass,
    wood_fuels=Wood and Wood Derived Fuels, other=Other.
    utility_scale_photovoltaic / utility_scale_thermal left blank (no split in
    the annual file). Values are divided by 1000 (MWh -> GWh).
"""

import sys

import pandas as pd

SRC_MAP = {
    "all_fuels": "Total",
    "coal": "Coal",
    "natural_gas": "Natural Gas",
    "other_gas": "Other Gases",
    "petro_liquids": "Petroleum",
    "nuclear": "Nuclear",
    "hydro_electric": "Hydroelectric Conventional",
    "hydro_electric_storage": "Pumped Storage",
    "utility_scale_solar": "Solar Thermal and Photovoltaic",
    "wind": "Wind",
    "geothermal": "Geothermal",
    "other_biomass": "Other Biomass",
    "wood_fuels": "Wood and Wood Derived Fuels",
    "other": "Other",
}


def load_annual(xlsx_path, year):
    xl = pd.ExcelFile(xlsx_path)
    sheet = [s for s in xl.sheet_names if "Net_Generation" in s][0]
    df = pd.read_excel(xl, sheet_name=sheet, header=1)
    df = df[
        (df["YEAR"] == year)
        & (df["TYPE OF PRODUCER"] == "Total Electric Power Industry")
    ]
    df["STATE"] = df["STATE"].astype(str).str.strip()
    df = df[df["STATE"].str.match(r"^[A-Z]{2}$")]
    piv = df.pivot_table(
        index="STATE", columns="ENERGY SOURCE",
        values="GENERATION (Megawatthours)", aggfunc="sum",
    )
    return piv


def load_small_scale(xlsx_path, year):
    df = pd.read_excel(
        xlsx_path, sheet_name="Monthly Totals- States", header=2
    )
    df = df[df["Year"] == year].copy()
    gen = pd.to_numeric(df["Total.1"], errors="coerce")
    return gen.groupby(df["State"]).sum(min_count=1) / 1000.0


if __name__ == "__main__":
    annual_path, ss_path, year, raw_path, out_path = (
        sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5],
    )

    piv = load_annual(annual_path, year)
    small = load_small_scale(ss_path, year)

    rows = []
    for state in sorted(piv.index):
        rec = {"state": state, "year": year}
        for dst, src in SRC_MAP.items():
            val = piv.loc[state, src] if src in piv.columns else 0
            rec[dst] = (0 if pd.isna(val) else val) / 1000.0
        rec["petro_coke"] = 0.0
        rec["utility_scale_photovoltaic"] = None
        rec["utility_scale_thermal"] = None
        ss = small.get(state)
        rec["small_scale_photovoltaic"] = (
            None if ss is None or pd.isna(ss) else round(float(ss), 3)
        )
        rec["all_solar"] = rec["utility_scale_solar"] + (
            rec["small_scale_photovoltaic"] or 0
        )
        rec["other_renewables"] = (
            rec["wind"] + rec["utility_scale_solar"] + rec["geothermal"]
            + rec["other_biomass"] + rec["wood_fuels"]
        )
        rows.append(rec)

    new = pd.DataFrame(rows)[
        ["state", "year", "all_fuels", "coal", "natural_gas", "other_gas",
         "petro_liquids", "petro_coke", "nuclear", "hydro_electric",
         "hydro_electric_storage", "all_solar", "wind", "utility_scale_solar",
         "utility_scale_photovoltaic", "small_scale_photovoltaic",
         "other_renewables", "utility_scale_thermal", "geothermal",
         "other_biomass", "wood_fuels", "other"]
    ]

    raw = pd.read_csv(raw_path)
    assert list(raw.columns) == list(new.columns)
    raw = raw[raw["year"] != year]
    out = pd.concat([raw, new], ignore_index=True)
    out.to_csv(out_path, index=False)
    print(f"wrote {out_path}: {len(out)} rows ({len(new)} new for {year})")

/**
 * Provenance / "as of" information for the datasets that feed a state page.
 *
 * Kept in one place so every state reports the same vintages. `coverage` is the
 * time span actually present in `data/final/**`; `reportDate` is when the
 * upstream source published it.
 */
export const stateDataFreshness = [
  {
    slug: "emissions",
    label: "Emissions by sector",
    coverage: "1990–2022",
    reportDate: "Sep 2024",
    source: "EPA Inventory of U.S. GHG Emissions and Sinks by State",
  },
  {
    slug: "power-generation",
    label: "Power generation mix",
    coverage: "2001–2024",
    reportDate: "Oct 2025",
    source: "EIA Historical State Data (EIA-923) + SEDS",
  },
  {
    slug: "power-plants",
    label: "Fossil fuel power plants",
    coverage: "data year 2019",
    reportDate: "Jan 2021",
    source: "EPA eGRID / EJScreen",
  },
  {
    slug: "vehicles",
    label: "Vehicle & EV registrations",
    coverage: "2017 vehicles / ~2019 EVs",
    reportDate: "Feb 2021",
    source: "FHWA Highway Statistics MV-1 + DOE AFDC",
  },
  {
    slug: "buildings",
    label: "Buildings & electrification",
    coverage: "2021",
    reportDate: "Dec 2021",
    source: "Microsoft Building Footprints + NREL ResStock/ComStock",
  },
]

export function getStateDataFreshness(slug) {
  return stateDataFreshness.find(dataset => dataset.slug === slug)
}

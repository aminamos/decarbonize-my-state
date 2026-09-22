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
    coverage: "2001–2025",
    reportDate: "Sep 2026",
    source: "EIA Historical State Data (EIA-923) + SEDS / EIA-861M",
  },
  {
    slug: "power-plants",
    label: "Fossil fuel power plants",
    coverage: "data year 2023",
    reportDate: "Jun 2025",
    source: "EPA eGRID / Power Plants & Neighboring Communities",
  },
  {
    slug: "vehicles",
    label: "Vehicle & EV registrations",
    coverage: "2024 vehicles / 2023 EVs",
    reportDate: "Jan 2026",
    source: "FHWA Highway Statistics MV-1 + DOE AFDC",
  },
  {
    slug: "buildings",
    label: "Buildings & electrification",
    coverage: "2024",
    reportDate: "Apr 2025",
    source: "Microsoft Building Footprints + NREL ResStock/ComStock 2024.2",
  },
]

export function getStateDataFreshness(slug) {
  return stateDataFreshness.find(dataset => dataset.slug === slug)
}

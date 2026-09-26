import React from "react"

export function getShortCitation(slug) {
  const citation = getCitation(slug)
  return (
    <a href={`/about#data-${slug}`} target="_blank" rel="noreferrer">
      {citation.source_short}, {citation.date}
    </a>
  )
}

export function getLongCitation(slug) {
  const citation = getCitation(slug)

  return (
    <p id={`data-${slug}`}>
      <a className="font-weight-bold" href={citation.link}>
        {citation.title}
      </a>
      <br />
      {citation.source}
      <br />
      {citation.date}
      {citation.note && (
        <>
          <br />
          <span className="text-muted">{citation.note}</span>
        </>
      )}
    </p>
  )
}

function getCitation(slug) {
  const citation = sourceCitations.filter(c => c.slug === slug)
  return citation[0]
}

const sourceCitations = [
  {
    slug: "emissions",
    title:
      "Inventory of U.S. Greenhouse Gas Emissions and Sinks by State, 1990-2022",
    source: "U.S. Environmental Protection Agency (EPA)",
    source_short: "EPA",
    date: "Sep 2024",
    link:
      "https://www.epa.gov/ghgemissions/methodology-report-inventory-us-greenhouse-gas-emissions-and-sinks-state-1990-2022",
    note:
      "Historical provenance: 1990-2018 values were published by the World Resources Institute (Climate Watch, Mar 2021) and rescaled to the EPA basis via 2018 overlap-ratio splicing -- see data/DATA_SOURCES.md.",
  },
  {
    slug: "building-footprints",
    title: "U.S. Building Footprints",
    source: "Microsoft Maps",
    source_short: "Microsoft",
    date: "Mar 2021",
    link: "https://github.com/microsoft/USBuildingFootprints",
  },
  {
    slug: "building-energy",
    title:
      "End Use Load Profiles for the U.S. Building Stock (ResStock & ComStock 2024.2)",
    source: "The National Renewable Energy Laboratory (NREL)",
    source_short: "NREL",
    date: "Apr 2025",
    link: "https://resstock.nrel.gov/datasets",
  },
  {
    slug: "vehicles",
    title: "State Motor-Vehicle Registrations",
    source: "U.S. Department of Transportation",
    source_short: "DOT",
    date: "Jan 2026",
    link: "https://www.fhwa.dot.gov/policyinformation/statistics/2024/mv1.cfm",
    note:
      "EV registrations from DOE AFDC 'Electric Vehicle Registrations by State' (Experian-sourced, Dec 31 2023 counts, Sep 2024 update): https://afdc.energy.gov/data/10962.",
  },
  {
    slug: "power-plants",
    title: "Power Plants and Neighboring Communities",
    source: "U.S. Environmental Protection Agency (EPA)",
    source_short: "EPA",
    date: "Jun 2025",
    link:
      "https://www.epa.gov/power-sector/power-plants-and-neighboring-communities-mapping-tool",
    note:
      "Plant roster and emissions from eGRID2023 revision 2 (data year 2023); neighboring-community columns from the PPNC uniform-buffers dataset (2022, published Jan 2025).",
  },
  {
    slug: "power-generation",
    title:
      "Historical State Data annual_generation_state.xlsx (1990-2025 final) plus small-scale solar",
    source: "U.S. Energy Information Administration (EIA)",
    source_short: "EIA",
    date: "Sep 2026",
    link: "https://www.eia.gov/electricity/data/state/",
    note:
      "Small-scale solar: SEDS use_all_phy.csv through 2024 (final, Jun 2026); EIA-861M for 2025 (SEDS-2025 not yet published; AL small-scale PV suppressed as NM). 2001-2020 values retain the retired EIA Open Data API v1 basis -- see data/DATA_SOURCES.md.",
  },
]

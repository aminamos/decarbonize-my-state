import React from "react"

import { slugToTitle } from "../helper-functions"
// Sim city power plant icons
import OilPlantImg from "../images/oil-plant.png?url"
import GasPlantImg from "../images/gas-plant.png?url"
import CoalPlantImg from "../images/coal-plant.png?url"

import PowerIcon from "../images/icons/power-cord.svg?url"
import CloudIcon from "../images/icons/cloud.svg?url"
import BackIcon from "../images/icons/arrow-left.svg?url"
import BackIconWhite from "../images/icons/arrow-left-white.svg?url"

import Layout from "./layout"
import NewTabIcon from "./new-tab-icon"
import { getShortCitation } from "../constants/source-citations"
import { parseStatValue, STAT_UNAVAILABLE } from "../lib/plant-stats"

/**
 * Helpful stats we use to provide context about power plant metrics
 */
const ContextStats = {
  netGeneration: {
    avgAmericanHomeMwhPerYear: 11,
    source:
      "https://www.eia.gov/energyexplained/use-of-energy/electricity-use-in-homes.php",
  },
  co2eEmissions: {
    avgAmericanCarEmissionsTonsPerYear: 4.6,
    source:
      "https://www.epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle",
  },
}

/**
 * Parse a value from the plant data into a number, or null when it is missing
 * or not numeric. Roughly 200 plants have blank or parenthesized
 * net-generation / CO2e values, so every stat below has to tolerate a null.
 */
function StatValue({ value, suffix = null }) {
  const parsed = parseStatValue(value)
  if (parsed === null) {
    return <>{STAT_UNAVAILABLE}</>
  }
  return (
    <>
      {parsed.toLocaleString()}
      {suffix ? <> {suffix}</> : null}
    </>
  )
}

const PowerPlantDetailPage = ({ plantSlug, data }) => {
  const PowerPlantStateSlug = data.allPowerPlantsJson.edges[0].node.state
  const PowerPlantSlug = plantSlug
  const PowerPlant = data.allPowerPlantsJson.edges[0].node.power_plants.find(
    plant => plant.slug === plantSlug
  )

  const StateFaceClass = PowerPlantStateSlug.toLowerCase().replaceAll(" ", "-")
  const PowerPlantStateTitle = slugToTitle(PowerPlantStateSlug)

  const PlantCoords = `${PowerPlant.Latitude},${PowerPlant.Longitude}`

  // t=k sets the map to sattelite view, then we specify a query of  Lat,Long
  const GoogleMapsLink = `https://maps.google.com/?t=k&q=${PlantCoords}`

  const MapImgUrl = `/power-plant-satellite-imgs/${PowerPlantStateSlug}-${PowerPlantSlug}.png`

  /** Calculate comparison stats (null when the source value is unavailable) */
  const NetGenerationInt = parseStatValue(
    PowerPlant.Plant_annual_net_generation__MWh_
  )
  const NetGenerationEquivalentHomes =
    NetGenerationInt === null
      ? null
      : NetGenerationInt / ContextStats.netGeneration.avgAmericanHomeMwhPerYear

  const CO2eEmissionsInt = parseStatValue(
    PowerPlant.Plant_annual_CO2_equivalent_emissions__tons_
  )
  const EmissionsEquivalentCars =
    CO2eEmissionsInt === null
      ? null
      : CO2eEmissionsInt /
        ContextStats.co2eEmissions.avgAmericanCarEmissionsTonsPerYear

  return (
    <Layout>
      <div className="power-plant-page">
        <a
          href={`/${PowerPlantStateSlug}#power`}
          className="btn btn-outline-dark font-weight-bold"
        >
          <div className="back-icon">
            <img src={BackIcon} alt="" />
            <img src={BackIconWhite} className="-white" alt="" />
          </div>
          Back to {PowerPlantStateTitle} Power Details
        </a>
        <div className="top-row">
          <div className="power-plant-profile">
            {PowerPlant.fossil_fuel_category.toLowerCase() === "oil" && (
              <img src={OilPlantImg} alt="Oil power plant" />
            )}
            {PowerPlant.fossil_fuel_category.toLowerCase() === "gas" && (
              <img src={GasPlantImg} alt="Gas power plant" />
            )}
            {PowerPlant.fossil_fuel_category.toLowerCase() === "coal" && (
              <img src={CoalPlantImg} alt="Coal power plant" />
            )}

            <div
              className={"state-icon sf-" + StateFaceClass}
              aria-hidden="true"
            ></div>
          </div>

          <div>
            <h1 id="main" className="mb-0">
              {PowerPlant.plant_name}
            </h1>

            <div className="h5 mb-0 font-weight-bold">
              <span className="text-capitalize">
                {PowerPlant.fossil_fuel_category.toLowerCase()}
              </span>{" "}
              Power Plant
            </div>
            <div>
              {PowerPlant.county} County, {PowerPlantStateTitle}
            </div>

            <a href={GoogleMapsLink} target="_blank" rel="noreferrer">
              View on Google Maps
              <NewTabIcon />
            </a>
          </div>

          <img src={MapImgUrl} className="map-img"></img>
        </div>

        <p className="mt-2 text-secondary">
          Power Plant Data Source: {getShortCitation("power-plants")}
        </p>

        <div className="stat-panel">
          <h2 className="h4">Quick Stats</h2>

          <div className="quick-stats-cont">
            <img src={PowerIcon} className="stat-icon" alt="" />

            <img src={CloudIcon} className="stat-icon" alt="" />

            <dl>
              <dt>Capacity</dt>
              <dd>{PowerPlant.capacity_mw.toLocaleString()} Megawatts</dd>

              <dt>Annual Net Generation</dt>
              <dd className="mb-0">
                <StatValue
                  value={PowerPlant.Plant_annual_net_generation__MWh_}
                  suffix={<>MWh (Megawatt Hours)</>}
                />
              </dd>

              {NetGenerationEquivalentHomes !== null && (
                <p className="context-msg">
                  <strong>Context:</strong> That&apos;s equivalent to the annual
                  power demand of{" "}
                  {Math.round(NetGenerationEquivalentHomes).toLocaleString()}{" "}
                  American homes (11 MWh each,{" "}
                  <a
                    href={ContextStats.netGeneration.source}
                    target="_blank"
                    rel="noreferrer"
                  >
                    source: EIA
                    <NewTabIcon />
                  </a>
                  )
                </p>
              )}

              <dt className="mt-4">
                Annual CO<sub>2</sub> equivalent emissions
              </dt>
              <dd className="mb-0">
                <StatValue
                  value={
                    PowerPlant.Plant_annual_CO2_equivalent_emissions__tons_
                  }
                  suffix={
                    <>
                      metric tons CO<sub>2</sub> equivalent
                    </>
                  }
                />
              </dd>

              {EmissionsEquivalentCars !== null && (
                <p className="context-msg">
                  <strong>Context:</strong> That&apos;s equivalent to the annual
                  emissions of about{" "}
                  {Math.round(EmissionsEquivalentCars).toLocaleString()}{" "}
                  American cars (4.6 metric tons each,{" "}
                  <a
                    href={ContextStats.co2eEmissions.source}
                    target="_blank"
                    rel="noreferrer"
                  >
                    source: EPA
                    <NewTabIcon />
                  </a>
                  )
                </p>
              )}
            </dl>
          </div>
        </div>
        <div className="stat-panel">
          <h2 className="h4">Detailed Emissions</h2>

          <dl className="detailed-emissions">
            <div>
              <dt>
                Annual CO<sub>2</sub> emissions
              </dt>
              <dd>
                <StatValue
                  value={PowerPlant.Plant_annual_CO2_emissions__tons_}
                  suffix={
                    <>
                      metric tons CO<sub>2</sub>
                    </>
                  }
                />
              </dd>
            </div>

            <div>
              <dt>
                Annual SO<sub>2</sub> (Sulfer Dioxide) emissions
              </dt>
              <dd>
                <StatValue
                  value={PowerPlant.Plant_annual_SO2_emissions__tons_}
                  suffix="tons"
                />
              </dd>
            </div>

            <div>
              <dt>Annual NOx (Nitrogen Oxide) emissions</dt>
              <dd>
                <StatValue
                  value={PowerPlant.Plant_annual_NOx_emissions__tons_}
                  suffix="tons"
                />
              </dd>
            </div>

            <div>
              <dt>
                Annual N<sub>2</sub>O (Nitrous Oxide) emissions
              </dt>
              <dd>
                <StatValue
                  value={PowerPlant.Plant_annual_N2O_emissions__lbs_}
                  suffix="lbs"
                />
              </dd>
            </div>

            <div>
              <dt>Annual CH4 (Methane) emissions</dt>
              <dd>
                <StatValue
                  value={PowerPlant.Plant_annual_CH4_emissions__lbs_}
                  suffix="lbs"
                />
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </Layout>
  )
}

export default PowerPlantDetailPage

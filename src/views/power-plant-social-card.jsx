import React, { useEffect, useState } from "react"

import { slugToTitle } from "../helper-functions"
import { getAllPowerPlantsEdges } from "../lib/data"
import OilPlantImg from "../images/oil-plant.png?url"
import GasPlantImg from "../images/gas-plant.png?url"
import CoalPlantImg from "../images/coal-plant.png?url"

// Built once at build time and shipped with this route's bundle. The page is
// only used by the puppeteer social card generator, not by site visitors.
const data = { allPowerPlantsJson: { edges: getAllPowerPlantsEdges() } }

/**
 *
 * http://localhost:8000/power-plant-social-card/?state=illinois&plant=baldwin-energy-complex
 */

const PowerPlantSocialCardPage = () => {
  /**
   * Process data at runtime, so even the static preview site can process the power plant data and
   * make a proper preview even on a prod build
   */
  const [FuelCategory, setFuelCategory] = useState()
  const [FuelCategoryOther, setFuelCategoryOther] = useState()
  const [PowerPlant, setPowerPlant] = useState({})
  const [StateFaceClass, setStateFaceClass] = useState()
  const [StateTitle, setStateTitle] = useState()

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)

    // Default to Baldwin Energy Complex in Illinois if no params specified
    const CurrentStateSlug = params.get("state") || "illinois"
    const CurrentPlantSlug = params.get("plant") || "baldwin-energy-complex"

    setStateTitle(slugToTitle(CurrentStateSlug))
    setStateFaceClass(CurrentStateSlug.toLowerCase().replaceAll(" ", "-"))

    const StateData = data.allPowerPlantsJson.edges.find(
      entry => entry.node.state === CurrentStateSlug
    )

    const powerPlant = StateData.node.power_plants.find(
      plant => plant.slug === CurrentPlantSlug
    )

    setPowerPlant(powerPlant)

    const fuelCategory = powerPlant.fossil_fuel_category.toLowerCase()
    setFuelCategory(fuelCategory)
    // If not coal, oil, or gas, we use the coal icon
    setFuelCategoryOther(!["oil", "gas", "coal"].includes(fuelCategory))
  }, [])

  return (
    <div
      className="social-card d-flex flex-column"
      data-power-plant-slug={PowerPlant.slug || ""}
    >
      <div
        className="d-flex justify-content-between"
        style={{ height: "418px", width: "800px" }}
      >
        <div className="d-flex align-items-center p-5">
          <div className="power-plant-profile ml-2">
            {FuelCategory === "oil" && (
              <img src={OilPlantImg} alt="Oil power plant" />
            )}
            {FuelCategory === "gas" && (
              <img src={GasPlantImg} alt="Gas power plant" />
            )}
            {(FuelCategory === "coal" || FuelCategoryOther) && (
              <img src={CoalPlantImg} alt="Coal power plant" />
            )}

            <div
              className={"state-icon sf-" + StateFaceClass}
              aria-hidden="true"
            ></div>
          </div>
        </div>

        <div className="d-flex flex-column justify-content-center flex-grow-1">
          <div>
            <h1 className="h2 mb-0 mt-0">{PowerPlant.plant_name}</h1>

            <div className="h5 mb-0 font-weight-bold">
              <span className="text-capitalize">{FuelCategory}</span> Power
              Plant
            </div>
            <div>
              {PowerPlant.county} County, {StateTitle}
            </div>
          </div>

          <div className="d-flex mt-3">
            <div>
              <strong>Capacity</strong>
              <br />
              <span>
                {Math.round(PowerPlant.capacity_mw).toLocaleString()} Megawatts
              </span>
            </div>

            <div className="ml-4">
              <strong>Annual Net Generation</strong>
              <br />
              <span>
                {PowerPlant.Plant_annual_net_generation__MWh_} Megawatt Hours
              </span>
            </div>
          </div>
        </div>
      </div>
      <h2 className="p-2 m-0 text-left" style={{ width: "800px" }}>
        Decarb My State
      </h2>
    </div>
  )
}

export default PowerPlantSocialCardPage

import { describe, expect, it } from "vitest"

import {
  getAllPowerPlantsEdges,
  getCleanEmissionsData,
  getPowerPlantBundle,
  getPowerPlantPaths,
  getStateBundle,
  placeNames,
} from "./data.js"

const DATASET_KEYS = [
  "allEmissionsJson",
  "allBuildingsJson",
  "allVehiclesJson",
  "allPowerPlantsJson",
  "allPowerGenerationJson",
  "allTargetGenerationJson",
]

describe("placeNames", () => {
  it("covers the 50 states plus DC, with no duplicates", () => {
    expect(placeNames).toHaveLength(51)
    expect(placeNames).toContain("district_of_columbia")
    expect(new Set(placeNames).size).toBe(placeNames.length)
  })
})

describe("getStateBundle", () => {
  it("resolves every dataset for every state", () => {
    for (const state of placeNames) {
      const bundle = getStateBundle(state)
      for (const key of DATASET_KEYS) {
        expect(bundle[key].edges, `${state} missing ${key}`).toHaveLength(1)
      }
    }
  })

  it("reports the coverage the state pages advertise", () => {
    const { allEmissionsJson, allPowerGenerationJson } = getStateBundle(
      "minnesota"
    )
    const emissions = allEmissionsJson.edges[0].node.emissionsByYear
    expect(emissions[0].year).toBe(1990)
    expect(emissions[emissions.length - 1].year).toBe(2022)

    const generationYears = allPowerGenerationJson.edges[0].node.generation.map(
      row => row.year
    )
    expect(Math.min(...generationYears)).toBe(2001)
    expect(Math.max(...generationYears)).toBe(2024)
  })

  it("includes a united_states row for the About page chart", () => {
    const clean = getCleanEmissionsData()
    expect(clean.united_states).toBeTruthy()
    expect(clean.united_states.emissionsByYear.length).toBeGreaterThan(30)
  })
})

describe("power plants", () => {
  it("sanitizes JSON keys the way gatsby-transformer-json did", () => {
    const plant = getAllPowerPlantsEdges()[0].node.power_plants[0]
    expect(plant).toHaveProperty("Plant_annual_net_generation__MWh_")
    expect(plant).toHaveProperty("Plant_annual_CO2_equivalent_emissions__tons_")
    expect(plant).not.toHaveProperty("Plant annual net generation (MWh)")
  })

  it("produces a unique route for every plant", () => {
    const paths = getPowerPlantPaths()
    expect(paths.length).toBeGreaterThan(3000)
    const keys = paths.map(p => `${p.state}/${p.slug}`)
    expect(new Set(keys).size).toBe(keys.length)
  })

  it("resolves a known plant", () => {
    const bundle = getPowerPlantBundle("minnesota", "sherburne-county")
    const plant = bundle.allPowerPlantsJson.edges[0].node.power_plants.find(
      candidate => candidate.slug === "sherburne-county"
    )
    expect(plant.plant_name).toMatch(/sherburne/i)
  })
})

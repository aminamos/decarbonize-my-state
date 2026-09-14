/**
 * Build-time data accessors.
 *
 * Gatsby loaded `data/final/**` into GraphQL via gatsby-transformer-json and
 * pages queried slices of it. Astro has no GraphQL layer, so these helpers read
 * the same JSON directly and return it in the exact `{ allXJson: { edges: [
 * { node } ] } }` shape the ported React components already expect. This keeps
 * the component data-handling code unchanged while letting Astro filter at
 * build time (so only the small, page-specific slice ships to the client).
 */
import emissions from "../../data/final/emissions/emissions.json"
import buildings from "../../data/final/buildings/buildings.json"
import vehicles from "../../data/final/vehicles/vehicles.json"
import powerPlants from "../../data/final/power_plants/power_plants.json"
import powerGeneration from "../../data/final/power_generation/power_generation.json"
import targetGeneration from "../../data/final/target_generation/target_generation.json"
import { placeNames } from "../constants/state-names.js"

/** Wrap an array of nodes as a GraphQL-ish connection */
const edges = arr => arr.map(node => ({ node }))

/** Wrap a single node as a GraphQL-ish connection (empty when missing) */
const single = node => ({ edges: node ? [{ node }] : [] })

/**
 * gatsby-transformer-json sanitized JSON keys into valid GraphQL field names,
 * which is why the components read `Plant_annual_net_generation__MWh_` even
 * though the source JSON key is `Plant annual net generation (MWh)`. Reproduce
 * that transform so the ported components keep working.
 */
const sanitizeKey = key => key.replace(/[^A-Za-z0-9_]/g, "_")

const sanitizePowerPlants = nodes =>
  nodes.map(node => ({
    ...node,
    power_plants: node.power_plants.map(plant => {
      const sanitized = {}
      for (const [key, value] of Object.entries(plant)) {
        sanitized[sanitizeKey(key)] = value
      }
      return sanitized
    }),
  }))

const powerPlantsByName = sanitizePowerPlants(powerPlants)

export { placeNames }

/** Every emissions record (includes `united_states`) */
export const getAllEmissionsEdges = () => edges(emissions)

/** Every buildings record */
export const getAllBuildingsEdges = () => edges(buildings)

/** Every power plant record (includes `puerto_rico`) */
export const getAllPowerPlantsEdges = () => edges(powerPlantsByName)

/**
 * The `{ [state]: { emissionsByYear } }` map the homepage / about / social card
 * helpers consume.
 */
export function getCleanEmissionsData() {
  const byState = {}
  for (const node of emissions) {
    byState[node.state] = { emissionsByYear: node.emissionsByYear }
  }
  return byState
}

/** All the per-state slices a state details page needs */
export function getStateBundle(state) {
  return {
    allEmissionsJson: single(emissions.find(node => node.state === state)),
    allBuildingsJson: single(buildings.find(node => node.state === state)),
    allVehiclesJson: single(vehicles.find(node => node.state === state)),
    allPowerPlantsJson: single(
      powerPlantsByName.find(node => node.state === state)
    ),
    allPowerGenerationJson: single(
      powerGeneration.find(node => node.state === state)
    ),
    allTargetGenerationJson: single(
      targetGeneration.find(node => node.state === state)
    ),
  }
}

/** The single power plant record the plant details page needs */
export function getPowerPlantBundle(state, slug) {
  const stateNode = powerPlantsByName.find(
    node =>
      node.state === state &&
      node.power_plants.some(plant => plant.slug === slug)
  )
  return { allPowerPlantsJson: single(stateNode) }
}

/** Every `{ state, slug }` power plant route, used by getStaticPaths */
export function getPowerPlantPaths() {
  const seen = new Set()
  const paths = []
  for (const node of powerPlantsByName) {
    for (const plant of node.power_plants) {
      const key = `${node.state}/${plant.slug}`
      if (seen.has(key)) continue
      seen.add(key)
      paths.push({ state: node.state, slug: plant.slug })
    }
  }
  return paths
}

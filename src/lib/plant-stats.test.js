import { describe, expect, it } from "vitest"

import {
  formatStatValue,
  parseStatValue,
  STAT_UNAVAILABLE,
} from "./plant-stats.js"

describe("parseStatValue", () => {
  it("parses comma-formatted integers and decimals", () => {
    expect(parseStatValue("5,842,650")).toBe(5842650)
    expect(parseStatValue("2,264,030.487")).toBeCloseTo(2264030.487, 3)
  })

  it("parses plain numbers and negative values", () => {
    expect(parseStatValue(2781.7)).toBe(2781.7)
    expect(parseStatValue("-12")).toBe(-12)
  })

  it("treats parenthesized values as negative", () => {
    expect(parseStatValue("(230)")).toBe(-230)
    expect(parseStatValue("(216)")).toBe(-216)
  })

  it("returns null for missing or non-numeric values", () => {
    for (const value of [
      "",
      "   ",
      null,
      undefined,
      "-",
      "--",
      "None",
      "n/a",
      "NaN",
    ]) {
      expect(parseStatValue(value), String(value)).toBeNull()
    }
  })
})

describe("formatStatValue", () => {
  it("formats numbers with a suffix", () => {
    expect(formatStatValue("5,842,650", " MWh")).toBe("5,842,650 MWh")
  })

  it("falls back to a readable message instead of NaN", () => {
    expect(formatStatValue("")).toBe(STAT_UNAVAILABLE)
    expect(formatStatValue("(230)")).not.toContain("NaN")
  })
})

describe("the real dataset", () => {
  it("never formats a plant stat as NaN", async () => {
    const { default: powerPlants } = await import(
      "../../data/final/power_plants/power_plants.json"
    )
    const fields = [
      "Plant_annual_net_generation__MWh_",
      "Plant_annual_CO2_equivalent_emissions__tons_",
      "Plant_annual_CO2_emissions__tons_",
      "Plant_annual_SO2_emissions__tons_",
      "Plant_annual_NOx_emissions__tons_",
      "Plant_annual_N2O_emissions__lbs_",
      "Plant_annual_CH4_emissions__lbs_",
    ]

    let checked = 0
    for (const node of powerPlants) {
      for (const plant of node.power_plants) {
        for (const field of fields) {
          const rendered = formatStatValue(plant[field])
          expect(
            rendered,
            `${node.state}/${plant.slug} ${field}`
          ).not.toContain("NaN")
          checked += 1
        }
      }
    }
    expect(checked).toBeGreaterThan(20000)
  })
})

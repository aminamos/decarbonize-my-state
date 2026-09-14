import { describe, expect, it } from "vitest"

import { formatOrdinal, ordinalSuffix } from "./ordinal.js"

describe("ordinalSuffix", () => {
  it("handles the standard cases", () => {
    expect(formatOrdinal(1)).toBe("1st")
    expect(formatOrdinal(2)).toBe("2nd")
    expect(formatOrdinal(3)).toBe("3rd")
    expect(formatOrdinal(4)).toBe("4th")
    expect(formatOrdinal(9)).toBe("9th")
    expect(formatOrdinal(21)).toBe("21st")
    expect(formatOrdinal(22)).toBe("22nd")
    expect(formatOrdinal(23)).toBe("23rd")
    expect(formatOrdinal(50)).toBe("50th")
  })

  it("handles the 11/12/13 exception", () => {
    expect(formatOrdinal(11)).toBe("11th")
    expect(formatOrdinal(12)).toBe("12th")
    expect(formatOrdinal(13)).toBe("13th")
    expect(formatOrdinal(111)).toBe("111th")
    expect(formatOrdinal(112)).toBe("112th")
    expect(formatOrdinal(113)).toBe("113th")
  })

  it("never produces a doubled suffix across the state-rank range", () => {
    for (let rank = 1; rank <= 51; rank += 1) {
      expect(formatOrdinal(rank)).toMatch(/^\d+(st|nd|rd|th)$/)
      expect(formatOrdinal(rank)).not.toMatch(/(st|nd|rd|th)(st|nd|rd|th)$/)
    }
    expect(ordinalSuffix(11)).toBe("th")
  })
})

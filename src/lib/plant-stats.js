/**
 * Parsing helpers for the power plant stats, which come from a scraped/joined
 * CSV and contain blanks and accounting-style parenthesized negatives.
 */

/**
 * Parse a source value into a number, or null when it is missing or not
 * numeric. Handles comma thousands separators and treats a value wrapped in
 * parentheses as negative, e.g. "(230)" -> -230.
 */
export function parseStatValue(value) {
  if (value === null || value === undefined) {
    return null
  }

  let cleaned = String(value)
    .replaceAll(",", "")
    .trim()
  if (cleaned === "") {
    return null
  }

  let isNegative = false
  const parenthesized = cleaned.match(/^\((.*)\)$/)
  if (parenthesized) {
    isNegative = true
    cleaned = parenthesized[1].trim()
  }

  if (!/^-?\d+(\.\d+)?$/.test(cleaned)) {
    return null
  }

  const parsed = parseFloat(cleaned)
  return isNegative ? -parsed : parsed
}

/** Human-readable fallback used across the plant page */
export const STAT_UNAVAILABLE = "Data not available"

/** Format a parsed stat for display, with an optional plain-text suffix */
export function formatStatValue(value, suffix = "") {
  const parsed = parseStatValue(value)
  if (parsed === null) {
    return STAT_UNAVAILABLE
  }
  return `${parsed.toLocaleString()}${suffix}`
}

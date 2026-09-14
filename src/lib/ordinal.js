/**
 * Correct English ordinal suffix for a 1-based rank.
 *
 * Handles the 11/12/13 exception, which digit-only logic gets wrong
 * (11st, 12nd, 13rd).
 */
export function ordinalSuffix(rank) {
  const mod100 = rank % 100
  if (mod100 >= 11 && mod100 <= 13) {
    return "th"
  }
  switch (rank % 10) {
    case 1:
      return "st"
    case 2:
      return "nd"
    case 3:
      return "rd"
    default:
      return "th"
  }
}

/** Format a rank with its ordinal suffix, e.g. 11 -> "11th" */
export function formatOrdinal(rank) {
  return `${rank}${ordinalSuffix(rank)}`
}

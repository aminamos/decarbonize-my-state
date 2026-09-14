import { expect, test } from "@playwright/test"

/** Collect page errors + console errors for a page and assert none occurred */
function trackErrors(page) {
  const errors = []
  page.on("pageerror", error => errors.push(String(error)))
  page.on("console", message => {
    if (message.type() === "error") {
      errors.push(message.text())
    }
  })
  return errors
}

test("home page renders the choropleth map", async ({ page }) => {
  const errors = trackErrors(page)
  const response = await page.goto("/")
  expect(response.status()).toBe(200)
  await expect(page).toHaveTitle("Decarb My State")

  const states = page.locator("svg path[name]")
  await expect(states).toHaveCount(51)

  const fills = await states.evaluateAll(elements =>
    elements.map(element => getComputedStyle(element).fill)
  )
  // More than one distinct fill means the data-driven shading rendered
  expect(new Set(fills).size).toBeGreaterThan(1)
  expect(errors).toEqual([])
})

test("state page shows data freshness and a working year selector", async ({
  page,
}) => {
  const errors = trackErrors(page)
  await page.goto("/minnesota")

  await expect(page.locator("text=Data updated:")).toBeVisible()

  const selector = page.locator("#snapshot-year")
  await expect(selector.locator("option")).toHaveCount(33)

  const graphTitle = page.locator("div.graph-title").first()
  await expect(graphTitle).toContainText("(2022)")

  await selector.selectOption("1995")
  await expect(graphTitle).toContainText("(1995)")

  await expect(page.locator(".snapshot-values")).toContainText("Total (1995)")
  expect(errors).toEqual([])
})

test("plant pages never render NaN", async ({ page }) => {
  // Covers the plants whose source values are blank or parenthesized
  const paths = [
    "/tennessee/power-plant/allen",
    "/wisconsin/power-plant/wisconsin-rapids-paper-mill",
    "/wisconsin/power-plant/fitchburg-generating-station",
    "/minnesota/power-plant/sherburne-county",
  ]

  for (const path of paths) {
    const response = await page.goto(path)
    expect(response.status(), path).toBe(200)
    const text = await page.locator("body").innerText()
    expect(text, path).not.toContain("NaN")
    expect(text, path).not.toContain("undefined")
  }
})

test("unknown routes serve the 404 page", async ({ page }) => {
  const response = await page.goto("/definitely-not-a-real-page")
  expect(response.status()).toBe(404)
  await expect(page.locator("body")).toContainText("Page not found")
})

test("nav reaches the supporting pages", async ({ page }) => {
  for (const [path, heading] of [
    ["/about", "About Decarb My State"],
    ["/faq", "Frequently Asked Questions"],
    ["/terminology", "Terminology"],
    ["/take-action", "Take Action!"],
  ]) {
    const response = await page.goto(path)
    expect(response.status(), path).toBe(200)
    await expect(page.locator("h1").first()).toContainText(heading)
  }
})

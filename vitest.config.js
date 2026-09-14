import { defineConfig } from "vitest/config"

export default defineConfig({
  test: {
    // Unit tests only; the Playwright suite in tests/ runs via `yarn test:e2e`
    include: ["src/**/*.test.js"],
    environment: "node",
  },
})

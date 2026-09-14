import { defineConfig } from "astro/config"
import react from "@astrojs/react"

// https://astro.build/config
export default defineConfig({
  site: "https://decarbmystate.com",
  // Gatsby served `static/` at the site root, so point Astro's public dir there
  // instead of moving thousands of social card / power plant images.
  publicDir: "./static",
  integrations: [react()],
  build: {
    // Match the old Gatsby URL shape: /about -> /about/index.html
    format: "directory",
  },
})

/**
 * Minimal foreground static server for `dist/`, used by the Playwright suite.
 *
 * `astro preview` detaches into a background daemon, which Playwright's
 * `webServer` cannot manage (and which leaves stray processes behind). This
 * serves the built output with the routing the Cloudflare Worker provides:
 * directory indexes (`/minnesota` -> `/minnesota/index.html`) and the
 * `404.html` fallback for unmatched paths.
 */
import { createReadStream, existsSync, statSync } from "node:fs"
import { createServer } from "node:http"
import { extname, join, normalize, resolve } from "node:path"

const distDir = resolve("dist")
const port = Number(process.env.PORT || 8000)
const host = process.env.HOST || "127.0.0.1"

const contentTypes = {
  ".css": "text/css; charset=utf-8",
  ".eot": "application/vnd.ms-fontobject",
  ".html": "text/html; charset=utf-8",
  ".ico": "image/x-icon",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".map": "application/json; charset=utf-8",
  ".otf": "font/otf",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".ttf": "font/ttf",
  ".txt": "text/plain; charset=utf-8",
  ".webmanifest": "application/manifest+json",
  ".webp": "image/webp",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".xml": "application/xml",
}

function sendFile(res, status, filePath) {
  res.writeHead(status, {
    "content-type": contentTypes[extname(filePath)] || "application/octet-stream",
  })
  createReadStream(filePath).pipe(res)
}

createServer((req, res) => {
  const { pathname } = new URL(req.url, `http://${host}`)
  const relative = normalize(decodeURIComponent(pathname)).replace(
    /^(\.\.[/\\])+/,
    ""
  )

  let filePath = join(distDir, relative)

  if (existsSync(filePath) && statSync(filePath).isDirectory()) {
    filePath = join(filePath, "index.html")
  }

  if (!existsSync(filePath) && existsSync(`${filePath}.html`)) {
    filePath = `${filePath}.html`
  }

  if (!existsSync(filePath) || statSync(filePath).isDirectory()) {
    const notFound = join(distDir, "404.html")
    if (existsSync(notFound)) {
      return sendFile(res, 404, notFound)
    }
    res.writeHead(404, { "content-type": "text/plain" })
    return res.end("Not found")
  }

  return sendFile(res, 200, filePath)
}).listen(port, host, () => {
  console.log(`Serving dist/ at http://${host}:${port}`)
})

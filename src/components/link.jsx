import React from "react"

/**
 * Drop-in replacement for Gatsby's `Link`. The site is fully static, so plain
 * anchors are enough (and avoid shipping a client-side router).
 */
export default function Link({ to, children, ...rest }) {
  return (
    <a href={to} {...rest}>
      {children}
    </a>
  )
}

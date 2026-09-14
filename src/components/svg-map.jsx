import React from "react"

/**
 * Minimal replacement for `react-svg-map`'s `SVGMap`, which is unmaintained and
 * only declares a React 16 peer range. This renders the same markup the old
 * dependency did (verified against the production Gatsby build):
 *
 *   <svg class="svg-map" role="none" aria-label="...">
 *     <path id name d class tabindex="0" role="link" aria-label="..." />
 *     ...
 *   </svg>
 *
 * so the existing CSS (`#frames`, `.state`, `.choropleth*`) and the event
 * handlers in `state-emissions-map.jsx` keep working unchanged.
 */
export default function SVGMap({
  map,
  locationClassName,
  locationRole,
  onLocationFocus,
  onLocationMouseOver,
  onLocationMouseOut,
  onLocationBlur,
  onLocationClick,
  onLocationKeyDown,
}) {
  const handler = fn => (fn ? event => fn(event) : undefined)

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox={map.viewBox}
      className="svg-map"
      role="none"
      aria-label={map.label}
    >
      {map.locations.map(location => (
        <path
          key={location.id}
          id={location.id}
          name={location.name}
          d={location.path}
          className={
            locationClassName
              ? locationClassName(location)
              : "svg-map__location"
          }
          tabIndex={0}
          role={locationRole}
          aria-label={location.name}
          onFocus={handler(onLocationFocus)}
          onMouseOver={handler(onLocationMouseOver)}
          onMouseOut={handler(onLocationMouseOut)}
          onBlur={handler(onLocationBlur)}
          onClick={handler(onLocationClick)}
          onKeyDown={handler(onLocationKeyDown)}
        />
      ))}
    </svg>
  )
}

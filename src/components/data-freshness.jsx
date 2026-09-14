import React, { useState } from "react"

import { stateDataFreshness } from "../constants/data-freshness"

/**
 * "Updated at" provenance block shown on every state page.
 *
 * Renders a one-line summary of the newest data on the page (emissions and
 * power generation) plus an expandable list of every dataset's coverage and
 * publication date, so users can see exactly which reporting periods each
 * number comes from.
 */
export default function DataFreshness({ className = "" }) {
  const [isOpen, setIsOpen] = useState(false)

  const emissions = stateDataFreshness.find(d => d.slug === "emissions")
  const generation = stateDataFreshness.find(d => d.slug === "power-generation")

  return (
    <div className={"data-freshness " + className}>
      <p className="small text-secondary mb-1">
        <strong>Data updated:</strong> emissions through {emissions.coverage}{" "}
        (reported {emissions.reportDate}); power generation through{" "}
        {generation.coverage} (reported {generation.reportDate}).{" "}
        <button
          type="button"
          className="btn btn-link btn-sm p-0 align-baseline"
          onClick={() => setIsOpen(open => !open)}
          aria-expanded={isOpen}
        >
          {isOpen ? "Hide all data sources" : "All data sources"}
        </button>
      </p>

      {isOpen && (
        <dl className="data-freshness-list small text-secondary mb-0">
          {stateDataFreshness.map(dataset => (
            <div key={dataset.slug} className="mb-1">
              <dt className="d-inline font-weight-bold">{dataset.label}: </dt>
              <dd className="d-inline">
                {dataset.source} — covers {dataset.coverage}; updated{" "}
                {dataset.reportDate}
              </dd>
            </div>
          ))}
        </dl>
      )}
    </div>
  )
}

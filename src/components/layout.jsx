import React from "react"
import PropTypes from "prop-types"
import { Row, Col } from "react-bootstrap"
import NewTabIcon from "./new-tab-icon"
import Header from "./header"

/**
 * Site chrome (header + footer) shared by every React island. Global styles and
 * the bootstrap stylesheet are imported once in `src/layouts/Base.astro`, and
 * the document head is rendered by Astro, so this only needs the title.
 */
const Layout = ({ children }) => {
  return (
    <>
      <Header siteTitle="Decarb My State" />
      <main role="main">
        <div className="container">
          <Row>
            <Col>{children}</Col>
          </Row>
        </div>
      </main>
      <footer>
        <hr />
        &#169; 2022 - A Project From{" "}
        <a href="https://chihacknight.org" target="_blank" rel="noreferrer">
          Chi Hack Night
          <NewTabIcon />
        </a>
      </footer>
    </>
  )
}

Layout.propTypes = {
  children: PropTypes.node.isRequired,
}

export default Layout

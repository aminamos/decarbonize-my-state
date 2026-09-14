import React from "react"
import Link from "../components/link"
import Layout from "../components/layout"
import OilPlantImg from "../images/oil-plant.png?url"

const NotFoundPage = () => (
  <Layout>
    <div className="error-page">
      <img src={OilPlantImg} alt="Oil power plant" />
      <div>
        <h1 className="error-page-h" id="main">
          404: Page not found
        </h1>
        <p className="error-page-p">
          Sorry, we can't find that page. Try going back to the{" "}
          <Link to="/">home page</Link>.
        </p>
      </div>
      <img src={OilPlantImg} alt="Oil power plant" />
    </div>
  </Layout>
)

export default NotFoundPage

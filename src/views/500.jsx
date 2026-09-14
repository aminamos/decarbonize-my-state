import React from "react"
import Layout from "../components/layout"
import CoalPlant from "../images/coal-plant.png?url"

const ServerError = () => (
  <Layout>
    <div className="error-page">
      <img src={CoalPlant} alt="Coal Power Plant" />
      <div>
        <h1>Server Error</h1>
        <p>Something went wrong. Please come again later.</p>
      </div>
      <img src={CoalPlant} alt="Coal Power Plant" />
    </div>
  </Layout>
)

export default ServerError

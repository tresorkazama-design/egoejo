import React from "react";
import { createBrowserRouter } from "react-router-dom";

import Layout from "../components/Layout.jsx";
import Home from "../pages/Home.jsx";
import Univers from "../pages/Univers.jsx";
import Admin from "../pages/Admin.jsx";

import Vision from "../pages/Vision.jsx";
import Alliances from "../pages/Alliances.jsx";
import Rejoindre from "../pages/Rejoindre.jsx";

function NotFound() {
  return (
    <div
      style={{
        minHeight: "60dvh",
        display: "grid",
        placeItems: "center",
        background: "#060b0a",
        color: "#dffdf5",
        fontFamily:
          "system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif",
        padding: "2rem",
        textAlign: "center",
      }}
    >
      <div>
        <div
          style={{
            color: "#74ffd7",
            fontWeight: 600,
            fontSize: "1.2rem",
            marginBottom: ".5rem",
          }}
        >
          404 – Page introuvable
        </div>
        <p style={{ maxWidth: "480px", margin: "0 auto", lineHeight: 1.5 }}>
          Nous n'avons pas trouvé la page demandée. Retournez vers l'accueil pour
          explorer le vivant.
        </p>
      </div>
    </div>
  );
}

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      { index: true, element: <Home /> },
      { path: "univers", element: <Univers /> },
      { path: "vision", element: <Vision /> },
      { path: "alliances", element: <Alliances /> },
      { path: "rejoindre", element: <Rejoindre /> },
      { path: "admin", element: <Admin /> },
      { path: "*", element: <NotFound /> },
    ],
  },
]);

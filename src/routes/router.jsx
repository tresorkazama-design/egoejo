import React, { lazy, Suspense } from "react";
import { createBrowserRouter } from "react-router-dom";

const Layout = lazy(() => import("../components/Layout.jsx"));
const Home = lazy(() => import("../pages/Home.jsx"));
const Univers = lazy(() => import("../pages/Univers.jsx"));
const Admin = lazy(() => import("../pages/Admin.jsx"));
const Projets = lazy(() => import("../pages/Projets.jsx"));
const Vision = lazy(() => import("../pages/Vision.jsx"));
const Alliances = lazy(() => import("../pages/Alliances.jsx"));
const Rejoindre = lazy(() => import("../pages/Rejoindre.jsx"));

function suspense(element) {
  return <Suspense fallback={<div />}>{element}</Suspense>;
}

function NotFound() {
  return (
    <div
      style={{
        minHeight: "60dvh",
        display: "grid",
        placeItems: "center",
        background: "#060b0a",
        color: "#dffdf5",
        fontFamily: "system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif",
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
          404 — Page non trouvée
        </div>
        <div style={{ opacity: 0.7, fontSize: ".9rem", lineHeight: 1.4 }}>
          Cette route n'existe pas (encore).
        </div>
      </div>
    </div>
  );
}

export const router = createBrowserRouter([
  {
    path: "/",
    element: suspense(<Layout />),
    errorElement: <NotFound />,
    children: [
      { index: true, element: suspense(<Home />) },
      { path: "univers", element: suspense(<Univers />) },
      { path: "admin", element: suspense(<Admin />) },
      { path: "vision", element: suspense(<Vision />) },
      { path: "alliances", element: suspense(<Alliances />) },
      { path: "rejoindre", element: suspense(<Rejoindre />) },
      { path: "projets", element: suspense(<Projets />) },
      { path: "*", element: <NotFound /> },
    ],
  },
]);
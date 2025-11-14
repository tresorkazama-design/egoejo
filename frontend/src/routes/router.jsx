import React, { lazy, Suspense } from "react";
import { createBrowserRouter } from "react-router-dom";

const Layout = lazy(() => import("../components/Layout.jsx"));
const Home = lazy(() => import("../pages/Home.jsx"));
const Univers = lazy(() => import("../pages/Univers.jsx"));
const Vision = lazy(() => import("../pages/Vision.jsx"));
const Citations = lazy(() => import("../pages/Citations.jsx"));
const Alliances = lazy(() => import("../pages/Alliances.jsx"));
const Community = lazy(() => import("../pages/Community.jsx"));
const Polls = lazy(() => import("../pages/Polls.jsx"));
const Projets = lazy(() => import("../pages/Projets.jsx"));
const Rejoindre = lazy(() => import("../pages/Rejoindre.jsx"));
const Admin = lazy(() => import("../pages/Admin.jsx"));
const AdminModeration = lazy(() => import("../pages/AdminModeration.jsx"));

const withSuspense = (element) => <Suspense fallback={<div className="page-loading" />}>{element}</Suspense>;

const NotFound = () => (
  <div className="page page--center">
    <h1>Page introuvable</h1>
    <p>Cette route n'existe pas encore.</p>
  </div>
);

export default createBrowserRouter([
  {
    path: "/",
    element: withSuspense(<Layout />),
    errorElement: <NotFound />,
    children: [
      { index: true, element: withSuspense(<Home />) },
      { path: "univers", element: withSuspense(<Univers />) },
      { path: "vision", element: withSuspense(<Vision />) },
      { path: "citations", element: withSuspense(<Citations />) },
      { path: "alliances", element: withSuspense(<Alliances />) },
      { path: "communaute", element: withSuspense(<Community />) },
      { path: "votes", element: withSuspense(<Polls />) },
      { path: "projets", element: withSuspense(<Projets />) },
      { path: "rejoindre", element: withSuspense(<Rejoindre />) },
      { path: "admin", element: withSuspense(<Admin />) },
      { path: "admin/moderation", element: withSuspense(<AdminModeration />) },
      { path: "*", element: <NotFound /> },
    ],
  },
]);

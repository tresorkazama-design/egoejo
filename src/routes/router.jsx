import React from "react";
import { createBrowserRouter } from "react-router-dom";
import Layout from "../components/Layout.jsx";
import Home from "../pages/Home.jsx";
import Univers from "../pages/Univers.jsx";

function NotFound(){
  return <div style={{padding:"2rem", color:"#fff"}}>404 — Page non trouvée</div>;
}

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    errorElement: <NotFound />,
    children: [ { path: "*", element: <NotFound /> },
      { index: true, element: <Home /> },
      { path: "univers", element: <Univers /> },   // ⬅️ la route demandée
    ],
  },
]);


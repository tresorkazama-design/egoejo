import { lazy, Suspense } from "react";
import React from "react";
import { createBrowserRouter } from "react-router-dom";

import Layout from "../components/Layout.jsx";
import Home from "../pages/Home.jsx";
import Univers from "../pages/Univers.jsx";
import Admin from "../pages/Admin.jsx";

const Vision = lazy(() => import("../pages/Vision.jsx"));
const Alliances = lazy(() => import("../pages/Alliances.jsx"));
const Rejoindre = lazy(() => import("../pages/Rejoindre.jsx"));

function NotFound(){
  return (
    <div
      style={{
        minHeight:"60dvh",
        display:"grid",
        placeItems:"center",
        background:"#060b0a",
        color:"#dffdf5",
        fontFamily:"system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif",
        padding:"2rem",
        textAlign:"center"
      }}
    >
      <div>
        <div
          style={{
            color:"#74ffd7",
            fontWeight:600,
            fontSize:"1.2rem",
            marginBottom:".5rem"
          }}
        >
          404 ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â Page non trouvÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©e
        </div>
        <div style={{opacity:.7,fontSize:".9rem",lineHeight:1.4}}>
          Cette route n'existe pas (encore).
        </div>
      </div>
    </div>
  );
}

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    errorElement: <NotFound />,
    children: [ { path: "admin", element: <Admin /> }, { path: "/admin", element: <Admin /> },
      { index: true, element: <Home /> }, { path: "admin", element: <Admin /> },
      { path: "univers", element: <Univers /> },{ path: "vision", element: <Suspense fallback={<div/>}><Vision/></Suspense> },
      { path: "alliances", element: <Suspense fallback={<div/>}><Alliances/></Suspense> },
      { path: "rejoindre", element: <Suspense fallback={<div/>}><Rejoindre/></Suspense> },
      { path: "*", element: <NotFound /> },
    ],
  },
]);













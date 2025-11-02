import React from "react";
import { createBrowserRouter } from "react-router-dom";

import Layout from "../components/Layout.jsx";
import Home from "../pages/Home.jsx";
import Univers from "../pages/Univers.jsx";
import Admin from "../pages/Admin.jsx";
import Admin from "../pages/Admin.jsx";
import Vision from "../pages/Vision.jsx";
import Alliances from "../pages/Alliances.jsx";
import Rejoindre from "../pages/Rejoindre.jsx";

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
          404 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Page non trouvÃƒÆ’Ã‚Â©e
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
    children: [
      { index: true, element: <Home /> },
      { path: "univers", element: <Univers /> },
      { path: "admin", element: <Admin /> },
      { path: "admin", element: <Admin /> },
      { path: "vision", element: <Vision /> },
      { path: "alliances", element: <Alliances /> },
      { path: "rejoindre", element: <Rejoindre /> },
      { path: "*", element: <NotFound /> },
    ],
  },
]);
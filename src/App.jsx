import React, { Suspense } from "react";
import { RouterProvider } from "react-router-dom";

let RouterDefault;
try {
  RouterDefault = require("./routes/router.jsx").default;
} catch (e) {
  console.warn("[EGOEJO] router.jsx introuvable ou export non standard", e);
}

function isComponent(x) {
  // composant fonction
  if (typeof x === "function") return true;
  // composant objet React (rare) : $$typeof présent
  if (x && typeof x === "object" && "$$typeof" in x) return true;
  return false;
}

export default function App() {
  try {
    if (RouterDefault) {
      // si composant
      if (isComponent(RouterDefault)) {
        return (
          <div style={{minHeight:"100vh", background:"#fff", color:"#111"}}>
            <RouterDefault />
          </div>
        );
      }
      // sinon on suppose objet "router"
      return (
        <div style={{minHeight:"100vh", background:"#fff", color:"#111"}}>
          <RouterProvider router={RouterDefault} />
        </div>
      );
    }
  } catch (e) {
    console.error("[EGOEJO] App render error", e);
  }
  return (
    <div style={{padding:16, fontFamily:"system-ui", background:"#fff", color:"#111"}}>
      <h2>Application en maintenance</h2>
      <p>Le routeur n'a pas pu être chargé. Vérifie <code>src/routes/router.jsx</code>.</p>
    </div>
  );
}

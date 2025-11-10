import React, { useEffect, useState } from "react";
import { RouterProvider } from "react-router-dom";

export default function App() {
  const [routerModule, setRouterModule] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const mod = await import("./routes/router.jsx");
        setRouterModule(mod);
      } catch (err) {
        console.error("[EGOEJO] router import error:", err);
        setError(err);
      }
    })();
  }, []);

  if (error) {
    return (
      <div style={{ padding: 16, fontFamily: "system-ui", background: "#fff", color: "#111" }}>
        <h2>Application indisponible</h2>
        <p>Le routeur n'a pas pu être chargé. Vérifie <code>src/routes/router.jsx</code>.</p>
        <pre style={{ whiteSpace: "pre-wrap" }}>{String(error)}</pre>
      </div>
    );
  }

  if (!routerModule) return <div />;

  const router = routerModule.router || routerModule.default;
  if (!router) {
    return (
      <div style={{ padding: 16, fontFamily: "system-ui", background: "#fff", color: "#111" }}>
        <h2>Application indisponible</h2>
        <p>Impossible de trouver un objet <code>router</code> exporté depuis <code>src/routes/router.jsx</code>.</p>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "#fff", color: "#111" }}>
      <RouterProvider router={router} />
    </div>
  );
}


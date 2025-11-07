import React from "react";
import { createRoot } from "react-dom/client";

function forceWhite() {
  try {
    document.documentElement.style.background = "#fff";
    document.body.style.background = "#fff";
    document.body.style.color = "#111";
  } catch {}
}

async function bootstrap() {
  forceWhite();
  const root = createRoot(document.getElementById("root"));
  try {
    // Si on est sur /admin => afficher l'Admin SANS passer par le router
    if (location.pathname.startsWith("/admin")) {
      const Admin = (await import("./pages/Admin.jsx")).default;
      root.render(<Admin />);
      return;
    }

    // Sinon: tenter l'ancienne appli si présente
    try {
      const Legacy = (await import("./main.backup.jsx")).default;
      root.render(<Legacy />);
      return;
    } catch (e) {
      // Dernier recours: message simple
      root.render(<div style={{padding:16,fontFamily:"system-ui"}}>Application en maintenance.</div>);
      console.error("[EGOEJO] fallback main:", e);
    }
  } catch (e) {
    root.render(<div style={{padding:16,fontFamily:"system-ui"}}>Erreur: {String(e)}</div>);
    console.error("[EGOEJO] bootstrap error:", e);
  }
}

bootstrap();

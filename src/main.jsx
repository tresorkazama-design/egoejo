import React from "react";
import { createRoot } from "react-dom/client";

function forceWhite() {
  try {
    document.documentElement.style.background = "#000"; // laisser le CSS global si besoin mais…
    document.body.style.background = "#fff";
    document.body.style.color = "#111";
    const r = document.getElementById("root");
    if (r) { r.style.background = "#fff"; r.style.minHeight = "100vh"; r.style.color = "#111"; }
  } catch {}
}

async function bootstrap() {
  const rootEl = document.getElementById("root");
  const root = createRoot(rootEl);
  forceWhite();
  try {
    if (location.pathname.startsWith("/admin")) {
      const Admin = (await import("./pages/Admin.jsx")).default;
      root.render(<Admin />);
      return;
    }
    const Legacy = (await import("./main.backup.jsx")).default;
    root.render(<Legacy />);
  } catch (e) {
    root.render(<div style={{padding:16,fontFamily:"system-ui"}}>Application chargée (mode fallback). {String(e)}</div>);
    console.error("[EGOEJO bootstrap]", e);
  }
}
bootstrap();

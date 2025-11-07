import React from "react";
import { createRoot } from "react-dom/client";

async function bootstrap(){
  const root = createRoot(document.getElementById("root"));
  try{
    if (location.pathname.startsWith("/admin")) {
      const Admin = (await import("./pages/Admin.jsx")).default;
      root.render(<Admin />);
      return;
    }
    const Home = (await import("./pages/Home.minimal.jsx")).default;
    root.render(<Home />);
  }catch(e){
    root.render(<div style={{padding:16,fontFamily:"system-ui"}}>Erreur: {String(e)}</div>);
    console.error(e);
  }
}
bootstrap();

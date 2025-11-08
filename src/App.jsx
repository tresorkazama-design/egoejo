import React, { useEffect, useMemo, useState, lazy, Suspense } from "react";
import { RouterProvider } from "react-router-dom";

const Admin = lazy(() => import("./pages/Admin.jsx"));

function AdminGate() {
  return (
    <div style={{minHeight:"100vh",background:"#fff",color:"#111"}}>
      <Suspense fallback={<div/>}>
        <Admin />
      </Suspense>
    </div>
  );
}

export default function App() {
  const isAdmin = useMemo(() => location.pathname.startsWith("/admin"), []);
  const [mod, setMod] = useState(null);
  const [err, setErr] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const m = await import("./routes/router.jsx");
        setMod(m);
      } catch (e) {
        console.error("[EGOEJO] router import error:", e);
        setErr(e);
      }
    })();
  }, []);

  if (isAdmin) return <AdminGate/>;
  if (err) {
    return (
      <div style={{padding:16,fontFamily:"system-ui",background:"#fff",color:"#111"}}>
        <h2>Application en maintenance</h2>
        <p>Le routeur n'a pas pu Ãªtre chargÃ©. VÃ©rifie <code>src/routes/router.jsx</code>.</p>
        <pre style={{whiteSpace:"pre-wrap"}}>{String(err)}</pre>
      </div>
    );
  }
  if (!mod) return <div/>;

  // Cas 1: exporte un composant React par dÃ©faut
  const MaybeComp = mod.default;
  const looksLikeComponent =
    typeof MaybeComp === "function" &&
    ((MaybeComp.prototype && MaybeComp.prototype.isReactComponent) || /^[A-Z]/.test(MaybeComp.name || ""));

  if (looksLikeComponent) {
    return <div style={{minHeight:"100vh",background:"#fff",color:"#111"}}><MaybeComp/></div>;
  }

  // Cas 2: exporte un objet "router" (createBrowserRouter)
  const router = mod.router || (typeof MaybeComp === "object" ? MaybeComp : null);
  if (router) {
    return <div style={{minHeight:"100vh",background:"#fff",color:"#111"}}><RouterProvider router={router}/></div>;
  }

  // Fallback
  return (
    <div style={{padding:16,fontFamily:"system-ui",background:"#fff",color:"#111"}}>
      <h2>Application en maintenance</h2>
      <p>Le routeur n'a pas pu Ãªtre dÃ©tectÃ©. Exporte soit un composant React par dÃ©faut, soit un objet <code>router</code>.</p>
    </div>
  );
}

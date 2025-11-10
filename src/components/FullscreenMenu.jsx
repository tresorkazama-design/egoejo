import { useEffect } from "react";
import { Link } from "react-router-dom";

export default function FullscreenMenu({ open, onClose }) {
  useEffect(() => {
    const onKey = (e) => { if (e.key === "Escape") onClose?.(); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onClose]);

  if (!open) return null;

  const overlay = {
    position:"fixed", inset:0, zIndex:9999,
    background:"rgba(5,10,9,.92)", backdropFilter:"blur(4px)",
    display:"grid", placeItems:"center"
  };
  const wrap = { width:"min(1100px,90vw)", padding:"min(6vh,40px) 0" };
  const title = { color:"#c8ffee", letterSpacing:".02em", fontSize:"min(12vw,110px)", lineHeight:.9, margin:0 };
  const list = { display:"grid", gap:"min(2vh,18px)", marginTop:"min(3vh,24px)" };
  const item = { color:"#e9fff7", fontSize:"min(8.2vw,56px)", fontWeight:800, textDecoration:"none" };
  const close = {
    position:"fixed", top:14, right:14, width:86, height:62,
    background:"#20f3a6", color:"#05110e", fontWeight:900, border:"none",
    cursor:"pointer", borderRadius:"12px", boxShadow:"0 0 0 2px #0a1e18 inset", zIndex:10000
  };

  const go = (to) => (e) => { onClose?.(); };

  return (
    <div style={overlay} onClick={onClose}>
      <button aria-label="Fermer le menu" style={close} onClick={onClose}>CLOSE</button>
      <div style={wrap} onClick={(e)=>e.stopPropagation()}>
        <h1 style={title}>MENU</h1>
        <nav style={list}>
          <Link to="/"          onClick={go("/")}          style={item}>Accueil</Link>
          <Link to="/univers"   onClick={go("/univers")}   style={item}>Univers</Link>
          <Link to="/vision"    onClick={go("/vision")}    style={item}>Vision</Link>
          <Link to="/alliances" onClick={go("/alliances")} style={item}>Alliances</Link>
          <Link to="/rejoindre" onClick={go("/rejoindre")} style={item}>Rejoindre</Link>
          <Link to="/projets"   onClick={go("/projets")}   style={item}>Projets</Link>
        </nav>
      </div>
    </div>
  );
}
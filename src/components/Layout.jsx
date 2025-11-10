import React, { useEffect, useMemo, useRef, useState } from "react";
import { Outlet, NavLink } from "react-router-dom";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

import FullscreenMenu from "./FullscreenMenu.jsx";
import PageTransition from "./PageTransition.jsx";
import { initScrollAnimations, cleanupScrollAnimations } from "../utils/scrollAnimations.js";

gsap.registerPlugin(ScrollTrigger);

const SHELL_STYLE = {
  minHeight: "100dvh",
  background: "#060b0a",
  color: "#dffdf5",
  fontFamily: "system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif",
  display: "flex",
  flexDirection: "column",
};

const HEADER_STYLE = {
  position: "sticky",
  top: 0,
  zIndex: 100,
  background: "rgba(6,11,10,.6)",
  WebkitBackdropFilter: "blur(6px)",
  backdropFilter: "blur(6px)",
  borderBottom: "1px solid rgba(255,255,255,.07)",
  padding: "1rem 6vw",
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  flexWrap: "wrap",
  rowGap: "0.75rem",
};

const MENU_BUTTON_STYLE = {
  position: "fixed",
  top: 14,
  right: 14,
  zIndex: 9998,
  width: 86,
  height: 62,
  borderRadius: 12,
  border: "none",
  cursor: "pointer",
  background: "#20f3a6",
  color: "#05110e",
  fontWeight: 900,
  boxShadow: "0 0 0 2px #0a1e18 inset",
  fontFamily: "inherit",
};

const NAV_STYLE = {
  display: "flex",
  flexWrap: "wrap",
  gap: "16px",
  fontSize: ".9rem",
};

const FOOTER_STYLE = {
  borderTop: "1px solid rgba(255,255,255,.07)",
  padding: "1.5rem 6vw",
  fontSize: ".75rem",
  lineHeight: 1.4,
  color: "#9bf6e5",
  background: "radial-gradient(circle at 50% 0%,rgba(0,255,170,.07) 0%,rgba(0,0,0,0) 70%)",
};

export default function Layout() {
  const [menuOpen, setMenuOpen] = useState(false);
  const headerRef = useRef(null);
  const footerRef = useRef(null);
  const footerContentRef = useRef(null);

  const navLinks = useMemo(
    () => [
      { to: "/univers", label: "Univers" },
      { to: "/vision", label: "Vision" },
      { to: "/alliances", label: "Alliances" },
      { to: "/rejoindre", label: "Rejoindre", highlight: true },
    ],
    []
  );

  useEffect(() => {
    const prefersReduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduce) return;

    const header = headerRef.current;
    if (!header) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        header,
        { background: "rgba(6,11,10,.2)", borderBottomColor: "rgba(255,255,255,0)" },
        {
          background: "rgba(6,11,10,.9)",
          borderBottomColor: "rgba(255,255,255,.12)",
          scrollTrigger: {
            trigger: document.body,
            start: "120px top",
            end: "240px top",
            scrub: true,
          },
        }
      );
    }, header);

    return () => ctx.revert();
  }, []);

  useEffect(() => {
    initScrollAnimations();
    return () => cleanupScrollAnimations();
  }, []);

  return (
    <div style={SHELL_STYLE}>
      <style
        id="egoejo-hide-inline"
        dangerouslySetInnerHTML={{
          __html: `
:root body header a[href*="/univers"], :root body header a[href*="/vision"], :root body header a[href*="/alliances"], :root body header a[href*="/rejoindre"],
:root body nav a[href*="/univers"], :root body nav a[href*="/vision"], :root body nav a[href*="/alliances"], :root body nav a[href*="/rejoindre"],
:root body .site-nav a[href*="/univers"], :root body .site-nav a[href*="/vision"], :root body .site-nav a[href*="/alliances"], :root body .site-nav a[href*="/rejoindre"],
:root body .top-nav  a[href*="/univers"], :root body .top-nav  a[href*="/vision"], :root body .top-nav  a[href*="/alliances"], :root body .top-nav  a[href*="/rejoindre"]{
  display:none!important
}
`,
        }}
      />
      <script
        dangerouslySetInnerHTML={{
          __html: `
(function(){
  const kill=["univers","vision","alliances","rejoindre"];
  const hide=()=>{document.querySelectorAll('header a,nav a,.site-nav a,.top-nav a').forEach(a=>{
    const t=(a.textContent||"").trim().toLowerCase(); if(kill.includes(t)) a.style.display="none";
  });};
  hide(); const mo=new MutationObserver(hide); mo.observe(document.body,{subtree:true,childList:true});
})();
`,
        }}
      />

      <header ref={headerRef} style={HEADER_STYLE}>
        <button
          type="button"
          aria-label={menuOpen ? "Fermer le menu" : "Ouvrir le menu"}
          onClick={() => setMenuOpen((v) => !v)}
          style={MENU_BUTTON_STYLE}
        >
          {menuOpen ? "CLOSE" : "MENU"}
        </button>

        <NavLink
          to="/"
          style={{
            textDecoration: "none",
            color: "#74ffd7",
            fontWeight: 700,
            fontSize: "1rem",
            textShadow: "0 0 10px rgba(0,255,170,.35)",
          }}
        >
          EGOEJO
        </NavLink>

        <nav style={NAV_STYLE}>
          {navLinks.map(({ to, label, highlight }) => (
            <NavLink
              key={to}
              to={to}
              style={{
                textDecoration: "none",
                color: highlight ? "#74ffd7" : "#9bf6e5",
                fontWeight: highlight ? 600 : 400,
                textShadow: highlight ? "0 0 10px rgba(0,255,170,.5)" : "none",
              }}
            >
              {label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main style={{ flex: "1 1 auto" }}>
        <PageTransition>
          <Outlet />
        </PageTransition>
      </main>

      <footer ref={footerRef} className="footer_area" style={FOOTER_STYLE}>
        <div ref={footerContentRef} className="footer__container" style={{ opacity: 0.85 }}>
          EGOEJO — Soutenir le vivant, et apprendre à habiter la Terre autrement.
        </div>
      </footer>

      <FullscreenMenu open={menuOpen} onClose={() => setMenuOpen(false)} />
    </div>
  );
}

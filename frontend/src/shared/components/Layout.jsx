import React, { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";

import { initScrollAnimations, cleanupScrollAnimations } from "../../utils/scrollAnimations.js";
import Logo3D from "./Logo3D.jsx";
import PageTransition from "./PageTransition.jsx";

const NAV_LINKS = [
  { to: "/", label: "Accueil", exact: true },
  { to: "/univers", label: "Univers" },
  { to: "/vision", label: "Vision" },
  { to: "/citations", label: "Citations" },
  { to: "/alliances", label: "Alliances" },
  { to: "/projets", label: "Projets" },
  { to: "/communaute", label: "Communauté" },
  { to: "/votes", label: "Votes" },
  { to: "/rejoindre", label: "Rejoindre" },
  { to: "/admin/moderation", label: "Modération" },
];

export default function Layout() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    initScrollAnimations();
    return () => cleanupScrollAnimations();
  }, []);

  return (
    <div className="layout">
      <header className="layout-header">
        <div className="container layout-header__inner">
          <NavLink to="/" className="layout-logo" aria-label="Accueil EGOEJO">
            <Logo3D />
          </NavLink>

          <button
            type="button"
            className="layout-nav__toggle"
            aria-label={isMenuOpen ? "Fermer le menu" : "Ouvrir le menu"}
            onClick={() => setIsMenuOpen((prev) => !prev)}
          >
            <span />
            <span />
          </button>

          <nav className={`layout-nav ${isMenuOpen ? "is-open" : ""}`}>
            {NAV_LINKS.map(({ to, label, exact }) => (
              <NavLink
                key={to}
                to={to}
                end={exact}
                className={({ isActive }) => `layout-nav__link ${isActive ? "is-active" : ""}`}
                onClick={() => setIsMenuOpen(false)}
              >
                {label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main className="layout-content">
        <PageTransition>
          <Outlet />
        </PageTransition>
      </main>

      <footer className="layout-footer">
        <div className="container layout-footer__inner">
          <div>
            <span className="layout-logo" aria-hidden="true">
              <Logo3D />
            </span>
            <p className="muted">
              Soutenir le vivant, apprendre à habiter la Terre autrement. Coopérations, alliances et transmissions pour
              une planète habitable.
            </p>
          </div>
          <div className="layout-footer__nav">
            {NAV_LINKS.map(({ to, label }) => (
              <NavLink key={to} to={to} className="layout-footer__link">
                {label}
              </NavLink>
            ))}
          </div>
        </div>
      </footer>
    </div>
  );
}


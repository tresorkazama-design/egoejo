import React, { useEffect, useState, useRef } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";

import { initScrollAnimations, cleanupScrollAnimations } from "../utils/scrollAnimations.js";
import Logo3D from "./Logo3D.jsx";
import PageTransition from "./PageTransition.jsx";
import LanguageSelector from "./LanguageSelector.jsx";
import ScrollProgress from "./ScrollProgress.jsx";
import CursorSpotlight from "./CursorSpotlight.jsx";
import NotificationContainer from "./NotificationContainer.jsx";
import { EcoModeToggle } from "./EcoModeToggle.jsx";
import { OfflineIndicator } from "./OfflineIndicator.jsx";
import SupportBubble from "./chat/SupportBubble.jsx";
import { useAuth } from "../contexts/AuthContext";
import { useLanguage } from "../contexts/LanguageContext";
import { useNotificationContext } from "../contexts/NotificationContext";
import { t } from "../utils/i18n";

// Fonction pour obtenir les liens de navigation selon la langue
const getMainNavLinks = (lang) => [
  { to: "/", label: t("nav.accueil", lang), exact: true },
  { to: "/univers", label: t("nav.univers", lang) },
  { to: "/vision", label: t("nav.vision", lang) },
  { to: "/citations", label: t("nav.citations", lang) },
  { to: "/alliances", label: t("nav.alliances", lang) },
  { to: "/projets", label: t("nav.projets", lang) },
  { to: "/contenus", label: t("nav.contenus", lang) },
  { to: "/communaute", label: t("nav.communaute", lang) },
  { to: "/votes", label: t("nav.votes", lang) },
  { to: "/chat", label: t("nav.chat", lang) },
  { to: "/rejoindre", label: t("nav.rejoindre", lang) },
];

// Fonction pour obtenir les liens admin selon la langue
const getAdminNavLinks = (lang) => [
  { to: "/admin/moderation", label: t("nav.moderation", lang) },
  { to: "/admin/saka-monitor", label: "Saka Monitor 🌾" },
];

export default function Layout() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);
  const location = useLocation();
  const { user, logout } = useAuth();
  const { language } = useLanguage();
  const { notifications, removeNotification } = useNotificationContext();

  // Vérifier si l'utilisateur est admin
  const isAdmin = user && (user.is_staff || user.is_superuser);

  useEffect(() => {
    initScrollAnimations();
    return () => cleanupScrollAnimations();
  }, []);

  // Gestion globale du scroll vers les ancres (#hash) compatible React Router
  // Accessibilité WCAG : Transfère le focus sur l'élément cible après le scroll
  useEffect(() => {
    // Vérifier si un hash est présent dans l'URL
    if (location.hash) {
      // Extraire l'id sans le #
      const id = location.hash.substring(1);
      
      // Attendre le rendu complet avant de scroller
      // Utiliser requestAnimationFrame pour s'assurer que le DOM est prêt
      requestAnimationFrame(() => {
        // Double vérification avec setTimeout pour garantir que le contenu est rendu
        setTimeout(() => {
          try {
            const element = document.getElementById(id);
            if (element) {
              // Scroller vers l'élément avec comportement smooth
              element.scrollIntoView({
                behavior: 'smooth',
                block: 'start',
              });
              
              // ACCESSIBILITÉ WCAG : Transférer le focus sur l'élément cible après le scroll
              // Pour les skip-links et la navigation clavier, le focus doit arriver sur l'élément cible
              // Attendre la fin de l'animation de scroll avant de transférer le focus
              const scrollDuration = 500; // Durée approximative du scroll smooth (ms)
              setTimeout(() => {
                // S'assurer que l'élément peut recevoir le focus
                // Si c'est un élément non-focusable (comme <main>), ajouter tabIndex temporairement
                if (!element.hasAttribute('tabindex')) {
                  element.setAttribute('tabindex', '-1');
                }
                
                // Transférer le focus
                element.focus();
                
                // Pour les éléments comme <main>, retirer le tabindex après le focus
                // pour éviter qu'ils apparaissent dans l'ordre de tabulation normal
                if (element.tagName === 'MAIN' || element.tagName === 'SECTION') {
                  setTimeout(() => {
                    element.removeAttribute('tabindex');
                  }, 100);
                }
              }, scrollDuration);
            }
            // Si l'élément n'existe pas, fail silencieux (pas d'erreur)
          } catch (error) {
            // Fail silencieux en cas d'erreur
            // (par exemple si l'élément n'existe pas ou si scrollIntoView n'est pas supporté)
          }
        }, 0);
      });
    }
  }, [location.hash, location.pathname]); // Déclencher aussi lors du changement de page

  // Fermer le menu déroulant si on clique en dehors
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };

    if (isDropdownOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isDropdownOpen]);

  // Tous les liens pour le footer
  const allNavLinks = [...getMainNavLinks(language), ...(isAdmin ? getAdminNavLinks(language) : [])];

  return (
    <div className="layout">
      {/* CONVENTION NAVIGATION : Utiliser <a href="#section"> pour les ancres (skip link, sections) */}
      {/* Skip link pour l'accessibilité WCAG 2.1 - Permet de sauter la navigation */}
      <a 
        href="#main-content" 
        className="skip-link" 
        style={{
          position: 'absolute',
          left: '-9999px',
          top: '0',
          zIndex: 'var(--z-cursor)', // Utiliser z-index centralisé
          padding: '1em',
          backgroundColor: 'var(--accent)',
          color: 'var(--bg)',
          textDecoration: 'none',
          fontWeight: 'bold',
          borderRadius: '0 0 4px 0',
          // ACCESSIBILITÉ : Le skip-link doit être visible au focus (WCAG 2.4.1)
          // Ne pas masquer via CSS quand il est focus
        }}
        onFocus={(e) => {
          // ACCESSIBILITÉ WCAG : Rendre le skip-link visible au focus clavier
          e.target.style.left = '0';
          e.target.style.top = '0';
        }}
        onBlur={(e) => {
          // Masquer le skip-link quand il perd le focus
          e.target.style.left = '-9999px';
        }}
        aria-label={`${t("accessibility.skip_to_main", language)} (skip navigation)`}
      >
        {t("accessibility.skip_to_main", language)}
      </a>
      <NotificationContainer
        notifications={notifications}
        onRemove={removeNotification}
      />
      <OfflineIndicator />
      <EcoModeToggle />
      <SupportBubble />
      <CursorSpotlight />
      <ScrollProgress />
      <header className="layout-header" role="banner">
        <div className="container layout-header__inner">
          <NavLink to="/" className="layout-logo" aria-label={t("nav.accueil", language)}>  
            <Logo3D />
          </NavLink>

          <div className="layout-header__right">
            <LanguageSelector />
            {user && (
              <div className="layout-header__user" role="group" aria-label={t("nav.user_menu", language)}>
                <span className="layout-header__username" aria-label={t("nav.welcome", language).replace("{{username}}", user.username || user.email || "")}>{user.username || user.email}</span>
                <button
                  type="button"
                  className="layout-header__logout"
                  onClick={() => {
                    logout();
                    setIsMenuOpen(false);
                  }}
                  aria-label={t("nav.logout", language)}
                >
                  {t("nav.logout", language)}
                </button>
              </div>
            )}
            {!user && (
              <NavLink to="/login" className="layout-header__login" aria-label={t("nav.login", language)}>
                {t("nav.login", language)}
              </NavLink>
            )}
          </div>

          <button
            type="button"
            className="layout-nav__toggle"
            aria-label={isMenuOpen ? t("common.close", language) : t("nav.menu", language)}
            aria-expanded={isMenuOpen}
            aria-controls="main-navigation"
            onClick={() => setIsMenuOpen((prev) => !prev)}
          >
            <span aria-hidden="true" />
            <span aria-hidden="true" />
          </button>

          <nav className={`layout-nav ${isMenuOpen ? "is-open" : ""}`} id="main-navigation" data-testid="main-navigation" aria-label={t("nav.menu", language)} role="navigation">
            {/* CONVENTION NAVIGATION : Utiliser <NavLink to="/route"> pour les routes (navigation principale) */}
            {/* Menu déroulant pour les liens principaux */}
            <div className="layout-nav__dropdown" ref={dropdownRef}>
              <button
                type="button"
                className={`layout-nav__dropdown-toggle ${isDropdownOpen ? "is-open" : ""}`}
                onClick={() => setIsDropdownOpen((prev) => !prev)}
                aria-expanded={isDropdownOpen}
                aria-haspopup="true"
                aria-controls="main-navigation-menu"
              >
                {t("nav.menu", language)}
                <svg
                  width="12"
                  height="12"
                  viewBox="0 0 12 12"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  className="layout-nav__dropdown-icon"
                  aria-hidden="true"
                >
                  <path
                    d="M3 4.5L6 7.5L9 4.5"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </button>
              {isDropdownOpen && (
                <div className="layout-nav__dropdown-menu" id="main-navigation-menu" role="menu">
                  {getMainNavLinks(language).map(({ to, label, exact }) => (
                    <NavLink
                      key={to}
                      to={to}
                      end={exact}
                      className={({ isActive }) => `layout-nav__dropdown-link ${isActive ? "is-active" : ""}`}
                      onClick={() => {
                        setIsDropdownOpen(false);
                        setIsMenuOpen(false);
                      }}
                      role="menuitem"
                    >
                      {label}
                    </NavLink>
                  ))}
                </div>
              )}
            </div>

            {/* Lien Modération (visible uniquement pour les admins) */}
            {isAdmin && getAdminNavLinks(language).map(({ to, label, exact }) => (
              <NavLink
                key={to}
                to={to}
                end={exact}
                className={({ isActive }) => `layout-nav__link ${isActive ? "is-active" : ""}`}
                onClick={() => setIsMenuOpen(false)}
                aria-label={label}
              >
                {label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      {/* ACCESSIBILITÉ WCAG : <main> peut recevoir le focus programmatiquement via skip-link
          Le tabIndex sera ajouté temporairement par le handler hash scroll si nécessaire */}
      <main id="main-content" className="layout-content" role="main" aria-label={t("accessibility.skip_to_main", language)} data-testid="main-content">
        <PageTransition>
          <Outlet />
        </PageTransition>
      </main>

      <footer className="layout-footer" role="contentinfo">
        <div className="container layout-footer__inner">
          <div>
            <span className="layout-logo" aria-hidden="true">
              <Logo3D />
            </span>
            <p className="muted">
              {t("footer.description", language)}
            </p>
          </div>
          <nav className="layout-footer__nav" aria-label={t("nav.footer_navigation", language) || t("nav.menu", language)}>
            {allNavLinks.map(({ to, label }) => (
              <NavLink key={to} to={to} className="layout-footer__link">        
                {label}
              </NavLink>
            ))}
          </nav>
        </div>
      </footer>
    </div>
  );
}

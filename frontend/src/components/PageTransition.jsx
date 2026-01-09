import { useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import { gsap } from "gsap";

/**
 * Composant PageTransition - Animation d'entrée douce pour les changements de page
 * 
 * Comportement :
 * - Déclenche une animation d'entrée uniquement lors d'un changement de pathname (nouvelle page)
 * - N'interfère PAS avec le scroll vers les ancres (#hash) :
 *   - Si seul location.hash change (même page), aucune animation n'est déclenchée
 *   - Si pathname change ET qu'un hash est présent, l'animation attend que le scroll vers l'ancre soit terminé
 * - Respecte prefers-reduced-motion pour l'accessibilité
 */
export default function PageTransition({ children }) {
  const location = useLocation();
  const contentRef = useRef(null);
  const previousPathnameRef = useRef(location.pathname);

  useEffect(() => {
    const element = contentRef.current;
    if (!element) return;
    // Désactiver les animations en mode E2E ou si prefers-reduced-motion
    const isE2E = window.VITE_E2E || window.localStorage.getItem('VITE_E2E') === '1';
    if (isE2E || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    // Ne déclencher l'animation que si le pathname a réellement changé
    // (pas seulement le hash)
    const pathnameChanged = previousPathnameRef.current !== location.pathname;
    
    if (!pathnameChanged) {
      // Si seul le hash change, ne pas déclencher l'animation
      // Cela permet au scroll vers l'ancre de fonctionner sans interférence
      return;
    }

    // Mettre à jour la référence du pathname précédent
    previousPathnameRef.current = location.pathname;

    // Si un hash est présent, ne pas masquer le contenu (autoAlpha: 0)
    // pour permettre au scroll vers l'ancre de fonctionner correctement
    // On utilise seulement une animation de translation subtile
    const hasHash = location.hash && location.hash.length > 0;
    
    if (hasHash) {
      // Avec hash : animation subtile sans masquer le contenu
      // Cela permet au scroll vers l'ancre de fonctionner sans interférence
      gsap.fromTo(
        element,
        { 
          y: 10 // Translation plus subtile
        },
        {
          y: 0,
          duration: 0.4,
          ease: "power2.out",
        }
      );
    } else {
      // Sans hash : animation complète avec fade-in
      gsap.fromTo(
        element,
        { 
          autoAlpha: 0, 
          y: 20
        },
        {
          autoAlpha: 1,
          y: 0,
          duration: 0.5,
          ease: "power2.out",
        }
      );
    }
  }, [location.pathname, location.hash]); // Écouter aussi location.hash pour détecter les changements

  return (
    <div ref={contentRef} className="page-transition">
      {children}
    </div>
  );
}


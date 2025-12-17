import { useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import { gsap } from "gsap";

export default function PageTransition({ children }) {
  const location = useLocation();
  const contentRef = useRef(null);

  useEffect(() => {
    const element = contentRef.current;
    if (!element) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;  

    // Animation d'entrée douce
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
  }, [location.pathname]);

  return (
    <div ref={contentRef} className="page-transition">
      {children}
    </div>
  );
}


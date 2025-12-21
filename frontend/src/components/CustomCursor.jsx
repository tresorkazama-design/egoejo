/**
 * CustomCursor avec interpolation linéaire (lerp) pour effet "liquide"
 * Le curseur "suit" la souris avec un léger retard organique, comme traîné dans l'eau
 */
import React, { useEffect, useState, useRef } from 'react';
import { gsap } from 'gsap';
import { breakpoints } from '../design-tokens';

export const CustomCursor = ({ 
  enabled = true,
  size = 20,
  color = '#3B82F6',
  className = '',
  lerpSpeed = 0.15 // Vitesse d'interpolation (0.1-0.2 pour effet liquide)
}) => {
  const cursorRef = useRef(null);
  const [isHovering, setIsHovering] = useState(false);
  const [isVisible, setIsVisible] = useState(true);
  
  // Position cible (souris) et position actuelle (curseur)
  const targetPos = useRef({ x: 0, y: 0 });
  const currentPos = useRef({ x: 0, y: 0 });
  const animationFrameRef = useRef(null);

  useEffect(() => {
    if (!enabled) return;

    // Utiliser breakpoint centralisé
    const isMobile = window.matchMedia(`(max-width: ${breakpoints.md})`).matches;
    if (isMobile) {
      setIsVisible(false);
      return;
    }

    // Fonction d'interpolation linéaire (lerp)
    const lerp = (start, end, factor) => {
      return start + (end - start) * factor;
    };

    // Animation loop pour interpolation fluide
    const animate = () => {
      if (!cursorRef.current) return;

      // Interpolation linéaire de la position
      currentPos.current.x = lerp(currentPos.current.x, targetPos.current.x, lerpSpeed);
      currentPos.current.y = lerp(currentPos.current.y, targetPos.current.y, lerpSpeed);

      // Appliquer la position avec GSAP pour fluidité maximale
      gsap.set(cursorRef.current, {
        x: currentPos.current.x,
        y: currentPos.current.y,
        transformOrigin: 'center center'
      });

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    // Démarrer l'animation loop
    animate();

    const handleMouseMove = (e) => {
      // Mettre à jour la position cible (souris)
      targetPos.current.x = e.clientX;
      targetPos.current.y = e.clientY;
    };

    const handleMouseEnter = () => {
      setIsHovering(true);
      // Animation GSAP pour l'agrandissement
      if (cursorRef.current) {
        gsap.to(cursorRef.current, {
          scale: 1.5,
          duration: 0.3,
          ease: 'elastic.out(1, 0.4)'
        });
      }
    };

    const handleMouseLeave = () => {
      setIsHovering(false);
      // Animation GSAP pour le retour à la taille normale
      if (cursorRef.current) {
        gsap.to(cursorRef.current, {
          scale: 1,
          duration: 0.3,
          ease: 'elastic.out(1, 0.4)'
        });
      }
    };

    const handleMouseOut = () => setIsVisible(false);
    const handleMouseOver = () => setIsVisible(true);

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseenter', handleMouseEnter);
    document.addEventListener('mouseleave', handleMouseLeave);
    document.addEventListener('mouseout', handleMouseOut);
    document.addEventListener('mouseover', handleMouseOver);

    // Détecter les éléments interactifs
    const interactiveElements = document.querySelectorAll('a, button, input, select, textarea, [role="button"]');
    interactiveElements.forEach((el) => {
      el.addEventListener('mouseenter', handleMouseEnter);
      el.addEventListener('mouseleave', handleMouseLeave);
    });

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseenter', handleMouseEnter);
      document.removeEventListener('mouseleave', handleMouseLeave);
      document.removeEventListener('mouseout', handleMouseOut);
      document.removeEventListener('mouseover', handleMouseOver);
      interactiveElements.forEach((el) => {
        el.removeEventListener('mouseenter', handleMouseEnter);
        el.removeEventListener('mouseleave', handleMouseLeave);
      });
    };
  }, [enabled, lerpSpeed]);

  if (!enabled || !isVisible) return null;

  return (
    <div
      ref={cursorRef}
      className={`fixed pointer-events-none ${className}`}
      style={{
        left: 0,
        top: 0,
        transform: 'translate(-50%, -50%)',
        width: `${size}px`,
        height: `${size}px`,
        borderRadius: '50%',
        backgroundColor: color,
        opacity: 0.5,
        mixBlendMode: 'difference',
        willChange: 'transform',
        zIndex: 'var(--z-cursor)', // Utiliser z-index centralisé
      }}
      aria-hidden="true"
    />
  );
};


/**
 * Button avec animations GSAP pour effet "vivant" et réactif
 * Remplace les transitions CSS par des animations GSAP elastic.out
 * 
 * MIGRATION TYPESCRIPT : Composant migré de .jsx vers .tsx
 * - Types stricts pour les props
 * - Support complet de TypeScript
 * - Aucun changement fonctionnel
 */
import React, { useRef, useEffect } from 'react';
import { gsap } from 'gsap';
import type { ButtonProps } from '../types/common';

export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  disabled = false,
  variant = 'primary',
  type = 'button',
  className = '',
  ...props
}) => {
  const buttonRef = useRef<HTMLButtonElement>(null);
  const baseClasses = 'px-4 py-2 rounded font-medium';
  const variantClasses: Record<string, string> = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-400',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300 disabled:bg-gray-100',
    outline: 'bg-transparent border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:bg-gray-100 disabled:text-gray-400',
    danger: 'bg-red-600 text-white hover:bg-red-700 disabled:bg-gray-400',
  };

  // S'assurer qu'il y a toujours un aria-label si pas de texte visible
  const hasVisibleText = typeof children === 'string' && children.trim().length > 0;
  const ariaLabel = props['aria-label'] || (hasVisibleText ? undefined : 'Bouton');

  useEffect(() => {
    if (!buttonRef.current || disabled) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const button = buttonRef.current;

    // Animation au survol (hover)
    const handleMouseEnter = () => {
      gsap.to(button, {
        scale: 1.05,
        duration: 0.3,
        ease: 'elastic.out(1, 0.3)'
      });
    };

    // Animation à la sortie (leave)
    const handleMouseLeave = () => {
      gsap.to(button, {
        scale: 1,
        duration: 0.3,
        ease: 'elastic.out(1, 0.3)'
      });
    };

    // Animation au clic (active)
    const handleMouseDown = () => {
      gsap.to(button, {
        scale: 0.95,
        duration: 0.1,
        ease: 'power2.out'
      });
    };

    const handleMouseUp = () => {
      gsap.to(button, {
        scale: 1.05,
        duration: 0.2,
        ease: 'elastic.out(1, 0.3)'
      });
    };

    button.addEventListener('mouseenter', handleMouseEnter);
    button.addEventListener('mouseleave', handleMouseLeave);
    button.addEventListener('mousedown', handleMouseDown);
    button.addEventListener('mouseup', handleMouseUp);

    return () => {
      button.removeEventListener('mouseenter', handleMouseEnter);
      button.removeEventListener('mouseleave', handleMouseLeave);
      button.removeEventListener('mousedown', handleMouseDown);
      button.removeEventListener('mouseup', handleMouseUp);
    };
  }, [disabled]);

  const finalClassName = `${baseClasses} ${variantClasses[variant] || variantClasses.primary} ${className}`.trim();

  return (
    <button
      ref={buttonRef}
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={finalClassName}
      aria-label={ariaLabel}
      {...props}
    >
      {children}
    </button>
  );
};


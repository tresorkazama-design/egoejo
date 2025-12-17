import React, { useEffect, useState } from 'react';

export const CustomCursor = ({ 
  enabled = true,
  size = 20,
  color = '#3B82F6',
  className = ''
}) => {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isHovering, setIsHovering] = useState(false);
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (!enabled) return;

    const isMobile = window.matchMedia('(max-width: 768px)').matches;
    if (isMobile) {
      setIsVisible(false);
      return;
    }

    const handleMouseMove = (e) => {
      setPosition({ x: e.clientX, y: e.clientY });
    };

    const handleMouseEnter = () => setIsHovering(true);
    const handleMouseLeave = () => setIsHovering(false);
    const handleMouseOut = () => setIsVisible(false);
    const handleMouseOver = () => setIsVisible(true);

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseenter', handleMouseEnter);
    document.addEventListener('mouseleave', handleMouseLeave);
    document.addEventListener('mouseout', handleMouseOut);
    document.addEventListener('mouseover', handleMouseOver);

    // Détecter les éléments interactifs
    const interactiveElements = document.querySelectorAll('a, button, input, select, textarea');
    interactiveElements.forEach((el) => {
      el.addEventListener('mouseenter', handleMouseEnter);
      el.addEventListener('mouseleave', handleMouseLeave);
    });

    return () => {
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
  }, [enabled]);

  if (!enabled || !isVisible) return null;

  return (
    <div
      className={`fixed pointer-events-none z-50 transition-all duration-150 ${className}`}
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
        transform: 'translate(-50%, -50%)',
        width: `${isHovering ? size * 1.5 : size}px`,
        height: `${isHovering ? size * 1.5 : size}px`,
        borderRadius: '50%',
        backgroundColor: color,
        opacity: 0.5,
        mixBlendMode: 'difference'
      }}
      aria-hidden="true"
    />
  );
};


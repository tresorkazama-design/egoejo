import { useRef, useEffect } from 'react';
import { useEcoMode } from '../contexts/EcoModeContext';
import { getSobrietyFeature } from '../design-tokens';

export default function CardTilt({ children, className = '', role, ...props }) {
  const cardRef = useRef(null);
  const { sobrietyLevel } = useEcoMode();
  
  // Vérifier si animations sont activées selon le niveau de sobriété
  const canAnimate = getSobrietyFeature(sobrietyLevel, 'enableAnimations');

  useEffect(() => {
    // Désactiver le tilt si animations désactivées ou prefers-reduced-motion
    if (!canAnimate || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const card = cardRef.current;
    if (!card) return;

    const handleMouseMove = (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const rotateX = (y - centerY) / 20;
      const rotateY = (centerX - x) / 20;

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(0)`;
    };

    const handleMouseLeave = () => {
      card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateZ(0)';
    };

    card.addEventListener('mousemove', handleMouseMove);
    card.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      card.removeEventListener('mousemove', handleMouseMove);
      card.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, []);

  return (
    <div ref={cardRef} className={`card-tilt ${className}`} style={{ transition: 'transform 0.3s ease-out', background: 'transparent' }} role={role} {...props}>
      {children}
    </div>
  );
}


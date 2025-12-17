/**
 * Hook pour détecter si l'appareil doit utiliser le mode low-power
 * Détecte : mobile, économie d'énergie, connexion lente, prefers-reduced-motion
 */
import { useState, useEffect } from 'react';

export const useLowPowerMode = () => {
  const [isLowPower, setIsLowPower] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    // Détecter prefers-reduced-motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    // Détecter mobile
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
      navigator.userAgent
    );
    
    // Détecter mode économie d'énergie (si disponible)
    const isLowPowerDevice = 
      (navigator.hardwareConcurrency && navigator.hardwareConcurrency < 4) || 
      (navigator.deviceMemory && navigator.deviceMemory < 4);
    
    // Détecter connexion lente
    const isSlowConnection = 
      navigator.connection && 
      (navigator.connection.effectiveType === 'slow-2g' || 
       navigator.connection.effectiveType === '2g');
    
    // Forcer via variable d'environnement
    const forceLowPower = import.meta.env.VITE_FORCE_LOW_POWER === 'true';
    
    setIsLowPower(
      forceLowPower ||
      prefersReducedMotion || 
      (isMobile && isLowPowerDevice) || 
      isSlowConnection
    );
  }, []);

  return isLowPower;
};


/**
 * Contexte pour le mode éco-responsable avec Échelle de Sobriété
 * Réduit l'empreinte carbone en désactivant les animations et images haute définition
 * 
 * ÉCHELLE DE SOBRIÉTÉ (1-5) :
 * - Niveau 1 : Full 3D + Bloom
 * - Niveau 2 : 3D simplifié (pas de bloom)
 * - Niveau 3 : 2D uniquement (pas de 3D)
 * - Niveau 4 : Animations minimales (transitions basiques)
 * - Niveau 5 : Texte seul, zéro animation
 * 
 * INTÉGRATION API BATTERIE :
 * - Bascule automatiquement en mode "Sobriété" si batterie < 20% OU non chargée
 * - Surveille l'état de la batterie en temps réel
 */
import { createContext, useContext, useState, useEffect, useRef, useMemo } from 'react';
import { SobrietyLevel, getSobrietyConfig } from '../design-tokens';
import { useDebouncedLocalStorage } from '../hooks/useDebouncedLocalStorage';
import { logger } from '../utils/logger';

const EcoModeContext = createContext();

export const EcoModeProvider = ({ children }) => {
  // Échelle de Sobriété (1-5) au lieu d'un booléen
  const [sobrietyLevel, setSobrietyLevel] = useState(() => {
    // Récupérer depuis localStorage
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('sobrietyLevel');
      return saved ? parseInt(saved, 10) : SobrietyLevel.FULL;
    }
    return SobrietyLevel.FULL;
  });

  // Migration : Si ancien ecoMode existe, convertir en sobrietyLevel
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const oldEcoMode = localStorage.getItem('ecoMode');
    const savedSobrietyLevel = localStorage.getItem('sobrietyLevel');
    
    // Si pas de sobrietyLevel mais ecoMode existe, migrer
    if (!savedSobrietyLevel && oldEcoMode === 'true') {
      setSobrietyLevel(SobrietyLevel.MINIMAL); // Niveau 4 par défaut
      localStorage.setItem('sobrietyLevel', SobrietyLevel.MINIMAL.toString());
    }
  }, []);

  // Compatibilité : ecoMode calculé depuis sobrietyLevel (pas d'état séparé)
  // Niveau >= 4 (MINIMAL) = ecoMode activé
  const ecoMode = sobrietyLevel >= SobrietyLevel.MINIMAL;

  const [batteryLevel, setBatteryLevel] = useState(null);
  const [isCharging, setIsCharging] = useState(null);
  const batteryRef = useRef(null);
  const isBatteryModeActive = useRef(false);

  // Fonction pour déterminer le niveau de sobriété basé sur la batterie
  const calculateBatterySobrietyLevel = (battery) => {
    if (!battery) return null;

    const level = battery.level; // 0.0 à 1.0
    const charging = battery.charging;

    // Niveau de sobriété basé sur la batterie
    if (level < 0.1 || (!charging && level < 0.15)) {
      return SobrietyLevel.TEXT_ONLY; // Niveau 5 : Batterie critique
    } else if (level < 0.2 || (!charging && level < 0.3)) {
      return SobrietyLevel.MINIMAL; // Niveau 4 : Batterie faible
    } else if (level < 0.4 || !charging) {
      return SobrietyLevel.FLAT; // Niveau 3 : Batterie moyenne
    } else if (level < 0.6) {
      return SobrietyLevel.SIMPLIFIED; // Niveau 2 : Batterie correcte
    }
    return SobrietyLevel.FULL; // Niveau 1 : Batterie suffisante
  };

  // Fonction pour activer le mode Sobriété basé sur la batterie
  const checkBatteryAndActivateSobriety = (battery) => {
    if (!battery) return;

    const level = battery.level; // 0.0 à 1.0
    const charging = battery.charging;

    setBatteryLevel(level);
    setIsCharging(charging);

    // Calculer le niveau de sobriété recommandé
    const recommendedLevel = calculateBatterySobrietyLevel(battery);

    // SI batterie < 20% OU non chargée : Bascule automatiquement en mode "Sobriété"
    const shouldActivateSobriety = level < 0.2 || !charging;

    if (shouldActivateSobriety && !isBatteryModeActive.current) {
      // Activer le mode Sobriété automatiquement avec le niveau recommandé
      isBatteryModeActive.current = true;
      setSobrietyLevel(recommendedLevel);
      logger.debug(`🔋 Mode Sobriété Niveau ${recommendedLevel} activé automatiquement (Batterie: ${(level * 100).toFixed(0)}%, Chargement: ${charging ? 'Oui' : 'Non'})`);
    } else if (!shouldActivateSobriety && isBatteryModeActive.current) {
      // Désactiver le mode Sobriété si la batterie est suffisante ET en charge
      isBatteryModeActive.current = false;
      // Ne pas désactiver si l'utilisateur l'a activé manuellement
      const userSobrietyLevel = localStorage.getItem('sobrietyLevel');
      const userActivated = userSobrietyLevel && parseInt(userSobrietyLevel, 10) >= SobrietyLevel.MINIMAL;
      if (!userActivated) {
        setSobrietyLevel(SobrietyLevel.FULL);
        logger.debug(`🔋 Mode Sobriété désactivé (Batterie: ${(level * 100).toFixed(0)}%, Chargement: ${charging ? 'Oui' : 'Non'})`);
      }
    } else if (shouldActivateSobriety && isBatteryModeActive.current && recommendedLevel !== sobrietyLevel) {
      // Mettre à jour le niveau si la batterie change
      setSobrietyLevel(recommendedLevel);
    }
  };

  // Intégration API Batterie
  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Vérifier si l'API Batterie est disponible
    if ('getBattery' in navigator) {
      navigator.getBattery().then((battery) => {
        batteryRef.current = battery;

        // État initial
        checkBatteryAndActivateSobriety(battery);

        // Écouter les changements de niveau de batterie
        battery.addEventListener('levelchange', () => {
          checkBatteryAndActivateSobriety(battery);
        });

        // Écouter les changements d'état de charge
        battery.addEventListener('chargingchange', () => {
          checkBatteryAndActivateSobriety(battery);
        });

        // Écouter les changements de temps de charge
        battery.addEventListener('chargingtimechange', () => {
          checkBatteryAndActivateSobriety(battery);
        });

        // Écouter les changements de temps de décharge
        battery.addEventListener('dischargingtimechange', () => {
          checkBatteryAndActivateSobriety(battery);
        });
      }).catch((error) => {
        logger.warn('API Batterie non disponible:', error);
      });
    } else {
      logger.warn('API Batterie non supportée par ce navigateur');
    }

    return () => {
      // Nettoyer les event listeners si nécessaire
      if (batteryRef.current) {
        batteryRef.current.removeEventListener('levelchange', checkBatteryAndActivateSobriety);
        batteryRef.current.removeEventListener('chargingchange', checkBatteryAndActivateSobriety);
        batteryRef.current.removeEventListener('chargingtimechange', checkBatteryAndActivateSobriety);
        batteryRef.current.removeEventListener('dischargingtimechange', checkBatteryAndActivateSobriety);
      }
    };
  }, []);

  // OPTIMISATION I/O : Utiliser debounce pour localStorage (évite les écritures synchrones bloquantes)
  // Sauvegarder dans localStorage avec debounce (sauf si activé automatiquement par la batterie)
  useDebouncedLocalStorage(
    !isBatteryModeActive.current ? 'sobrietyLevel' : null,
    !isBatteryModeActive.current ? sobrietyLevel.toString() : null,
    300 // 300ms de debounce
  );
  
  // Sauvegarder aussi ecoMode pour rétrocompatibilité (avec debounce)
  useDebouncedLocalStorage(
    !isBatteryModeActive.current ? 'ecoMode' : null,
    !isBatteryModeActive.current ? (sobrietyLevel >= SobrietyLevel.MINIMAL).toString() : null,
    300 // 300ms de debounce
  );

  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    // Appliquer les classes CSS selon le niveau de sobriété
    // Retirer toutes les classes de sobriété
    document.documentElement.classList.remove(
      'eco-mode', // Ancienne classe (rétrocompatibilité)
      'sobriety-1',
      'sobriety-2',
      'sobriety-3',
      'sobriety-4',
      'sobriety-5'
    );

    // Ajouter la classe correspondante au niveau
    document.documentElement.classList.add(`sobriety-${sobrietyLevel}`);
    
    // Rétrocompatibilité : ajouter eco-mode si niveau >= 4
    if (sobrietyLevel >= SobrietyLevel.MINIMAL) {
      document.documentElement.classList.add('eco-mode');
    }

    // Ajouter l'attribut data-sobriety pour CSS avancé
    document.documentElement.setAttribute('data-sobriety', sobrietyLevel.toString());
  }, [sobrietyLevel]);

  // Rétrocompatibilité : setEcoMode met à jour sobrietyLevel
  const handleSetEcoMode = (value) => {
    if (value) {
      setSobrietyLevel(SobrietyLevel.MINIMAL); // Niveau 4 par défaut
    } else {
      setSobrietyLevel(SobrietyLevel.FULL); // Niveau 1 par défaut
    }
  };

  // OPTIMISATION : Mémoriser l'objet value pour éviter les rerenders inutiles
  // L'objet value change à chaque render, causant des rerenders de tous les consommateurs
  // Note : isBatteryModeActive est un ref, donc pas besoin de le mettre dans les dépendances
  const contextValue = useMemo(() => ({
    // Nouvelle API : Échelle de Sobriété
    sobrietyLevel,
    setSobrietyLevel,
    sobrietyConfig: getSobrietyConfig(sobrietyLevel),
    
    // Rétrocompatibilité : API booléenne
    ecoMode,
    setEcoMode: handleSetEcoMode,
    
    // API Batterie
    batteryLevel,
    isCharging,
    isBatteryModeActive: isBatteryModeActive.current
  }), [sobrietyLevel, ecoMode, batteryLevel, isCharging]);

  return (
    <EcoModeContext.Provider value={contextValue}>
      {children}
    </EcoModeContext.Provider>
  );
};

export const useEcoMode = () => {
  const context = useContext(EcoModeContext);
  if (!context) {
    throw new Error('useEcoMode must be used within EcoModeProvider');
  }
  return context;
};


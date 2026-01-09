/**
 * Design Tokens - Module centralisé pour les constantes de design EGOEJO
 * 
 * Ce module fournit :
 * - Niveaux de sobriété (performance)
 * - Z-index layers (gestion des couches)
 * - Breakpoints responsive
 * - Configurations de sobriété
 */

/**
 * Niveaux de Sobriété (1-5)
 * Contrôle le niveau de performance et d'animations
 */
export const SobrietyLevel = {
  FULL: 1,              // Performance maximale : Full 3D + Bloom
  SIMPLIFIED: 2,       // 3D simplifié (pas de bloom)
  FLAT: 3,             // 2D uniquement (pas de 3D) - alias pour MINIMAL
  MINIMAL: 4,          // Animations minimales (transitions basiques)
  TEXT_ONLY: 5,        // Texte seul, zéro animation
  // Alias pour compatibilité
  ULTRA_MINIMAL: 4,    // Alias de MINIMAL
};

/**
 * Configuration de sobriété par niveau
 */
export const sobrietyConfig = {
  [SobrietyLevel.FULL]: {
    name: 'Full',
    description: 'Performance maximale avec toutes les animations et effets visuels',
    performance: 'Haute',
    enable3D: true,
    enableBloom: true,
    enableAnimations: true,
    enableParticles: true,
  },
  [SobrietyLevel.SIMPLIFIED]: {
    name: 'Simplifié',
    description: '3D simplifié sans bloom, animations réduites',
    performance: 'Moyenne',
    enable3D: true,
    enableBloom: false,
    enableAnimations: true,
    enableParticles: false,
  },
  [SobrietyLevel.FLAT]: {
    name: 'Flat',
    description: '2D uniquement, pas de 3D, animations basiques',
    performance: 'Basse',
    enable3D: false,
    enableBloom: false,
    enableAnimations: true,
    enableParticles: false,
  },
  [SobrietyLevel.MINIMAL]: {
    name: 'Minimal',
    description: 'Animations minimales, transitions basiques uniquement',
    performance: 'Très basse',
    enable3D: false,
    enableBloom: false,
    enableAnimations: false,
    enableParticles: false,
  },
  [SobrietyLevel.TEXT_ONLY]: {
    name: 'Texte Seul',
    description: 'Zéro animation, texte et images statiques uniquement',
    performance: 'Minimale',
    enable3D: false,
    enableBloom: false,
    enableAnimations: false,
    enableParticles: false,
  },
};

/**
 * Récupère la configuration de sobriété pour un niveau donné
 * @param {number} level - Niveau de sobriété (1-5)
 * @returns {Object} Configuration du niveau
 */
export const getSobrietyConfig = (level) => {
  return sobrietyConfig[level] || sobrietyConfig[SobrietyLevel.FULL];
};

/**
 * Récupère une fonctionnalité spécifique selon le niveau de sobriété
 * @param {number} level - Niveau de sobriété (1-5)
 * @param {string} feature - Nom de la fonctionnalité ('enableAnimations', 'enable3D', 'enableBloom', 'enableParticles')
 * @returns {boolean} true si la fonctionnalité est activée
 */
export const getSobrietyFeature = (level, feature) => {
  const config = getSobrietyConfig(level);
  
  // Retourner directement la propriété si elle existe
  if (Object.prototype.hasOwnProperty.call(config, feature)) {
    return config[feature];
  }
  
  // Fallback pour les features non définies
  switch (feature) {
    case 'enableAnimations':
      return level <= SobrietyLevel.MINIMAL;
    case 'enable3D':
      return level <= SobrietyLevel.SIMPLIFIED;
    case 'enableBloom':
      return level === SobrietyLevel.FULL;
    case 'enableParticles':
      return level === SobrietyLevel.FULL;
    default:
      // Par défaut, activer si niveau bas (performance)
      return level <= SobrietyLevel.SIMPLIFIED;
  }
};

/**
 * Z-index Layers - Gestion des couches d'affichage
 */
export const zIndexLayers = {
  background: -1,
  content: 1,
  overlay: 100,
  modal: 200,
  tooltip: 300,
  notification: 400,
  // Alias pour compatibilité
  menu: 200,
  loader: 300,
  cursor: 500,
  floating: 400,  // Pour les éléments flottants (ex: EcoModeToggle)
  dropdown: 350,  // Pour les menus déroulants (au-dessus des tooltips)
};

/**
 * Breakpoints Responsive
 * Utilisés pour les media queries et la détection de taille d'écran
 */
export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
};

/**
 * Valeurs numériques des breakpoints (pour comparaisons JS)
 */
export const breakpointsValues = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
};

/**
 * Helper pour vérifier si on est sur mobile
 * @param {string} breakpoint - Breakpoint à vérifier (défaut: 'md')
 * @returns {boolean} true si la largeur d'écran est inférieure au breakpoint
 */
export const isMobile = (breakpoint = 'md') => {
  if (typeof window === 'undefined') return false;
  const bpValue = breakpointsValues[breakpoint] || breakpointsValues.md;
  return window.innerWidth < bpValue;
};

/**
 * Helper pour vérifier si on est sur desktop
 * @param {string} breakpoint - Breakpoint à vérifier (défaut: 'lg')
 * @returns {boolean} true si la largeur d'écran est supérieure au breakpoint
 */
export const isDesktop = (breakpoint = 'lg') => {
  if (typeof window === 'undefined') return false;
  const bpValue = breakpointsValues[breakpoint] || breakpointsValues.lg;
  return window.innerWidth >= bpValue;
};


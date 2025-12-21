/**
 * Version lazy-loadée de HeroSorgho
 * Three.js n'est chargé que si nécessaire selon l'échelle de sobriété
 */
import { lazy, Suspense } from 'react';
import { useEcoMode } from '../contexts/EcoModeContext';
import { getSobrietyFeature } from '../design-tokens';

// Import conditionnel de Three.js uniquement si nécessaire
const HeroSorgho3D = lazy(() => 
  import('./HeroSorgho').then(module => ({ default: module.default }))
);

export default function HeroSorghoLazy() {
  const { sobrietyLevel } = useEcoMode();
  
  // Vérifier si 3D est activé selon le niveau de sobriété
  const canRender3D = getSobrietyFeature(sobrietyLevel, 'enable3D');

  // Si 3D désactivé (sobriété >= 3), ne pas charger Three.js du tout
  if (!canRender3D) {
    return (
      <div 
        className="hero-sorgho-static" 
        style={{ 
          minHeight: "70svh", 
          background: "transparent", 
          backgroundColor: "transparent", 
          width: "100%", 
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexDirection: "column"
        }}
      >
        <div className="hero-content">
          <h1 style={{ fontSize: "4rem", color: "#00ffa3", marginBottom: "1rem" }}>EGOEJO</h1>
          <p style={{ fontSize: "1.5rem", color: "#ffffff" }}>Collectif pour le vivant</p>
        </div>
      </div>
    );
  }

  // Charger Three.js uniquement si nécessaire
  return (
    <Suspense fallback={
      <div style={{ minHeight: "70svh", background: "transparent", backgroundColor: "transparent", width: "100%", height: "100%" }} />
    }>
      <HeroSorgho3D />
    </Suspense>
  );
}


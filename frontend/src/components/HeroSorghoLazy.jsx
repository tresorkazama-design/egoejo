/**
 * Version lazy-loadée de HeroSorgho
 * Three.js n'est chargé que si nécessaire (pas en mode low-power)
 */
import { lazy, Suspense } from 'react';
import { useLowPowerMode } from '../hooks/useLowPowerMode';

// Import conditionnel de Three.js uniquement si nécessaire
const HeroSorgho3D = lazy(() => 
  import('./HeroSorgho').then(module => ({ default: module.default }))
);

export default function HeroSorghoLazy() {
  const isLowPower = useLowPowerMode();

  // Si low power mode, ne pas charger Three.js du tout
  if (isLowPower) {
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


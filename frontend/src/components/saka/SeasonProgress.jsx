/**
 * Composant SeasonProgress - Barre de progression vers le prochain badge de saison
 * Affiche l'avancement visuel vers la saison suivante
 */
import { useMemo } from 'react';

/**
 * Seuils des saisons SAKA
 */
const SEASON_THRESHOLDS = {
  semailles: { min: 0, max: 99, emoji: '🌱', label: 'Saison des semailles', color: '#84cc16' },
  croissance: { min: 100, max: 499, emoji: '🌿', label: 'Saison de croissance', color: '#22c55e' },
  abondance: { min: 500, max: Infinity, emoji: '🌾', label: "Saison d'abondance", color: '#f59e0b' },
};

/**
 * @param {Object} props
 * @param {number} props.balance - Solde SAKA actuel
 */
export default function SeasonProgress({ balance = 0 }) {
  // Déterminer la saison actuelle et la suivante
  const { currentSeason, nextSeason, progress } = useMemo(() => {
    let current = 'semailles';
    let next = 'croissance';
    
    if (balance >= 500) {
      current = 'abondance';
      next = null; // Pas de saison supérieure
    } else if (balance >= 100) {
      current = 'croissance';
      next = 'abondance';
    } else {
      current = 'semailles';
      next = 'croissance';
    }

    const currentThreshold = SEASON_THRESHOLDS[current];
    const nextThreshold = next ? SEASON_THRESHOLDS[next] : null;

    // Calculer la progression dans la saison actuelle
    let progressValue = 0;
    if (nextThreshold) {
      const range = nextThreshold.min - currentThreshold.min;
      const currentProgress = balance - currentThreshold.min;
      progressValue = Math.max(0, Math.min(100, (currentProgress / range) * 100));
    } else {
      // Saison maximale atteinte
      progressValue = 100;
    }

    return {
      currentSeason: current,
      nextSeason: next,
      progress: progressValue,
    };
  }, [balance]);

  const currentThreshold = SEASON_THRESHOLDS[currentSeason];
  const nextThreshold = nextSeason ? SEASON_THRESHOLDS[nextSeason] : null;

  // Si on est à la saison maximale, afficher un message spécial
  if (!nextThreshold) {
    return (
      <div
        style={{
          padding: '1rem',
          backgroundColor: `${currentThreshold.color}15`,
          border: `1px solid ${currentThreshold.color}40`,
          borderRadius: 'var(--radius)',
          textAlign: 'center',
        }}
      >
        <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>{currentThreshold.emoji}</div>
        <p style={{ margin: 0, fontSize: '0.875rem', fontWeight: '600', color: currentThreshold.color }}>
          {currentThreshold.label}
        </p>
        <p style={{ margin: 0, marginTop: '0.25rem', fontSize: '0.75rem', color: 'var(--muted)' }}>
          Vous avez atteint la saison maximale ! 🌾
        </p>
      </div>
    );
  }

  const remaining = nextThreshold.min - balance;

  return (
    <div
      style={{
        padding: '1rem',
        backgroundColor: 'var(--surface)',
        borderRadius: 'var(--radius)',
        border: '1px solid var(--border)',
      }}
      className="season-progress"
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '1.25rem' }}>{currentThreshold.emoji}</span>
          <span style={{ fontSize: '0.875rem', color: 'var(--muted)' }}>
            {currentThreshold.label}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '0.875rem', color: 'var(--muted)' }}>
            {nextThreshold.emoji} {nextThreshold.label}
          </span>
        </div>
      </div>

      {/* Barre de progression */}
      <div
        role="progressbar"
        aria-label={`Progression vers ${nextThreshold.label}`}
        aria-valuenow={progress}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuetext={`${progress.toFixed(0)}% - ${balance} SAKA sur ${nextThreshold.min} SAKA`}
        style={{
          width: '100%',
          height: '16px',
          backgroundColor: 'var(--border)',
          borderRadius: '9999px',
          overflow: 'hidden',
          position: 'relative',
          marginBottom: '0.5rem',
        }}
      >
        <div
          style={{
            width: `${progress}%`,
            height: '100%',
            background: `linear-gradient(90deg, ${currentThreshold.color}, ${nextThreshold.color})`,
            borderRadius: '9999px',
            transition: 'width 0.5s ease',
            position: 'relative',
          }}
        >
          {/* Animation de brillance */}
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)',
              animation: 'shimmer 2s infinite',
            }}
          />
        </div>
      </div>

      {/* Informations de progression */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '0.75rem', color: 'var(--muted)' }}>
          {balance} / {nextThreshold.min} SAKA
        </span>
        {remaining > 0 && (
          <span style={{ fontSize: '0.75rem', fontWeight: '600', color: nextThreshold.color }}>
            {remaining} SAKA pour la prochaine saison
          </span>
        )}
        {remaining <= 0 && (
          <span style={{ fontSize: '0.75rem', fontWeight: '600', color: nextThreshold.color }}>
            Prochaine saison atteinte ! 🎉
          </span>
        )}
      </div>
    </div>
  );
}


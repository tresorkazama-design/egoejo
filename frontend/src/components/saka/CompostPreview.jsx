/**
 * Composant CompostPreview - Visualisation du compostage SAKA
 * Affiche une barre de progression, compte à rebours et simulateur
 */
import { useMemo } from 'react';

/**
 * @param {Object} props
 * @param {Object} props.compost - Données de preview du compostage
 * @param {number} props.sakaBalance - Solde SAKA actuel
 */
export default function CompostPreview({ compost, sakaBalance = 0 }) {
  if (!compost || !compost.enabled) {
    return null;
  }

  // Récupérer la configuration depuis l'API (ou valeurs par défaut si non disponible)
  const config = compost.config || {};
  // Utiliser inactivity_days depuis la config du backend
  const requiredDays = config.inactivity_days || 90;
  const minBalance = config.min_balance || 50;
  const compostRate = config.rate || 0.1;
  const minAmount = config.min_amount || 10;

  // Calculer le pourcentage de progression vers l'éligibilité
  const daysUntilEligible = compost.days_until_eligible || 0;
  const progressPercent = useMemo(() => {
    if (daysUntilEligible <= 0) return 100; // Éligible
    return Math.max(0, Math.min(100, ((requiredDays - daysUntilEligible) / requiredDays) * 100));
  }, [daysUntilEligible, requiredDays]);

  // Simulateur : calculer ce qui serait composté ce soir
  const simulatedCompost = useMemo(() => {
    if (!sakaBalance || sakaBalance < minBalance) return 0;
    const simulated = Math.floor(sakaBalance * compostRate);
    return Math.max(minAmount, simulated);
  }, [sakaBalance, minBalance, compostRate, minAmount]);

  return (
    <div
      style={{
        padding: '1.5rem',
        backgroundColor: 'var(--surface)',
        borderRadius: 'var(--radius)',
        border: '1px solid var(--border)',
        marginBottom: '2rem',
      }}
      className="compost-preview"
    >
      <h3 style={{ margin: 0, marginBottom: '1rem', fontSize: '1.25rem', fontWeight: '600', color: 'var(--text)' }}>
        🌱 Compostage SAKA
      </h3>

      {/* Barre de progression vers l'éligibilité */}
      {daysUntilEligible > 0 && (
        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.875rem', color: 'var(--muted)' }}>
              Progression vers l'éligibilité
            </span>
            <span style={{ fontSize: '0.875rem', fontWeight: '600', color: 'var(--accent)' }}>
              {daysUntilEligible} jour{daysUntilEligible > 1 ? 's' : ''} restant{daysUntilEligible > 1 ? 's' : ''}
            </span>
          </div>
          <div
            role="progressbar"
            aria-label="Progression vers l'éligibilité au compostage"
            aria-valuenow={progressPercent}
            aria-valuemin={0}
            aria-valuemax={100}
            style={{
              width: '100%',
              height: '12px',
              backgroundColor: 'var(--border)',
              borderRadius: '9999px',
              overflow: 'hidden',
              position: 'relative',
            }}
          >
            <div
              style={{
                width: `${progressPercent}%`,
                height: '100%',
                backgroundColor: '#84cc16',
                borderRadius: '9999px',
                transition: 'width 0.3s ease',
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
                  background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
                  animation: 'shimmer 2s infinite',
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Simulateur */}
      <div
        style={{
          padding: '1rem',
          backgroundColor: 'var(--bg)',
          borderRadius: 'var(--radius)',
          border: '1px solid var(--border)',
          marginBottom: '1rem',
        }}
      >
        <p style={{ margin: 0, marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--muted)' }}>
          <strong>Simulateur :</strong> Si le compostage avait lieu ce soir
        </p>
        <p style={{ margin: 0, fontSize: '1rem', fontWeight: '600', color: '#84cc16' }}>
          {simulatedCompost} SAKA → Silo Commun
        </p>
        <p style={{ margin: 0, marginTop: '0.25rem', fontSize: '0.75rem', color: 'var(--muted)' }}>
          Basé sur votre solde actuel ({sakaBalance} SAKA) et le taux de compostage ({(compostRate * 100).toFixed(0)}%)
        </p>
      </div>

      {/* Informations d'éligibilité */}
      {compost.eligible && compost.amount && compost.amount >= 20 && (
        <div
          style={{
            padding: '0.75rem',
            backgroundColor: '#f0fdf4',
            border: '1px solid #84cc16',
            borderRadius: 'var(--radius)',
          }}
        >
          <p style={{ margin: 0, fontSize: '0.875rem', color: '#15803d' }}>
            ✅ Vous êtes éligible au compostage. Environ <strong>{compost.amount} grains</strong> seront compostés au prochain cycle.
          </p>
        </div>
      )}

      {!compost.eligible && daysUntilEligible > 0 && (
        <p style={{ margin: 0, fontSize: '0.875rem', color: 'var(--muted)' }}>
          Restez actif pour éviter le compostage automatique après {requiredDays} jours d'inactivité.
        </p>
      )}
    </div>
  );
}



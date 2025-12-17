/**
 * Composant "Mon Impact 4P" pour le Dashboard utilisateur.
 * Affiche les 4 dimensions de performance partagée agrégées pour l'utilisateur.
 */
import React from 'react';
import { formatMoney } from '../../utils/money';

/**
 * @param {Object} props
 * @param {Object} props.assets - Données des assets globaux de l'utilisateur
 */
export default function UserImpact4P({ assets }) {
  if (!assets) {
    return null;
  }

  // Calculer les 4 dimensions à partir des assets
  // P1 : Total contributions financières (dons + investissements)
  const p1_financier = parseFloat(assets.donations?.total_amount || '0') + 
                       parseFloat(assets.equity_portfolio?.valuation || '0');

  // P2 : SAKA total récolté (ou planté)
  const p2_saka = assets.saka?.total_harvested || assets.saka?.balance || 0;

  // P3 : Score social agrégé (PROXY V1 INTERNE)
  // ⚠️ ATTENTION : Ce score est un indicateur interne simplifié, non académique.
  // On peut utiliser impact_score si disponible, sinon calculer à partir des métriques
  const p3_social = assets.impact_score || 
                     (assets.donations?.metrics_count ? Math.min(assets.donations.metrics_count * 10, 100) : 0);

  // P4 : Purpose / Sens (PROXY V1 INTERNE)
  // ⚠️ ATTENTION : Ce score est un indicateur interne simplifié, non académique.
  // Placeholder simple : nombre de projets soutenus * 5
  const p4_sens = (assets.donations?.metrics_count || 0) * 5;

  // Si tous les scores sont à 0, afficher un message encourageant
  if (p1_financier === 0 && p2_saka === 0 && p3_social === 0 && p4_sens === 0) {
    return (
      <section style={{ marginBottom: '3rem' }}>
        <h2 style={{ marginBottom: '1.5rem', fontSize: '1.8rem' }}>Mon Impact 4P</h2>
        <div
          style={{
            padding: '2rem',
            backgroundColor: 'var(--surface)',
            borderRadius: 'var(--radius)',
            border: '1px solid var(--border)',
            textAlign: 'center',
          }}
        >
          <p style={{ color: 'var(--muted)', fontSize: '0.875rem' }}>
            Commencez votre impact en soutenant un projet ou en soumettant une intention.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section style={{ marginBottom: '3rem' }}>
      <h2 style={{ marginBottom: '1.5rem', fontSize: '1.8rem' }}>Mon Impact 4P</h2>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1rem',
        }}
      >
        {/* P1 : Financier */}
        <div
          style={{
            padding: '1.5rem',
            backgroundColor: 'var(--surface)',
            borderRadius: 'var(--radius)',
            border: '1px solid var(--border)',
            textAlign: 'center',
          }}
        >
          <div
            style={{
              fontSize: '0.75rem',
              color: 'var(--muted)',
              marginBottom: '0.5rem',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}
          >
            💰 P1 - Financier
          </div>
          <div
            style={{
              fontSize: '1.75rem',
              fontWeight: 'bold',
              color: 'var(--accent)',
              marginBottom: '0.25rem',
            }}
          >
            {formatMoney(p1_financier)}
          </div>
          <p
            style={{
              margin: 0,
              fontSize: '0.75rem',
              color: 'var(--muted)',
            }}
          >
            Total contributions
          </p>
        </div>

        {/* P2 : SAKA */}
        <div
          style={{
            padding: '1.5rem',
            backgroundColor: 'var(--surface)',
            borderRadius: 'var(--radius)',
            border: '1px solid var(--border)',
            textAlign: 'center',
          }}
        >
          <div
            style={{
              fontSize: '0.75rem',
              color: 'var(--muted)',
              marginBottom: '0.5rem',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}
          >
            🌾 P2 - SAKA
          </div>
          <div
            style={{
              fontSize: '1.75rem',
              fontWeight: 'bold',
              color: '#84cc16',
              marginBottom: '0.25rem',
            }}
          >
            {p2_saka.toLocaleString('fr-FR')} <span style={{ fontSize: '1rem', fontWeight: 'normal' }}>grains</span>
          </div>
          <p
            style={{
              margin: 0,
              fontSize: '0.75rem',
              color: 'var(--muted)',
            }}
          >
            {assets.saka?.total_planted > 0 ? `${assets.saka.total_planted} plantés` : 'Engagement non monétaire'}
          </p>
        </div>

        {/* P3 : Social (PROXY V1) */}
        <div
          style={{
            padding: '1.5rem',
            backgroundColor: 'var(--surface)',
            borderRadius: 'var(--radius)',
            border: '1px solid var(--border)',
            textAlign: 'center',
          }}
          title="Ce score est un indicateur interne simplifié (V1) qui sera affiné avec des données d'impact plus riches."
        >
          <div
            style={{
              fontSize: '0.75rem',
              color: 'var(--muted)',
              marginBottom: '0.5rem',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}
          >
            🌍 P3 - Signal social (V1)
          </div>
          <div
            style={{
              fontSize: '1.75rem',
              fontWeight: 'bold',
              color: '#3b82f6',
              marginBottom: '0.25rem',
            }}
          >
            {p3_social}/100
          </div>
          <p
            style={{
              margin: 0,
              fontSize: '0.75rem',
              color: 'var(--muted)',
            }}
          >
            Indicateur interne simplifié
          </p>
        </div>

        {/* P4 : Sens (PROXY V1) */}
        <div
          style={{
            padding: '1.5rem',
            backgroundColor: 'var(--surface)',
            borderRadius: 'var(--radius)',
            border: '1px solid var(--border)',
            textAlign: 'center',
          }}
          title="Ce score est un indicateur interne simplifié (V1) qui sera affiné avec des indicateurs qualitatifs plus robustes."
        >
          <div
            style={{
              fontSize: '0.75rem',
              color: 'var(--muted)',
              marginBottom: '0.5rem',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}
          >
            💡 P4 - Signal de sens (V1)
          </div>
          <div
            style={{
              fontSize: '1.75rem',
              fontWeight: 'bold',
              color: '#a855f7',
              marginBottom: '0.25rem',
            }}
          >
            {p4_sens}
          </div>
          <p
            style={{
              margin: 0,
              fontSize: '0.75rem',
              color: 'var(--muted)',
            }}
          >
            Indicateur interne simplifié
          </p>
        </div>
      </div>
    </section>
  );
}


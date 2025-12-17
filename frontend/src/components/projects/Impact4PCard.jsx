/**
 * Composant pour afficher les scores 4P (Performance Partagée) d'un projet.
 * Affiche les 4 dimensions : Financier, SAKA, Social, Sens
 */
import React from 'react';
import { formatMoney } from '../../utils/money';

/**
 * @param {Object} props
 * @param {Object} props.impact4p - Données 4P du projet (p1_financier, p2_saka, p3_social, p4_sens)
 * @param {boolean} props.compact - Mode compact (affichage réduit)
 */
export default function Impact4PCard({ impact4p, compact = false }) {
  if (!impact4p) {
    return null;
  }

  const {
    p1_financier = 0,
    p2_saka = 0,
    p3_social = 0,
    p4_sens = 0,
  } = impact4p;

  // Si tous les scores sont à 0, ne rien afficher
  if (p1_financier === 0 && p2_saka === 0 && p3_social === 0 && p4_sens === 0) {
    return null;
  }

  if (compact) {
    // Mode compact : affichage en une ligne
    return (
      <div
        style={{
          display: 'flex',
          gap: '1rem',
          padding: '0.75rem',
          backgroundColor: 'var(--surface)',
          borderRadius: 'var(--radius)',
          border: '1px solid var(--border)',
          fontSize: '0.875rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ color: 'var(--muted)' }}>💰</span>
          <span>{formatMoney(p1_financier)}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ color: 'var(--muted)' }}>🌾</span>
          <span>{p2_saka} SAKA</span>
        </div>
        <div 
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          title="Indicateur interne simplifié (V1)"
        >
          <span style={{ color: 'var(--muted)' }}>🌍</span>
          <span>{p3_social}/100</span>
        </div>
        <div 
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          title="Indicateur interne simplifié (V1)"
        >
          <span style={{ color: 'var(--muted)' }}>💡</span>
          <span>{p4_sens}</span>
        </div>
      </div>
    );
  }

  // Mode complet : affichage en cartes
  return (
    <div
      style={{
        marginTop: '1rem',
        padding: '1rem',
        backgroundColor: 'var(--surface)',
        borderRadius: 'var(--radius)',
        border: '1px solid var(--border)',
      }}
    >
      <h3
        style={{
          margin: 0,
          marginBottom: '1rem',
          fontSize: '1rem',
          fontWeight: '600',
          color: 'var(--text)',
        }}
      >
        Performance Partagée (4P)
      </h3>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
          gap: '1rem',
        }}
      >
        {/* P1 : Financier */}
        <div
          style={{
            padding: '0.75rem',
            backgroundColor: 'var(--background)',
            borderRadius: 'var(--radius)',
            border: '1px solid var(--border)',
          }}
        >
          <div
            style={{
              fontSize: '0.75rem',
              color: 'var(--muted)',
              marginBottom: '0.25rem',
            }}
          >
            💰 Financier
          </div>
          <div
            style={{
              fontSize: '1.25rem',
              fontWeight: 'bold',
              color: 'var(--text)',
            }}
          >
            {formatMoney(p1_financier)}
          </div>
        </div>

        {/* P2 : SAKA */}
        <div
          style={{
            padding: '0.75rem',
            backgroundColor: 'var(--background)',
            borderRadius: 'var(--radius)',
            border: '1px solid var(--border)',
          }}
        >
          <div
            style={{
              fontSize: '0.75rem',
              color: 'var(--muted)',
              marginBottom: '0.25rem',
            }}
          >
            🌾 SAKA
          </div>
          <div
            style={{
              fontSize: '1.25rem',
              fontWeight: 'bold',
              color: 'var(--text)',
            }}
          >
            {p2_saka.toLocaleString()} grains
          </div>
        </div>

        {/* P3 : Social (PROXY V1) */}
        <div
          style={{
            padding: '0.75rem',
            backgroundColor: 'var(--background)',
            borderRadius: 'var(--radius)',
            border: '1px solid var(--border)',
          }}
          title="Ce score est un indicateur interne simplifié (V1) qui sera affiné avec des données d'impact plus riches."
        >
          <div
            style={{
              fontSize: '0.75rem',
              color: 'var(--muted)',
              marginBottom: '0.25rem',
            }}
          >
            🌍 Signal social (V1)
          </div>
          <div
            style={{
              fontSize: '1.25rem',
              fontWeight: 'bold',
              color: 'var(--text)',
            }}
          >
            {p3_social}/100
          </div>
        </div>

        {/* P4 : Sens (PROXY V1) */}
        <div
          style={{
            padding: '0.75rem',
            backgroundColor: 'var(--background)',
            borderRadius: 'var(--radius)',
            border: '1px solid var(--border)',
          }}
          title="Ce score est un indicateur interne simplifié (V1) qui sera affiné avec des indicateurs qualitatifs plus robustes."
        >
          <div
            style={{
              fontSize: '0.75rem',
              color: 'var(--muted)',
              marginBottom: '0.25rem',
            }}
          >
            💡 Signal de sens (V1)
          </div>
          <div
            style={{
              fontSize: '1.25rem',
              fontWeight: 'bold',
              color: 'var(--text)',
            }}
          >
            {p4_sens}
          </div>
        </div>
      </div>
    </div>
  );
}


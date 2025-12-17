/**
 * Composant FourPStrip - Bandeau "4P / Triple capital"
 * Affiche les 3 dimensions du capital : financier, vivant (SAKA), impact social/écologique
 */
import { formatMoney } from '../../utils/money';

/**
 * @param {Object} props
 * @param {number|null} props.financial - Capital financier (euros)
 * @param {number|null} props.saka - Capital vivant SAKA (grains)
 * @param {number|null} props.impact - Impact social/écologique (score)
 */
export default function FourPStrip({ financial, saka, impact }) {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1rem',
        marginBottom: '2rem',
      }}
      className="four-p-strip"
    >
      {/* Carte Capital financier */}
      <div
        style={{
          padding: '1.5rem',
          backgroundColor: 'var(--surface)',
          borderRadius: 'var(--radius)',
          border: '1px solid var(--border)',
          textAlign: 'center',
        }}
        className="four-p-card financial"
      >
        <h3
          style={{
            margin: 0,
            marginBottom: '0.75rem',
            fontSize: '0.875rem',
            fontWeight: '600',
            color: 'var(--muted)',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
          }}
        >
          Capital financier
        </h3>
        <div
          style={{
            fontSize: '1.75rem',
            fontWeight: 'bold',
            color: 'var(--accent)',
            marginBottom: '0.5rem',
          }}
        >
          {financial !== null && financial !== undefined ? formatMoney(String(financial)) : '0,00 €'}
        </div>
        <p
          style={{
            margin: 0,
            fontSize: '0.75rem',
            color: 'var(--muted)',
          }}
        >
          Liquidités disponibles
        </p>
      </div>

      {/* Carte Capital vivant SAKA */}
      <div
        style={{
          padding: '1.5rem',
          backgroundColor: 'var(--surface)',
          borderRadius: 'var(--radius)',
          border: '1px solid var(--border)',
          textAlign: 'center',
        }}
        className="four-p-card saka"
      >
        <h3
          style={{
            margin: 0,
            marginBottom: '0.75rem',
            fontSize: '0.875rem',
            fontWeight: '600',
            color: 'var(--muted)',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
          }}
        >
          Capital vivant (SAKA)
        </h3>
        <div
          style={{
            fontSize: '1.75rem',
            fontWeight: 'bold',
            color: '#84cc16',
            marginBottom: '0.5rem',
          }}
        >
          {saka !== null && saka !== undefined ? `${saka.toLocaleString('fr-FR')} SAKA` : '0 SAKA'}
        </div>
        <p
          style={{
            margin: 0,
            fontSize: '0.75rem',
            color: 'var(--muted)',
            marginBottom: '0.25rem',
          }}
        >
          Grains d'engagement
        </p>
        <p
          style={{
            margin: 0,
            fontSize: '0.625rem',
            color: 'var(--muted)',
            fontStyle: 'italic',
          }}
        >
          Les SAKA mesurent votre engagement non monétaire.
        </p>
      </div>

      {/* Carte Impact social/écologique */}
      <div
        style={{
          padding: '1.5rem',
          backgroundColor: 'var(--surface)',
          borderRadius: 'var(--radius)',
          border: '1px solid var(--border)',
          textAlign: 'center',
        }}
        className="four-p-card impact"
      >
        <h3
          style={{
            margin: 0,
            marginBottom: '0.75rem',
            fontSize: '0.875rem',
            fontWeight: '600',
            color: 'var(--muted)',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
          }}
          title="Ce score est un indicateur interne simplifié (V1) qui sera affiné avec des données d'impact plus riches."
        >
          Signal social (V1 interne)
        </h3>
        <div
          style={{
            fontSize: '1.75rem',
            fontWeight: 'bold',
            color: '#3b82f6',
            marginBottom: '0.5rem',
          }}
        >
          {impact !== null && impact !== undefined ? `${impact}/100` : '—'}
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
  );
}


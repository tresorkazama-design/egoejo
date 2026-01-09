/**
 * Composant FourPStrip - Bandeau "4P / Triple capital"
 * Affiche les 3 dimensions du capital : financier, vivant (SAKA), impact social/écologique
 */
import { formatMoney } from '../../utils/money';
import Tooltip from '../ui/Tooltip';
import { useLanguage } from '../../contexts/LanguageContext';
import { t } from '../../utils/i18n';

/**
 * @param {Object} props
 * @param {number|null} props.financial - Capital financier (euros)
 * @param {number|null} props.saka - Capital vivant SAKA (grains)
 * @param {number|null} props.impact - Impact social/écologique (score)
 */
export default function FourPStrip({ financial, saka, impact }) {
  const { language } = useLanguage();
  
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
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
        <h3
          style={{
            margin: 0,
            fontSize: '0.875rem',
            fontWeight: '600',
            color: 'var(--muted)',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
          }}
        >
          Capital vivant (SAKA)
        </h3>
          {/* Badge visuel distinctif SAKA */}
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              padding: '0.125rem 0.375rem',
              borderRadius: '0.25rem',
              fontSize: '0.625rem',
              fontWeight: '600',
              backgroundColor: '#84cc16',
              color: '#1a1a1a',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}
            aria-label={t('common.saka_not_convertible', language, {})}
            title={t('common.saka_not_convertible', language, {})}
          >
            {t('common.non_monetary', language, {})}
          </span>
          <Tooltip
            content={
              <div style={{ padding: '0.25rem 0' }}>
                <p style={{ margin: 0, marginBottom: '0.5rem', fontWeight: '600' }}>
                  {t('dashboard.saka_tooltip_line1', language, {})}
                </p>
                <p style={{ margin: 0, marginBottom: '0.5rem' }}>
                  {t('dashboard.saka_tooltip_line2', language, {})}
                </p>
                <p style={{ margin: 0, marginBottom: '0.5rem' }}>
                  {t('dashboard.saka_tooltip_line3', language, {})}
                </p>
                <p style={{ 
                  margin: 0, 
                  marginTop: '0.5rem', 
                  paddingTop: '0.5rem', 
                  borderTop: '1px solid rgba(255, 255, 255, 0.2)',
                  fontWeight: '600',
                  color: '#fbbf24'
                }}>
                  {t('common.saka_not_convertible', language, {})}
                </p>
              </div>
            }
            position="top"
            delay={300}
          >
            <button
              type="button"
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--muted)',
                cursor: 'help',
                fontSize: '0.875rem',
                padding: '0.25rem',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '50%',
                width: '1.25rem',
                height: '1.25rem',
                transition: 'color 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.color = 'var(--accent)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = 'var(--muted)';
              }}
              aria-label={t('dashboard.saka_tooltip_aria_label', language, {})}
            >
              ?
            </button>
          </Tooltip>
        </div>
        <div
          style={{
            fontSize: '1.75rem',
            fontWeight: 'bold',
            color: '#84cc16',
            marginBottom: '0.5rem',
          }}
        >
          {saka !== null && saka !== undefined ? `${saka.toLocaleString(language === 'fr' ? 'fr-FR' : 'en-US')} SAKA` : '0 SAKA'}
        </div>
        <p
          style={{
            margin: 0,
            fontSize: '0.75rem',
            color: 'var(--muted)',
            marginBottom: '0.25rem',
          }}
        >
          {t('dashboard.saka_grains_engagement', language, {})}
        </p>
        <p
          style={{
            margin: 0,
            fontSize: '0.625rem',
            color: 'var(--muted)',
            fontStyle: 'italic',
          }}
        >
          {t('dashboard.saka_non_monetary_desc', language, {})}
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


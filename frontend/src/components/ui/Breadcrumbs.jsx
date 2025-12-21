/**
 * Composant Breadcrumbs - Fil d'Ariane pour la navigation
 * Affiche le chemin de navigation avec liens cliquables
 */
import { Link } from 'react-router-dom';
import { useLanguage } from '../../contexts/LanguageContext';
import { t } from '../../utils/i18n';

/**
 * @param {Object} props
 * @param {Array<{label: string, to?: string}>} props.items - Items du breadcrumb
 * @param {string} props.separator - Séparateur (défaut: '>')
 */
export default function Breadcrumbs({ 
  items = [],
  separator = '>'
}) {
  const { language } = useLanguage();

  if (!items || items.length === 0) {
    return null;
  }

  return (
    <nav
      aria-label="Breadcrumb"
      style={{
        marginBottom: '1.5rem',
        padding: '0.75rem 0',
      }}
    >
      <ol
        style={{
          display: 'flex',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '0.5rem',
          listStyle: 'none',
          margin: 0,
          padding: 0,
          fontSize: '0.875rem',
          color: 'var(--muted)',
        }}
      >
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          const isFirst = index === 0;

          return (
            <li
              key={index}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
              }}
            >
              {!isFirst && (
                <span
                  style={{
                    color: 'var(--muted)',
                    margin: '0 0.25rem',
                    userSelect: 'none',
                  }}
                  aria-hidden="true"
                >
                  {separator}
                </span>
              )}
              {isLast ? (
                <span
                  style={{
                    color: 'var(--text)',
                    fontWeight: '500',
                    cursor: 'default',
                  }}
                  aria-current="page"
                >
                  {item.label}
                </span>
              ) : item.to ? (
                <Link
                  to={item.to}
                  style={{
                    color: 'var(--accent)',
                    textDecoration: 'none',
                    transition: 'opacity 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.opacity = '0.8';
                    e.currentTarget.style.textDecoration = 'underline';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.opacity = '1';
                    e.currentTarget.style.textDecoration = 'none';
                  }}
                >
                  {item.label}
                </Link>
              ) : (
                <span style={{ color: 'var(--muted)' }}>{item.label}</span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}


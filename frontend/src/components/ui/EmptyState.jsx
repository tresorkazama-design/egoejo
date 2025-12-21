/**
 * Composant EmptyState - État vide élégant avec guidance
 * Affiche un message et des actions suggérées quand une liste est vide
 */
import { Link } from 'react-router-dom';
import { useLanguage } from '../../contexts/LanguageContext';
import { t } from '../../utils/i18n';

/**
 * @param {Object} props
 * @param {string} props.title - Titre de l'état vide
 * @param {string} props.message - Message descriptif
 * @param {Array<{label: string, to: string, icon?: string}>} props.actions - Actions suggérées
 * @param {string} props.icon - Emoji ou icône (optionnel)
 */
export default function EmptyState({ 
  title = "Bienvenue !", 
  message = "Voici comment commencer :",
  actions = [],
  icon = "🌱"
}) {
  const { language } = useLanguage();

  return (
    <div
      style={{
        padding: '3rem 2rem',
        textAlign: 'center',
        backgroundColor: 'var(--surface)',
        borderRadius: 'var(--radius)',
        border: '1px solid var(--border)',
        margin: '2rem 0',
      }}
      className="empty-state"
      role="status"
      aria-live="polite"
    >
      <div
        style={{
          fontSize: '3rem',
          marginBottom: '1rem',
        }}
        aria-hidden="true"
      >
        {icon}
      </div>
      
      <h2
        style={{
          margin: 0,
          marginBottom: '0.75rem',
          fontSize: '1.5rem',
          fontWeight: '600',
          color: 'var(--text)',
        }}
      >
        {title}
      </h2>
      
      <p
        style={{
          margin: 0,
          marginBottom: '2rem',
          fontSize: '1rem',
          color: 'var(--muted)',
          lineHeight: 1.6,
        }}
      >
        {message}
      </p>

      {actions.length > 0 && (
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '0.75rem',
            alignItems: 'center',
            maxWidth: '400px',
            margin: '0 auto',
          }}
        >
          {actions.map((action, index) => (
            <Link
              key={index}
              to={action.to}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.75rem 1.5rem',
                backgroundColor: 'var(--accent)',
                color: 'white',
                borderRadius: 'var(--radius)',
                textDecoration: 'none',
                fontSize: '0.875rem',
                fontWeight: '500',
                transition: 'opacity 0.2s',
                width: '100%',
                justifyContent: 'center',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.opacity = '0.9';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.opacity = '1';
              }}
              aria-label={action.label}
            >
              {action.icon && <span aria-hidden="true">{action.icon}</span>}
              <span>{action.label}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}


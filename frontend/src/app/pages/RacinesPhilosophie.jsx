/**
 * Page Racines & Philosophie
 * Section dédiée aux fondements historiques de l'agriculture respectueuse du vivant
 */
import { useState, useEffect } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { fetchAPI } from '../../utils/api';
import { t } from '../../utils/i18n';
import SEO from '../../components/SEO';
import ErrorBoundary from '../../components/ErrorBoundary';

export default function RacinesPhilosophie() {
  const { language } = useLanguage();
  const [contents, setContents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAPI('/api/contents/?category=racines-philosophie&status=published')
      .then(data => {
        setContents(data.results || data || []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Erreur chargement contenus:', err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <ErrorBoundary>
      <SEO 
        title={t('racines.title', language) || 'Racines & Philosophie'}
        description={t('racines.description', language) || 'Découvrez les fondements historiques de l\'agriculture respectueuse du vivant'}
      />
      <div className="racines-philosophie" style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
        <h1 style={{ marginBottom: '1rem' }}>
          {t('racines.title', language) || 'Racines & Philosophie'}
        </h1>
        
        <p className="intro" style={{ 
          fontSize: '1.1rem', 
          color: 'var(--muted)', 
          marginBottom: '2rem',
          lineHeight: '1.6',
        }}>
          {t('racines.intro', language) || 
            'Découvrez les fondements historiques de l\'agriculture respectueuse du vivant, notamment le "Cours aux agriculteurs" de Rudolf Steiner (1924). Cette section explore les racines philosophiques de notre approche systémique du vivant.'}
        </p>

        {loading && (
          <p style={{ textAlign: 'center', color: 'var(--muted)' }}>
            {t('common.loading', language) || 'Chargement...'}
          </p>
        )}

        {error && (
          <p style={{ textAlign: 'center', color: 'red' }}>
            {error}
          </p>
        )}

        {!loading && !error && contents.length === 0 && (
          <p style={{ textAlign: 'center', color: 'var(--muted)' }}>
            {t('racines.no_content', language) || 'Aucun contenu disponible pour le moment.'}
          </p>
        )}

        {!loading && !error && contents.length > 0 && (
          <div 
            className="contents-grid" 
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
              gap: '1.5rem',
            }}
          >
            {contents.map(content => (
              <div 
                key={content.id} 
                className="content-card"
                style={{
                  padding: '1.5rem',
                  backgroundColor: 'var(--surface)',
                  borderRadius: 'var(--radius)',
                }}
              >
                <h3 style={{ marginBottom: '0.5rem', color: 'var(--accent)' }}>
                  {content.title}
                </h3>
                {content.description && (
                  <p style={{ color: 'var(--muted)', marginBottom: '1rem' }}>
                    {content.description}
                  </p>
                )}
                {content.tags && content.tags.length > 0 && (
                  <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                    {content.tags.map((tag, idx) => (
                      <span 
                        key={idx}
                        style={{
                          padding: '0.25rem 0.5rem',
                          backgroundColor: 'var(--accent-soft)',
                          borderRadius: '4px',
                          fontSize: '0.85rem',
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
                {content.external_url && (
                  <a 
                    href={content.external_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    style={{
                      display: 'inline-block',
                      marginTop: '1rem',
                      color: 'var(--accent)',
                      textDecoration: 'none',
                    }}
                  >
                    {t('racines.read_more', language) || 'Lire la suite →'}
                  </a>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
}


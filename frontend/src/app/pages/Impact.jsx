/**
 * Page du tableau de bord d'impact utilisateur
 * Affiche les métriques de contribution et d'engagement
 */
import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { fetchAPI } from '../../utils/api';
import { t } from '../../utils/i18n';
import SEO from '../../components/SEO';
import ErrorBoundary from '../../components/ErrorBoundary';

export default function Impact() {
  const { user } = useAuth();
  const { language } = useLanguage();
  const [impact, setImpact] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!user) {
      setLoading(false);
      return;
    }

    fetchAPI('/api/impact/dashboard/')
      .then(data => {
        setImpact(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Erreur chargement impact:', err);
        setError(err.message);
        setLoading(false);
      });
  }, [user]);

  if (!user) {
    return (
      <div className="impact-page" style={{ padding: '2rem', textAlign: 'center' }}>
        <h1>{t('impact.title', language) || 'Votre Impact'}</h1>
        <p>{t('impact.login_required', language) || 'Veuillez vous connecter pour voir votre impact.'}</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="impact-page" style={{ padding: '2rem', textAlign: 'center' }}>
        <p>{t('common.loading', language) || 'Chargement...'}</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="impact-page" style={{ padding: '2rem', textAlign: 'center' }}>
        <p style={{ color: 'red' }}>{error}</p>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <SEO 
        title={t('impact.title', language) || 'Votre Impact'}
        description={t('impact.description', language) || 'Découvrez votre impact sur les projets EGOEJO'}
      />
      <div className="impact-page" style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
        <h1 style={{ marginBottom: '2rem' }}>{t('impact.title', language) || 'Votre Impact'}</h1>
        
        {impact?.impact_message && (
          <div 
            className="impact-message" 
            style={{
              padding: '1.5rem',
              backgroundColor: 'var(--accent-soft)',
              borderRadius: 'var(--radius)',
              marginBottom: '2rem',
              fontSize: '1.2rem',
              fontWeight: '500',
            }}
          >
            {impact.impact_message}
          </div>
        )}

        <div 
          className="impact-stats" 
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '1.5rem',
            marginBottom: '2rem',
          }}
        >
          <div 
            className="stat-card" 
            style={{
              padding: '1.5rem',
              backgroundColor: 'var(--surface)',
              borderRadius: 'var(--radius)',
              textAlign: 'center',
            }}
          >
            <h2 style={{ fontSize: '2.5rem', color: 'var(--accent)', marginBottom: '0.5rem' }}>
              {impact?.total_contributions?.toFixed(2) || '0.00'}€
            </h2>
            <p style={{ color: 'var(--muted)' }}>
              {t('impact.total_contributions', language) || 'Total contribué'}
            </p>
          </div>

          <div 
            className="stat-card" 
            style={{
              padding: '1.5rem',
              backgroundColor: 'var(--surface)',
              borderRadius: 'var(--radius)',
              textAlign: 'center',
            }}
          >
            <h2 style={{ fontSize: '2.5rem', color: 'var(--accent)', marginBottom: '0.5rem' }}>
              {impact?.projects_supported || 0}
            </h2>
            <p style={{ color: 'var(--muted)' }}>
              {t('impact.projects_supported', language) || 'Projets soutenus'}
            </p>
          </div>

          <div 
            className="stat-card" 
            style={{
              padding: '1.5rem',
              backgroundColor: 'var(--surface)',
              borderRadius: 'var(--radius)',
              textAlign: 'center',
            }}
          >
            <h2 style={{ fontSize: '2.5rem', color: 'var(--accent)', marginBottom: '0.5rem' }}>
              {impact?.cagnottes_contributed || 0}
            </h2>
            <p style={{ color: 'var(--muted)' }}>
              {t('impact.cagnottes_contributed', language) || 'Cagnottes'}
            </p>
          </div>

          <div 
            className="stat-card" 
            style={{
              padding: '1.5rem',
              backgroundColor: 'var(--surface)',
              borderRadius: 'var(--radius)',
              textAlign: 'center',
            }}
          >
            <h2 style={{ fontSize: '2.5rem', color: 'var(--accent)', marginBottom: '0.5rem' }}>
              {impact?.intentions_submitted || 0}
            </h2>
            <p style={{ color: 'var(--muted)' }}>
              {t('impact.intentions_submitted', language) || 'Intentions soumises'}
            </p>
          </div>
        </div>

        {impact?.last_updated && (
          <p style={{ color: 'var(--muted)', fontSize: '0.9rem', textAlign: 'center' }}>
            {t('impact.last_updated', language) || 'Dernière mise à jour'} :{' '}
            {new Date(impact.last_updated).toLocaleString(language === 'fr' ? 'fr-FR' : 'en-US')}
          </p>
        )}
      </div>
    </ErrorBoundary>
  );
}


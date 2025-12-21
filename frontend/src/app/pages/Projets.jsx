import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Loader } from '../../components/Loader';
import CardTilt from '../../components/CardTilt';
import { fetchAPI, handleAPIError } from '../../utils/api';
import { useLanguage } from '../../contexts/LanguageContext';
import { t } from '../../utils/i18n';
import SEO from '../../components/SEO';
import { useSEO } from '../../hooks/useSEO';
import { useGlobalAssets } from '../../hooks/useGlobalAssets';
import { useNotificationContext } from '../../contexts/NotificationContext';
import { useAuth } from '../../contexts/AuthContext';
import Impact4PCard from '../../components/projects/Impact4PCard';
import EmptyState from '../../components/ui/EmptyState';
import { Skeleton, SkeletonCard } from '../../components/ui/Skeleton';
import Breadcrumbs from '../../components/ui/Breadcrumbs';

export const Projets = React.memo(() => {
  const { language } = useLanguage();
  const { user } = useAuth();
  const { showSuccess, showError } = useNotificationContext();
  const { data: assets, refetch: refetchAssets } = useGlobalAssets();
  const [projets, setProjets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [sakaBoostEnabled, setSakaBoostEnabled] = useState(false);
  const [boostingProjects, setBoostingProjects] = useState(new Set()); // IDs des projets en cours de boost
  
  const sakaBalance = assets?.saka?.balance ?? 0;
  const sakaBoostCost = 10; // Aligné avec le backend SAKA_PROJECT_BOOST_COST

  const seoProps = useSEO({
    titleKey: "seo.projets_title",
    descriptionKey: "seo.projets_description",
    keywords: t("seo.projets_keywords", language),
    jsonLd: {
      '@context': 'https://schema.org',
      '@type': 'CollectionPage',
      name: t("seo.projets_title", language),
      description: t("seo.projets_description", language),
      url: `${import.meta.env.VITE_SITE_URL || 'https://egoejo.org'}/projets`,
    },
  });

  const loadProjets = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchAPI('/projets/');
      setProjets(data.results || data || []);
    } catch (err) {
      setError(handleAPIError(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProjets();
  }, [loadProjets]);

  // Vérifier si SAKA_PROJECT_BOOST_ENABLED est activé
  useEffect(() => {
    const checkSakaFeatures = async () => {
      try {
        const config = await fetchAPI('/config/features/');
        setSakaBoostEnabled(config?.saka_project_boost_enabled || false);
      } catch (err) {
        console.warn('Impossible de récupérer la config SAKA, désactivation par défaut');
        setSakaBoostEnabled(false);
      }
    };
    checkSakaFeatures();
  }, []);

  // Fonction pour booster un projet avec SAKA
  const handleBoost = useCallback(async (projectId) => {
    if (!user) {
      showError('Vous devez être connecté pour nourrir un projet.');
      return;
    }

    if (sakaBalance < sakaBoostCost) {
      showError(`Solde SAKA insuffisant. Vous avez ${sakaBalance} SAKA, il en faut ${sakaBoostCost}.`);
      return;
    }

    setBoostingProjects(prev => new Set(prev).add(projectId));

    try {
      const response = await fetchAPI(`/projets/${projectId}/boost/`, {
        method: 'POST',
        body: JSON.stringify({ amount: sakaBoostCost }),
      });

      // fetchAPI retourne déjà le JSON parsé, pas de response.ok
      if (response && response.ok !== false) {
        showSuccess('🌾 Merci, vos SAKA nourrissent ce projet.');
        
        // Mettre à jour le projet localement avec les valeurs retournées par l'API
        setProjets(prevProjets => 
          prevProjets.map(proj => 
            proj.id === projectId
              ? {
                  ...proj,
                  saka_score: response.new_saka_score || ((proj.saka_score || 0) + sakaBoostCost),
                  saka_supporters_count: response.new_saka_supporters_count || ((proj.saka_supporters_count || 0) + 1),
                }
              : proj
          )
        );
        
        // Mettre à jour le solde SAKA
        await refetchAssets();
      }
    } catch (err) {
      const errorMessage = err.message || 'Erreur lors du boost du projet';
      
      // Message spécifique pour solde insuffisant
      if (errorMessage.includes('insuffisant') || errorMessage.includes('Solde')) {
        showError(`Solde SAKA insuffisant. ${errorMessage}`);
      } else {
        showError(errorMessage);
      }
    } finally {
      setBoostingProjects(prev => {
        const newSet = new Set(prev);
        newSet.delete(projectId);
        return newSet;
      });
    }
  }, [user, sakaBalance, sakaBoostCost, showSuccess, showError, refetchAssets]);

  if (loading) {
    return (
      <div className="page page--citations" data-testid="projets-page">
        <SEO {...seoProps} />
        <section className="citations-hero">
          <Skeleton width="200px" height="1rem" style={{ marginBottom: '1rem' }} />
          <Skeleton width="60%" height="2.5rem" style={{ marginBottom: '1rem' }} />
          <Skeleton width="80%" height="1.25rem" />
        </section>
        <section className="citation-group" style={{ padding: '2rem' }}>
          <div style={{ display: 'grid', gap: '2rem' }}>
            {[1, 2, 3].map((i) => (
              <SkeletonCard key={i} withImage={true} textLines={3} />
            ))}
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="page page--citations" data-testid="projets-page">
      <SEO {...seoProps} />
      
      {/* Breadcrumbs */}
      <div style={{ padding: '2rem 2rem 0', maxWidth: '1400px', margin: '0 auto' }}>
        <Breadcrumbs
          items={[
            { label: 'Accueil', to: '/' },
            { label: t("projets.title", language) || 'Projets' },
          ]}
        />
      </div>

      <section className="citations-hero" aria-labelledby="projets-title" role="region" aria-label={t("projets.title", language)}>
        <div className="citations-hero__badge" role="text" aria-label={t("projets.badge", language)}>{t("projets.badge", language)}</div>
        <h1 id="projets-title" className="citations-hero__title">{t("projets.title", language)}</h1>
        <p className="citations-hero__subtitle">
          {t("projets.subtitle", language)}
        </p>

        <blockquote className="citations-hero__highlight" aria-labelledby="projets-cite">
          <p>{t("projets.highlight_text", language)}</p>
          <cite id="projets-cite">{t("projets.highlight_author", language)}</cite>
        </blockquote>

        <dl className="citations-hero__stats" aria-label={t("projets.stats", language) || "Statistiques"}>
          <div>
            <dt>{projets.length} {projets.length > 1 ? t("projets.stats_projets_plural", language) : t("projets.stats_projets", language)}</dt>
            <dd>{t("projets.stats_projets_desc", language)}</dd>
          </div>
          <div>
            <dt>{t("projets.stats_formats", language)}</dt>
            <dd>{t("projets.stats_formats_desc", language)}</dd>
          </div>
          <div>
            <dt>{t("projets.stats_communaute", language)}</dt>
            <dd>{t("projets.stats_communaute_desc", language)}</dd>
          </div>
        </dl>
      </section>

      {error ? (
        <section className="citation-group" role="alert" aria-live="polite">
          <div style={{ padding: "24px", color: "var(--muted)" }}>
            <p>{t("common.error", language)} : {error}</p>
          </div>
        </section>
      ) : projets.length === 0 ? (
        <EmptyState
          title="Aucun projet pour le moment"
          message="Les projets de la communauté apparaîtront ici. Revenez bientôt pour découvrir de nouvelles initiatives !"
          icon="🌾"
          actions={[
            {
              label: 'Explorer les contenus',
              to: '/contenus',
              icon: '📚',
            },
            {
              label: 'Revenir à l\'accueil',
              to: '/',
              icon: '🏠',
            },
          ]}
        />
      ) : (
        <div className="citations-grid" role="list" aria-label={t("projets.list", language) || "Liste des projets"}>
          {projets.map((projet) => (
            <CardTilt key={projet.id || projet.slug} role="listitem">
              <section className="citation-group" aria-labelledby={`projet-${projet.id || projet.slug}`}>
                <header className="citation-group__header">
                  <span className="citation-group__tag">{t("projets.project_tag", language)}</span>
                  <h2 id={`projet-${projet.id || projet.slug}`} className="citation-group__title">{projet.titre || projet.nom || projet.name || t("projets.untitled", language)}</h2>
                  {projet.description && (
                    <p className="citation-group__description" aria-labelledby={`projet-${projet.id || projet.slug}`}>{projet.description}</p>
                  )}
                </header>
                {projet.contenu && (
                  <div className="citation-group__quotes">
                    <div className="citation-card">
                      <p className="citation-card__text">{projet.contenu}</p>
                    </div>
                  </div>
                )}
                
                {/* Affichage 4P */}
                {projet.impact_4p && (
                  <Impact4PCard impact4p={projet.impact_4p} compact={true} />
                )}
                
                {/* Phase 2 SAKA : Informations et bouton Sorgho-boost */}
                {(sakaBoostEnabled || projet.saka_score > 0) && (
                  <div className="citation-group__saka" style={{ marginTop: '1rem', padding: '1rem', backgroundColor: 'var(--surface)', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}>
                    <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginBottom: '0.25rem' }}>
                      Soutien SAKA : {projet.saka_score || 0} grains
                    </p>
                    {projet.saka_supporters_count > 0 && (
                      <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginBottom: '0.5rem' }}>
                        Soutenu par {projet.saka_supporters_count} membre{projet.saka_supporters_count > 1 ? 's' : ''}
                      </p>
                    )}
                    {sakaBoostEnabled && user && (
                      <button
                        onClick={() => handleBoost(projet.id)}
                        disabled={boostingProjects.has(projet.id) || sakaBalance < sakaBoostCost}
                        style={{
                          width: '100%',
                          padding: '0.75rem',
                          backgroundColor: boostingProjects.has(projet.id) || sakaBalance < sakaBoostCost ? 'var(--muted)' : 'var(--accent)',
                          color: 'white',
                          border: 'none',
                          borderRadius: 'var(--radius)',
                          cursor: boostingProjects.has(projet.id) || sakaBalance < sakaBoostCost ? 'not-allowed' : 'pointer',
                          fontSize: '0.875rem',
                          fontWeight: '500',
                        }}
                      >
                        {boostingProjects.has(projet.id)
                          ? 'Nourrissage...'
                          : `Nourrir ce projet (−${sakaBoostCost} SAKA)`}
                      </button>
                    )}
                  </div>
                )}
              </section>
            </CardTilt>
          ))}
        </div>
      )}

      <section className="citations-cta" aria-labelledby="projets-cta-title">
        <h2 id="projets-cta-title" className="heading-l">{t("projets.cta_title", language)}</h2>
        <p className="lead">
          {t("projets.cta_subtitle", language)}
        </p>
        <div style={{ display: "flex", gap: "14px", flexWrap: "wrap" }} role="group" aria-label={t("projets.actions", language) || "Actions"}>
          <Link to="/rejoindre" className="btn btn-primary" aria-label={t("nav.rejoindre", language)}>
            {t("nav.rejoindre", language)}
          </Link>
          <a
            href="mailto:contact@egoejo.org?subject=Proposition%20de%20projet"
            className="btn btn-ghost"
            aria-label={t("projets.cta_proposer", language)}
          >
            {t("projets.cta_proposer", language)}
          </a>
        </div>
      </section>
    </div>
  );
});

Projets.displayName = 'Projets';

export default Projets;

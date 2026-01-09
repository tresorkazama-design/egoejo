import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Loader } from '../../components/Loader';
import CardTilt from '../../components/CardTilt';
import { useLanguage } from '../../contexts/LanguageContext';
import { t } from '../../utils/i18n';
import SEO from '../../components/SEO';
import { useSEO } from '../../hooks/useSEO';
import { Skeleton, SkeletonCard } from '../../components/ui/Skeleton';
import Breadcrumbs from '../../components/ui/Breadcrumbs';
import { sanitizeContent } from '../../utils/content';
import { useContents } from '../../hooks/useContents';

const getTypeLabels = (lang) => ({
  podcast: t("contenus.type_podcast", lang),
  video: t("contenus.type_video", lang),
  pdf: t("contenus.type_pdf", lang),
  article: t("contenus.type_article", lang),
  poeme: t("contenus.type_poeme", lang),
  chanson: t("contenus.type_chanson", lang),
  autre: t("contenus.type_autre", lang),
});

export const Contenus = () => {
  const { language } = useLanguage();
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(20); // Taille de page fixe
  const TYPE_LABELS = getTypeLabels(language);

  const seoProps = useSEO({
    titleKey: "seo.contenus_title",
    descriptionKey: "seo.contenus_description",
    keywords: t("seo.contenus_keywords", language),
  });

  // Utiliser React Query pour récupérer les contenus avec pagination et cache
  const {
    data: contentsData,
    isLoading: loading,
    isError,
    error: queryError,
    isFetching, // Indique si une requête est en cours (y compris revalidation)
    isPaused, // Indique si la requête est en pause (ex: offline)
  } = useContents({
    page: currentPage,
    pageSize: pageSize,
    status: 'published',
  });

  const contenus = contentsData?.contents || [];
  const error = isError ? (queryError?.message || t("common.error", language)) : '';
  const totalCount = contentsData?.count || 0;
  const totalPages = contentsData?.totalPages || 1;
  const hasNextPage = contentsData?.next !== null;
  const hasPreviousPage = contentsData?.previous !== null;
  const isOffline = typeof navigator !== 'undefined' && !navigator.onLine;

  if (loading) {
    return (
      <div className="page page--citations" data-testid="contenus-page">
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
    <div className="page page--citations" data-testid="contenus-page">
      <SEO {...seoProps} />
      
      {/* Breadcrumbs */}
      <div style={{ padding: '2rem 2rem 0', maxWidth: '1400px', margin: '0 auto' }}>
        <Breadcrumbs
          items={[
            { label: 'Accueil', to: '/' },
            { label: t("contenus.title", language) || 'Contenus' },
          ]}
        />
      </div>

      <section className="citations-hero" aria-labelledby="contenus-title" role="region" aria-label={t("contenus.title", language)}>
        <div className="citations-hero__badge" role="text" aria-label={t("contenus.badge", language)} data-testid="contenus-badge">{t("contenus.badge", language)}</div>
        <h1 id="contenus-title" className="citations-hero__title">{t("contenus.title", language)}</h1>
        <p className="citations-hero__subtitle">
          {t("contenus.subtitle", language)}
        </p>

        <blockquote className="citations-hero__highlight" aria-labelledby="contenus-cite">
          <p>{t("contenus.highlight_text", language)}</p>
          <cite id="contenus-cite">{t("contenus.highlight_author", language)}</cite>
        </blockquote>

        <dl className="citations-hero__stats" aria-label={t("contenus.stats", language) || "Statistiques"} data-testid="contenus-stats">
          <div data-testid="contenus-stats-count">
            <dt>{totalCount} {totalCount > 1 ? t("contenus.stats_count_plural", language) : t("contenus.stats_count", language)}</dt>
            <dd>{totalCount > 1 ? t("contenus.stats_available_plural", language) : t("contenus.stats_available", language)}</dd>
          </div>
          <div data-testid="contenus-stats-formats">
            <dt>{t("contenus.stats_formats_title", language)}</dt>
            <dd>{t("contenus.stats_formats_desc", language)}</dd>
          </div>
          <div data-testid="contenus-stats-library">
            <dt>{t("contenus.stats_library_title", language)}</dt>
            <dd>{t("contenus.stats_library_desc", language)}</dd>
          </div>
        </dl>
      </section>

      {error ? (
        <section className="citation-group" role="alert" aria-live="polite">
          <div style={{ padding: "24px", color: "var(--muted)" }}>
            {isOffline ? (
              <>
                <p style={{ marginBottom: '1rem', fontWeight: '500' }}>
                  📡 {t("contenus.offline_title", language) || "Mode hors-ligne"}
                </p>
                <p style={{ marginBottom: '1rem' }}>
                  {t("contenus.offline_message", language) || "Vous êtes hors-ligne. Les contenus que vous avez déjà visités sont disponibles depuis le cache."}
                </p>
                <p style={{ fontSize: '0.9rem', color: 'var(--muted)', marginBottom: '1rem' }}>
                  {t("contenus.offline_hint", language) || "Reconnectez-vous pour voir les nouveaux contenus."}
                </p>
              </>
            ) : (
              <>
                <p>{t("common.error", language)} : {error}</p>
                <button 
                  onClick={() => window.location.reload()} 
                  className="btn btn-ghost"
                  style={{ marginTop: '1rem' }}
                >
                  {t("common.retry", language) || "Réessayer"}
                </button>
              </>
            )}
          </div>
        </section>
      ) : !loading && contenus.length === 0 ? (
        <section className="citation-group" aria-labelledby="no-contenus-title">
          <header className="citation-group__header">
            <span className="citation-group__tag">{t("contenus.info_tag", language)}</span>
            <h2 id="no-contenus-title" className="citation-group__title">
              {isOffline 
                ? (t("contenus.offline_no_cache_title", language) || "Aucun contenu en cache")
                : (t("contenus.no_content_title", language) || "Aucun contenu disponible")
              }
            </h2>
            <p className="citation-group__description" aria-labelledby="no-contenus-title">
              {isOffline 
                ? (t("contenus.offline_no_cache_desc", language) || "Vous êtes hors-ligne et aucun contenu n'est disponible en cache. Reconnectez-vous pour accéder aux contenus.")
                : (t("contenus.no_content_desc", language) || "Aucun contenu n'est disponible pour le moment.")
              }
            </p>
          </header>
        </section>
      ) : (
        <div className="citations-grid" role="list" aria-label={t("contenus.list", language) || "Liste des contenus"}>
          {contenus.map((contenu) => (
            <CardTilt key={contenu.id || contenu.slug} role="listitem">
              <section className="citation-group" aria-labelledby={`contenu-${contenu.id || contenu.slug}`}>
              <header className="citation-group__header">
                <span className="citation-group__tag">{TYPE_LABELS[sanitizeContent(contenu.type)] || t("contenus.type_autre", language)}</span>
                <h2 id={`contenu-${contenu.id || contenu.slug}`} className="citation-group__title">{sanitizeContent(contenu.title) || t("contenus.no_content_title", language)}</h2>
                {contenu.description && (
                  <p className="citation-group__description" aria-labelledby={`contenu-${contenu.id || contenu.slug}`}>{sanitizeContent(contenu.description)}</p>
                )}
              </header>
              {(contenu.external_url || contenu.file) && (
                <div className="citation-group__quotes">
                  <div className="citation-card">
                    {contenu.external_url ? (
                      <p className="citation-card__text">
                        <a
                          href={contenu.external_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ color: 'var(--accent)', textDecoration: 'underline' }}
                          aria-label={`${t("contenus.access_content", language)} - ${sanitizeContent(contenu.title) || t("contenus.no_content_title", language)}`}
                        >
                          {t("contenus.access_content", language)} →
                        </a>
                      </p>
                    ) : contenu.file ? (
                      <p className="citation-card__text">
                        <a
                          href={contenu.file}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ color: 'var(--accent)', textDecoration: 'underline' }}
                          aria-label={`${t("contenus.download_file", language)} - ${sanitizeContent(contenu.title) || t("contenus.no_content_title", language)}`}
                        >
                          {t("contenus.download_file", language)} →
                        </a>
                      </p>
                    ) : null}
                    {contenu.anonymous_display_name && (
                      <cite className="citation-card__author">
                        {t("contenus.by_author", language, { author: sanitizeContent(contenu.anonymous_display_name) })}
                      </cite>
                    )}
                  </div>
                </div>
              )}
              </section>
            </CardTilt>
          ))}
        </div>
      )}

      {/* Pagination */}
      {!loading && !error && contenus.length > 0 && totalPages > 1 && (
        <section className="citations-pagination" aria-label={t("contenus.pagination", language) || "Pagination"}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            gap: '1rem',
            padding: '2rem',
            flexWrap: 'wrap'
          }}>
            <button
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={!hasPreviousPage || isFetching}
              className="btn btn-ghost"
              aria-label={t("contenus.pagination_previous", language) || "Page précédente"}
              data-testid="pagination-prev"
            >
              ← {t("contenus.pagination_previous", language) || "Précédent"}
            </button>
            
            <span style={{ 
              color: 'var(--muted)',
              fontSize: '0.9rem'
            }} data-testid="pagination-info">
              {t("contenus.pagination_page", language, { 
                current: currentPage, 
                total: totalPages 
              }) || `Page ${currentPage} sur ${totalPages}`}
            </span>
            
            <button
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={!hasNextPage || isFetching}
              className="btn btn-ghost"
              aria-label={t("contenus.pagination_next", language) || "Page suivante"}
              data-testid="pagination-next"
            >
              {t("contenus.pagination_next", language) || "Suivant"} →
            </button>
          </div>
          
          {isFetching && (
            <div style={{ 
              textAlign: 'center', 
              color: 'var(--muted)',
              fontSize: '0.85rem',
              padding: '0.5rem'
            }} data-testid="pagination-loading">
              {t("common.loading", language) || "Chargement..."}
            </div>
          )}
        </section>
      )}

      <section className="citations-cta" aria-labelledby="contenus-cta-title">
        <h2 id="contenus-cta-title" className="heading-l">{t("contenus.share_title", language)}</h2>
        <p className="lead">
          {t("contenus.share_subtitle", language)}
        </p>
        <div style={{ display: "flex", gap: "14px", flexWrap: "wrap" }} role="group" aria-label={t("contenus.actions", language) || "Actions"}>
          <a
            href="mailto:contact@egoejo.org?subject=Proposition%20de%20contenu"
            className="btn btn-primary"
            aria-label={t("contenus.propose_content", language)}
            data-testid="contenus-link-propose"
          >
            {t("contenus.propose_content", language)}
          </a>
          <Link to="/rejoindre" className="btn btn-ghost" aria-label={t("nav.rejoindre", language)} data-testid="contenus-link-rejoindre">
            {t("nav.rejoindre", language)}
          </Link>
        </div>
      </section>

      <section className="citations-references" aria-labelledby="contenus-types-title" data-testid="contenus-types-section">
        <h3 id="contenus-types-title" className="heading-m">{t("contenus.types_title", language)}</h3>
        <p className="muted" style={{ margin: 0, lineHeight: 1.6 }}>
          {t("contenus.types_desc", language)}
        </p>
      </section>
    </div>
  );
};

export default Contenus;


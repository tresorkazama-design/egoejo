import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Loader } from '../../components/Loader';
import CardTilt from '../../components/CardTilt';
import { fetchAPI, handleAPIError } from '../../utils/api';
import { useLanguage } from '../../contexts/LanguageContext';
import { t } from '../../utils/i18n';
import SEO from '../../components/SEO';
import { useSEO } from '../../hooks/useSEO';
import { Skeleton, SkeletonCard } from '../../components/ui/Skeleton';
import Breadcrumbs from '../../components/ui/Breadcrumbs';

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
  const [contenus, setContenus] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const TYPE_LABELS = getTypeLabels(language);

  const seoProps = useSEO({
    titleKey: "seo.contenus_title",
    descriptionKey: "seo.contenus_description",
    keywords: t("seo.contenus_keywords", language),
  });

  useEffect(() => {
    const loadContenus = async () => {
      try {
        setLoading(true);
        // Récupérer uniquement les contenus publiés
        const data = await fetchAPI('/contents/?status=published');
        setContenus(data.results || data || []);
      } catch (err) {
        setError(handleAPIError(err));
      } finally {
        setLoading(false);
      }
    };

    loadContenus();
  }, []);

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
        <div className="citations-hero__badge" role="text" aria-label={t("contenus.badge", language)}>{t("contenus.badge", language)}</div>
        <h1 id="contenus-title" className="citations-hero__title">{t("contenus.title", language)}</h1>
        <p className="citations-hero__subtitle">
          {t("contenus.subtitle", language)}
        </p>

        <blockquote className="citations-hero__highlight" aria-labelledby="contenus-cite">
          <p>{t("contenus.highlight_text", language)}</p>
          <cite id="contenus-cite">{t("contenus.highlight_author", language)}</cite>
        </blockquote>

        <dl className="citations-hero__stats" aria-label={t("contenus.stats", language) || "Statistiques"}>
          <div>
            <dt>{contenus.length} {contenus.length > 1 ? t("contenus.stats_count_plural", language) : t("contenus.stats_count", language)}</dt>
            <dd>{contenus.length > 1 ? t("contenus.stats_available_plural", language) : t("contenus.stats_available", language)}</dd>
          </div>
          <div>
            <dt>{t("contenus.stats_formats_title", language)}</dt>
            <dd>{t("contenus.stats_formats_desc", language)}</dd>
          </div>
          <div>
            <dt>{t("contenus.stats_library_title", language)}</dt>
            <dd>{t("contenus.stats_library_desc", language)}</dd>
          </div>
        </dl>
      </section>

      {error ? (
        <section className="citation-group" role="alert" aria-live="polite">
          <div style={{ padding: "24px", color: "var(--muted)" }}>
            <p>{t("common.error", language)} : {error}</p>
          </div>
        </section>
      ) : contenus.length === 0 ? (
        <section className="citation-group" aria-labelledby="no-contenus-title">
          <header className="citation-group__header">
            <span className="citation-group__tag">{t("contenus.info_tag", language)}</span>
            <h2 id="no-contenus-title" className="citation-group__title">{t("contenus.no_content_title", language)}</h2>
            <p className="citation-group__description" aria-labelledby="no-contenus-title">
              {t("contenus.no_content_desc", language)}
            </p>
          </header>
        </section>
      ) : (
        <div className="citations-grid" role="list" aria-label={t("contenus.list", language) || "Liste des contenus"}>
          {contenus.map((contenu) => (
            <CardTilt key={contenu.id || contenu.slug} role="listitem">
              <section className="citation-group" aria-labelledby={`contenu-${contenu.id || contenu.slug}`}>
              <header className="citation-group__header">
                <span className="citation-group__tag">{TYPE_LABELS[contenu.type] || t("contenus.type_autre", language)}</span>
                <h2 id={`contenu-${contenu.id || contenu.slug}`} className="citation-group__title">{contenu.title || t("contenus.no_content_title", language)}</h2>
                {contenu.description && (
                  <p className="citation-group__description" aria-labelledby={`contenu-${contenu.id || contenu.slug}`}>{contenu.description}</p>
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
                          aria-label={`${t("contenus.access_content", language)} - ${contenu.title || t("contenus.no_content_title", language)}`}
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
                          aria-label={`${t("contenus.download_file", language)} - ${contenu.title || t("contenus.no_content_title", language)}`}
                        >
                          {t("contenus.download_file", language)} →
                        </a>
                      </p>
                    ) : null}
                    {contenu.anonymous_display_name && (
                      <cite className="citation-card__author">
                        {t("contenus.by_author", language, { author: contenu.anonymous_display_name })}
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
          >
            {t("contenus.propose_content", language)}
          </a>
          <Link to="/rejoindre" className="btn btn-ghost" aria-label={t("nav.rejoindre", language)}>
            {t("nav.rejoindre", language)}
          </Link>
        </div>
      </section>

      <section className="citations-references" aria-labelledby="contenus-types-title">
        <h3 id="contenus-types-title" className="heading-m">{t("contenus.types_title", language)}</h3>
        <p className="muted" style={{ margin: 0, lineHeight: 1.6 }}>
          {t("contenus.types_desc", language)}
        </p>
      </section>
    </div>
  );
};

export default Contenus;


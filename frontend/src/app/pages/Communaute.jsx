import React from "react";
import { Link } from "react-router-dom";
import CardTilt from "../../components/CardTilt";
import { useLanguage } from "../../contexts/LanguageContext";
import { t } from "../../utils/i18n";
import SEO from "../../components/SEO";
import { useSEO } from "../../hooks/useSEO";

const getCommunitySections = (lang) => [
  {
    title: t("communaute.engagement_rejoindre", lang),
    description: t("communaute.engagement_rejoindre_desc", lang),
  },
  {
    title: t("communaute.engagement_evenements", lang),
    description: t("communaute.engagement_evenements_desc", lang),
  },
  {
    title: t("communaute.engagement_contribuer", lang),
    description: t("communaute.engagement_contribuer_desc", lang),
  },
];

export default function Communaute() {
  const { language } = useLanguage();
  const COMMUNITY_SECTIONS = getCommunitySections(language);

  const seoProps = useSEO({
    titleKey: "seo.communaute_title",
    descriptionKey: "seo.communaute_description",
    keywords: t("seo.communaute_keywords", language),
  });

  return (
    <div className="page page--citations" data-testid="communaute-page">
      <SEO {...seoProps} />
      <section className="citations-hero" aria-labelledby="communaute-title" role="region" aria-label={t("communaute.title", language)}>
        <div className="citations-hero__badge" role="text" aria-label={t("communaute.badge", language)}>{t("communaute.badge", language)}</div>
        <h1 id="communaute-title" className="citations-hero__title">{t("communaute.title", language)}</h1>
        <p className="citations-hero__subtitle">
          {t("communaute.subtitle", language)}
        </p>

        <blockquote className="citations-hero__highlight" aria-labelledby="communaute-cite">
          <p>{t("communaute.highlight_text", language)}</p>
          <cite id="communaute-cite">{t("communaute.highlight_author", language)}</cite>
        </blockquote>

        <dl className="citations-hero__stats" aria-label={t("communaute.stats", language) || "Statistiques"}>
          <div>
            <dt>{t("communaute.stats_facons", language)}</dt>
            <dd>{t("communaute.stats_facons_desc", language)}</dd>
          </div>
          <div>
            <dt>{t("communaute.stats_evenements", language)}</dt>
            <dd>{t("communaute.stats_evenements_desc", language)}</dd>
          </div>
          <div>
            <dt>{t("communaute.stats_communaute", language)}</dt>
            <dd>{t("communaute.stats_communaute_desc", language)}</dd>
          </div>
        </dl>
      </section>

      <div className="citations-grid" role="list" aria-label={t("communaute.engagements", language) || "Façons de s'engager"}>
        {COMMUNITY_SECTIONS.map(({ title, description }) => (
          <CardTilt key={title} role="listitem">
            <section className="citation-group" aria-labelledby={`engagement-${title}`}>
              <header className="citation-group__header">
                <span className="citation-group__tag">{t("communaute.engagement_tag", language)}</span>
                <h2 id={`engagement-${title}`} className="citation-group__title">{title}</h2>
                <p className="citation-group__description" aria-labelledby={`engagement-${title}`}>{description}</p>
              </header>
            </section>
          </CardTilt>
        ))}
      </div>

      <section className="citations-cta" aria-labelledby="communaute-cta-title">
        <h2 id="communaute-cta-title" className="heading-l">{t("communaute.cta_title", language)}</h2>
        <p className="lead">
          {t("communaute.cta_subtitle", language)}
        </p>
        <div style={{ display: "flex", gap: "14px", flexWrap: "wrap" }} role="group" aria-label={t("communaute.actions", language) || "Actions"}>
          <Link to="/rejoindre" className="btn btn-primary" aria-label={t("communaute.cta_rejoindre", language)}>
            {t("communaute.cta_rejoindre", language)}
          </Link>
          <Link to="/projets" className="btn btn-ghost" aria-label={t("communaute.cta_projets", language)}>
            {t("communaute.cta_projets", language)}
          </Link>
        </div>
      </section>

      <section className="citations-references" aria-labelledby="communaute-values-title">
        <h3 id="communaute-values-title" className="heading-m">{t("communaute.values_title", language)}</h3>
        <p className="muted" style={{ margin: 0, lineHeight: 1.6 }}>
          {t("communaute.values_desc", language)}
        </p>
      </section>
    </div>
  );
}


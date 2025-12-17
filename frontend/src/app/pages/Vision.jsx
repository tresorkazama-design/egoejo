import React from "react";
import { Link } from "react-router-dom";
import CardTilt from "../../components/CardTilt";
import { useLanguage } from "../../contexts/LanguageContext";
import { t } from "../../utils/i18n";
import SEO from "../../components/SEO";
import { useSEO } from "../../hooks/useSEO";

const getPillars = (lang) => [
  {
    title: t("vision.pillar_relier", lang),
    description: t("vision.pillar_relier_desc", lang),
  },
  {
    title: t("vision.pillar_apprendre", lang),
    description: t("vision.pillar_apprendre_desc", lang),
  },
  {
    title: t("vision.pillar_transmettre", lang),
    description: t("vision.pillar_transmettre_desc", lang),
  },
];

export default function Vision() {
  const { language } = useLanguage();
  const PILLARS = getPillars(language);

  const seoProps = useSEO({
    titleKey: "seo.vision_title",
    descriptionKey: "seo.vision_description",
    keywords: t("seo.vision_keywords", language),
  });

  return (
    <div className="page page--citations" data-testid="vision-page">
      <SEO {...seoProps} />
      <section className="citations-hero" aria-labelledby="vision-title" role="region" aria-label={t("vision.title", language)}>
        <div className="citations-hero__badge" role="text" aria-label={t("vision.badge", language)}>{t("vision.badge", language)}</div>
        <h1 id="vision-title" className="citations-hero__title">{t("vision.title", language)}</h1>
        <p className="citations-hero__subtitle">
          {t("vision.subtitle", language)}
        </p>

        <blockquote className="citations-hero__highlight" aria-labelledby="vision-cite">
          <p>{t("vision.highlight_text", language)}</p>
          <cite id="vision-cite">{t("vision.highlight_author", language)}</cite>
        </blockquote>

        <dl className="citations-hero__stats" aria-label={t("vision.stats", language) || "Statistiques"}>
          <div>
            <dt>{t("vision.stats_piliers", language)}</dt>
            <dd>{t("vision.stats_piliers_desc", language)}</dd>
          </div>
          <div>
            <dt>{t("vision.stats_projets", language)}</dt>
            <dd>{t("vision.stats_projets_desc", language)}</dd>
          </div>
          <div>
            <dt>{t("vision.stats_communaute", language)}</dt>
            <dd>{t("vision.stats_communaute_desc", language)}</dd>
          </div>
        </dl>
      </section>

      <div className="citations-grid" role="list" aria-label={t("vision.pillars", language) || "Piliers"}>
        {PILLARS.map(({ title, description }) => (
          <CardTilt key={title} role="listitem">
            <section className="citation-group" aria-labelledby={`pillar-${title}`}>
              <header className="citation-group__header">
                <span className="citation-group__tag">{t("vision.pillar_tag", language)}</span>
                <h2 id={`pillar-${title}`} className="citation-group__title">{title}</h2>
                <p className="citation-group__description" aria-labelledby={`pillar-${title}`}>{description}</p>
              </header>
            </section>
          </CardTilt>
        ))}
      </div>

      <section className="citations-cta" aria-labelledby="vision-cta-title">
        <h2 id="vision-cta-title" className="heading-l">{t("vision.cta_title", language)}</h2>
        <p className="lead">
          {t("vision.cta_subtitle", language)}
        </p>
        <div style={{ display: "flex", gap: "14px", flexWrap: "wrap" }} role="group" aria-label={t("vision.actions", language) || "Actions"}>
          <Link to="/rejoindre" className="btn btn-primary" aria-label={t("vision.cta_rejoindre", language)}>
            {t("vision.cta_rejoindre", language)}
          </Link>
          <Link to="/projets" className="btn btn-ghost" aria-label={t("vision.cta_projets", language)}>
            {t("vision.cta_projets", language)}
          </Link>
        </div>
      </section>

      <section className="citations-references" aria-labelledby="vision-values-title">
        <h3 id="vision-values-title" className="heading-m">{t("vision.values_title", language)}</h3>
        <p className="muted" style={{ margin: 0, lineHeight: 1.6 }}>
          {t("vision.values_desc", language)}
        </p>
      </section>
    </div>
  );
}

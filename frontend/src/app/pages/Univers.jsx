import React from "react";
import { Link } from "react-router-dom";
import CardTilt from "../../components/CardTilt";
import { useLanguage } from "../../contexts/LanguageContext";
import { t } from "../../utils/i18n";
import SEO from "../../components/SEO";
import { useSEO } from "../../hooks/useSEO";

const getThemes = (lang) => [
  {
    title: t("univers.theme_vivant", lang),
    description: t("univers.theme_vivant_desc", lang),
  },
  {
    title: t("univers.theme_histoire", lang),
    description: t("univers.theme_histoire_desc", lang),
  },
  {
    title: t("univers.theme_reliance", lang),
    description: t("univers.theme_reliance_desc", lang),
  },
];

export default function Univers() {
  const { language } = useLanguage();
  const THEMES = getThemes(language);

  const seoProps = useSEO({
    titleKey: "seo.univers_title",
    descriptionKey: "seo.univers_description",
    keywords: t("seo.univers_keywords", language),
  });

  return (
    <div className="page page--citations" data-testid="univers-page">
      <SEO {...seoProps} />
      <section className="citations-hero" aria-labelledby="univers-title" role="region" aria-label={t("univers.title", language)}>
        <div className="citations-hero__badge">{t("univers.badge", language)}</div>
        <h1 id="univers-title" className="citations-hero__title">{t("univers.title", language)}</h1>
        <p className="citations-hero__subtitle">
          {t("univers.subtitle", language)}
        </p>

        <dl className="citations-hero__stats" aria-label={t("univers.stats", language) || "Statistiques"}>
          <div>
            <dt>{t("univers.stats_themes", language)}</dt>
            <dd>{t("univers.stats_themes_desc", language)}</dd>
          </div>
          <div>
            <dt>{t("univers.stats_recits", language)}</dt>
            <dd>{t("univers.stats_recits_desc", language)}</dd>
          </div>
          <div>
            <dt>{t("univers.stats_pistes", language)}</dt>
            <dd>{t("univers.stats_pistes_desc", language)}</dd>
          </div>
        </dl>
      </section>

      <div className="citations-grid" role="list" aria-label={t("univers.themes", language) || "Thématiques"}>
        {THEMES.map(({ title, description }) => (
          <CardTilt key={title} role="listitem">
            <section className="citation-group" aria-labelledby={`theme-${title}`}>
              <header className="citation-group__header">
                <span className="citation-group__tag">{t("univers.thematic_tag", language)}</span>
                <h2 id={`theme-${title}`} className="citation-group__title">{title}</h2>
                <p className="citation-group__description" aria-labelledby={`theme-${title}`}>{description}</p>
              </header>
            </section>
          </CardTilt>
        ))}
      </div>

      <section className="citations-cta" aria-labelledby="univers-cta-title">
        <h2 id="univers-cta-title" className="heading-l">{t("univers.cta_title", language)}</h2>
        <p className="lead">
          {t("univers.cta_subtitle", language)}
        </p>
        <div style={{ display: "flex", gap: "14px", flexWrap: "wrap" }} role="group" aria-label={t("univers.actions", language) || "Actions"}>
          <Link to="/projets" className="btn btn-primary" aria-label={t("univers.cta_projets", language)}>
            {t("univers.cta_projets", language)}
          </Link>
          <Link to="/rejoindre" className="btn btn-ghost" aria-label={t("univers.cta_rejoindre", language)}>
            {t("univers.cta_rejoindre", language)}
          </Link>
        </div>
      </section>

      <section className="citations-references" aria-labelledby="univers-ref-title">
        <h3 id="univers-ref-title" className="heading-m">{t("univers.references_title", language)}</h3>
        <ul style={{ margin: 0, paddingLeft: "20px", color: "var(--muted)", lineHeight: 1.8 }} role="list">
          <li>{t("univers.references_item1", language)}</li>
          <li>{t("univers.references_item2", language)}</li>
          <li>{t("univers.references_item3", language)}</li>
          <li>{t("univers.references_item4", language)}</li>
        </ul>
      </section>
    </div>
  );
}

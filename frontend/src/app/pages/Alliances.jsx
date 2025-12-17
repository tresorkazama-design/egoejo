import React from "react";
import { Link } from "react-router-dom";
import CardTilt from "../../components/CardTilt";
import { useLanguage } from "../../contexts/LanguageContext";
import { t } from "../../utils/i18n";
import SEO from "../../components/SEO";
import { useSEO } from "../../hooks/useSEO";

const getAlliances = (lang) => [
  {
    title: t("alliances.type_territoriales", lang),
    description: t("alliances.type_territoriales_desc", lang),
  },
  {
    title: t("alliances.type_savoirs", lang),
    description: t("alliances.type_savoirs_desc", lang),
  },
  {
    title: t("alliances.type_internationales", lang),
    description: t("alliances.type_internationales_desc", lang),
  },
];

export default function Alliances() {
  const { language } = useLanguage();
  const ALLIANCES = getAlliances(language);

  const seoProps = useSEO({
    titleKey: "seo.alliances_title",
    descriptionKey: "seo.alliances_description",
    keywords: t("seo.alliances_keywords", language),
  });

  return (
    <div className="page page--citations" data-testid="alliances-page">
      <SEO {...seoProps} />
      <section className="citations-hero" aria-labelledby="alliances-title" role="region" aria-label={t("alliances.title", language)}>
        <div className="citations-hero__badge" role="text" aria-label={t("alliances.badge", language)}>{t("alliances.badge", language)}</div>
        <h1 id="alliances-title" className="citations-hero__title">{t("alliances.title", language)}</h1>
        <p className="citations-hero__subtitle">
          {t("alliances.subtitle", language)}
        </p>

        <blockquote className="citations-hero__highlight" aria-labelledby="alliances-cite">
          <p>{t("alliances.highlight_text", language)}</p>
          <cite id="alliances-cite">{t("alliances.highlight_author", language)}</cite>
        </blockquote>

        <dl className="citations-hero__stats" aria-label={t("alliances.stats", language) || "Statistiques"}>
          <div>
            <dt>{t("alliances.stats_types", language)}</dt>
            <dd>{t("alliances.stats_types_desc", language)}</dd>
          </div>
          <div>
            <dt>{t("alliances.stats_partenaires", language)}</dt>
            <dd>{t("alliances.stats_partenaires_desc", language)}</dd>
          </div>
          <div>
            <dt>{t("alliances.stats_reseau", language)}</dt>
            <dd>{t("alliances.stats_reseau_desc", language)}</dd>
          </div>
        </dl>
      </section>

      <div className="citations-grid" role="list" aria-label={t("alliances.types", language) || "Types d'alliances"}>
        {ALLIANCES.map(({ title, description }) => (
          <CardTilt key={title} role="listitem">
            <section className="citation-group" aria-labelledby={`alliance-${title}`}>
              <header className="citation-group__header">
                <span className="citation-group__tag">{t("alliances.type_tag", language)}</span>
                <h2 id={`alliance-${title}`} className="citation-group__title">{title}</h2>
                <p className="citation-group__description" aria-labelledby={`alliance-${title}`}>{description}</p>
              </header>
            </section>
          </CardTilt>
        ))}
      </div>

      <section className="citations-cta" aria-labelledby="alliances-cta-title">
        <h2 id="alliances-cta-title" className="heading-l">{t("alliances.cta_title", language)}</h2>
        <p className="lead">
          {t("alliances.cta_subtitle", language)}
        </p>
        <div style={{ display: "flex", gap: "14px", flexWrap: "wrap" }} role="group" aria-label={t("alliances.actions", language) || "Actions"}>
          <Link to="/rejoindre" className="btn btn-primary" aria-label={t("alliances.cta_rejoindre", language)}>
            {t("alliances.cta_rejoindre", language)}
          </Link>
          <a
            href="mailto:contact@egoejo.org?subject=Proposition%20d'alliance"
            className="btn btn-ghost"
            aria-label={t("alliances.cta_contact", language)}
          >
            {t("alliances.cta_contact", language)}
          </a>
        </div>
      </section>

      <section className="citations-references" aria-labelledby="alliances-partners-title">
        <h3 id="alliances-partners-title" className="heading-m">{t("alliances.partners_title", language)}</h3>
        <p className="muted" style={{ margin: 0, lineHeight: 1.6 }}>
          {t("alliances.partners_desc", language)}
        </p>
      </section>
    </div>
  );
}

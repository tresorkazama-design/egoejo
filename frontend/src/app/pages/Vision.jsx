import React from "react";
import { Link } from "react-router-dom";
import CardTilt from "../../components/CardTilt";
import { useLanguage } from "../../contexts/LanguageContext";
import { t } from "../../utils/i18n";
import SEO from "../../components/SEO";
import { useSEO } from "../../hooks/useSEO";

const getPrinciples = (lang) => [
  {
    title: t("vision.principle_relational_title", lang),
    description: t("vision.principle_relational_desc", lang),
  },
  {
    title: t("vision.principle_anti_accumulation_title", lang),
    description: t("vision.principle_anti_accumulation_desc", lang),
  },
  {
    title: t("vision.principle_cycle_title", lang),
    description: t("vision.principle_cycle_desc", lang),
  },
];

export default function Vision() {
  const { language } = useLanguage();
  const PRINCIPLES = getPrinciples(language);

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

      {/* Mission */}
      <section className="page" aria-labelledby="vision-mission-title" role="region" data-testid="vision-mission">
        <div className="container">
          <h2 id="vision-mission-title" className="heading-l">{t("vision.mission_title", language)}</h2>
          <div className="grid" style={{ gap: "1rem" }}>
            <p className="lead">{t("vision.mission_line1", language)}</p>
            <p className="lead">{t("vision.mission_line2", language)}</p>
            <p className="lead">{t("vision.mission_line3", language)}</p>
          </div>
        </div>
      </section>

      {/* Principes fondamentaux */}
      <section className="page surface" aria-labelledby="vision-principles-title" role="region" data-testid="vision-principles">
        <div className="container">
          <h2 id="vision-principles-title" className="heading-l">{t("vision.principles_title", language)}</h2>
          <div className="citations-grid" role="list" aria-label={t("vision.principles_title", language)}>
            {PRINCIPLES.map(({ title, description }) => (
              <CardTilt key={title} role="listitem">
                <section className="citation-group" aria-labelledby={`principle-${title}`}>
                  <header className="citation-group__header">
                    <span className="citation-group__tag">{t("vision.pillar_tag", language)}</span>
                    <h3 id={`principle-${title}`} className="citation-group__title">{title}</h3>
                    <p className="citation-group__description" aria-labelledby={`principle-${title}`}>{description}</p>
                  </header>
                </section>
              </CardTilt>
            ))}
          </div>
        </div>
      </section>

      {/* Ce que nous faisons */}
      <section className="page" aria-labelledby="vision-what-we-do-title" role="region" data-testid="vision-what-we-do">
        <div className="container">
          <h2 id="vision-what-we-do-title" className="heading-l">{t("vision.what_we_do_title", language)}</h2>
          <p className="lead">{t("vision.what_we_do_desc", language)}</p>
          <ul className="grid" style={{ gap: "1rem", listStyle: "none", padding: 0 }}>
            <li><p>{t("vision.what_we_do_item1", language)}</p></li>
            <li><p>{t("vision.what_we_do_item2", language)}</p></li>
            <li><p>{t("vision.what_we_do_item3", language)}</p></li>
            <li><p>{t("vision.what_we_do_item4", language)}</p></li>
            <li><p>{t("vision.what_we_do_item5", language)}</p></li>
          </ul>
        </div>
      </section>

      {/* Ce que nous refusons */}
      <section className="page surface" aria-labelledby="vision-what-we-refuse-title" role="region" data-testid="vision-what-we-refuse">
        <div className="container">
          <h2 id="vision-what-we-refuse-title" className="heading-l">{t("vision.what_we_refuse_title", language)}</h2>
          <p className="lead">{t("vision.what_we_refuse_desc", language)}</p>
          <ul className="grid" style={{ gap: "1rem", listStyle: "none", padding: 0 }}>
            <li><p><strong>{t("vision.what_we_refuse_item1", language)}</strong></p></li>
            <li><p><strong>{t("vision.what_we_refuse_item2", language)}</strong></p></li>
            <li><p><strong>{t("vision.what_we_refuse_item3", language)}</strong></p></li>
          </ul>
        </div>
      </section>

      {/* Gouvernance & traçabilité */}
      <section className="page" aria-labelledby="vision-governance-title" role="region" data-testid="vision-governance">
        <div className="container">
          <h2 id="vision-governance-title" className="heading-l">{t("vision.governance_title", language)}</h2>
          <p className="lead">{t("vision.governance_desc", language)}</p>
          <ul className="grid" style={{ gap: "1rem", listStyle: "none", padding: 0 }}>
            <li><p>{t("vision.governance_item1", language)}</p></li>
            <li><p>{t("vision.governance_item2", language)}</p></li>
            <li><p>{t("vision.governance_item3", language)}</p></li>
            <li><p>{t("vision.governance_item4", language)}</p></li>
            <li><p>{t("vision.governance_item5", language)}</p></li>
          </ul>
        </div>
      </section>

      {/* Glossaire */}
      <section className="page surface" aria-labelledby="vision-glossary-title" role="region" data-testid="vision-glossary">
        <div className="container">
          <h2 id="vision-glossary-title" className="heading-l">{t("vision.glossary_title", language)}</h2>
          <dl className="grid" style={{ gap: "1.5rem" }}>
            <div>
              <dt className="heading-m" style={{ marginBottom: "0.5rem" }}>{t("vision.glossary_vivant_term", language)}</dt>
              <dd><p>{t("vision.glossary_vivant_def", language)}</p></dd>
            </div>
            <div>
              <dt className="heading-m" style={{ marginBottom: "0.5rem" }}>{t("vision.glossary_saka_term", language)}</dt>
              <dd><p>{t("vision.glossary_saka_def", language)}</p></dd>
            </div>
            <div>
              <dt className="heading-m" style={{ marginBottom: "0.5rem" }}>{t("vision.glossary_eur_term", language)}</dt>
              <dd><p>{t("vision.glossary_eur_def", language)}</p></dd>
            </div>
            <div>
              <dt className="heading-m" style={{ marginBottom: "0.5rem" }}>{t("vision.glossary_silo_term", language)}</dt>
              <dd><p>{t("vision.glossary_silo_def", language)}</p></dd>
            </div>
            <div>
              <dt className="heading-m" style={{ marginBottom: "0.5rem" }}>{t("vision.glossary_compostage_term", language)}</dt>
              <dd><p>{t("vision.glossary_compostage_def", language)}</p></dd>
            </div>
            <div>
              <dt className="heading-m" style={{ marginBottom: "0.5rem" }}>{t("vision.glossary_alliance_term", language)}</dt>
              <dd><p>{t("vision.glossary_alliance_def", language)}</p></dd>
            </div>
            <div>
              <dt className="heading-m" style={{ marginBottom: "0.5rem" }}>{t("vision.glossary_gardiens_term", language)}</dt>
              <dd><p>{t("vision.glossary_gardiens_def", language)}</p></dd>
            </div>
          </dl>
        </div>
      </section>

      {/* Citations avec disclaimer */}
      <section className="page" aria-labelledby="vision-citations-title" role="region" data-testid="vision-citations">
        <div className="container">
          <h2 id="vision-citations-title" className="heading-l">{t("vision.citations_title", language)}</h2>
          <blockquote className="citations-hero__highlight" aria-labelledby="vision-cite">
            <p>{t("vision.highlight_text", language)}</p>
            <cite id="vision-cite">{t("vision.highlight_author", language)}</cite>
          </blockquote>
          <p className="muted" style={{ marginTop: "1.5rem", fontSize: "0.875rem", lineHeight: 1.6 }} data-testid="vision-disclaimer">
            {t("vision.citations_disclaimer", language)}
          </p>
        </div>
      </section>

      {/* CTA */}
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
    </div>
  );
}

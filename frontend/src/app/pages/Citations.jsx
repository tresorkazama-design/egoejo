import React from "react";
import { useLanguage } from "../../contexts/LanguageContext";
import { t } from "../../utils/i18n";
import CardTilt from "../../components/CardTilt";
import SEO from "../../components/SEO";
import { useSEO } from "../../hooks/useSEO";
import frTranslations from "../../locales/fr.json";
import enTranslations from "../../locales/en.json";
import arTranslations from "../../locales/ar.json";
import esTranslations from "../../locales/es.json";
import deTranslations from "../../locales/de.json";
import swTranslations from "../../locales/sw.json";

const translations = {
  fr: frTranslations,
  en: enTranslations,
  ar: arTranslations,
  es: esTranslations,
  de: deTranslations,
  sw: swTranslations,
};

const getGroups = (lang) => {
  const langTranslations = translations[lang] || translations.fr;
  const groupKeys = ["voix_autochtones", "metamorphoses", "feminin_sacre", "regards_critiques"];

  return groupKeys.map((key) => {
    const groupData = langTranslations.citations?.groups?.[key];
    if (!groupData) {
      // Fallback vers le français si le groupe n'existe pas
      const fallbackGroup = translations.fr.citations?.groups?.[key];
      if (!fallbackGroup) return null;
      
      return {
        title: fallbackGroup.title,
        description: fallbackGroup.description,
        quotes: fallbackGroup.quotes || [],
      };
    }

    return {
      title: groupData.title,
      description: groupData.description,
      quotes: groupData.quotes || [],
    };
  }).filter(Boolean);
};

export default function Citations() {
  const { language } = useLanguage();
  const GROUPS = getGroups(language);

  const seoProps = useSEO({
    titleKey: "seo.citations_title",
    descriptionKey: "seo.citations_description",
    keywords: t("seo.citations_keywords", language),
  });
  
  return (
    <div className="page page--citations" data-testid="citations-page">
      <SEO {...seoProps} />
      <section className="citations-hero" aria-labelledby="citations-title" role="region" aria-label={t("citations.title", language)}>
        <div className="citations-hero__badge" role="text" aria-label={t("citations.badge", language)}>{t("citations.badge", language)}</div>
        <h1 id="citations-title" className="citations-hero__title">{t("citations.title", language)}</h1>
        <p className="citations-hero__subtitle">
          {t("citations.subtitle", language)}
        </p>

        <blockquote className="citations-hero__highlight" aria-labelledby="citations-cite">
          <p>{t("citations.highlight_text", language)}</p>
          <cite id="citations-cite">{t("citations.highlight_author", language)}</cite>
        </blockquote>

        <dl className="citations-hero__stats" aria-label={t("citations.stats", language) || "Statistiques"}>
          <div>
            <dt>{t("citations.stats_thematiques", language)}</dt>
            <dd>{t("citations.stats_thematiques_desc", language)}</dd>
          </div>
          <div>
            <dt>{t("citations.stats_extraits", language)}</dt>
            <dd>{t("citations.stats_extraits_desc", language)}</dd>
          </div>
          <div>
            <dt>{t("citations.stats_bibliographie", language)}</dt>
            <dd>{t("citations.stats_bibliographie_desc", language)}</dd>
          </div>
        </dl>
      </section>

      <div className="citations-grid" role="list" aria-label={t("citations.groups", language) || "Groupes de citations"}>
        {GROUPS.map(({ title, description, quotes }) => (
          <section key={title} className="citation-group" role="listitem" aria-labelledby={`citation-group-${title}`}>
            <header className="citation-group__header">
              <span className="citation-group__tag">{t("citations.thematic_tag", language)}</span>
              <h2 id={`citation-group-${title}`} className="citation-group__title">{title}</h2>
              <p className="citation-group__description" aria-labelledby={`citation-group-${title}`}>{description}</p>
            </header>

            <div className="citation-group__quotes" role="list" aria-label={t("citations.quotes", language) || "Citations"}>
              {quotes.map(({ text, author }, idx) => (
                <CardTilt key={`${author}-${idx}`} role="listitem">
                  <blockquote className="citation-card" aria-labelledby={`citation-${title}-${idx}`}>
                    <p id={`citation-${title}-${idx}`} className="citation-card__text">{text}</p>
                    <cite className="citation-card__author">{author}</cite>
                  </blockquote>
                </CardTilt>
              ))}
            </div>
          </section>
        ))}
      </div>

      <section className="citations-cta" aria-labelledby="citations-cta-title">
        <h2 id="citations-cta-title" className="heading-l">{t("citations.cta_title", language)}</h2>
        <p className="lead">
          {t("citations.cta_subtitle", language)}
        </p>
        <a
          href="mailto:contact@egoejo.org?subject=Contribution%20Citations%20EGOEJO"
          className="btn btn-primary"
          aria-label={t("citations.cta_button", language)}
        >
          {t("citations.cta_button", language)}
        </a>
      </section>

      <section className="citations-references" aria-labelledby="citations-ref-title">
        <h3 id="citations-ref-title" className="heading-m">{t("citations.references_title", language)}</h3>
        <p className="muted">
          {t("citations.references_desc", language)}
        </p>
      </section>
    </div>
  );
}

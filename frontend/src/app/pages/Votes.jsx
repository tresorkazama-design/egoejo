import React from "react";
import { Link } from "react-router-dom";
import CardTilt from "../../components/CardTilt";
import { useLanguage } from "../../contexts/LanguageContext";
import { t } from "../../utils/i18n";
import SEO from "../../components/SEO";
import { useSEO } from "../../hooks/useSEO";

const getVoteSections = (lang) => [
  {
    title: t("votes.governance_democratie", lang),
    description: t("votes.governance_democratie_desc", lang),
  },
  {
    title: t("votes.governance_processus", lang),
    description: t("votes.governance_processus_desc", lang),
  },
  {
    title: t("votes.governance_transparence", lang),
    description: t("votes.governance_transparence_desc", lang),
  },
];

export default function Votes() {
  const { language } = useLanguage();
  const VOTE_SECTIONS = getVoteSections(language);

  const seoProps = useSEO({
    titleKey: "seo.votes_title",
    descriptionKey: "seo.votes_description",
    keywords: t("seo.votes_keywords", language),
  });

  return (
    <div className="page page--citations" data-testid="votes-page">
      <SEO {...seoProps} />
      <section className="citations-hero" aria-labelledby="votes-title" role="region" aria-label={t("votes.title", language)}>
        <div className="citations-hero__badge" role="text" aria-label={t("votes.badge", language)}>{t("votes.badge", language)}</div>
        <h1 id="votes-title" className="citations-hero__title">{t("votes.title", language)}</h1>
        <p className="citations-hero__subtitle">
          {t("votes.subtitle", language)}
        </p>

        <blockquote className="citations-hero__highlight" aria-labelledby="votes-cite">
          <p>{t("votes.highlight_text", language)}</p>
          <cite id="votes-cite">{t("votes.highlight_author", language)}</cite>
        </blockquote>

        <dl className="citations-hero__stats" aria-label={t("votes.stats", language) || "Statistiques"}>
          <div>
            <dt>{t("votes.stats_principes", language)}</dt>
            <dd>{t("votes.stats_principes_desc", language)}</dd>
          </div>
          <div>
            <dt>{t("votes.stats_votes", language)}</dt>
            <dd>{t("votes.stats_votes_desc", language)}</dd>
          </div>
          <div>
            <dt>{t("votes.stats_communaute", language)}</dt>
            <dd>{t("votes.stats_communaute_desc", language)}</dd>
          </div>
        </dl>
      </section>

      <div className="citations-grid" role="list" aria-label={t("votes.governance", language) || "Principes de gouvernance"}>
        {VOTE_SECTIONS.map(({ title, description }) => (
          <CardTilt key={title} role="listitem">
            <section className="citation-group" aria-labelledby={`vote-${title}`}>
              <header className="citation-group__header">
                <span className="citation-group__tag">{t("votes.governance_tag", language)}</span>
                <h2 id={`vote-${title}`} className="citation-group__title">{title}</h2>
                <p className="citation-group__description" aria-labelledby={`vote-${title}`}>{description}</p>
              </header>
            </section>
          </CardTilt>
        ))}
      </div>

      <section className="citations-cta" aria-labelledby="votes-cta-title">
        <h2 id="votes-cta-title" className="heading-l">{t("votes.cta_title", language)}</h2>
        <p className="lead">
          {t("votes.cta_subtitle", language)}
        </p>
        <div style={{ display: "flex", gap: "14px", flexWrap: "wrap" }} role="group" aria-label={t("votes.actions", language) || "Actions"}>
          <Link to="/rejoindre" className="btn btn-primary" aria-label={t("votes.cta_rejoindre", language)}>
            {t("votes.cta_rejoindre", language)}
          </Link>
          <Link to="/communaute" className="btn btn-ghost" aria-label={t("votes.cta_communaute", language)}>
            {t("votes.cta_communaute", language)}
          </Link>
        </div>
      </section>

      <section className="citations-references" aria-labelledby="votes-how-title">
        <h3 id="votes-how-title" className="heading-m">{t("votes.how_title", language)}</h3>
        <p className="muted" style={{ margin: 0, lineHeight: 1.6 }}>
          {t("votes.how_desc", language)}
        </p>
      </section>
    </div>
  );
}


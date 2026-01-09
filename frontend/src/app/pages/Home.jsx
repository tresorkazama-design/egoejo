import React from "react";
import { Link } from "react-router-dom";
import CardTilt from "../../components/CardTilt";
import { useLanguage } from "../../contexts/LanguageContext";
import { t } from "../../utils/i18n";
import SEO from "../../components/SEO";
import { useSEO } from "../../hooks/useSEO";
import ErrorBoundary from "../../components/ErrorBoundary";

const getDonationLinks = (lang) => [
  {
    label: t("home.membership_helloasso", lang),
    description: t("home.membership_desc", lang),
    href: "https://www.helloasso.com/associations",
    variant: "ghost",
  },
  {
    label: t("home.international_support", lang),
    description: t("home.international_support_desc", lang),
    href: "https://donate.stripe.com",
    variant: "primary",
  },
];

const getPillars = (lang) => [
  {
    title: t("home.relier", lang),
    text: t("home.relier_desc", lang),
  },
  {
    title: t("home.apprendre", lang),
    text: t("home.apprendre_desc", lang),
  },
  {
    title: t("home.transmettre", lang),
    text: t("home.transmettre_desc", lang),
  },
];

export default function Home() {
  const { language } = useLanguage();
  const DONATION_LINKS = getDonationLinks(language);
  const PILLARS = getPillars(language);
  
  const seoProps = useSEO({
    titleKey: "seo.home_title",
    descriptionKey: "seo.home_description",
    keywords: t("seo.home_keywords", language),
    jsonLd: {
      '@context': 'https://schema.org',
      '@type': 'WebSite',
      name: t('seo.site_name', language),
      url: import.meta.env.VITE_SITE_URL || 'https://egoejo.org',
      description: t("seo.home_description", language),
      potentialAction: {
        '@type': 'SearchAction',
        target: {
          '@type': 'EntryPoint',
          urlTemplate: `${import.meta.env.VITE_SITE_URL || 'https://egoejo.org'}/projets?q={search_term_string}`,
        },
        'query-input': 'required name=search_term_string',
      },
    },
  });

  return (
    <div className="home-page" data-testid="home-page">
      <ErrorBoundary>
        <SEO {...seoProps} />
      </ErrorBoundary>
      <section className="page hero" aria-labelledby="hero-title" style={{ background: "transparent", backgroundColor: "transparent" }}>
        <div className="container hero__content" style={{ background: "transparent", backgroundColor: "transparent" }}>
          <div className="hero__tag">{t("home.tag", language)}</div>
          <h1 id="hero-title" className="heading-xl">
            {t("home.title", language).split('\n').map((line, i) => (
              <React.Fragment key={i}>
                {line}
                {i < t("home.title", language).split('\n').length - 1 && <br />}
              </React.Fragment>
            ))}
          </h1>
          <p className="lead">
            {t("home.subtitle", language)}
          </p>
          <div className="hero__actions" role="group" aria-label={t("home.actions", language) || t("common.actions", language)}>
            {/* CONVENTION NAVIGATION : Utiliser <a href="#section"> pour les ancres (sections sur la même page) */}
            <a className="btn btn-primary" href="#soutenir" aria-label={`${t("home.soutenir", language)} - ${t("home.soutenir_desc", language)}`}>
              {t("home.soutenir", language)}
            </a>
            {/* CONVENTION NAVIGATION : Utiliser <Link to="/route"> pour les routes (changement de page) */}
            <Link className="btn btn-primary" to="/rejoindre" aria-label={t("home.rejoindre", language)}>
              {t("home.rejoindre", language)}
            </Link>
          </div>
        </div>
      </section>

      <section className="page" aria-labelledby="pillars-heading" role="region">
        <h2 id="pillars-heading" className="sr-only">{t("home.pillars_title", language) || t("home.relier", language)}</h2>
        <div className="container grid grid-3" role="list" aria-label={t("home.pillars", language) || t("home.pillars_title", language)}>
          {PILLARS.map(({ title, text }, index) => (
            <CardTilt key={title} role="listitem">
              <article className="glass">
                <h3 className="tag" id={`pillar-${title}`}>{title}</h3>
                <p className="lead" style={{ marginTop: 12 }} aria-labelledby={`pillar-${title}`}>
                  {text}
                </p>
              </article>
            </CardTilt>
          ))}
        </div>
      </section>

      <section id="soutenir" className="page surface" aria-labelledby="soutenir-heading" role="region" data-testid="home-section-soutenir">
        <div className="container grid" style={{ gap: "32px" }}>
            <div>
              <span className="tag">{t("home.nous_soutenir", language)}</span>
              <h2 id="soutenir-heading" className="heading-l">{t("home.soutenir_title", language)}</h2>
              <p className="muted" style={{ lineHeight: 1.6 }} data-testid="home-donation-claim">
                {t("home.soutenir_desc", language)}
              </p>
              <p className="muted" style={{ lineHeight: 1.6, marginTop: "1rem" }} data-testid="home-saka-eur-note">
                {t("home.saka_eur_note", language) || ""}
              </p>
            </div>

          <div className="grid" role="list" aria-label={t("home.donation_options", language) || t("home.nous_soutenir", language)}>
            {DONATION_LINKS.map(({ label, description, href, variant }) => (    
              <CardTilt key={href} role="listitem">
                <a
                  href={href}
                  target="_blank"
                  rel="noreferrer noopener"
                  className={`home-support__card glass ${variant === "primary" ? "is-primary" : ""}`}
                  aria-label={`${label} - ${description} - ${t("home.contribuer", language)}`}
                >
                  <h3>{label}</h3>
                  <p className="muted">{description}</p>
                  <span className="home-support__cta" aria-hidden="true">{t("home.contribuer", language)} →</span>
                </a>
              </CardTilt>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

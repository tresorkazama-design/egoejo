import HeroSorgho from "../shared/components/HeroSorgho.jsx";

const DONATION_LINKS = [
  {
    label: "Adhésion • HelloAsso",
    description: "Rejoindre l’association et contribuer en France",
    href: "https://www.helloasso.com/associations",
    variant: "ghost",
  },
  {
    label: "Soutien international",
    description: "Faire un don ponctuel ou récurrent via Stripe",
    href: "https://donate.stripe.com",
    variant: "primary",
  },
];

const PILLARS = [
  {
    title: "Relier",
    text: "Tisser des alliances entre habitants, organisations et territoires pour restaurer les communs du vivant.",
  },
  {
    title: "Apprendre en faisant",
    text: "Expérimenter sur le terrain, documenter et partager des pratiques régénératives à l’échelle locale.",
  },
  {
    title: "Transmettre",
    text: "Accompagner les acteurs du changement avec des formats immersifs, sensibles et ancrés dans le réel.",
  },
];

export default function Home() {
  return (
    <div>
      <section className="page hero">
        <div className="container hero__content">
          <div className="hero__tag">Collectif pour le vivant</div>
          <h1 className="heading-xl">
            Habiter la Terre autrement,
            <br />
            ensemble.
          </h1>
          <p className="lead">
            EGOEJO rassemble des gardiens du vivant. Nous mettons en réseau les ressources, les
            savoirs et les personnes engagées pour prendre soin du monde. Ateliers, lieux vivants,
            recherche-action : chaque projet est une expérience à partager.
          </p>
          <div className="hero__actions">
            <a className="btn btn-primary" href="#soutenir">
              Soutenir EGOEJO
            </a>
            <a className="btn btn-ghost" href="/rejoindre">
              Rejoindre l’Alliance
            </a>
          </div>
        </div>
        <HeroSorgho />
      </section>

      <section className="page">
        <div className="container grid grid-3">
          {PILLARS.map(({ title, text }) => (
            <article key={title} className="glass">
              <div className="tag">{title}</div>
              <p className="lead" style={{ marginTop: 12 }}>
                {text}
              </p>
            </article>
          ))}
        </div>
      </section>

      <section id="soutenir" className="page surface">
        <div className="container grid" style={{ gap: "32px" }}>
          <div>
            <span className="tag">Nous soutenir</span>
            <h2 className="heading-l">Devenez allié·e du vivant</h2>
            <p className="muted" style={{ lineHeight: 1.6 }}>
              Chaque contribution alimente des actions concrètes : refuges, jardins nourriciers,
              ateliers de transmission, résidences de recherche, accompagnement des communautés
              locales. <strong>100&nbsp;% des dons</strong> sont utilisés pour financer ces projets.
            </p>
          </div>

          <div className="grid">
            {DONATION_LINKS.map(({ label, description, href, variant }) => (
              <a
                key={href}
                href={href}
                target="_blank"
                rel="noreferrer"
                className={`home-support__card glass ${variant === "primary" ? "is-primary" : ""}`}
              >
                <h3>{label}</h3>
                <p className="muted">{description}</p>
                <span className="home-support__cta">Contribuer →</span>
              </a>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
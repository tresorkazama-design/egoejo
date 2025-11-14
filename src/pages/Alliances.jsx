
const ALLIANCES = [
  {
    title: "Communes et territoires",
    description:
      "Nous accompagnons les collectivités qui veulent réhabiliter des lieux en refuges du vivant et dynamiser les communs.",
  },
  {
    title: "Collectifs citoyens",
    description:
      "Jardins partagés, tiers-lieux, réseaux de soins : nous mettons en lien des initiatives proches pour qu’elles se renforcent.",
  },
  {
    title: "Entreprises engagées",
    description:
      "Nous créons des partenariats pour transformer les pratiques : réduction d’empreinte, mécénat de compétences, soutien financier.",
  },
];

export default function Alliances() {
  return (
    <div className="page">
      <div className="container grid" style={{ gap: "36px" }}>
        <header className="grid" style={{ gap: "18px" }}>
          <span className="tag">Alliances</span>
          <h1 className="heading-l">Grandir ensemble</h1>
          <p className="lead">
            EGOEJO fédère des partenaires qui partagent une même intention : rendre la Terre
            habitable, ici et maintenant. Nous réunissons les ressources, le financement, les outils
            pédagogiques et les lieux pour accélérer les transformations.
          </p>
        </header>

        <section className="grid grid-3">
          {ALLIANCES.map(({ title, description }) => (
            <article key={title} className="glass">
              <h3 style={{ marginTop: 0 }}>{title}</h3>
              <p className="muted" style={{ lineHeight: 1.55 }}>
                {description}
              </p>
            </article>
          ))}
        </section>

        <section className="glass">
          <h2 style={{ marginTop: 0 }}>Envie de collaborer ?</h2>
          <p className="muted" style={{ lineHeight: 1.6 }}>
            Écrivez-nous à <a href="mailto:alliances@egoejo.com">alliances@egoejo.com</a>. Nous
            co-construisons des formats adaptés : résidences, co-financement de projets, création
            d’outils communs, accompagnement stratégique.
          </p>
        </section>
      </div>
    </div>
  );
}

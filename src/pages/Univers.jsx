const THEMES = [
  {
    title: "Sites refuges",
    description:
      "Réhabilitation de friches, de forêts nourricières et de lieux d’expérimentation pour accueillir humains et non-humains.",
  },
  {
    title: "Transmission sensible",
    description:
      "Résidences artistiques et scientifiques, programmes d’immersions et cercles d’apprentissage pour ressentir et comprendre.",
  },
  {
    title: "Alliance des territoires",
    description:
      "Partenariats entre communes, collectifs citoyens et acteurs économiques pour mettre en commun ressources et savoirs.",
  },
];

export default function Univers() {
  return (
    <div className="page">
      <div className="container grid" style={{ gap: "36px" }}>
        <div className="grid" style={{ gap: "20px" }}>
          <span className="tag">Univers</span>
          <h1 className="heading-l">L’écosystème EGOEJO</h1>
          <p className="lead">
            EGOEJO tisse une alliance de gardiens du vivant. Notre univers est un archipel de lieux,
            de pratiques et d’êtres engagés qui travaillent à restaurer les liens entre humains et
            non-humains.
          </p>
        </div>

        <section className="grid grid-3">
          {THEMES.map(({ title, description }) => (
            <article key={title} className="glass">
              <h3 style={{ marginTop: 0 }}>{title}</h3>
              <p className="muted" style={{ lineHeight: 1.55 }}>
                {description}
              </p>
            </article>
          ))}
        </section>

        <section className="glass">
          <h2 style={{ marginTop: 0 }}>Une alliance en mouvement</h2>
          <ul style={{ margin: "16px 0 0", padding: 0, listStyle: "none", lineHeight: 1.7 }}>
            <li>• Parcours d’initiation pour devenir gardien.ne du vivant</li>
            <li>• Communauté d’entraide entre lieux expérimentaux</li>
            <li>• Plateforme d’outils ouverts (documentation, podcasts, rituels)</li>
            <li>• Observatoire vivant : recherche-action, mesures et récits</li>
          </ul>
        </section>
      </div>
    </div>
  );
}

const PERSPECTIVES = [
  {
    title: "Prendre soin comme principe",
    text: "Nous privilégions les logiques de soin, de régénération et de reliance plutôt que l’extraction. Chaque geste répond à la question : cela nourrit-il le vivant ?",
  },
  {
    title: "Des alliances plurielles",
    text: "Artistes, botanistes, paysan·nes, artisan·es, thérapeutes : la diversité des regards nourrit des réponses adaptées aux territoires.",
  },
  {
    title: "Le sensible comme boussole",
    text: "L’émerveillement, l’écoute et la présence sont des outils politiques. Nous créons des expériences qui réactivent le lien sensible à la Terre.",
  },
];

export default function Vision() {
  return (
    <div className="page">
      <div className="container grid" style={{ gap: "32px" }}>
        <header className="grid" style={{ gap: "18px" }}>
          <span className="tag">Vision</span>
          <h1 className="heading-l">Ce que nous voulons transformer</h1>
          <p className="lead">
            La crise écologique est une crise du lien. EGOEJO imagine une alliance de gardiens qui
            expérimentent, prennent soin et transmettent pour régénérer les territoires et les
            relations.
          </p>
        </header>

        <section className="grid grid-3">
          {PERSPECTIVES.map(({ title, text }) => (
            <article key={title} className="glass">
              <h3 style={{ marginTop: 0 }}>{title}</h3>
              <p className="muted" style={{ lineHeight: 1.55 }}>
                {text}
              </p>
            </article>
          ))}
        </section>
      </div>
    </div>
  );
}

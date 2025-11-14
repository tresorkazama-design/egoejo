const PROJECTS = [
  {
    title: "Sanctuaire de la Vallée",
    description: "Transformation d’une friche agricole en refuge du vivant et espace pédagogique.",
    cover: "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1000&q=60",
  },
  {
    title: "Résidence Écopoétique",
    description: "Rencontre entre artistes, paysan·nes et chercheur·euses pour créer de nouveaux récits.",
    cover: "https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=1000&q=60",
  },
  {
    title: "Atlas des Reliances",
    description: "Cartographie collaborative des initiatives régénératives sur les territoires.",
    cover: "https://images.unsplash.com/photo-1452570053594-1b985d6ea890?auto=format&fit=crop&w=1000&q=60",
  },
];

export default function Projets() {
  return (
    <div className="page">
      <div className="container grid" style={{ gap: "32px" }}>
        <header className="grid" style={{ gap: "18px" }}>
          <span className="tag">Projets</span>
          <h1 className="heading-l">Nos terrains d’action</h1>
          <p className="lead">
            Les projets EGOEJO sont des laboratoires vivants : refuges, ateliers itinérants, outils
            communs et expérimentations collectives. Ils forment un réseau de lieux où prendre soin
            devient un acte partagé.
          </p>
        </header>

        <section className="grid" style={{ gap: "24px" }}>
          {PROJECTS.map(({ title, description, cover }) => (
            <article key={title} className="glass home-support__card">
              <div
                style={{
                  borderRadius: "14px",
                  overflow: "hidden",
                  aspectRatio: "16/9",
                  background: "rgba(255,255,255,0.04)",
                }}
              >
                <img
                  src={cover}
                  alt={title}
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                />
              </div>
              <h3 style={{ margin: "16px 0 6px" }}>{title}</h3>
              <p className="muted" style={{ lineHeight: 1.55 }}>
                {description}
              </p>
            </article>
          ))}
        </section>
      </div>
    </div>
  );
}
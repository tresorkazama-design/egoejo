const PERSPECTIVES = [
  {
    title: "Rendre visibles les heritages",
    text:
      "Rehabiliter les savoirs millenaires et les cultures releguees au rang d'anecdotes pour en faire des boussoles vivantes.",
  },
  {
    title: "Reenchanter nos alliances",
    text:
      "Mettre en relation celles et ceux qui osent sortir des sentiers battus pour raviver des manieres d'habiter la Terre plus harmonieuses.",
  },
  {
    title: "Apprendre de l'ailleurs",
    text:
      "Accueillir avec humilite les connaissances venues d'autres horizons et reconnaitre que chaque peuple, malgre ses complexites, porte des solutions pour demain.",
  },
];

const PILLARS = [
  {
    title: "Rehabiliter le feminin sacre",
    text:
      "Remettre le divin feminin au centre de nos societes, honorer les corps, les cycles, les meres et les gardiennes de la vie, pour reconcilier l'humain avec son ecosysteme.",
  },
  {
    title: "Resacraliser la nature",
    text:
      "Reapprendre a considerer la Terre comme un espace vivant, sensible et sacre. Retisser des liens de respect avec toutes les formes du vivant et les esprits qui les habitent.",
  },
  {
    title: "Reinventer nos echanges",
    text:
      "Redonner a la finance sa fonction premiere d'echange pour batir des economies de soin, capables de soutenir des lendemains sans culpabilite.",
  },
  {
    title: "Encourager les audaces",
    text:
      "Soutenir celles et ceux qui experimentent, transforment et ouvrent des chemins inattendus. Faire de l'imaginaire un terrain d'action partagee.",
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
            Notre but est de relier les etres habites par l'humilite et la volonte d'agir, celles et ceux qui savent
            qu'il existe des millions d'autres manieres d'habiter le monde, souvent plus harmonieuses avec l'ecosysteme.
            Nous creons des ponts entre les porteuses de memoires anciennes, les chercheuses de possibles et les
            pionnieres qui entreprennent pour les ressusciter et reenchanter nos territoires.
          </p>
          <p className="muted" style={{ lineHeight: 1.65 }}>
            Pour que cette alliance existe, nous choisissons de raconter l'histoire longue des peuples dont les modes de
            vie ont ete invisibilises. Nous nous inspirons de celles et ceux qui ont habite la Terre differemment tout en
            restant lucides : aucun peuple n'est parfait, chacun est traverse par des complexites humaines. Notre role est
            de soutenir les audaces qui proposent des chemins inedits, hors des zones de confort.
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

        <section className="grid" style={{ gap: "24px" }}>
          {PILLARS.map(({ title, text }) => (
            <article key={title} className="glass">
              <h3 style={{ marginTop: 0 }}>{title}</h3>
              <p className="muted" style={{ lineHeight: 1.6 }}>
                {text}
              </p>
            </article>
          ))}
        </section>
      </div>
    </div>
  );
}

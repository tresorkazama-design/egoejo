const PERSPECTIVES = [
  {
    title: "Rendre visibles les hÃ©ritages",
    text:
      "RÃ©habiliter les savoirs millÃ©naires et les cultures relÃ©guÃ©es au rang dâ€™anecdotes pour en faire des boussoles vivantes.",
  },
  {
    title: "RÃ©enchanter nos alliances",
    text:
      "Mettre en relation celles et ceux qui osent sortir des sentiers battus pour raviver des maniÃ¨res dâ€™habiter la Terre plus harmonieuses.",
  },
  {
    title: "Apprendre de lâ€™ailleurs",
    text:
      "Accueillir avec humilitÃ© les connaissances venues dâ€™autres horizons et reconnaÃ®tre que chaque peuple, malgrÃ© ses complexitÃ©s, porte des solutions pour demain.",
  },
];

const PILLARS = [
  {
    title: "RÃ©habiliter le fÃ©minin sacrÃ©",
    text:
      "Remettre le divin fÃ©minin au centre de nos sociÃ©tÃ©s, honorer les corps, les cycles, les mÃ¨res et les gardiennes de la vie, pour rÃ©concilier lâ€™humain avec son Ã©cosystÃ¨me.",
  },
  {
    title: "Resacraliser la nature",
    text:
      "RÃ©apprendre Ã  considÃ©rer la Terre comme un espace vivant, sensible et sacrÃ©. Retisser des liens de respect avec toutes les formes du vivant et les esprits qui les habitent.",
  },
  {
    title: "RÃ©inventer nos Ã©changes",
    text:
      "Redonner Ã  la finance sa fonction premiÃ¨re dâ€™Ã©change pour bÃ¢tir des Ã©conomies de soin, capables de soutenir des lendemains sans culpabilitÃ©.",
  },
  {
    title: "Encourager les audaces",
    text:
      "Soutenir celles et ceux qui expÃ©rimentent, transforment et ouvrent des chemins inattendus. Faire de lâ€™imaginaire un terrain dâ€™action partagÃ©e.",
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
            Notre but est de relier les Ãªtres habitÃ©s par lâ€™humilitÃ© et la volontÃ© dâ€™agir, celles et ceux qui savent
            quâ€™il existe des millions dâ€™autres maniÃ¨res dâ€™habiter le monde, souvent plus harmonieuses avec lâ€™Ã©cosystÃ¨me.
            Nous crÃ©ons des ponts entre les porteuses de mÃ©moires anciennes, les chercheuses de possibles et les
            pionniÃ¨res qui entreprennent pour les ressusciter et rÃ©enchanter nos territoires.
          </p>
          <p className="muted" style={{ lineHeight: 1.65 }}>
            Pour que cette alliance existe, nous choisissons de raconter lâ€™histoire longue des peuples dont les modes de
            vie ont Ã©tÃ© invisibilisÃ©s. Nous nous inspirons de celles et ceux qui ont habitÃ© la Terre diffÃ©remment tout en
            restant lucides : aucun peuple nâ€™est parfait, chacun est traversÃ© par des complexitÃ©s humaines. Notre rÃ´le est
            de soutenir les audaces qui proposent des chemins inÃ©dits, hors des zones de confort.
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


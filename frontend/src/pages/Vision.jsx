const PERSPECTIVES = [
  {
    title: "Rendre visibles les héritages",
    text:
      "Réhabiliter les savoirs millénaires et les cultures reléguées au rang d’anecdotes pour en faire des boussoles vivantes.",
  },
  {
    title: "Réenchanter nos alliances",
    text:
      "Mettre en relation celles et ceux qui osent sortir des sentiers battus pour raviver des manières d’habiter la Terre plus harmonieuses.",
  },
  {
    title: "Apprendre de l’ailleurs",
    text:
      "Accueillir avec humilité les connaissances venues d’autres horizons et reconnaître que chaque peuple, malgré ses complexités, porte des solutions pour demain.",
  },
];

const PILLARS = [
  {
    title: "Réhabiliter le féminin sacré",
    text:
      "Remettre le divin féminin au centre de nos sociétés, honorer les corps, les cycles, les mères et les gardiennes de la vie, pour réconcilier l’humain avec son écosystème.",
  },
  {
    title: "Resacraliser la nature",
    text:
      "Réapprendre à considérer la Terre comme un espace vivant, sensible et sacré. Retisser des liens de respect avec toutes les formes du vivant et les esprits qui les habitent.",
  },
  {
    title: "Réinventer nos échanges",
    text:
      "Redonner à la finance sa fonction première d’échange pour bâtir des économies de soin, capables de soutenir des lendemains sans culpabilité.",
  },
  {
    title: "Encourager les audaces",
    text:
      "Soutenir celles et ceux qui expérimentent, transforment et ouvrent des chemins inattendus. Faire de l’imaginaire un terrain d’action partagée.",
  },
];

const QUOTES = [
  {
    text:
      "« Je suis une maudite Sauvagesse. Je suis très fière quand, aujourd’hui, je m’entends traiter de Sauvagesse… Puisse le Blanc me toujours traiter de Sauvagesse. »",
    author: "Antane Kapesh, An.",
  },
  {
    text: "« Ce que la chenille appelle la mort, le papillon l’appelle renaissance. »",
    author: "Violette Lebon",
  },
  {
    text:
      "« Nous vivons un des changements les plus fondamentaux de l’histoire : la transformation du système de croyances de la société occidentale… En changeant délibérément leur image de la réalité, les hommes sont en train de changer le monde. »",
    author: "Willis Harman",
  },
  {
    text:
      "« La civilisation née en Occident… Si la modernité se définit comme foi inconditionnelle dans le progrès, dans la technique, dans la science, dans le développement économique, alors cette modernité est morte. »",
    author: "Edgar Morin",
  },
  {
    text:
      "« Cette nouvelle société de la connaissance transmoderne et post-capitaliste est déjà née… nous continuons à regarder avec des lunettes industrielles, si bien que nous ne voyons même pas la nouvelle société qui est devant nous. »",
    author: "Marc Luyckx Ghisi",
  },
  {
    text:
      "« Le Blanc n’a probablement jamais su que l’Indien possède un diplôme… c’est dans sa tête que se trouve son diplôme. »",
    author: "Antane Kapesh, An.",
  },
  {
    text: "« Pour une civilisation, l’histoire est inconsciente. »",
    author: "Richard Tarnas",
  },
  {
    text: "« Ce que nous ne hissons pas au niveau de notre conscient réapparaît dans nos vies comme le destin. »",
    author: "Attribué à Carl Gustav Jung",
  },
  {
    text:
      "« Un des moyens les plus puissants pour comprendre ce qui mobilise une société est d’observer sa représentation du divin… »",
    author: "Bernard Lietaer",
  },
  {
    text: "« Au commencement était le sein… Un sein maternel signifiait la vie ou la mort pour chaque nouveau-né. »",
    author: "Marylin Yalom",
  },
  {
    text: "« Le mystère est toujours le corps, le mystère est toujours le corps d’une femme. »",
    author: "Hélène Cixous",
  },
  {
    text:
      "« Ils disent qu’une certaine femme nommée Eataentsic est celle qui a fait la terre et les hommes… Et ce sont parmi eux des mystères si cachés. »",
    author: "Jean de Brébeuf, Relations des Jésuites (1635-1648)",
  },
  {
    text:
      "« Tandis que les hommes s’aventuraient au-delà de leurs terres pour chercher du gibier, les femmes protégeaient les vaches… Ensemble, elles ont fourni les notions fondamentales de la religion égyptienne. »",
    author: "Fekri A.",
  },
  {
    text:
      "« Le cauri connecte la mort avec les principes cosmologiques de l’eau, de la lune, du féminin et de la renaissance dans un monde nouveau. »",
    author: "Abbé Breuil",
  },
  {
    text:
      "« On croit généralement que la culture chinoise a toujours été un solide système patriarcal… Nu Kua avait établi l’ordre de l’univers. »",
    author: "Merlin Stone",
  },
  {
    text:
      "« L’évolution de la mentalité occidentale a été impulsée par un effort héroïque pour forger un être humain autonome et rationnel… l’évolution de la pensée occidentale a été fondée sur la répression du féminin. »",
    author: "Richard Tarnas",
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
            Notre but est de relier les êtres habités par l’humilité et la volonté d’agir, celles et
            ceux qui savent qu’il existe des millions d’autres manières d’habiter le monde, souvent
            plus harmonieuses avec l’écosystème. Nous créons des ponts entre les porteuses de
            mémoires anciennes, les chercheuses de possibles et les pionnières qui entreprennent pour
            les ressusciter et réenchanter nos territoires.
          </p>
          <p className="muted" style={{ lineHeight: 1.65 }}>
            Pour que cette alliance existe, nous choisissons de raconter l’histoire longue des peuples
            dont les modes de vie ont été invisibilisés. Nous nous inspirons de celles et ceux qui ont
            habité la Terre différemment tout en restant lucides : aucun peuple n’est parfait, chacun
            est traversé par des complexités humaines. Notre rôle est de soutenir les audaces qui
            proposent des chemins inédits, hors des zones de confort.
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

        <section className="glass" style={{ display: "grid", gap: "18px" }}>
          <h2 className="heading-l" style={{ marginBottom: 0 }}>
            Voix qui nous inspirent
          </h2>
          <p className="muted" style={{ lineHeight: 1.6 }}>
            Ces paroles, venues de terres et d’époques diverses, nourrissent notre imaginaire et nous
            rappellent que la transformation passe par le sensible, la mémoire, la justice et la
            réconciliation du féminin et du masculin.
          </p>
          <div className="grid" style={{ gap: "18px" }}>
            {QUOTES.map(({ text, author }) => (
              <blockquote
                key={text}
                className="glass"
                style={{
                  margin: 0,
                  padding: "20px",
                  borderLeft: "3px solid var(--accent)",
                  background: "rgba(5, 11, 14, 0.55)",
                  display: "grid",
                  gap: "12px",
                }}
              >
                <p className="muted" style={{ margin: 0, lineHeight: 1.65 }}>
                  {text}
                </p>
                <cite style={{ fontStyle: "normal", color: "var(--accent)" }}>{author}</cite>
              </blockquote>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

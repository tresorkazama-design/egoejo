import React from "react";

const GROUPS = [
  {
    title: "Voix autochtones",
    description:
      "Des prises de parole qui réancrent nos imaginaires dans la dignité des peuples premiers, dans la mémoire de leurs cosmologies et de leurs résistances.",
    quotes: [
      {
        text: `« Je suis une maudite Sauvagesse. Je suis très fière quand, aujourd’hui, je m’entends traiter de Sauvagesse. Quand j’entends le Blanc prononcer ce mot, je comprends qu’il me redit sans cesse que je suis une vraie Indienne et que c’est moi la première à avoir vécu dans la forêt. Or, toute chose qui vit dans la forêt correspond à la vie la meilleure. Puisse le Blanc me toujours traiter de Sauvagesse. »`,
        author: "Antane Kapesh, An.",
      },
      {
        text: `« Ils disent qu’une certaine femme nommée Eataentsic est celle qui a fait la terre et les hommes. Ils luy baillent pour adioint un certain appelé Iouskeha, qu’ils disent être son petit-fils, avec lequel elle gouverne le monde ; c’est Iouskeha a soin des vivants & des choses qui concernent la vie, & par conséquent ils disent qu’il est bon : Eataentsic a soin des âmes, & parce qu’ils croient qu’elle fait mourir les hommes, ils disent qu’elle est méchante. Et ce sont parmi eux des mystères si cachez, qu’il n’y a que les vieillards qui en puissent parler avec crédit & autorité, pour être creus. D’où vient qu’un certain jeune homme m’en ayant discouru, me dist en se ventant, Ne suis-je pas bien sçauant ? Quelques uns me disent que la maison de ces deux Divinités est au bout du monde vers l’Orient. Or chez eux le monde ne passe point leur Pays, c’est à dire l’Amerique, d’autres les logent au milieu. Ce Dieu & cette Déesse vivent comme eux, mais sans disette ; font des festins comme eux, sont lascifs aussi bien qu’eux : bref ils se les figurent tous tels qu’ils sont eux mesmes. Et encor qu’ils les facent hommes & corporels, ils semblent néanmoins leur attribuer une certaine immensité en tous lieux. Ils disent que cette Eataentsic est tombée du Ciel, où il y a des habitans comme icy, & que quand elle tomba, elle était enceinte. Que si vous leur demandez qui a fait le Ciel & les habitans, ils n’ont autre réponse, sinon qu’ils n’en sçavent rien. Et quand nous leur preschons un Dieu, Createur du Ciel & de la terre & de toutes choses : de mesme quand nous leur parlons d’un Enfer & d’un Paradis, & du reste de nos mystères ; les opiniastres répondent, que cela est bon pour nostre Pays, non pour le leur ; que chaque Pays a ses façons de faire. »`,
        author: "Jean de Brébeuf, Les Relations de ce qui s’est passé au Pays des Hurons (1635-1648)",
      },
      {
        text: `« Le Blanc n’a probablement jamais su que l’Indien possède un diplôme : lorsqu’il est allé le trouver dans son territoire, l’Indien le lui a caché. Mais aujourd’hui il n’a pas honte de montrer au Blanc que lui aussi, en sa qualité d’Indien, possède un diplôme et il n’a pas honte de le faire valoir. L’Indien, lui, n’a pas de certificat à accrocher au mur attestant qu’il est diplômé : c’est dans sa tête que se trouve son diplôme. »`,
        author: "Antane Kapesh, An.",
      },
    ],
  },
  {
    title: "Métamorphoses et devenirs",
    description:
      "Ces textes invitent à regarder les ruptures en cours comme autant de passages vers d’autres façons d’habiter le monde, en assumant l’inconfort des transitions.",
    quotes: [
      {
        text: "« Ce que la chenille appelle la mort, le papillon l’appelle renaissance. »",
        author: "Violette Lebon",
      },
      {
        text: `« Nous vivons un des changements les plus fondamentaux de l’histoire : la transformation du système de croyances de la société occidentale. Aucune puissance politique, économique ou militaire ne peut se comparer à la puissance d’un changement au niveau de notre esprit. En changeant délibérément leur image de la réalité, les hommes sont en train de changer le monde. »`,
        author: "Willis Harman",
      },
      {
        text: `« La civilisation née en Occident,

en larguant ses amarres avec le passé,

croyait se diriger vers un futur de progrès à l'infini,

grâce aux progrès conjoints de la science, de la raison,

de l'histoire, de l'économie, de la démocratie.

Or nous avons appris, avec Hiroshima,
que la science était ambivalente ;
nous avons vu la raison régresser et le délire stalinien
prendre le masque de la raison historique ;
nous avons vu qu'il n'y avait pas de lois de l’Histoire
guidant irrésistiblement vers un avenir radieux ;
nous avons vu que le triomphe de la démocratie n'était
nulle part définitivement assuré ;
nous avons vu que le développement industriel pouvait entraîner
des ravages culturels et des pollutions mortifères ;
nous avons vu que la civilisation du bien-être
pouvait produire en même temps du mal-être.

Si la modernité se définit comme foi inconditionnelle
dans le progrès, dans la technique, dans la science,
dans le développement économique,
alors cette modernité est morte. »`,
        author: "Edgar Morin",
      },
      {
        text: `« Cette nouvelle société de la connaissance transmoderne et post-capitaliste est déjà née, elle est là sous nos yeux. Mais nous ne la voyons pas, parce que personne ne nous en parle mais aussi et surtout parce que nos lunettes sont encore trop souvent modernes, industrielles, capitalistes et patriarcales.

Pour le dire de manière imagée, nous continuons à regarder avec des lunettes industrielles, si bien que nous ne voyons même pas la nouvelle société qui est devant nous et dans laquelle nous baignons. Parfois nous rencontrons des entreprises ou des groupes de la société civile qui sont déjà dans cette nouvelle mouvance, mais nous ne les voyons pas parce que nous n'avons pas les bonnes lunettes. »`,
        author: "Marc Luyckx Ghisi",
      },
    ],
  },
  {
    title: "Féminin sacré et cycles du vivant",
    description:
      "Un ensemble de paroles qui réhabilitent le corps, les cycles, la sensualité et la force créatrice du féminin dans les sociétés humaines.",
    quotes: [
      {
        text: "« Un des moyens les plus puissants pour comprendre ce qui mobilise une société est d’observer sa représentation du divin. Une vision de ce divin, qui nie tout rôle significatif au féminin, laisse peu de place aux femmes pour s’honorer elles-mêmes ou pour honorer leur corps. »",
        author: "Bernard Lietaer",
      },
      {
        text: `« Au commencement était le sein. Pour presque toute l’histoire humaine, il n’y avait pas de substitut au lait maternel. En effet, jusqu’à la fin du XIXᵉ siècle, quand la pasteurisation a rendu le lait animal sûr. Un sein maternel signifiait la vie ou la mort pour chaque nouveau-né. Il n’est guère surprenant que nos ancêtres préhistoriques dotassent leurs idoles féminines d’impressionnantes poitrines. »`,
        author: "Marylin Yalom",
      },
      {
        text: "« Le mystère est toujours le corps, le mystère est toujours le corps d’une femme. »",
        author: "Hélène Cixous",
      },
      {
        text: "« Tandis que les hommes s’aventuraient au-delà de leurs terres pour chercher du gibier, les femmes protégeaient les vaches, les approvisionnant en nourriture et en boisson. Toutes les deux, femmes et vaches, donnaient du lait. Toutes les deux étaient source de régénération et de vie. L’eau, le bétail, le lait et les femmes étaient la source de régénération et d’alimentation. Ces associations mentales eurent une profonde signification psychologique. Ensemble, elles ont fourni les notions fondamentales de la religion égyptienne : naissance, mort et résurrection. L’image d’une déesse vache est omniprésente en Égypte dès la première dynastie comme le montre la fameuse palette de Narmer. »",
        author: "Fekri A.",
      },
      {
        text: "« Le coquillage appelé cauri a été, de toutes les formes de monnaie, une monnaie bien plus répandue et pour une durée bien supérieure aux autres formes, y compris même les métaux précieux. Le cauri, avec sa forme de vulve, est associé à l’eau dans laquelle il se forme et à la fertilité spécifique à cet élément. Il est traditionnellement lié au plaisir sexuel, à la prospérité, à la chance et à la fécondité. Pour les Aztèques, le dieu lune Tecaciztecatl signifiant littéralement “celui du coquillage”, possède de nombreux attributs : le processus de la naissance et de la génération. »",
        author: "Jean Chevalier & Alain Gheerbrant",
      },
      {
        text: "« Le cauri connecte la mort avec les principes cosmologiques de l’eau, de la lune, du féminin et de la renaissance dans un monde nouveau. »",
        author: "Abbé Breuil",
      },
      {
        text: "« On croit généralement que la culture chinoise a toujours été un solide système patriarcal. Il n’en est pas ainsi car la Chine a également eu, en Nu Kua, l’archétype d’une déesse mère toute puissante. Selon des textes de la période Zhou, Nu Kua était une déesse ayant la forme d’un serpent qui avait créé tous les gens avec de l’argile. Elle avait également établi l’ordre de l’univers en fabriquant les quatre directions du compas, en créant l’ordre des saisons et en mettant les étoiles et les planètes sur leurs trajectoires respectives. »",
        author: "Merlin Stone",
      },
    ],
  },
  {
    title: "Regards critiques sur la modernité",
    description:
      "Des penseurs qui questionnent l’Occident moderne et proposent de réhabiliter notre part sensible, intuitive et collective.",
    quotes: [
      {
        text: "« Pour une civilisation, l’histoire est inconsciente. »",
        author: "Richard Tarnas",
      },
      {
        text: "« Ce que nous ne hissons pas au niveau de notre conscient réapparaît dans nos vies comme le destin. »",
        author: "Carl Gustav Jung (attribué)",
      },
      {
        text: `« L’évolution de la mentalité occidentale a été impulsée par un effort héroïque pour forger un être humain autonome et rationnel en le séparant de l’unité primordiale avec la nature.

Les perspectives religieuses, scientifiques et philosophiques de la culture occidentale ont été affectées par cette masculinité décisive, débutant il y a quatre millénaires avec la grande conquête patriarcale des nomades, en Grèce et au Levant, des anciennes cultures matrifocales, conquêtes manifestes dans la religion patriarcale de l’Occident, du Judaïsme, dans la philosophie rationaliste de la Grèce et dans la science objectiviste de l’Europe moderne.

Toutes ont servi la cause du développement de la volonté et de l’intellect autonome humain : le moi transcendant, l’ego individuel indépendant, et l’être humain autodéterminé dans son unicité, sa différence et sa liberté. Mais pour ce faire, l’esprit masculin a réprimé le féminin. Que l’on le voie dans la subjugation des mythologies matrifocales préhelléniques de la Grèce antique, dans le déni judéo-chrétien de la déesse Mère, ou dans l’exaltation de l’ego rationnel détaché et auto-conscient de l’Illustration, un ego qui est radicalement séparé d’une nature extérieure désenchantée, l’évolution de la pensée occidentale a été fondée sur la répression du féminin, sur la répression de la conscience unitaire indifférenciée, de la participation mystique avec la nature : un déni progressif de l’anima mundi, de la communauté de l’être, du tout imprégné, du mystère et de l’ambiguïté, de l’imagination, de l’émotion, de l’instinct, du corps, de la nature, de la femme, de tout ce en quoi le masculin s’est projeté en l’identifiant comme “autre”. »`,
        author: "Richard Tarnas",
      },
    ],
  },
];

export default function Citations() {
  return (
    <div className="page">
      <div className="container" style={{ display: "grid", gap: "40px" }}>
        <header className="grid" style={{ gap: "16px" }}>
          <span className="tag">Citations</span>
          <h1 className="heading-l">Voix qui nous accompagnent</h1>
          <p className="lead">
            Cette anthologie rassemble des paroles fondatrices qui nourrissent EGOEJO. Elles sont présentées dans leur
            intégralité, regroupées par thématiques pour inviter à la lecture contemplative et à la mise en relation des
            idées.
          </p>
        </header>

        <div className="grid" style={{ gap: "32px" }}>
          {GROUPS.map(({ title, description, quotes }) => (
            <section key={title} className="glass" style={{ padding: "28px", display: "grid", gap: "24px" }}>
              <div className="grid" style={{ gap: "8px" }}>
                <h2 className="heading-l" style={{ margin: 0, fontSize: "clamp(1.4rem, 3vw, 2rem)" }}>
                  {title}
                </h2>
                <p className="muted" style={{ margin: 0, lineHeight: 1.6 }}>
                  {description}
                </p>
              </div>

              <div className="grid" style={{ gap: "20px" }}>
                {quotes.map(({ text, author }, idx) => (
                  <blockquote
                    key={`${author}-${idx}`}
                    className="glass"
                    style={{
                      margin: 0,
                      padding: "24px",
                      borderLeft: "3px solid var(--accent)",
                      background: "rgba(6, 12, 16, 0.55)",
                      display: "grid",
                      gap: "12px",
                    }}
                  >
                    <p className="muted" style={{ margin: 0, lineHeight: 1.65, whiteSpace: "pre-wrap" }}>
                      {text}
                    </p>
                    <cite style={{ fontStyle: "normal", color: "var(--accent)" }}>{author}</cite>
                  </blockquote>
                ))}
              </div>
            </section>
          ))}
        </div>
      </div>
    </div>
  );
}

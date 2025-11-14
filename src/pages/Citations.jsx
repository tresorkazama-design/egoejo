import React from "react";

const GROUPS = [
  {
    title: "Voix autochtones",
    description:
      "Des prises de parole qui reancrent nos imaginaires dans la dignite des peuples premiers, dans la memoire de leurs cosmologies et de leurs resistances.",
    quotes: [
      {
        text: `« Je suis une maudite Sauvagesse. Je suis tres fiere quand, aujourd'hui, je m'entends traiter de Sauvagesse. Quand j'entends le Blanc prononcer ce mot, je comprends qu'il me redit sans cesse que je suis une vraie Indienne et que c'est moi la premiere a avoir vecu dans la foret. Or, toute chose qui vit dans la foret correspond a la vie la meilleure. Puisse le Blanc me toujours traiter de Sauvagesse. »`,
        author: "Antane Kapesh, An.",
      },
      {
        text: `« Ils disent qu'une certaine femme nommee Eataentsic est celle qui a fait la terre et les hommes. Ils luy baillent pour adioint un certain appele Iouskeha, qu'ils disent etre son petit-fils, avec lequel elle gouverne le monde ; c'est Iouskeha a soin des vivants & des choses qui concernent la vie, & par consequent ils disent qu'il est bon : Eataentsic a soin des ames, & parce qu'ils croyent qu'elle fait mourir les hommes, ils disent qu'elle est mechante. Et ce sont parmi eux des mysteres si cachez, qu'il n'y a que les vieillards qui en puissent parler avec credit & autorite, pour estre creus. D'ou vient qu'un certain jeune homme m'en ayant discouru, me dist en se ventant, Ne suis-je pas bien scauant ? Quelques uns me disent que la maison de ces deux Divinites est au bout du monde vers l'Orient. Or chez eux le monde ne passe point leur Pays, c'est a dire l'Amerique, d'autres les logent au milieu. Ce Dieu & cette Deesse vivent comme eux, mais sans disette ; font des festins comme eux, sont lascifs aussi bien qu'eux : bref ils se les figurent tous tels qu'ils sont eux mesmes. Et encor qu'ils les facent hommes & corporels, ils semblent neanmoins leur attribuer une certaine immensite en tous lieux. Ils disent que cette Eataentsic est tombee du Ciel, ou il y a des habitans comme icy, & que quand elle tomba, elle estoit enceinte. Que si vous leur demandez qui a fait le Ciel & les habitans, ils n'ont autre reponse, sinon qu'ils n'en scauent rien. Et quand nous leur preschons un Dieu, Createur du Ciel & de la terre & de toutes choses : de mesme quand nous leur parlons d'un Enfer & d'un Paradis, & du reste de nos mysteres ; les opiniastres respondent, que cela est bon pour nostre Pays, non pour le leur ; que chaque Pays a ses facons de faire. »`,
        author: "Jean de Brebeuf, Les Relations de ce qui s'est passe au Pays des Hurons (1635-1648)",
      },
      {
        text: `« Le Blanc n'a probablement jamais su que l'Indien possede un diplome : lorsqu'il est alle le trouver dans son territoire, l'Indien le lui a cache. Mais aujourd'hui il n'a pas honte de montrer au Blanc que lui aussi, en sa qualite d'Indien, possede un diplome et il n'a pas honte de le faire valoir. L'Indien, lui, n'a pas de certificat a accrocher au mur attestant qu'il est diplome : c'est dans sa tete que se trouve son diplome. »`,
        author: "Antane Kapesh, An.",
      },
    ],
  },
  {
    title: "Metamorphoses et devenirs",
    description:
      "Ces textes invitent a regarder les ruptures en cours comme autant de passages vers d'autres facons d'habiter le monde, en assumant l'inconfort des transitions.",
    quotes: [
      {
        text: "« Ce que la chenille appelle la mort, le papillon l'appelle renaissance. »",
        author: "Violette Lebon",
      },
      {
        text: `« Nous vivons un des changements les plus fondamentaux de l'histoire : la transformation du systeme de croyances de la societe occidentale. Aucune puissance politique, economique ou militaire ne peut se comparer a la puissance d'un changement au niveau de notre esprit. En changeant deliberement leur image de la realite, les hommes sont en train de changer le monde. »`,
        author: "Willis Harman",
      },
      {
        text: `« La civilisation nee en Occident,

en larguant ses amarres avec le passe,

croyait se diriger vers un futur de progres a l'infini,

grâce aux progres conjoints de la science, de la raison,

de l'histoire, de l'economie, de la democratie.

Or nous avons appris, avec Hiroshima,
que la science etait ambivalente ;
nous avons vu la raison regresser et le delire stalinien
prendre le masque de la raison historique ;
nous avons vu qu'il n'y avait pas de lois de l'Histoire
guidant irresistibly vers un avenir radieux ;
nous avons vu que le triomphe de la democratie n'etait
nulle part definitivement assure ;
nous avons vu que le developpement industriel pouvait entrainer
des ravages culturels et des pollutions mortiferes ;
nous avons vu que la civilisation du bien-etre
pouvait produire en meme temps du mal-etre.

Si la modernite se definit comme foi inconditionnelle
dans le progres, dans la technique, dans la science,
dans le developpement economique,
alors cette modernite est morte. »`,
        author: "Edgar Morin",
      },
      {
        text: `« Cette nouvelle societe de la connaissance transmoderne et post-capitaliste est deja nee, elle est la sous nos yeux. Mais nous ne la voyons pas, parce que personne ne nous en parle mais aussi et surtout parce que nos lunettes sont encore trop souvent modernes, industrielles, capitalistes et patriarcales.

Pour le dire de maniere imagee, nous continuons a regarder avec des lunettes industrielles, si bien que nous ne voyons meme pas la nouvelle societe qui est devant nous et dans laquelle nous baignons. Parfois nous rencontrons des entreprises ou des groupes de la societe civile qui sont deja dans cette nouvelle mouvance, mais nous ne les voyons pas parce que nous n'avons pas les bonnes lunettes. »`,
        author: "Marc Luyckx Ghisi",
      },
    ],
  },
  {
    title: "Feminin sacre et cycles du vivant",
    description:
      "Un ensemble de paroles qui rehabilitent le corps, les cycles, la sensualite et la force creatrice du feminin dans les societes humaines.",
    quotes: [
      {
        text: "« Un des moyens les plus puissants pour comprendre ce qui mobilise une societe est d'observer sa representation du divin. Une vision de ce divin, qui nie tout role significatif au feminin, laisse peu de place aux femmes pour s'honorer elles-memes ou pour honorer leur corps. »",
        author: "Bernard Lietaer",
      },
      {
        text: `« Au commencement etait le sein. Pour presque toute l'histoire humaine, il n'y avait pas de substitut au lait maternel. En effet, jusqu'a la fin du XIXe siecle, quand la pasteurisation a rendu le lait animal sur. Un sein maternel signifiait la vie ou la mort pour chaque nouveau-ne. Il n'est guere surprenant que nos ancetres prehistoriques dotassent leurs idoles feminines d'impressionnantes poitrines. »`,
        author: "Marylin Yalom",
      },
      {
        text: "« Le mystere est toujours le corps, le mystere est toujours le corps d'une femme. »",
        author: "Helene Cixous",
      },
      {
        text: "« Tandis que les hommes s'aventuraient au-dela de leurs terres pour chercher du gibier, les femmes protegeaient les vaches, les approvisionnant en nourriture et en boisson. Toutes les deux, femmes et vaches, donnaient du lait. Toutes les deux etaient source de regeneration et de vie. L'eau, le betail, le lait et les femmes etaient la source de regeneration et d'alimentation. Ces associations mentales eurent une profonde signification psychologique. Ensemble, elles ont fourni les notions fondamentales de la religion egyptienne : naissance, mort et resurrection. L'image d'une deesse vache est omnipresente en Egypte des la premiere dynastie comme le montre la fameuse palette de Narmer. »",
        author: "Fekri A.",
      },
      {
        text: "« Le coquillage appele cauri a ete, de toutes les formes de monnaie, une monnaie bien plus repandue et pour une duree bien superieure aux autres formes, y compris meme les metaux precieux. Le cauri, avec sa forme de vulve, est associe a l'eau dans laquelle il se forme et a la fertilite specifique a cet element. Il est traditionnellement lie au plaisir sexuel, a la prosperite, a la chance et a la fecondite. Pour les Azteques, le dieu lune Tecaciztecatl signifiant litteralement “celui du coquillage”, possede de nombreux attributs : le processus de la naissance et de la generation. »",
        author: "Jean Chevalier & Alain Gheerbrant",
      },
      {
        text: "« Le cauri connecte la mort avec les principes cosmologiques de l'eau, de la lune, du feminin et de la renaissance dans un monde nouveau. »",
        author: "Abbe Breuil",
      },
      {
        text: "« On croit generalement que la culture chinoise a toujours ete un solide systeme patriarcal. Il n'en est pas ainsi car la Chine a egalement eu, en Nu Kua, l'archetype d'une deesse mere toute puissante. Selon des textes de la periode Zhou, Nu Kua etait une deesse ayant la forme d'un serpent qui avait cree tous les gens avec de l'argile. Elle avait egalement etabli l'ordre de l'univers en fabriquant les quatre directions du compas, en creant l'ordre des saisons et en mettant les etoiles et les planetes sur leurs trajectoires respectives. »",
        author: "Merlin Stone",
      },
    ],
  },
  {
    title: "Regards critiques sur la modernite",
    description:
      "Des penseurs qui questionnent l'Occident moderne et proposent de rehabiliter notre part sensible, intuitive et collective.",
    quotes: [
      {
        text: "« Pour une civilisation, l'histoire est inconsciente. »",
        author: "Richard Tarnas",
      },
      {
        text: "« Ce que nous ne hissons pas au niveau de notre conscient reapparait dans nos vies comme le destin. »",
        author: "Carl Gustav Jung (attribue)",
      },
      {
        text: `« L'evolution de la mentalite occidentale a ete impulsee par un effort heroique pour forger un etre humain autonome et rationnel en le separant de l'unite primordiale avec la nature.

Les perspectives religieuses, scientifiques et philosophiques de la culture occidentale ont ete affectees par cette masculinite decisive, debutant il y a quatre millenaires avec la grande conquete patriarcale des nomades, en Grece et au Levant, des anciennes cultures matrifocales, conquetes manifestes dans la religion patriarcale de l'Occident, du Judaisme, dans la philosophie rationaliste de la Grece et dans la science objectiviste de l'Europe moderne.

Toutes ont servi la cause du developpement de la volonte et de l'intellect autonome humain : le moi transcendant, l'ego individuel independant, et l'etre humain autodetermine dans son unicite, sa difference et sa liberte. Mais pour ce faire, l'esprit masculin a reprime le feminin. Que l'on le voie dans la subjugation des mythologies matrifocales prehelleniques de la Grece antique, dans le deni judeo-chretien de la deesse Mere, ou dans l'exaltation de l'ego rationnel detache et auto-conscient de l'Illustration, un ego qui est radicalement separe d'une nature exterieure desenchantee, l'evolution de la pensee occidentale a ete fondee sur la repression du feminin, sur la repression de la conscience unitaire indifferenciee, de la participation mystique avec la nature : un deni progressif de l'anima mundi, de la communaute de l'etre, du tout impregne, du mystere et de l'ambiguite, de l'imagination, de l'emotion, de l'instinct, du corps, de la nature, de la femme, de tout ce en quoi le masculin s'est projete en l'identifiant comme “autre”. »`,
        author: "Richard Tarnas",
      },
    ],
  },
];

const HIGHLIGHT_QUOTE = {
  text: "Relier les voix du monde, c'est eclairer les chemins qui restent a inventer.",
  author: "Collectif EGOEJO",
};

export default function Citations() {
  return (
    <div className="page page--citations">
      <div className="citations-hero">
        <div className="citations-hero__badge">Anthologie vivante</div>
        <h1 className="citations-hero__title">Voix qui nous accompagnent</h1>
        <p className="citations-hero__subtitle">
          Ces paroles sont des repaires sensibles pour orienter nos decisions, nourrir nos projets et rappeler la place du
          vivant au coeur de nos alliances.
        </p>
        <blockquote className="citations-hero__highlight">
          <p>{HIGHLIGHT_QUOTE.text}</p>
          <cite>{HIGHLIGHT_QUOTE.author}</cite>
        </blockquote>
        <dl className="citations-hero__stats">
          <div>
            <dt>4 thematiques</dt>
            <dd>pour cartographier nos inspirations</dd>
          </div>
          <div>
            <dt>20+ extraits</dt>
            <dd>presentes dans leur integrite</dd>
          </div>
          <div>
            <dt>1 bibliographie</dt>
            <dd>a partager et a prolonger</dd>
          </div>
        </dl>
      </div>

      <div className="citations-grid">
        {GROUPS.map(({ title, description, quotes }) => (
          <section key={title} className="citation-group">
            <header className="citation-group__header">
              <span className="citation-group__tag">Thematique</span>
              <h2 className="citation-group__title">{title}</h2>
              <p className="citation-group__description">{description}</p>
            </header>

            <div className="citation-group__quotes">
              {quotes.map(({ text, author }, idx) => (
                <blockquote key={`${author}-${idx}`} className="citation-card">
                  <p className="citation-card__text">{text}</p>
                  <cite className="citation-card__author">{author}</cite>
                </blockquote>
              ))}
            </div>
          </section>
        ))}
      </div>

      <div className="citations-cta">
        <h2 className="heading-l">Votre voix compte</h2>
        <p className="lead">
          Vous souhaitez partager une citation ou une reference qui nourrit la vision EGOEJO ? Envoyez-nous votre
          suggestion et nous la documenterons avec soin.
        </p>
        <a
          href="mailto:contact@egoejo.org?subject=Contribution%20Citations%20EGOEJO"
          className="btn btn-primary"
        >
          Proposer une citation
        </a>
      </div>

      <div className="citations-references">
        <h3 className="heading-m">Ressources</h3>
        <p className="muted">
          Une bibliographie detaillee est en cours de mise a jour. En attendant, contactez-nous pour obtenir les
          references liees a chaque citation ou pour partager vos propres sources.
        </p>
      </div>
    </div>
  );
}

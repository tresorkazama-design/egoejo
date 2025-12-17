import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Traductions complètes pour l'allemand
const deTranslations = {
  nav: {
    accueil: "Startseite",
    univers: "Universum",
    vision: "Vision",
    citations: "Zitate",
    alliances: "Allianzen",
    projets: "Projekte",
    contenus: "Inhalte",
    communaute: "Gemeinschaft",
    votes: "Stimmen",
    rejoindre: "Beitreten",
    chat: "Chat",
    login: "Anmeldung",
    logout: "Abmelden",
    welcome: "Willkommen {{username}}!",
    moderation: "Moderation",
    menu: "Menü",
    languages: "Sprachen",
    footer_navigation: "Fußzeile Navigation",
    user_menu: "Benutzermenü"
  },
  common: {
    user: "Benutzer",
    required: "Pflichtfeld",
    close: "Schließen",
    loading: "Laden",
    error: "Fehler",
    actions: "Aktionen",
    retry: "Wiederholen",
    not_found: "Seite nicht gefunden",
    not_found_desc: "Die gesuchte Seite existiert nicht oder wurde verschoben.",
    back_home: "Zurück zur Startseite"
  },
  home: {
    tag: "KOLLEKTIV FÜR DAS LEBENDIGE",
    title: "Die Erde anders bewohnen,\ngemeinsam.",
    subtitle: "EGOEJO bringt Hüter des Lebendigen zusammen. Wir vernetzen Ressourcen, Wissen und engagierte Menschen, um sich um die Welt zu kümmern. Workshops, lebendige Orte, Aktionsforschung: Jedes Projekt ist eine Erfahrung zum Teilen.",
    actions: "Hauptaktionen",
    pillars: "Grundpfeiler",
    pillars_title: "Die drei Pfeiler",
    soutenir: "EGOEJO unterstützen",
    rejoindre: "Der Allianz beitreten",
    relier: "Verbinden",
    relier_desc: "Allianzen zwischen Bewohnern, Organisationen und Territorien knüpfen, um die Gemeingüter des Lebendigen wiederherzustellen.",
    apprendre: "Lernen durch Tun",
    apprendre_desc: "Im Feld experimentieren, regenerative Praktiken auf lokaler Ebene dokumentieren und teilen.",
    transmettre: "Übertragen",
    transmettre_desc: "Akteure des Wandels mit immersiven, sensiblen und in der Realität verwurzelten Formaten begleiten.",
    soutenir_title: "Werden Sie Verbündeter·in des Lebendigen",
    soutenir_desc: "Jeder Beitrag speist konkrete Aktionen: Zufluchtsorte, Nahrungsgärten, Übertragungsworkshops, Forschungsresidenzen, Begleitung lokaler Gemeinschaften. 100% der Spenden werden zur Finanzierung dieser Projekte verwendet.",
    contribuer: "Beitragen",
    donation_options: "Spendenoptionen",
    nous_soutenir: "Unterstützen Sie uns",
    membership_helloasso: "Mitgliedschaft • HelloAsso",
    membership_desc: "Der Verein beitreten und in Frankreich beitragen",
    international_support: "Internationale Unterstützung",
    international_support_desc: "Einmalige oder wiederkehrende Spende über Stripe"
  }
};

// Fonction pour compléter les traductions
function completeTranslations(lang, translations) {
  const filePath = path.join(__dirname, 'src', 'locales', `${lang}.json`);
  const existing = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  
  // Fusionner les traductions
  function mergeDeep(target, source) {
    for (const key in source) {
      if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
        if (!target[key]) target[key] = {};
        mergeDeep(target[key], source[key]);
      } else {
        target[key] = source[key];
      }
    }
  }
  
  mergeDeep(existing, translations);
  
  fs.writeFileSync(filePath, JSON.stringify(existing, null, 2), 'utf8');
  console.log(`✓ ${lang}.json complété`);
}

// Compléter les traductions
completeTranslations('de', deTranslations);

console.log('Traductions complétées!');


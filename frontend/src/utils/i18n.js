import frTranslations from '../locales/fr.json';
import enTranslations from '../locales/en.json';
import arTranslations from '../locales/ar.json';
import esTranslations from '../locales/es.json';
import deTranslations from '../locales/de.json';
import swTranslations from '../locales/sw.json';

const translations = {
  fr: frTranslations,
  en: enTranslations,
  ar: arTranslations,
  es: esTranslations,
  de: deTranslations,
  sw: swTranslations,
};

/**
 * Récupère une traduction par clé
 * @param {string} key - Clé de traduction (ex: "nav.accueil")
 * @param {string} lang - Langue (fr, en, ou ar)
 * @param {object} params - Paramètres à remplacer dans la traduction
 * @returns {string} - Texte traduit
 */
export const t = (key, lang = 'fr', params = {}) => {
  const keys = key.split('.');
  let value = translations[lang] || translations.fr;

  for (const k of keys) {
    if (value && typeof value === 'object') {
      value = value[k];
    } else {
      // Fallback vers le français si la clé n'existe pas
      value = translations.fr;
      for (const fallbackKey of keys) {
        if (value && typeof value === 'object') {
          value = value[fallbackKey];
        } else {
          return key; // Retourner la clé si aucune traduction n'est trouvée
        }
      }
      break;
    }
  }

  if (typeof value !== 'string') {
    return key;
  }

  // Remplacer les paramètres dans la traduction
  let translated = value;
  Object.keys(params).forEach((param) => {
    translated = translated.replace(new RegExp(`\\{\\{${param}\\}\\}`, 'g'), params[param]);
  });

  return translated;
};

/**
 * Hook personnalisé pour utiliser les traductions
 */
export const useTranslation = (lang) => {
  return (key, params) => t(key, lang, params);
};


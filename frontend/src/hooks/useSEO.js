import { useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { t } from '../utils/i18n';
import { useLanguage } from '../contexts/LanguageContext';

/**
 * Hook pour faciliter l'utilisation du composant SEO
 * @param {Object} options
 * @param {string} options.titleKey - Clé de traduction pour le titre
 * @param {string} options.descriptionKey - Clé de traduction pour la description
 * @param {string} options.image - URL de l'image (optionnel)
 * @param {string} options.type - Type Open Graph (optionnel)
 * @param {Object} options.jsonLd - Données JSON-LD (optionnel)
 * @param {string} options.keywords - Mots-clés (optionnel)
 * @returns {Object} Props à passer au composant SEO
 */
export function useSEO({
  titleKey,
  descriptionKey,
  image,
  type = 'website',
  jsonLd,
  keywords,
}) {
  const { language } = useLanguage();
  const location = useLocation();

  const siteUrl = import.meta.env.VITE_SITE_URL || 'https://egoejo.org';
  const currentUrl = `${siteUrl}${location.pathname}`;

  return useMemo(() => {
    const title = titleKey ? t(titleKey, language) : undefined;
    const description = descriptionKey ? t(descriptionKey, language) : undefined;

    // JSON-LD par défaut pour Organization
    const defaultJsonLd = {
      '@context': 'https://schema.org',
      '@type': 'Organization',
      name: t('seo.site_name', language) || 'EGOEJO',
      url: siteUrl,
      description: description || t('seo.default_description', language),
      ...(jsonLd || {}),
    };

    return {
      title,
      description,
      image,
      type,
      canonical: currentUrl,
      jsonLd: jsonLd !== null ? (jsonLd || defaultJsonLd) : null,
      keywords,
    };
  }, [titleKey, descriptionKey, image, type, jsonLd, keywords, language, currentUrl, siteUrl]);
}


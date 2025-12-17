import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { t } from '../utils/i18n';
import { useLanguage } from '../contexts/LanguageContext';

/**
 * Composant SEO pour gérer les meta tags dynamiques
 * @param {Object} props
 * @param {string} props.title - Titre de la page
 * @param {string} props.description - Description de la page
 * @param {string} props.image - URL de l'image pour Open Graph (optionnel)
 * @param {string} props.type - Type Open Graph (website, article, etc.) - défaut: "website"
 * @param {string} props.canonical - URL canonique (optionnel)
 * @param {Object} props.jsonLd - Données JSON-LD structurées (optionnel)
 * @param {string} props.keywords - Mots-clés SEO (optionnel)
 */
export default function SEO({
  title,
  description,
  image,
  type = 'website',
  canonical,
  jsonLd,
  keywords,
}) {
  const { language } = useLanguage();
  const location = useLocation();

  // URL de base du site
  const siteUrl = import.meta.env.VITE_SITE_URL || 'https://egoejo.org';
  const currentUrl = canonical || `${siteUrl}${location.pathname}`;
  const ogImage = image || `${siteUrl}/og-image.jpg`;
  const siteTitle = t('seo.site_name', language) || 'EGOEJO';
  const fullTitle = title ? `${title} | ${siteTitle}` : siteTitle;

  useEffect(() => {
    // Mettre à jour le titre
    document.title = fullTitle;

    // Fonction helper pour mettre à jour ou créer un meta tag
    const updateMetaTag = (property, content) => {
      if (!content) return;

      let element = document.querySelector(`meta[property="${property}"]`) ||
                   document.querySelector(`meta[name="${property}"]`);

      if (!element) {
        element = document.createElement('meta');
        const isProperty = property.startsWith('og:') || property.startsWith('twitter:');
        if (isProperty) {
          element.setAttribute('property', property);
        } else {
          element.setAttribute('name', property);
        }
        document.head.appendChild(element);
      }

      element.setAttribute('content', content);
    };

    // Meta tags de base
    updateMetaTag('description', description);
    if (keywords) {
      updateMetaTag('keywords', keywords);
    }

    // Open Graph tags
    updateMetaTag('og:title', fullTitle);
    updateMetaTag('og:description', description);
    updateMetaTag('og:type', type);
    updateMetaTag('og:url', currentUrl);
    updateMetaTag('og:image', ogImage);
    updateMetaTag('og:image:width', '1200');
    updateMetaTag('og:image:height', '630');
    updateMetaTag('og:site_name', siteTitle);
    updateMetaTag('og:locale', language === 'fr' ? 'fr_FR' : language === 'en' ? 'en_US' : 'fr_FR');

    // Twitter Card tags
    updateMetaTag('twitter:card', 'summary_large_image');
    updateMetaTag('twitter:title', fullTitle);
    updateMetaTag('twitter:description', description);
    updateMetaTag('twitter:image', ogImage);

    // URL canonique
    let canonicalLink = document.querySelector('link[rel="canonical"]');
    if (!canonicalLink) {
      canonicalLink = document.createElement('link');
      canonicalLink.setAttribute('rel', 'canonical');
      document.head.appendChild(canonicalLink);
    }
    canonicalLink.setAttribute('href', currentUrl);

    // Langue de la page
    document.documentElement.lang = language;

    // JSON-LD structured data
    let jsonLdScript = document.querySelector('script[type="application/ld+json"]');
    if (jsonLd) {
      if (!jsonLdScript) {
        jsonLdScript = document.createElement('script');
        jsonLdScript.setAttribute('type', 'application/ld+json');
        document.head.appendChild(jsonLdScript);
      }
      jsonLdScript.textContent = JSON.stringify(jsonLd);
    } else if (jsonLdScript) {
      jsonLdScript.remove();
    }
  }, [title, description, image, type, canonical, jsonLd, keywords, language, currentUrl, fullTitle, ogImage, siteTitle]);

  return null; // Ce composant ne rend rien
}


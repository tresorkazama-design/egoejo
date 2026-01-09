/**
 * Utilitaires pour la sanitization et le rendu sécurisé de contenu
 */

import { escapeHtml } from './validation.js';

/**
 * Sanitize le contenu backend (description, body, excerpt) pour prévenir XSS
 * 
 * Cette fonction échappe tous les caractères HTML dangereux pour un rendu textuel sécurisé.
 * Si du HTML valide est nécessaire, utiliser DOMPurify (non implémenté pour l'instant).
 * 
 * @param {string|null|undefined|number} content - Contenu à sanitizer
 * @returns {string} - Contenu sanitizé (échappé)
 * 
 * @example
 * sanitizeContent('<script>alert("XSS")</script>') // '&lt;script&gt;alert("XSS")&lt;/script&gt;'
 * sanitizeContent('Texte normal') // 'Texte normal'
 * sanitizeContent(null) // ''
 */
export const sanitizeContent = (content) => {
  if (content == null || content === undefined) {
    return '';
  }
  
  if (typeof content !== 'string') {
    // Convertir en string si ce n'est pas déjà une string
    return String(content);
  }
  
  // Échapper tous les caractères HTML dangereux
  return escapeHtml(content);
};

/**
 * Vérifie si le contenu contient du HTML potentiellement dangereux
 * 
 * @param {string|null|undefined} content - Contenu à vérifier
 * @returns {boolean} - True si du HTML dangereux est détecté
 */
export const containsDangerousHTML = (content) => {
  if (!content || typeof content !== 'string') {
    return false;
  }
  
  // Détecter les balises script, iframe, object, embed, etc.
  const dangerousPatterns = [
    /<script[\s\S]*?<\/script>/gi,
    /<iframe[\s\S]*?<\/iframe>/gi,
    /<object[\s\S]*?<\/object>/gi,
    /<embed[\s\S]*?>/gi,
    /on\w+\s*=/gi, // Attributs événements (onclick, onerror, etc.)
    /javascript:/gi, // Protocole javascript:
    /data:text\/html/gi, // Data URI HTML
  ];
  
  return dangerousPatterns.some(pattern => pattern.test(content));
};

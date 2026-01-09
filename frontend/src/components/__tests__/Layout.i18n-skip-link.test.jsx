import { describe, it, expect } from 'vitest';
import { renderWithProviders, SUPPORTED_LANGUAGES } from '../../test/test-utils';
import Layout from '../Layout';
import { BrowserRouter } from 'react-router-dom';

/**
 * Test i18n BLOQUANT : Vérifier que le skip-link utilise une clé de traduction
 * et n'est PAS hardcodé uniquement en français.
 * 
 * Note : Ce test vérifie statiquement le code source pour détecter
 * si le skip-link utilise t("accessibility.skip_to_main", language) ou un texte hardcodé.
 */
describe('Layout - i18n Skip-Link (BLOQUANT)', () => {
  it('devrait utiliser la clé de traduction accessibility.skip_to_main (PAS de texte hardcodé uniquement FR)', () => {
    // Tester avec toutes les langues supportées
    SUPPORTED_LANGUAGES.forEach((lang) => {
      // renderWithProviders inclut déjà BrowserRouter, ne pas l'ajouter deux fois
      const { container } = renderWithProviders(
        <Layout />,
        { language: lang }
      );
      
      // Trouver le skip-link
      const skipLink = container.querySelector('a[href="#main-content"]');
      
      if (!skipLink) {
        throw new Error(
          'BLOQUANT : Le skip-link est absent du Layout.\n' +
          'Exigence audit : Le skip-link doit exister et utiliser la clé de traduction accessibility.skip_to_main.'
        );
      }
      
      const skipLinkText = skipLink.textContent || '';
      
      // Vérifier que le texte n'est PAS "Aller au contenu principal" (hardcodé FR)
      // pour les langues autres que FR
      if (lang !== 'fr' && skipLinkText === 'Aller au contenu principal') {
        throw new Error(
          `BLOQUANT : Le skip-link est hardcodé en français pour la langue "${lang}".\n` +
          `Texte actuel : "${skipLinkText}"\n` +
          `Exigence audit : Le skip-link doit utiliser la clé de traduction accessibility.skip_to_main\n` +
          `et être traduit dans toutes les langues supportées.\n` +
          `Modifier Layout.jsx pour utiliser t("accessibility.skip_to_main", language) au lieu du texte hardcodé.`
        );
      }
      
      // Vérifier que le skip-link a un texte non vide
      expect(skipLinkText.trim().length).toBeGreaterThan(0);
    });
  });

  it('devrait vérifier que la clé accessibility.skip_to_main existe et est utilisée (test statique)', async () => {
    // Ce test vérifie statiquement que le code source utilise la traduction
    // On importe le fichier Layout et on vérifie qu'il n'y a pas de texte hardcodé
    const fs = await import('fs');
    const path = await import('path');
    
    const layoutPath = path.resolve(__dirname, '../Layout.jsx');
    const layoutCode = fs.readFileSync(layoutPath, 'utf-8');
    
    // Vérifier que le code contient t("accessibility.skip_to_main", language)
    const usesTranslation = /t\(["']accessibility\.skip_to_main["']/i.test(layoutCode);
    
    // Vérifier qu'il n'y a pas de texte hardcodé "Aller au contenu principal" dans le JSX
    const hasHardcodedText = />\s*Aller au contenu principal\s*</.test(layoutCode);
    
    if (hasHardcodedText && !usesTranslation) {
      throw new Error(
        'BLOQUANT : Le skip-link utilise un texte hardcodé "Aller au contenu principal" au lieu de la traduction.\n' +
        'Exigence audit : Le skip-link doit utiliser t("accessibility.skip_to_main", language).\n' +
        'Modifier Layout.jsx ligne ~164 pour remplacer le texte hardcodé par la traduction.'
      );
    }
    
    // Si la traduction est utilisée, le test passe
    expect(usesTranslation || !hasHardcodedText).toBe(true);
  });
});


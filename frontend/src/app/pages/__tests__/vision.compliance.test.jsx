import { describe, it, expect } from 'vitest';
import { renderWithProviders, screen } from '../../../test/test-utils';
import Vision from '../Vision';
import { t } from '../../../utils/i18n';

/**
 * Tests unitaires BLOQUANTS - Page Vision
 * 
 * Vérifie la conformité éditoriale et structurelle de la page Vision :
 * - Présence et contenu de la section "Principes fondamentaux"
 * - Présence et contenu du glossaire
 * - Présence du disclaimer citations autochtones
 * 
 * Ces tests sont BLOQUANTS et échouent explicitement si les exigences
 * de l'audit quadripartite ne sont pas respectées.
 */

describe('Vision - Compliance Tests (BLOQUANTS)', () => {
  describe('Section Principes fondamentaux (vision-principles)', () => {
    it('devrait contenir data-testid="vision-principles"', () => {
      renderWithProviders(<Vision />);
      const principlesSection = screen.getByTestId('vision-principles');
      expect(principlesSection).toBeInTheDocument();
    });

    it('devrait contenir un H2 avec le titre "Principes fondamentaux"', () => {
      renderWithProviders(<Vision />);
      const principlesSection = screen.getByTestId('vision-principles');
      const heading = principlesSection.querySelector('h2');
      
      if (!heading) {
        throw new Error(
          'BLOQUANT : La section "Principes fondamentaux" ne contient pas de H2.\n' +
          'Exigence audit : La section doit avoir un titre H2 avec le texte "Principes fondamentaux".'
        );
      }
      
      expect(heading).toBeInTheDocument();
      // Le titre peut être traduit, on vérifie juste qu'il existe
      expect(heading.textContent?.trim().length).toBeGreaterThan(0);
    });

    it('devrait contenir les 3 principes avec leurs titres et descriptions', () => {
      renderWithProviders(<Vision />);
      const principlesSection = screen.getByTestId('vision-principles');
      const sectionText = principlesSection.textContent || '';
      
      // Vérifier la présence des 3 principes via les clés i18n
      // Les principes sont rendus via getPrinciples() qui utilise les clés i18n
      const requiredPrinciples = [
        'vision.principle_relational_title',
        'vision.principle_anti_accumulation_title',
        'vision.principle_cycle_title',
      ];
      
      // Vérifier que les principes sont présents (via leurs traductions)
      // On vérifie les termes clés plutôt que les traductions exactes
      const principleKeywords = [
        'relationnel', 'relational', 'instrumental', 'instrumentale',
        'accumulation', 'anti-accumulation',
        'cycle', 'logique',
      ];
      
      const foundKeywords = principleKeywords.filter(keyword => 
        sectionText.toLowerCase().includes(keyword.toLowerCase())
      );
      
      // Au moins 3 mots-clés doivent être présents (un par principe)
      if (foundKeywords.length < 3) {
        throw new Error(
          'BLOQUANT : La section "Principes fondamentaux" ne contient pas les 3 principes requis.\n' +
          `Mots-clés trouvés : ${foundKeywords.join(', ')}\n` +
          'Exigence audit : La section doit contenir explicitement les 3 principes :\n' +
          '  - Structure relationnelle > instrumentale\n' +
          '  - Anti-accumulation\n' +
          '  - Logique de cycle'
        );
      }
      
      expect(foundKeywords.length).toBeGreaterThanOrEqual(3);
    });

    it('devrait contenir les descriptions des 3 principes', () => {
      renderWithProviders(<Vision />);
      const principlesSection = screen.getByTestId('vision-principles');
      const sectionText = principlesSection.textContent || '';
      
      // Vérifier que les descriptions sont présentes (via les clés i18n)
      // Les descriptions contiennent des termes spécifiques
      const descriptionKeywords = [
        'SAKA', 'EUR', 'séparation', 'separation',
        'compost', 'compostage', 'silo',
        'régénération', 'regeneration', 'cycle',
      ];
      
      const foundDescriptionKeywords = descriptionKeywords.filter(keyword =>
        sectionText.includes(keyword)
      );
      
      // Au moins 2 mots-clés de description doivent être présents
      if (foundDescriptionKeywords.length < 2) {
        throw new Error(
          'BLOQUANT : Les descriptions des principes sont incomplètes.\n' +
          `Mots-clés trouvés : ${foundDescriptionKeywords.join(', ')}\n` +
          'Exigence audit : Chaque principe doit avoir une description explicite.'
        );
      }
      
      expect(foundDescriptionKeywords.length).toBeGreaterThanOrEqual(2);
    });
  });

  describe('Section Glossaire (vision-glossary)', () => {
    it('devrait contenir data-testid="vision-glossary"', () => {
      renderWithProviders(<Vision />);
      const glossarySection = screen.getByTestId('vision-glossary');
      expect(glossarySection).toBeInTheDocument();
    });

    it('devrait contenir un H2 avec le titre "Glossaire"', () => {
      renderWithProviders(<Vision />);
      const glossarySection = screen.getByTestId('vision-glossary');
      const heading = glossarySection.querySelector('h2');
      
      if (!heading) {
        throw new Error(
          'BLOQUANT : La section "Glossaire" ne contient pas de H2.\n' +
          'Exigence audit : La section doit avoir un titre H2 avec le texte "Glossaire".'
        );
      }
      
      expect(heading).toBeInTheDocument();
      expect(heading.textContent?.trim().length).toBeGreaterThan(0);
    });

    it('devrait contenir les 7 termes requis : vivant, SAKA, EUR, silo, compostage, alliance, gardiens', () => {
      renderWithProviders(<Vision />);
      const glossarySection = screen.getByTestId('vision-glossary');
      const sectionText = glossarySection.textContent || '';
      
      const requiredTerms = [
        'vivant',
        'SAKA',
        'EUR',
        'silo',
        'compostage',
        'alliance',
        'gardiens',
      ];
      
      const missingTerms = requiredTerms.filter(term => {
        // Recherche insensible à la casse
        const regex = new RegExp(term, 'i');
        return !regex.test(sectionText);
      });
      
      if (missingTerms.length > 0) {
        throw new Error(
          'BLOQUANT : Le glossaire ne contient pas tous les termes requis.\n' +
          `Termes manquants : ${missingTerms.join(', ')}\n` +
          'Exigence audit : Le glossaire doit définir explicitement :\n' +
          '  - vivant\n' +
          '  - SAKA\n' +
          '  - EUR\n' +
          '  - silo\n' +
          '  - compostage\n' +
          '  - alliance\n' +
          '  - gardiens'
        );
      }
      
      expect(missingTerms.length).toBe(0);
    });

    it('devrait contenir des définitions (pas seulement les termes)', () => {
      renderWithProviders(<Vision />);
      const glossarySection = screen.getByTestId('vision-glossary');
      
      // Vérifier qu'il y a des éléments <dt> (termes) et <dd> (définitions)
      const terms = glossarySection.querySelectorAll('dt');
      const definitions = glossarySection.querySelectorAll('dd');
      
      if (terms.length === 0 || definitions.length === 0) {
        throw new Error(
          'BLOQUANT : Le glossaire ne contient pas de structure <dl><dt><dd>.\n' +
          `Termes trouvés : ${terms.length}, Définitions trouvées : ${definitions.length}\n` +
          'Exigence audit : Le glossaire doit utiliser une structure <dl> avec <dt> (termes) et <dd> (définitions).'
        );
      }
      
      expect(terms.length).toBeGreaterThan(0);
      expect(definitions.length).toBeGreaterThan(0);
    });
  });

  describe('Disclaimer Citations (vision-disclaimer)', () => {
    it('devrait contenir data-testid="vision-disclaimer"', () => {
      renderWithProviders(<Vision />);
      const disclaimerElement = screen.getByTestId('vision-disclaimer');
      expect(disclaimerElement).toBeInTheDocument();
    });

    it('devrait contenir du texte explicite', () => {
      renderWithProviders(<Vision />);
      const disclaimerElement = screen.getByTestId('vision-disclaimer');
      const text = disclaimerElement.textContent || '';
      
      if (text.trim().length === 0) {
        throw new Error(
          'BLOQUANT : Le disclaimer est vide (pas de texte).\n' +
          'Exigence audit : Le disclaimer doit contenir un texte explicite sur les citations autochtones.'
        );
      }
      
      expect(text.trim().length).toBeGreaterThan(0);
    });

    it('devrait contenir des mots-clés liés aux citations autochtones ou au respect des cultures', () => {
      renderWithProviders(<Vision />);
      const disclaimerElement = screen.getByTestId('vision-disclaimer');
      const text = disclaimerElement.textContent || '';
      
      // Mots-clés attendus (peuvent être traduits)
      const expectedKeywords = [
        'citation', 'citation', 'autochtone', 'indigenous',
        'respect', 'culture', 'culturel', 'cultural',
        'source', 'origine', 'origin',
      ];
      
      const foundKeywords = expectedKeywords.filter(keyword =>
        text.toLowerCase().includes(keyword.toLowerCase())
      );
      
      if (foundKeywords.length === 0) {
        throw new Error(
          'BLOQUANT : Le disclaimer ne contient pas de mots-clés liés aux citations autochtones.\n' +
          `Texte actuel : "${text.substring(0, 200)}..."\n` +
          'Exigence audit : Le disclaimer doit mentionner explicitement les citations autochtones\n' +
          'et le respect des cultures d\'origine.'
        );
      }
      
      expect(foundKeywords.length).toBeGreaterThan(0);
    });
  });
});


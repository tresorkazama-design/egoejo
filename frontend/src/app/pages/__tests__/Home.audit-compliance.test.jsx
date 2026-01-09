import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '../../../test/test-utils';
import Home from '../Home';

// Mock HeroSorgho pour éviter les problèmes avec Three.js dans les tests
vi.mock('../../components/HeroSorgho', () => ({
  default: () => <div data-testid="hero-sorgho" style={{ minHeight: '70svh' }} />,
}));

describe('Home - Audit Compliance (BLOQUANTS)', () => {
  beforeEach(() => {
    // Mock window.matchMedia pour HeroSorgho
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation(query => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
  });

  describe('B7) Note explicite SAKA/EUR', () => {
    it('devrait contenir une note explicite SAKA/EUR (data-testid ou texte)', () => {
      const { container } = renderWithProviders(<Home />);
      
      // Chercher par data-testid
      const sakaEurNote = container.querySelector('[data-testid="home-saka-eur-note"]');
      
      if (!sakaEurNote) {
        // Chercher par texte dans la section "Soutenir"
        const soutenirSection = container.querySelector('#soutenir');
        if (soutenirSection) {
          const soutenirText = soutenirSection.textContent || '';
          const hasSakaEurMention = /SAKA|relationnel|relational|EUR.*instrumental|instrumental.*EUR/i.test(soutenirText);
          
          if (!hasSakaEurMention) {
            throw new Error(
              'BLOQUANT : La note explicite SAKA/EUR est absente de la page Accueil.\n' +
              'Exigence audit : Accueil doit contenir une note explicite distinguant SAKA (relationnel) et EUR (instrumental).\n' +
              'Ajouter data-testid="home-saka-eur-note" ou inclure le texte dans la section #soutenir.'
            );
          }
        } else {
          throw new Error(
            'BLOQUANT : La section #soutenir est absente, impossible de vérifier la note SAKA/EUR.'
          );
        }
      }
      
      // Vérifier que la note est visible
      expect(sakaEurNote || container.querySelector('#soutenir')).toBeTruthy();
    });

    it('ne devrait PAS contenir de conversion ou équivalence monétaire SAKA/EUR', () => {
      const { container } = renderWithProviders(<Home />);
      const pageContent = container.textContent || '';
      
      const forbiddenPatterns = [
        /SAKA.*=.*EUR|EUR.*=.*SAKA/i,
        /1.*SAKA.*=.*\d+.*EUR|\d+.*EUR.*=.*1.*SAKA/i,
        /convertir.*SAKA.*EUR|convert.*SAKA.*EUR/i,
        /équivalent.*monétaire|monetary.*equivalent/i,
      ];
      
      for (const pattern of forbiddenPatterns) {
        if (pattern.test(pageContent)) {
          throw new Error(
            `BLOQUANT : Conversion ou équivalence monétaire SAKA/EUR détectée.\n` +
            `Pattern interdit : ${pattern.source}\n` +
            `Exigence audit : Aucune conversion ou équivalence monétaire ne doit être suggérée.`
          );
        }
      }
    });
  });

  describe('B8) Texte "100% des dons" corrigé', () => {
    it('devrait contenir "100% des dons nets" ou formulation équivalente', () => {
      const { container } = renderWithProviders(<Home />);
      
      // Chercher dans la section "Soutenir"
      const soutenirSection = container.querySelector('#soutenir');
      if (!soutenirSection) {
        throw new Error('BLOQUANT : La section #soutenir est absente.');
      }
      
      const soutenirText = soutenirSection.textContent || '';
      
      // Vérifier que le texte contient "100%" ET "dons"
      const has100Percent = /100\s*%/.test(soutenirText);
      const hasDons = /don/i.test(soutenirText);
      
      if (!has100Percent || !hasDons) {
        // Si le texte n'existe pas, le test passe (pas de promesse trompeuse)
        return;
      }
      
      // Vérifier que le texte contient "nets" ou "après frais" ou formulation équivalente
      const correctedPatterns = [
        /100\s*%.*dons.*nets/i,
        /100\s*%.*dons.*après.*frais/i,
        /100\s*%.*dons.*net/i,
        /100\s*%.*dons.*after.*fees/i,
        /100\s*%.*dons.*frais.*plateforme/i,
        /100\s*%.*dons.*platform.*fees/i,
      ];
      
      const isCorrected = correctedPatterns.some(pattern => pattern.test(soutenirText));
      
      // Vérifier aussi par data-testid si la note existe
      const donationClaim = container.querySelector('[data-testid="home-donation-claim"]');
      if (donationClaim) {
        const claimText = donationClaim.textContent || '';
        const isCorrectedInClaim = correctedPatterns.some(pattern => pattern.test(claimText));
        
        if (!isCorrectedInClaim && !isCorrected) {
          throw new Error(
            'BLOQUANT : Le texte "100% des dons" n\'est pas corrigé.\n' +
            'Exigence audit : Le texte doit être "100% des dons nets (après frais de plateforme)"\n' +
            'ou formulation équivalente non trompeuse.\n' +
            `Texte actuel : "${soutenirText.substring(0, 200)}..."`
          );
        }
      } else if (!isCorrected) {
        throw new Error(
          'BLOQUANT : Le texte "100% des dons" n\'est pas corrigé.\n' +
          'Exigence audit : Le texte doit être "100% des dons nets (après frais de plateforme)"\n' +
          'ou formulation équivalente non trompeuse.\n' +
          `Texte actuel : "${soutenirText.substring(0, 200)}..."`
        );
      }
    });
  });
});


import { describe, it, expect } from 'vitest';
import { renderWithProviders, screen } from '../../../test/test-utils';
import Home from '../Home';

/**
 * Tests unitaires BLOQUANTS - Page Accueil
 * 
 * Vérifie la conformité éditoriale et structurelle de la page Accueil :
 * - Présence et contenu de la section donation
 * - Présence et contenu de la note SAKA/EUR
 * 
 * Ces tests sont BLOQUANTS et échouent explicitement si les exigences
 * de l'audit quadripartite ne sont pas respectées.
 */

describe('Home - Compliance Tests (BLOQUANTS)', () => {
  describe('Section Donation (home-donation-claim)', () => {
    it('devrait contenir data-testid="home-donation-claim"', () => {
      renderWithProviders(<Home />);
      const donationClaim = screen.getByTestId('home-donation-claim');
      expect(donationClaim).toBeInTheDocument();
    });

    it('devrait contenir "dons nets" ou formulation équivalente mentionnant frais', () => {
      renderWithProviders(<Home />);
      const donationClaim = screen.getByTestId('home-donation-claim');
      const text = donationClaim.textContent || '';
      
      // Patterns acceptables : "dons nets", "après frais", "after fees", etc.
      const acceptablePatterns = [
        /dons?\s*nets?/i,
        /après\s*frais/i,
        /after\s*fees/i,
        /frais\s*plateforme/i,
        /platform\s*fees/i,
        /net\s*des?\s*dons?/i,
      ];
      
      const hasAcceptableText = acceptablePatterns.some(pattern => pattern.test(text));
      
      if (!hasAcceptableText) {
        throw new Error(
          'BLOQUANT : Le texte de donation ne contient pas "dons nets" ou mention de frais.\n' +
          `Texte actuel : "${text.substring(0, 200)}..."\n` +
          'Exigence audit : Le texte doit être "100% des dons nets (après frais de plateforme)"\n' +
          'ou formulation équivalente non trompeuse.'
        );
      }
      
      expect(hasAcceptableText).toBe(true);
    });

    it('ne devrait PAS contenir "100% des dons" sans mention de frais ou "nets"', () => {
      renderWithProviders(<Home />);
      const donationClaim = screen.getByTestId('home-donation-claim');
      const text = donationClaim.textContent || '';
      
      // Pattern interdit : "100% des dons" suivi d'un espace puis autre chose que "nets" ou mention de frais
      // On cherche "100% des dons" suivi d'un espace puis quelque chose qui n'est PAS "nets" ou "après" ou "frais"
      const forbiddenPattern = /100\s*%\s*des?\s*dons\s+(?!nets?|après|after|frais|fees|platform)/i;
      
      if (forbiddenPattern.test(text)) {
        throw new Error(
          'BLOQUANT : Le texte contient "100% des dons" sans "nets" ou mention de frais.\n' +
          `Texte actuel : "${text.substring(0, 200)}..."\n` +
          'Exigence audit : Le texte doit être "100% des dons nets (après frais de plateforme)"\n' +
          'ou formulation équivalente non trompeuse.'
        );
      }
      
      expect(forbiddenPattern.test(text)).toBe(false);
    });
  });

  describe('Note SAKA/EUR (home-saka-eur-note)', () => {
    it('devrait contenir data-testid="home-saka-eur-note"', () => {
      renderWithProviders(<Home />);
      const sakaEurNote = screen.getByTestId('home-saka-eur-note');
      expect(sakaEurNote).toBeInTheDocument();
    });

    it('devrait contenir SAKA et EUR dans le texte', () => {
      renderWithProviders(<Home />);
      const sakaEurNote = screen.getByTestId('home-saka-eur-note');
      const text = sakaEurNote.textContent || '';
      
      const hasSaka = /SAKA/i.test(text);
      const hasEur = /EUR/i.test(text);
      
      if (!hasSaka || !hasEur) {
        throw new Error(
          'BLOQUANT : La note SAKA/EUR ne contient pas SAKA et EUR.\n' +
          `Texte actuel : "${text.substring(0, 200)}..."\n` +
          'Exigence audit : La page Accueil doit contenir une note explicite distinguant\n' +
          'SAKA (structure relationnelle) et EUR (structure instrumentale).'
        );
      }
      
      expect(hasSaka).toBe(true);
      expect(hasEur).toBe(true);
    });

    it('ne devrait PAS contenir de termes de conversion ou équivalence monétaire', () => {
      renderWithProviders(<Home />);
      const sakaEurNote = screen.getByTestId('home-saka-eur-note');
      const text = sakaEurNote.textContent || '';
      
      // Patterns interdits : conversion, équivalence monétaire, valeur monétaire
      const forbiddenPatterns = [
        /conversion/i,
        /équivalence\s*monétaire/i,
        /valeur\s*monétaire/i,
        /monétisation/i,
        /convertir/i,
        /équivalent/i,
        /SAKA.*EUR.*=|EUR.*SAKA.*=/i, // Équivalence explicite
      ];
      
      const hasForbidden = forbiddenPatterns.some(pattern => pattern.test(text));
      
      if (hasForbidden) {
        throw new Error(
          'BLOQUANT : La note SAKA/EUR contient des termes de conversion ou équivalence monétaire.\n' +
          `Texte actuel : "${text.substring(0, 200)}..."\n` +
          'Exigence audit : La note doit distinguer SAKA et EUR sans suggérer de conversion\n' +
          'ou d\'équivalence monétaire.'
        );
      }
      
      expect(hasForbidden).toBe(false);
    });
  });

  describe('Section Soutenir (home-section-soutenir)', () => {
    it('devrait contenir data-testid="home-section-soutenir" et id="soutenir"', () => {
      renderWithProviders(<Home />);
      const soutenirSection = screen.getByTestId('home-section-soutenir');
      expect(soutenirSection).toBeInTheDocument();
      
      // Vérifier que l'id est aussi présent
      expect(soutenirSection).toHaveAttribute('id', 'soutenir');
    });
  });
});


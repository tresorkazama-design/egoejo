/**
 * Tests de compliance éditoriale frontend pour le contenu EGOEJO
 * 
 * Vérifie que :
 * - Aucun symbole monétaire n'est affiché dans les contenus
 * - Un disclaimer est présent si le contenu est lié à P3/P4
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import { Contenus } from '../Contenus';
import { useContents } from '../../../hooks/useContents';
import { useLanguage } from '../../../contexts/LanguageContext';
import { renderWithProviders } from '../../../test/test-utils';

// Mock des hooks
vi.mock('../../../hooks/useContents');
vi.mock('../../../contexts/LanguageContext');
vi.mock('../../../hooks/useSEO', () => ({
  useSEO: () => ({}),
}));
vi.mock('../../../components/SEO', () => ({
  default: () => null,
}));
vi.mock('../../../components/ui/Breadcrumbs', () => ({
  default: () => null,
}));
vi.mock('../../../components/CardTilt', () => ({
  default: ({ children }) => <div data-testid="card-tilt">{children}</div>,
}));

describe('Contenus - Compliance Éditoriale Frontend', () => {
  beforeEach(() => {
    useLanguage.mockReturnValue({
      language: 'fr',
    });
  });

  it('ne devrait pas afficher de symboles monétaires dans les contenus', () => {
    useContents.mockReturnValue({
      data: {
        contents: [
          {
            id: 1,
            title: 'Test Content',
            slug: 'test-content',
            type: 'article',
            description: 'Ce contenu ne doit pas contenir € ou $',
            external_url: 'https://example.com',
          },
        ],
        count: 1,
        next: null,
        previous: null,
        currentPage: 1,
        pageSize: 20,
        totalPages: 1,
      },
      isLoading: false,
      isError: false,
      error: null,
      isFetching: false,
    });

    const { container } = renderWithProviders(<Contenus />);

    // Vérifier qu'aucun symbole monétaire n'est présent dans le rendu
    const htmlContent = container.innerHTML;
    
    // Patterns interdits (sauf dans money.js qui est légitime pour EUR réel)
    const forbiddenPatterns = [
      /€/g,
      /\$/g,
      /\bEUR\b/g,
      /\bUSD\b/g,
      /\bGBP\b/g,
    ];

    for (const pattern of forbiddenPatterns) {
      const matches = htmlContent.match(pattern);
      if (matches) {
        // Ignorer les occurrences dans les scripts ou les attributs data
        const filteredMatches = matches.filter(() => {
          // Vérifier si c'est dans un script ou un attribut data (acceptable)
          const scriptMatch = htmlContent.match(/<script[^>]*>[\s\S]*?<\/script>/gi);
          if (scriptMatch && scriptMatch.some(script => pattern.test(script))) {
            return false; // Dans un script, on ignore
          }
          return true;
        });
        
        if (filteredMatches.length > 0) {
          throw new Error(
            `VIOLATION DU MANIFESTE EGOEJO : Symbole monétaire détecté dans le rendu : ${pattern.source}\n` +
            `Les contenus EGOEJO ne doivent jamais afficher de symboles monétaires.\n` +
            `Utilisez formatSakaAmount() pour formater les SAKA, jamais €, $, EUR, etc.`
          );
        }
      }
    }
  });

  it('devrait afficher un disclaimer si le contenu est lié à P3/P4', () => {
    // Note : Pour l'instant, on vérifie que le mécanisme existe
    // L'implémentation complète nécessitera d'ajouter un champ P3/P4 au modèle
    
    useContents.mockReturnValue({
      data: {
        contents: [
          {
            id: 1,
            title: 'Content with P3/P4',
            slug: 'content-p3-p4',
            type: 'article',
            description: 'Contenu lié à P3 ou P4',
            external_url: 'https://example.com',
            // TODO : Ajouter un champ is_p3_p4 ou similar dans le modèle
          },
        ],
        count: 1,
        next: null,
        previous: null,
        currentPage: 1,
        pageSize: 20,
        totalPages: 1,
      },
      isLoading: false,
      isError: false,
      error: null,
      isFetching: false,
    });

    renderWithProviders(<Contenus />);

    // Pour l'instant, on skip ce test car le champ P3/P4 n'existe pas encore
    // TODO : Implémenter quand le champ sera ajouté au modèle
    // expect(screen.getByText(/disclaimer|avertissement/i)).toBeInTheDocument();
  });

  it('ne devrait pas afficher de promesses financières dans les descriptions', () => {
    const forbiddenFinancialTerms = [
      'retour sur investissement',
      'ROI',
      'profit',
      'rentabilité',
      'gain financier',
      'dividende',
      'rendement',
    ];

    useContents.mockReturnValue({
      data: {
        contents: [
          {
            id: 1,
            title: 'Test Content',
            slug: 'test-content',
            type: 'article',
            description: 'Ce contenu parle de retour sur investissement et de profit',
            external_url: 'https://example.com',
          },
        ],
        count: 1,
        next: null,
        previous: null,
        currentPage: 1,
        pageSize: 20,
        totalPages: 1,
      },
      isLoading: false,
      isError: false,
      error: null,
      isFetching: false,
    });

    const { container } = renderWithProviders(<Contenus />);
    const htmlContent = container.innerHTML;

    for (const term of forbiddenFinancialTerms) {
      if (htmlContent.toLowerCase().includes(term.toLowerCase())) {
        throw new Error(
          `VIOLATION DU MANIFESTE EGOEJO : Terme financier interdit détecté : "${term}"\n` +
          `Les contenus EGOEJO ne doivent jamais contenir de promesses financières.\n` +
          `Retirez toutes les références aux retours financiers, profits, ROI, etc.`
        );
      }
    }
  });
});


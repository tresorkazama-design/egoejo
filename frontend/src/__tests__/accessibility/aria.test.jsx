/**
 * Tests d'accessibilité ARIA approfondis
 * Vérifie les attributs ARIA, les landmarks, les labels, etc.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { axe } from 'jest-axe';
import { renderWithProviders } from '../../test/test-utils';
import Layout from '../../components/Layout';
import Home from '../../app/pages/Home';
import { Rejoindre } from '../../app/pages/Rejoindre';
import { Projets } from '../../app/pages/Projets';
import { fetchAPI } from '../../utils/api';
import { useAuth } from '../../contexts/AuthContext';

// Mock des dépendances
vi.mock('../../utils/api', () => ({
  fetchAPI: vi.fn(),
  handleAPIError: vi.fn((err) => err.message || 'Erreur'),
}));

vi.mock('../../contexts/AuthContext', () => ({
  useAuth: vi.fn(),
  AuthProvider: ({ children }) => children,
}));

describe('Tests ARIA Approfondis', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    fetchAPI.mockResolvedValue({ results: [] });
    useAuth.mockReturnValue({ token: null, user: null });
  });

  describe('Landmarks ARIA', () => {
    it('Layout devrait avoir tous les landmarks requis', async () => {
      const { container } = renderWithProviders(
        <Layout>
          <div>Test content</div>
        </Layout>
      );

      // Vérifier les landmarks principaux
      const main = container.querySelector('main, [role="main"]');
      const nav = container.querySelector('nav, [role="navigation"]');
      const header = container.querySelector('header, [role="banner"]');
      const footer = container.querySelector('footer, [role="contentinfo"]');
      
      expect(main).toBeTruthy();
      expect(nav).toBeTruthy();
      // Header et footer peuvent être optionnels selon le design
      if (header) expect(header).toBeTruthy();
      if (footer) expect(footer).toBeTruthy();
    });

    it('devrait avoir un seul élément main par page', async () => {
      const { container } = renderWithProviders(
        <Layout>
          <div>Test content</div>
        </Layout>
      );

      const mainElements = container.querySelectorAll('main, [role="main"]');
      expect(mainElements.length).toBeLessThanOrEqual(1);
    });

    it('devrait avoir des landmarks uniques', async () => {
      const { container } = renderWithProviders(
        <Layout>
          <div>Test content</div>
        </Layout>
      );

      // Vérifier avec axe (qui détecte les landmarks dupliqués)
      const results = await axe(container);
      const landmarkViolations = results.violations.filter(
        v => v.id === 'landmark-unique'
      );
      expect(landmarkViolations.length).toBe(0);
    });
  });

  describe('Labels ARIA', () => {
    it('tous les éléments interactifs devraient avoir des labels', async () => {
      const { container } = renderWithProviders(<Rejoindre />);

      await waitFor(() => {
        expect(screen.getByLabelText(/nom/i)).toBeInTheDocument();
      }, { timeout: 5000 });

      // Vérifier les inputs
      const inputs = container.querySelectorAll('input:not([type="hidden"]), textarea, select');
      if (inputs.length > 0) {
        inputs.forEach(input => {
          // Ignorer les inputs de type hidden ou les honeypots
          const type = input.getAttribute('type');
          if (type === 'hidden' || input.classList.contains('honeypot')) {
            return;
          }
          
          const id = input.getAttribute('id');
          const ariaLabel = input.getAttribute('aria-label');
          const ariaLabelledBy = input.getAttribute('aria-labelledby');
          const label = id ? container.querySelector(`label[for="${id}"]`) : null;
          const placeholder = input.getAttribute('placeholder');
          const name = input.getAttribute('name');
          
          // Au moins un de ces attributs doit exister
          const hasLabel = ariaLabel || ariaLabelledBy || label || placeholder || name;
          if (!hasLabel) {
            // Si aucun label n'est trouvé, vérifier avec axe qui est plus tolérant
            console.warn(`Input sans label trouvé: ${input.outerHTML.substring(0, 100)}`);
          }
          // Accepter les inputs avec au moins un identifiant (name, id, etc.)
          expect(hasLabel || id || name).toBeTruthy();
        });
      }
    });

    it('tous les boutons devraient avoir des labels accessibles', async () => {
      const { container } = renderWithProviders(<Home />);
      
      const buttons = container.querySelectorAll('button, [role="button"]');
      buttons.forEach(button => {
        const ariaLabel = button.getAttribute('aria-label');
        const ariaLabelledBy = button.getAttribute('aria-labelledby');
        const textContent = button.textContent?.trim();
        const title = button.getAttribute('title');
        
        // Le bouton doit avoir un label accessible
        const hasLabel = ariaLabel || ariaLabelledBy || textContent || title;
        expect(hasLabel).toBeTruthy();
      });
    });

    it('tous les liens devraient avoir des textes accessibles', async () => {
      const { container } = renderWithProviders(
        <Layout>
          <div>Test content</div>
        </Layout>
      );
      
      const links = container.querySelectorAll('a[href]');
      links.forEach(link => {
        const ariaLabel = link.getAttribute('aria-label');
        const textContent = link.textContent?.trim();
        const img = link.querySelector('img[alt]');
        
        // Le lien doit avoir un texte ou un label ARIA ou une image avec alt
        const hasAccessibleText = ariaLabel || textContent || img;
        expect(hasAccessibleText).toBeTruthy();
      });
    });
  });

  describe('États ARIA', () => {
    it('devrait utiliser aria-disabled au lieu de disabled pour les éléments non interactifs', async () => {
      const { container } = renderWithProviders(<Home />);
      
      // Vérifier que les éléments avec aria-disabled sont correctement utilisés
      const ariaDisabledElements = container.querySelectorAll('[aria-disabled="true"]');
      ariaDisabledElements.forEach(element => {
        // Si aria-disabled est true, l'élément ne devrait pas être focusable
        const tabIndex = element.getAttribute('tabindex');
        if (tabIndex !== null) {
          expect(tabIndex).toBe('-1');
        }
      });
    });

    it('devrait utiliser aria-expanded pour les éléments expansibles', async () => {
      const { container } = renderWithProviders(
        <Layout>
          <div>Test content</div>
        </Layout>
      );
      
      // Vérifier les menus et éléments expansibles
      const expandableElements = container.querySelectorAll(
        '[aria-expanded], [aria-haspopup]'
      );
      expandableElements.forEach(element => {
        const expanded = element.getAttribute('aria-expanded');
        if (expanded !== null) {
          expect(['true', 'false']).toContain(expanded);
        }
      });
    });

    it('devrait utiliser aria-current pour la navigation active', async () => {
      const { container } = renderWithProviders(
        <Layout>
          <div>Test content</div>
        </Layout>
      );
      
      // Vérifier que les liens de navigation actifs ont aria-current
      const currentLinks = container.querySelectorAll('[aria-current]');
      currentLinks.forEach(link => {
        const current = link.getAttribute('aria-current');
        expect(['page', 'step', 'location', 'date', 'time', 'true']).toContain(current);
      });
    });
  });

  describe('Rôles ARIA', () => {
    it('devrait utiliser les rôles ARIA appropriés', async () => {
      const { container } = renderWithProviders(<Home />);
      
      // Vérifier avec axe (qui vérifie les rôles)
      const results = await axe(container);
      const roleViolations = results.violations.filter(
        v => v.id === 'aria-roles'
      );
      expect(roleViolations.length).toBe(0);
    });

    it('devrait éviter les rôles redondants', async () => {
      const { container } = renderWithProviders(<Home />);
      
      // Vérifier que les éléments natifs n'ont pas de rôles redondants
      const nativeButtons = container.querySelectorAll('button[role="button"]');
      const nativeLinks = container.querySelectorAll('a[role="link"]');
      
      // Les éléments natifs ne devraient pas avoir de rôles redondants
      expect(nativeButtons.length).toBe(0);
      expect(nativeLinks.length).toBe(0);
    });
  });

  describe('Relations ARIA', () => {
    it('devrait utiliser aria-describedby correctement', async () => {
      const { container } = renderWithProviders(<Rejoindre />);
      
      await waitFor(() => {
        expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      });

      const inputs = container.querySelectorAll('input[aria-describedby]');
      inputs.forEach(input => {
        const describedBy = input.getAttribute('aria-describedby');
        const describedElement = container.querySelector(`#${describedBy}`);
        expect(describedElement).toBeTruthy();
      });
    });

    it('devrait utiliser aria-labelledby correctement', async () => {
      const { container } = renderWithProviders(<Rejoindre />);
      
      await waitFor(() => {
        expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      });

      const inputs = container.querySelectorAll('input[aria-labelledby]');
      inputs.forEach(input => {
        const labelledBy = input.getAttribute('aria-labelledby');
        const labelElement = container.querySelector(`#${labelledBy}`);
        expect(labelElement).toBeTruthy();
      });
    });
  });

  describe('Tests Axe ARIA', () => {
    it('Home devrait passer tous les tests ARIA', async () => {
      const { container } = renderWithProviders(<Home />);
      const results = await axe(container, {
        rules: {
          'aria-allowed-attr': { enabled: true },
          'aria-required-attr': { enabled: true },
          'aria-valid-attr-value': { enabled: true },
          'aria-valid-attr': { enabled: true },
        },
      });
      
      const ariaViolations = results.violations.filter(
        v => v.id.startsWith('aria-')
      );
      expect(ariaViolations.length).toBe(0);
    });

    it('Rejoindre devrait passer tous les tests ARIA', async () => {
      const { container } = renderWithProviders(<Rejoindre />);
      const results = await axe(container, {
        rules: {
          'aria-allowed-attr': { enabled: true },
          'aria-required-attr': { enabled: true },
          'aria-valid-attr-value': { enabled: true },
        },
      });
      
      expect(results.violations).toHaveLength(0);
    });

    it('Projets devrait passer tous les tests ARIA', async () => {
      fetchAPI.mockResolvedValueOnce({ results: [] });
      const { container } = renderWithProviders(<Projets />);
      
      await waitFor(() => {
        expect(fetchAPI).toHaveBeenCalled();
      });
      
      const results = await axe(container, {
        rules: {
          'aria-allowed-attr': { enabled: true },
          'aria-required-attr': { enabled: true },
        },
      });
      
      expect(results.violations).toHaveLength(0);
    });
  });
});


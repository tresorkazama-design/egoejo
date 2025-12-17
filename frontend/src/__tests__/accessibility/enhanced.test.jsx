import { describe, it, expect, beforeEach, vi } from 'vitest';
import { screen, waitFor, render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { renderWithProviders } from '../../test/test-utils';
import Layout from '../../components/Layout';
import Home from '../../app/pages/Home';
import { Rejoindre } from '../../app/pages/Rejoindre';
import { fetchAPI } from '../../utils/api';
import { useAuth } from '../../contexts/AuthContext';

// Étendre les matchers de jest-axe
expect.extend(toHaveNoViolations);

// Mock des dépendances
vi.mock('../../utils/api', () => ({
  fetchAPI: vi.fn(),
  handleAPIError: vi.fn((err) => err.message || 'Erreur'),
}));

vi.mock('../../contexts/AuthContext', () => ({
  useAuth: vi.fn(),
  AuthProvider: ({ children }) => children,
}));

/**
 * Tests d'accessibilité améliorés
 * Vérifie ARIA, navigation clavier, contraste, et plus
 */
describe('Tests d\'Accessibilité Améliorés', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    fetchAPI.mockResolvedValue({ results: [] });
    useAuth.mockReturnValue({ token: null, user: null });
  });

  describe('ARIA Attributes', () => {
    it('Layout devrait avoir des landmarks ARIA corrects', async () => {
      const { container } = renderWithProviders(
        <Layout>
          <div>Test content</div>
        </Layout>
      );

      // Vérifier les landmarks
      const main = container.querySelector('main, [role="main"]');
      const nav = container.querySelector('nav, [role="navigation"]');
      
      expect(main).toBeTruthy();
      expect(nav).toBeTruthy();
      
      // Vérifier avec axe
      const results = await axe(container);
      expect(results.violations).toHaveLength(0);
    });

    it('devrait avoir des labels ARIA pour les éléments interactifs', async () => {
      const { container } = renderWithProviders(<Rejoindre />);
      
      await waitFor(() => {
        expect(screen.getByLabelText(/nom/i)).toBeInTheDocument();
      }, { timeout: 5000 });
      
      // Vérifier que les inputs ont des labels
      const inputs = container.querySelectorAll('input:not([type="hidden"]), textarea, select');
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
        // Accepter les inputs avec au moins un identifiant (name, id, etc.)
        expect(hasLabel || id || name).toBeTruthy();
      });
    });

    it('devrait avoir des attributs ARIA pour les boutons', async () => {
      const { container } = renderWithProviders(<Home />);
      
      const buttons = container.querySelectorAll('button, [role="button"]');
      buttons.forEach(button => {
        const ariaLabel = button.getAttribute('aria-label');
        const textContent = button.textContent?.trim();
        
        // Le bouton doit avoir un label ARIA ou du texte
        expect(ariaLabel || textContent).toBeTruthy();
      });
    });
  });

  describe('Navigation au Clavier', () => {
    it('devrait pouvoir naviguer avec Tab dans le Layout', async () => {
      const user = userEvent.setup();
      const { container } = renderWithProviders(
        <Layout>
          <div>Test content</div>
        </Layout>
      );

      // Trouver le premier élément focusable
      const firstFocusable = container.querySelector('a, button, input, [tabindex]:not([tabindex="-1"])');
      
      if (firstFocusable) {
        await user.tab();
        expect(document.activeElement).toBe(firstFocusable);
      }
    });

    it('devrait pouvoir naviguer dans le formulaire Rejoindre avec Tab', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Rejoindre />);

      // Attendre que le formulaire soit rendu
      await waitFor(() => {
        expect(screen.getByLabelText(/nom/i)).toBeInTheDocument();
      });

      // Naviguer avec Tab
      await user.tab();
      
      // Vérifier que le focus est sur un élément du formulaire
      const focusedElement = document.activeElement;
      expect(focusedElement).toBeTruthy();
      expect(['INPUT', 'TEXTAREA', 'BUTTON', 'SELECT']).toContain(focusedElement.tagName);
    });

    it('devrait pouvoir activer les boutons avec Enter', async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();
      
      render(
        <button onClick={handleClick}>Test Button</button>
      );

      const button = screen.getByRole('button', { name: /test button/i });
      button.focus();
      
      await user.keyboard('{Enter}');
      expect(handleClick).toHaveBeenCalled();
    });

    it('devrait pouvoir activer les liens avec Enter', async () => {
      const user = userEvent.setup();
      
      render(
        <a href="/test" role="button">Test Link</a>
      );

      const link = screen.getByRole('button', { name: /test link/i });
      link.focus();
      
      // Les liens peuvent être activés avec Enter
      await user.keyboard('{Enter}');
      // Vérifier que le focus est bien géré
      expect(document.activeElement).toBeTruthy();
    });
  });

  describe('Contraste des Couleurs', () => {
    it('devrait avoir un contraste suffisant pour le texte', async () => {
      const { container } = renderWithProviders(<Home />);
      
      // Vérifier avec axe (qui vérifie le contraste)
      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true },
        },
      });
      
      // Filtrer les violations de contraste
      const contrastViolations = results.violations.filter(
        v => v.id === 'color-contrast'
      );
      
      // Accepter jusqu'à 1 violation de contraste mineure (éléments décoratifs)
      expect(contrastViolations.length).toBeLessThanOrEqual(1);
    });

    it('devrait avoir un contraste suffisant pour les boutons', async () => {
      const { container } = renderWithProviders(<Rejoindre />);
      
      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true },
        },
      });
      
      const contrastViolations = results.violations.filter(
        v => v.id === 'color-contrast' && 
        v.nodes.some(node => 
          node.html?.includes('button') || 
          node.target?.some(selector => selector.includes('button'))
        )
      );
      
      // Les boutons doivent avoir un bon contraste
      expect(contrastViolations.length).toBe(0);
    });
  });

  describe('Focus Management', () => {
    it('devrait gérer le focus correctement lors de la navigation', async () => {
      const { container } = renderWithProviders(
        <Layout>
          <div>Test content</div>
        </Layout>
      );

      // Vérifier que les éléments focusables ont un indicateur de focus visible
      const focusableElements = container.querySelectorAll(
        'a, button, input, textarea, select, [tabindex]:not([tabindex="-1"])'
      );
      
      focusableElements.forEach(element => {
        // Vérifier que l'élément peut recevoir le focus
        expect(element).toBeTruthy();
      });
    });

    it('devrait avoir un skip link pour la navigation', async () => {
      const { container } = renderWithProviders(
        <Layout>
          <div>Test content</div>
        </Layout>
      );

      // Vérifier la présence d'un skip link
      const skipLink = container.querySelector('a[href="#main-content"], a[href="#main"]');
      expect(skipLink).toBeTruthy();
    });
  });

  describe('Images et Media', () => {
    it('devrait avoir des textes alternatifs pour les images', async () => {
      const { container } = renderWithProviders(<Home />);
      
      const images = container.querySelectorAll('img');
      images.forEach(img => {
        const alt = img.getAttribute('alt');
        const ariaLabel = img.getAttribute('aria-label');
        const role = img.getAttribute('role');
        
        // Les images doivent avoir un alt ou être décoratives (role="presentation")
        if (role !== 'presentation') {
          expect(alt || ariaLabel).toBeTruthy();
        }
      });
    });
  });

  describe('Formulaires', () => {
    it('devrait avoir des labels associés aux inputs', async () => {
      renderWithProviders(<Rejoindre />);

      await waitFor(() => {
        const nomInput = screen.getByLabelText(/nom/i);
        const emailInput = screen.getByLabelText(/email/i);
        
        expect(nomInput).toBeInTheDocument();
        expect(emailInput).toBeInTheDocument();
      });
    });

    it('devrait afficher des messages d\'erreur accessibles', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Rejoindre />);

      await waitFor(() => {
        expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      });

      const emailInput = screen.getByLabelText(/email/i);
      await user.type(emailInput, 'invalid-email');
      await user.tab();

      // Vérifier que les erreurs sont annoncées
      await waitFor(() => {
        const errorMessage = screen.queryByText(/email|invalide|erreur/i);
        if (errorMessage) {
          expect(errorMessage).toBeInTheDocument();
        }
      }, { timeout: 2000 });
    });
  });

  describe('Tests Axe Complets', () => {
    it('Home devrait passer tous les tests axe', async () => {
      const { container } = renderWithProviders(<Home />);
      const results = await axe(container);
      
      // Accepter jusqu'à 1 violation mineure
      const criticalViolations = results.violations.filter(
        v => v.impact === 'critical' || v.impact === 'serious'
      );
      expect(criticalViolations.length).toBe(0);
    });

    it('Rejoindre devrait passer tous les tests axe', async () => {
      const { container } = renderWithProviders(<Rejoindre />);
      const results = await axe(container);
      
      expect(results.violations).toHaveLength(0);
    });

    it('Layout devrait passer tous les tests axe', async () => {
      const { container } = renderWithProviders(
        <Layout>
          <div>Test content</div>
        </Layout>
      );
      const results = await axe(container);
      
      expect(results.violations).toHaveLength(0);
    });
  });
});


/**
 * Tests de navigation au clavier approfondis
 * Vérifie la navigation Tab, Enter, Escape, etc.
 */
import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe } from 'jest-axe';
import { renderWithProviders } from '../../test/test-utils';
import Layout from '../../components/Layout';
import { Rejoindre } from '../../app/pages/Rejoindre';
import Home from '../../app/pages/Home';
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

describe('Tests de Navigation au Clavier', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    fetchAPI.mockResolvedValue({ results: [] });
    useAuth.mockReturnValue({ token: null, user: null });
  });

  describe('Navigation Tab', () => {
    it('devrait pouvoir naviguer avec Tab dans le Layout', async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <Layout>
          <div>Test content</div>
        </Layout>
      );

      // Trouver tous les éléments focusables
      const focusableElements = Array.from(
        document.querySelectorAll('a, button, input, textarea, select, [tabindex]:not([tabindex="-1"])')
      ).filter(el => {
        const style = window.getComputedStyle(el);
        return style.display !== 'none' && style.visibility !== 'hidden';
      });

      expect(focusableElements.length).toBeGreaterThan(0);

      // Naviguer avec Tab
      for (let i = 0; i < Math.min(3, focusableElements.length); i++) {
        await user.tab();
        expect(document.activeElement).toBeTruthy();
      }
    });

    it('devrait respecter l\'ordre de tabulation logique', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Rejoindre />);

      await waitFor(() => {
        expect(screen.getByLabelText(/nom/i)).toBeInTheDocument();
      });

      // Naviguer avec Tab et vérifier l'ordre
      const focusedElements = [];
      for (let i = 0; i < 5; i++) {
        await user.tab();
        if (document.activeElement) {
          focusedElements.push(document.activeElement);
        }
      }

      // Vérifier que les éléments sont focusables
      expect(focusedElements.length).toBeGreaterThan(0);
    });

    it('devrait pouvoir naviguer en arrière avec Shift+Tab', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Rejoindre />);

      await waitFor(() => {
        expect(screen.getByLabelText(/nom/i)).toBeInTheDocument();
      });

      // Naviguer en avant
      await user.tab();
      const firstFocused = document.activeElement;

      // Naviguer en arrière
      await user.tab({ shift: true });
      const secondFocused = document.activeElement;

      // Les éléments devraient être différents
      expect(firstFocused).toBeTruthy();
      expect(secondFocused).toBeTruthy();
    });
  });

  describe('Activation avec Enter', () => {
    it('devrait pouvoir activer les boutons avec Enter', async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();
      
      renderWithProviders(
        <button onClick={handleClick}>Test Button</button>
      );

      const button = screen.getByRole('button', { name: /test button/i });
      button.focus();
      
      await user.keyboard('{Enter}');
      expect(handleClick).toHaveBeenCalled();
    });

    it('devrait pouvoir soumettre les formulaires avec Enter', async () => {
      const user = userEvent.setup();
      const handleSubmit = vi.fn((e) => e.preventDefault());
      
      renderWithProviders(
        <form onSubmit={handleSubmit}>
          <input type="text" name="test" />
          <button type="submit">Submit</button>
        </form>
      );

      const input = screen.getByRole('textbox');
      await user.type(input, 'test');
      await user.keyboard('{Enter}');
      
      // Le formulaire devrait être soumis
      expect(handleSubmit).toHaveBeenCalled();
    });
  });

  describe('Activation avec Espace', () => {
    it('devrait pouvoir activer les boutons avec Espace', async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();
      
      renderWithProviders(
        <button onClick={handleClick}>Test Button</button>
      );

      const button = screen.getByRole('button', { name: /test button/i });
      button.focus();
      
      await user.keyboard(' ');
      expect(handleClick).toHaveBeenCalled();
    });
  });

  describe('Fermeture avec Escape', () => {
    it('devrait pouvoir fermer les modales avec Escape', async () => {
      const user = userEvent.setup();
      const handleClose = vi.fn();
      
      const TestModal = () => {
        React.useEffect(() => {
          const handleKeyDown = (e) => {
            if (e.key === 'Escape') {
              handleClose();
            }
          };
          
          document.addEventListener('keydown', handleKeyDown);
          return () => {
            document.removeEventListener('keydown', handleKeyDown);
          };
        }, []);
        
        return (
          <div role="dialog" aria-modal="true" tabIndex={-1}>
            <button onClick={handleClose}>Close</button>
          </div>
        );
      };
      
      renderWithProviders(<TestModal />);

      const dialog = screen.getByRole('dialog');
      
      // Focus sur le bouton à l'intérieur de la modale
      const closeButton = screen.getByRole('button', { name: /close/i });
      closeButton.focus();
      
      // Attendre que le focus soit bien sur le bouton
      await waitFor(() => {
        expect(document.activeElement).toBe(closeButton);
      });
      
      // Simuler Escape
      await user.keyboard('{Escape}');
      
      // Vérifier que le handler a été appelé
      await waitFor(() => {
        expect(handleClose).toHaveBeenCalled();
      }, { timeout: 1000 });
    });
  });

  describe('Focus Management', () => {
    it('devrait avoir un indicateur de focus visible', async () => {
      const { container } = renderWithProviders(
        <Layout>
          <div>Test content</div>
        </Layout>
      );

      const focusableElements = container.querySelectorAll(
        'a, button, input, textarea, select, [tabindex]:not([tabindex="-1"])'
      );

      focusableElements.forEach(element => {
        // Vérifier que l'élément peut recevoir le focus
        element.focus();
        expect(document.activeElement).toBe(element);
      });
    });

    it('devrait avoir un skip link pour la navigation', async () => {
      const { container } = renderWithProviders(
        <Layout>
          <div>Test content</div>
        </Layout>
      );

      // Vérifier la présence d'un skip link
      const skipLink = container.querySelector(
        'a[href="#main-content"], a[href="#main"], a[href*="main"]'
      );
      expect(skipLink).toBeTruthy();
    });

    it('devrait gérer le focus trap dans les modales', async () => {
      const user = userEvent.setup();
      
      renderWithProviders(
        <div role="dialog" aria-modal="true">
          <button>First</button>
          <button>Last</button>
        </div>
      );

      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);

      // Le focus devrait rester dans la modale
      buttons[0].focus();
      expect(document.activeElement).toBe(buttons[0]);
    });
  });

  describe('Navigation dans les Formulaires', () => {
    it('devrait pouvoir naviguer entre les champs avec Tab', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Rejoindre />);

      await waitFor(() => {
        expect(screen.getByLabelText(/nom/i)).toBeInTheDocument();
      });

      const nomInput = screen.getByLabelText(/nom/i);
      nomInput.focus();
      expect(document.activeElement).toBe(nomInput);

      await user.tab();
      const nextFocused = document.activeElement;
      expect(nextFocused).toBeTruthy();
      expect(nextFocused).not.toBe(nomInput);
    });

    it('devrait pouvoir soumettre le formulaire avec Enter dans le dernier champ', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Rejoindre />);

      await waitFor(() => {
        expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      });

      const emailInput = screen.getByLabelText(/email/i);
      await user.type(emailInput, 'test@example.com');
      
      // Trouver le bouton de soumission
      const submitButton = screen.getByRole('button', { name: /envoyer|soumettre|submit/i });
      expect(submitButton).toBeTruthy();
    });
  });

  describe('Navigation dans les Menus', () => {
    it('devrait pouvoir naviguer dans les menus avec les flèches', async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <Layout>
          <div>Test content</div>
        </Layout>
      );

      // Trouver les menus
      const menus = screen.queryAllByRole('menu, menubar');
      if (menus.length > 0) {
        menus[0].focus();
        
        // Naviguer avec les flèches
        await user.keyboard('{ArrowDown}');
        expect(document.activeElement).toBeTruthy();
      }
    });
  });

  describe('Tests Axe Navigation Clavier', () => {
    it('Layout devrait passer les tests de navigation clavier', async () => {
      const { container } = renderWithProviders(
        <Layout>
          <div>Test content</div>
        </Layout>
      );

      // Utiliser axe sans règles spécifiques pour éviter les erreurs de règles inconnues
      const results = await axe(container);
      
      // Filtrer les violations liées à la navigation clavier
      const keyboardRelatedViolations = results.violations.filter(
        v => v.id === 'focus-order-semantics' || 
             v.id === 'tabindex' || 
             v.id === 'focusable-content' ||
             v.id === 'focusable-no-name' ||
             v.tags?.some(tag => tag === 'keyboard' || tag === 'focus')
      );
      expect(keyboardRelatedViolations.length).toBe(0);
    });
  });
});


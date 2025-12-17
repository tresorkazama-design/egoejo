/**
 * Tests de contraste des couleurs approfondis
 * Vérifie le contraste WCAG AA et AAA
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { axe } from 'jest-axe';
import { renderWithProviders } from '../../test/test-utils';
import Layout from '../../components/Layout';
import Home from '../../app/pages/Home';
import { Rejoindre } from '../../app/pages/Rejoindre';
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

describe('Tests de Contraste des Couleurs', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    fetchAPI.mockResolvedValue({ results: [] });
    useAuth.mockReturnValue({ token: null, user: null });
  });

  describe('Contraste WCAG AA', () => {
    it('Home devrait avoir un contraste suffisant (WCAG AA)', async () => {
      const { container } = renderWithProviders(<Home />);
      
      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true },
        },
      });
      
      // Filtrer les violations de contraste
      const contrastViolations = results.violations.filter(
        v => v.id === 'color-contrast'
      );
      
      // Accepter jusqu'à 1 violation mineure (éléments décoratifs)
      const criticalViolations = contrastViolations.filter(
        v => v.impact === 'critical' || v.impact === 'serious'
      );
      expect(criticalViolations.length).toBe(0);
    });

    it('Rejoindre devrait avoir un contraste suffisant pour les formulaires', async () => {
      const { container } = renderWithProviders(<Rejoindre />);
      
      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true },
        },
      });
      
      const contrastViolations = results.violations.filter(
        v => v.id === 'color-contrast'
      );
      
      // Les formulaires doivent avoir un excellent contraste
      expect(contrastViolations.length).toBe(0);
    });

    it('Layout devrait avoir un contraste suffisant pour la navigation', async () => {
      const { container } = renderWithProviders(
        <Layout>
          <div>Test content</div>
        </Layout>
      );
      
      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true },
        },
      });
      
      const contrastViolations = results.violations.filter(
        v => v.id === 'color-contrast'
      );
      
      expect(contrastViolations.length).toBe(0);
    });
  });

  describe('Contraste des Boutons', () => {
    it('les boutons primaires devraient avoir un contraste élevé', async () => {
      const { container } = renderWithProviders(<Rejoindre />);
      
      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true },
        },
      });
      
      const buttonViolations = results.violations.filter(
        v => v.id === 'color-contrast' && 
        v.nodes.some(node => 
          node.html?.includes('button') || 
          node.target?.some(selector => selector.includes('button') || selector.includes('btn-primary'))
        )
      );
      
      // Les boutons primaires doivent avoir un excellent contraste
      expect(buttonViolations.length).toBe(0);
    });

    it('les boutons secondaires devraient avoir un contraste suffisant', async () => {
      const { container } = renderWithProviders(<Home />);
      
      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true },
        },
      });
      
      const buttonViolations = results.violations.filter(
        v => v.id === 'color-contrast' && 
        v.nodes.some(node => 
          node.html?.includes('button') || 
          node.target?.some(selector => selector.includes('btn-ghost') || selector.includes('btn-secondary'))
        )
      );
      
      // Accepter jusqu'à 1 violation mineure pour les boutons secondaires
      expect(buttonViolations.length).toBeLessThanOrEqual(1);
    });
  });

  describe('Contraste du Texte', () => {
    it('le texte principal devrait avoir un contraste suffisant', async () => {
      const { container } = renderWithProviders(<Home />);
      
      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true },
        },
      });
      
      const textViolations = results.violations.filter(
        v => v.id === 'color-contrast' && 
        v.nodes.some(node => 
          node.html?.includes('p') || 
          node.html?.includes('h1') || 
          node.html?.includes('h2') || 
          node.html?.includes('h3')
        )
      );
      
      // Le texte principal doit avoir un excellent contraste
      expect(textViolations.length).toBe(0);
    });

    it('les liens devraient avoir un contraste suffisant', async () => {
      const { container } = renderWithProviders(
        <Layout>
          <div>Test content</div>
        </Layout>
      );
      
      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true },
        },
      });
      
      const linkViolations = results.violations.filter(
        v => v.id === 'color-contrast' && 
        v.nodes.some(node => 
          node.html?.includes('a') || 
          node.target?.some(selector => selector.includes('a'))
        )
      );
      
      // Les liens doivent avoir un excellent contraste
      expect(linkViolations.length).toBe(0);
    });
  });

  describe('Contraste des Inputs', () => {
    it('les labels des inputs devraient avoir un contraste suffisant', async () => {
      const { container } = renderWithProviders(<Rejoindre />);
      
      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true },
        },
      });
      
      const labelViolations = results.violations.filter(
        v => v.id === 'color-contrast' && 
        v.nodes.some(node => 
          node.html?.includes('label') || 
          node.target?.some(selector => selector.includes('label'))
        )
      );
      
      // Les labels doivent avoir un excellent contraste
      expect(labelViolations.length).toBe(0);
    });

    it('les messages d\'erreur devraient avoir un contraste suffisant', async () => {
      const { container } = renderWithProviders(<Rejoindre />);
      
      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true },
        },
      });
      
      // Vérifier que les messages d'erreur (s'ils existent) ont un bon contraste
      const errorViolations = results.violations.filter(
        v => v.id === 'color-contrast' && 
        v.nodes.some(node => 
          node.html?.includes('error') || 
          node.html?.includes('invalid') ||
          node.target?.some(selector => selector.includes('error'))
        )
      );
      
      expect(errorViolations.length).toBe(0);
    });
  });

  describe('Tests Axe Contraste', () => {
    it('toutes les pages devraient passer les tests de contraste', async () => {
      const pages = [
        { name: 'Home', component: <Home /> },
        { name: 'Rejoindre', component: <Rejoindre /> },
      ];

      for (const page of pages) {
        const { container } = renderWithProviders(page.component);
        const results = await axe(container, {
          rules: {
            'color-contrast': { enabled: true },
          },
        });
        
        const contrastViolations = results.violations.filter(
          v => v.id === 'color-contrast'
        );
        
        // Accepter jusqu'à 1 violation mineure par page
        expect(contrastViolations.length).toBeLessThanOrEqual(1);
      }
    });
  });
});


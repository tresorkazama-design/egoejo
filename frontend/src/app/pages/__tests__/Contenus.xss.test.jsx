/**
 * Tests de sécurité XSS pour la page Contenus
 * Vérifie que le contenu backend est correctement sanitizé
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, render } from '@testing-library/react';
import { Contenus } from '../Contenus';
import { fetchAPI } from '../../../utils/api';
import { renderWithProviders } from '../../../test/test-utils';

vi.mock('../../../utils/api', () => ({
  fetchAPI: vi.fn(),
  handleAPIError: vi.fn((err) => {
    if (err instanceof Error) {
      return err.message;
    }
    return 'Une erreur est survenue';
  }),
}));

describe('Contenus - Sécurité XSS', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('devrait neutraliser un script injecté dans le titre', async () => {
    const maliciousTitle = '<script>alert("XSS")</script>Contenu malveillant';
    const mockContenus = [
      {
        id: 1,
        title: maliciousTitle,
        description: 'Description normale',
        type: 'article',
        slug: 'test',
      },
    ];

    fetchAPI.mockResolvedValueOnce({ results: mockContenus });

    renderWithProviders(<Contenus />);

    // Attendre que le contenu soit chargé
    await screen.findByText(/Contenu malveillant/i);

    // Vérifier que le script n'est pas exécuté (pas de balise <script> dans le DOM)
    const titleElement = screen.getByText(/Contenu malveillant/i);
    expect(titleElement).toBeInTheDocument();
    
    // Le script doit être échappé, pas exécuté
    // React échappe automatiquement, donc on vérifie textContent (pas innerHTML)
    expect(titleElement.textContent).not.toContain('<script>');
    expect(titleElement.textContent).toContain('Contenu malveillant'); // Le texte reste lisible
    // Vérifier que le HTML est bien échappé (pas de balise exécutable)
    expect(titleElement.innerHTML).not.toContain('<script>');
    // Le script est échappé, donc présent sous forme de texte (sécurisé)
    expect(titleElement.textContent).toContain('script'); // Le mot "script" est présent mais échappé
  });

  it('devrait neutraliser un script injecté dans la description', async () => {
    const maliciousDescription = '<img src="x" onerror="alert(\'XSS\')" />';
    const mockContenus = [
      {
        id: 1,
        title: 'Titre normal',
        description: maliciousDescription,
        type: 'article',
        slug: 'test',
      },
    ];

    fetchAPI.mockResolvedValueOnce({ results: mockContenus });

    const { container } = renderWithProviders(<Contenus />);

    // Attendre que le contenu soit chargé
    await screen.findByText(/Titre normal/i);

    // Vérifier que le script n'est pas exécuté
    const descriptionElement = container.querySelector('.citation-group__description');
    expect(descriptionElement).toBeInTheDocument();
    
    // L'attribut onerror doit être échappé, pas exécuté
    // React échappe automatiquement, donc on vérifie textContent
    expect(descriptionElement.textContent).not.toContain('<img');
    // Le mot "onerror" est présent dans le texte échappé mais ne peut pas être exécuté
    // (c'est correct : le HTML est échappé, donc sécurisé)
    // Vérifier que le HTML est bien échappé (pas de balise exécutable)
    // React échappe automatiquement, donc innerHTML contient le HTML échappé par React
    // sanitizeContent échappe aussi, donc le HTML est doublement échappé
    expect(descriptionElement.innerHTML).not.toContain('<img');
    // Vérifier que le HTML échappé ne contient pas d'attribut onerror exécutable
    // Le HTML échappé par React contient &lt;img src=&quot;x&quot; onerror=...
    // Donc onerror= est présent mais échappé, ce qui est sécurisé
    // On vérifie que le HTML ne contient pas de balise <img non échappée
    const htmlContent = descriptionElement.innerHTML;
    // Le HTML échappé ne doit pas contenir de balise <img (mais peut contenir &lt;img)
    expect(htmlContent).not.toMatch(/<img[^>]*onerror=/i); // Pas de balise <img avec onerror non échappée
  });

  it('devrait neutraliser un protocole javascript: dans le titre', async () => {
    const maliciousTitle = '<a href="javascript:alert(\'XSS\')">Click me</a>';
    const mockContenus = [
      {
        id: 1,
        title: maliciousTitle,
        description: 'Description normale',
        type: 'article',
        slug: 'test',
      },
    ];

    fetchAPI.mockResolvedValueOnce({ results: mockContenus });

    const { container } = renderWithProviders(<Contenus />);

    await screen.findByText(/Click me/i);

    // Vérifier que le protocole javascript: est échappé
    const titleElement = container.querySelector('.citation-group__title');
    expect(titleElement).toBeInTheDocument();
    // React échappe automatiquement, donc on vérifie textContent
    expect(titleElement.textContent).not.toContain('<a');
    expect(titleElement.textContent).toContain('Click me'); // Le texte reste lisible
    // Vérifier que le HTML est bien échappé (pas de balise exécutable)
    expect(titleElement.innerHTML).not.toContain('<a');
  });

  it('devrait préserver le HTML valide mais le rendre sûr (échappé)', async () => {
    const htmlContent = '<p>Paragraphe avec <strong>gras</strong></p>';
    const mockContenus = [
      {
        id: 1,
        title: 'Titre normal',
        description: htmlContent,
        type: 'article',
        slug: 'test',
      },
    ];

    fetchAPI.mockResolvedValueOnce({ results: mockContenus });

    const { container } = renderWithProviders(<Contenus />);

    await screen.findByText(/Titre normal/i);

    // Le HTML doit être échappé, pas exécuté
    const descriptionElement = container.querySelector('.citation-group__description');
    expect(descriptionElement).toBeInTheDocument();
    // React échappe automatiquement, donc on vérifie textContent
    expect(descriptionElement.textContent).not.toContain('<p>');
    expect(descriptionElement.textContent).not.toContain('<strong>');
    // Vérifier que le HTML est bien échappé (pas de balise exécutable)
    expect(descriptionElement.innerHTML).not.toContain('<p>');
    expect(descriptionElement.innerHTML).not.toContain('<strong>');
    
    // Le texte doit rester lisible
    expect(descriptionElement.textContent).toContain('Paragraphe avec');
    expect(descriptionElement.textContent).toContain('gras');
  });

  it('devrait préserver l\'accessibilité (aria-labelledby fonctionne)', async () => {
    const mockContenus = [
      {
        id: 1,
        title: 'Titre avec <script>alert("XSS")</script>',
        description: 'Description normale',
        type: 'article',
        slug: 'test',
      },
    ];

    fetchAPI.mockResolvedValueOnce({ results: mockContenus });

    const { container } = renderWithProviders(<Contenus />);

    await screen.findByText(/Titre avec/i);

    // Vérifier que aria-labelledby est présent et fonctionne
    const section = container.querySelector('section[aria-labelledby="contenu-1"]');
    expect(section).toBeInTheDocument();
    
    const titleElement = container.querySelector('#contenu-1');
    expect(titleElement).toBeInTheDocument();
    expect(titleElement.tagName).toBe('H2'); // Heading préservé
    
    // Vérifier que la description a aria-labelledby
    const descriptionElement = container.querySelector('.citation-group__description');
    expect(descriptionElement).toHaveAttribute('aria-labelledby', 'contenu-1');
  });

  it('devrait préserver la structure des headings (h1, h2, h3)', async () => {
    const mockContenus = [
      {
        id: 1,
        title: 'Titre <h1>malveillant</h1>',
        description: 'Description normale',
        type: 'article',
        slug: 'test',
      },
    ];

    fetchAPI.mockResolvedValueOnce({ results: mockContenus });

    const { container } = renderWithProviders(<Contenus />);

    await screen.findByText(/Titre/i);

    // Vérifier que la structure des headings est préservée
    const h1 = container.querySelector('h1#contenus-title');
    expect(h1).toBeInTheDocument();
    
    const h2 = container.querySelector('h2#contenu-1');
    expect(h2).toBeInTheDocument();
    expect(h2.tagName).toBe('H2');
    
    // Le HTML dans le titre doit être échappé
    // React échappe automatiquement, donc on vérifie textContent
    expect(h2.textContent).not.toContain('<h1>');
    expect(h2.textContent).toContain('malveillant'); // Le texte reste lisible
    // Vérifier que le HTML est bien échappé (pas de balise exécutable)
    expect(h2.innerHTML).not.toContain('<h1>');
  });

  it('devrait préserver les attributs aria-label dans les liens', async () => {
    const mockContenus = [
      {
        id: 1,
        title: 'Titre avec <script>alert("XSS")</script>',
        description: 'Description normale',
        type: 'article',
        slug: 'test',
        external_url: 'https://example.com',
      },
    ];

    fetchAPI.mockResolvedValueOnce({ results: mockContenus });

    const { container } = renderWithProviders(<Contenus />);

    await screen.findByText(/Titre avec/i);

    // Vérifier que aria-label est présent et contient le titre sanitizé
    const link = container.querySelector('a[href="https://example.com"]');
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('aria-label');
    
    // L'aria-label doit contenir le titre sanitizé (échappé)
    const ariaLabel = link.getAttribute('aria-label');
    expect(ariaLabel).toContain('Titre avec');
    expect(ariaLabel).not.toContain('<script>');
  });
});


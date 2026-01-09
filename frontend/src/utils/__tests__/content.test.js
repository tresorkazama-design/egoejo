/**
 * Tests unitaires pour sanitizeContent()
 * Vérifie la protection contre les attaques XSS
 */

import { describe, it, expect } from 'vitest';
import { sanitizeContent, containsDangerousHTML } from '../content.js';

describe('sanitizeContent', () => {
  describe('Protection XSS - Scripts injectés', () => {
    it('devrait neutraliser un script injecté', () => {
      const malicious = '<script>alert("XSS")</script>';
      const sanitized = sanitizeContent(malicious);
      
      // Le script doit être échappé, pas exécuté
      expect(sanitized).toBe('&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;');
      expect(sanitized).not.toContain('<script>');
      expect(sanitized).not.toContain('</script>');
    });

    it('devrait neutraliser un script avec attributs', () => {
      const malicious = '<script src="evil.js"></script>';
      const sanitized = sanitizeContent(malicious);
      
      expect(sanitized).toBe('&lt;script src=&quot;evil.js&quot;&gt;&lt;/script&gt;');
      expect(sanitized).not.toContain('<script');
    });

    it('devrait neutraliser un script inline avec événement', () => {
      const malicious = '<img src="x" onerror="alert(\'XSS\')">';
      const sanitized = sanitizeContent(malicious);
      
      // Le HTML doit être échappé, pas exécuté
      expect(sanitized).toBe('&lt;img src=&quot;x&quot; onerror=&quot;alert(&#039;XSS&#039;)&quot;&gt;');
      // Vérifier que le HTML est échappé (pas de balise <img> non échappée)
      expect(sanitized).not.toContain('<img');
      expect(sanitized).not.toContain('onerror="');
      // Mais contient l'échappement
      expect(sanitized).toContain('&lt;img');
      expect(sanitized).toContain('onerror=&quot;');
    });

    it('devrait neutraliser un iframe malveillant', () => {
      const malicious = '<iframe src="javascript:alert(\'XSS\')"></iframe>';
      const sanitized = sanitizeContent(malicious);
      
      expect(sanitized).toBe('&lt;iframe src=&quot;javascript:alert(&#039;XSS&#039;)&quot;&gt;&lt;/iframe&gt;');
      expect(sanitized).not.toContain('<iframe');
    });

    it('devrait neutraliser un objet embed', () => {
      const malicious = '<object data="evil.swf"></object>';
      const sanitized = sanitizeContent(malicious);
      
      expect(sanitized).toBe('&lt;object data=&quot;evil.swf&quot;&gt;&lt;/object&gt;');
      expect(sanitized).not.toContain('<object');
    });

    it('devrait neutraliser un lien javascript:', () => {
      const malicious = '<a href="javascript:alert(\'XSS\')">Cliquez ici</a>';
      const sanitized = sanitizeContent(malicious);
      
      // Le HTML doit être échappé, pas exécuté
      expect(sanitized).toBe('&lt;a href=&quot;javascript:alert(&#039;XSS&#039;)&quot;&gt;Cliquez ici&lt;/a&gt;');
      // Vérifier que le HTML est échappé (pas de balise <a> non échappée)
      expect(sanitized).not.toContain('<a');
      expect(sanitized).not.toContain('href="javascript:');
      // Mais contient l'échappement
      expect(sanitized).toContain('&lt;a');
      expect(sanitized).toContain('href=&quot;javascript:');
    });

    it('devrait neutraliser un data URI HTML', () => {
      const malicious = '<img src="data:text/html,<script>alert(\'XSS\')</script>">';
      const sanitized = sanitizeContent(malicious);
      
      // Le HTML doit être échappé, pas exécuté
      expect(sanitized).toContain('&lt;img');
      expect(sanitized).not.toContain('<img');
      // Le data URI est échappé dans les guillemets
      expect(sanitized).toContain('data:text/html');
      expect(sanitized).toContain('&quot;data:text/html');
    });
  });

  describe('Rendu textuel - HTML valide échappé', () => {
    it('devrait échapper du HTML valide sans l\'exécuter', () => {
      const html = '<p>Hello <strong>world</strong></p>';
      const sanitized = sanitizeContent(html);
      
      // Le HTML doit être échappé, pas rendu
      expect(sanitized).toBe('&lt;p&gt;Hello &lt;strong&gt;world&lt;/strong&gt;&lt;/p&gt;');
      expect(sanitized).not.toContain('<p>');
      expect(sanitized).not.toContain('<strong>');
    });

    it('devrait échapper des balises de liste', () => {
      const html = '<ul><li>Item 1</li><li>Item 2</li></ul>';
      const sanitized = sanitizeContent(html);
      
      expect(sanitized).toBe('&lt;ul&gt;&lt;li&gt;Item 1&lt;/li&gt;&lt;li&gt;Item 2&lt;/li&gt;&lt;/ul&gt;');
      expect(sanitized).not.toContain('<ul>');
    });

    it('devrait échapper des liens', () => {
      const html = '<a href="https://example.com">Lien</a>';
      const sanitized = sanitizeContent(html);
      
      expect(sanitized).toBe('&lt;a href=&quot;https://example.com&quot;&gt;Lien&lt;/a&gt;');
      expect(sanitized).not.toContain('<a');
    });
  });

  describe('Texte normal - Non modifié', () => {
    it('devrait laisser le texte normal inchangé', () => {
      const text = 'Texte normal sans HTML';
      const sanitized = sanitizeContent(text);
      
      expect(sanitized).toBe(text);
    });

    it('devrait gérer les caractères spéciaux', () => {
      const text = 'Texte avec "guillemets" et \'apostrophes\'';
      const sanitized = sanitizeContent(text);
      
      expect(sanitized).toBe('Texte avec &quot;guillemets&quot; et &#039;apostrophes&#039;');
    });

    it('devrait gérer les caractères accentués', () => {
      const text = 'Texte avec é, è, à, ç, ñ';
      const sanitized = sanitizeContent(text);
      
      expect(sanitized).toBe(text);
    });
  });

  describe('Gestion des valeurs nulles/undefined', () => {
    it('devrait retourner une chaîne vide pour null', () => {
      expect(sanitizeContent(null)).toBe('');
    });

    it('devrait retourner une chaîne vide pour undefined', () => {
      expect(sanitizeContent(undefined)).toBe('');
    });

    it('devrait convertir un nombre en string', () => {
      expect(sanitizeContent(123)).toBe('123');
      expect(sanitizeContent(0)).toBe('0');
    });

    it('devrait convertir un booléen en string', () => {
      expect(sanitizeContent(true)).toBe('true');
      expect(sanitizeContent(false)).toBe('false');
    });
  });

  describe('Échappement des caractères HTML', () => {
    it('devrait échapper &', () => {
      expect(sanitizeContent('A & B')).toBe('A &amp; B');
    });

    it('devrait échapper <', () => {
      expect(sanitizeContent('A < B')).toBe('A &lt; B');
    });

    it('devrait échapper >', () => {
      expect(sanitizeContent('A > B')).toBe('A &gt; B');
    });

    it('devrait échapper "', () => {
      expect(sanitizeContent('Texte "entre guillemets"')).toBe('Texte &quot;entre guillemets&quot;');
    });

    it('devrait échapper \'', () => {
      expect(sanitizeContent("Texte 'avec apostrophe'")).toBe('Texte &#039;avec apostrophe&#039;');
    });
  });
});

describe('containsDangerousHTML', () => {
  it('devrait détecter un script', () => {
    expect(containsDangerousHTML('<script>alert("XSS")</script>')).toBe(true);
  });

  it('devrait détecter un iframe', () => {
    expect(containsDangerousHTML('<iframe src="evil.html"></iframe>')).toBe(true);
  });

  it('devrait détecter un attribut événement', () => {
    expect(containsDangerousHTML('<img onerror="alert(\'XSS\')">')).toBe(true);
  });

  it('devrait détecter javascript:', () => {
    expect(containsDangerousHTML('<a href="javascript:alert(\'XSS\')">')).toBe(true);
  });

  it('ne devrait pas détecter de HTML valide simple', () => {
    expect(containsDangerousHTML('<p>Hello</p>')).toBe(false);
    expect(containsDangerousHTML('<strong>Bold</strong>')).toBe(false);
  });

  it('ne devrait pas détecter de texte normal', () => {
    expect(containsDangerousHTML('Texte normal')).toBe(false);
  });

  it('devrait retourner false pour null/undefined', () => {
    expect(containsDangerousHTML(null)).toBe(false);
    expect(containsDangerousHTML(undefined)).toBe(false);
  });
});

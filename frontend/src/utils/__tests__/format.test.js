import { describe, it, expect } from 'vitest';

// Fonctions utilitaires de formatage
export const formatDate = (date) => {
  if (!date) return '';
  const d = new Date(date);
  if (isNaN(d.getTime())) return '';
  return d.toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

export const formatCurrency = (amount, currency = 'EUR') => {
  if (typeof amount !== 'number' || isNaN(amount)) return '';
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: currency
  }).format(amount);
};

export const truncateText = (text, maxLength = 100) => {
  if (!text || typeof text !== 'string') return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

describe('Format Utilities', () => {
  describe('formatDate', () => {
    it('devrait formater une date correctement', () => {
      const date = new Date('2025-01-27');
      const formatted = formatDate(date);
      expect(formatted).toContain('2025');
      expect(formatted).toContain('janvier');
      expect(formatted).toContain('27');
    });

    it('devrait gérer les cas limites', () => {
      expect(formatDate(null)).toBe('');
      expect(formatDate(undefined)).toBe('');
      expect(formatDate('invalid')).toBe('');
      expect(formatDate('')).toBe('');
    });
  });

  describe('formatCurrency', () => {
    it('devrait formater un montant en euros', () => {
      expect(formatCurrency(100)).toContain('100');
      expect(formatCurrency(1000)).toContain('1');
      expect(formatCurrency(99.99)).toContain('99');
    });

    it('devrait gérer les cas limites', () => {
      expect(formatCurrency(null)).toBe('');
      expect(formatCurrency(undefined)).toBe('');
      expect(formatCurrency('invalid')).toBe('');
      expect(formatCurrency(NaN)).toBe('');
    });
  });

  describe('truncateText', () => {
    it('devrait tronquer un texte trop long', () => {
      const longText = 'a'.repeat(150);
      const truncated = truncateText(longText, 100);
      expect(truncated.length).toBe(103); // 100 + '...'
      expect(truncated.endsWith('...')).toBe(true);
    });

    it('ne devrait pas tronquer un texte court', () => {
      const shortText = 'Texte court';
      expect(truncateText(shortText, 100)).toBe(shortText);
    });

    it('devrait gérer les cas limites', () => {
      expect(truncateText(null)).toBe('');
      expect(truncateText(undefined)).toBe('');
      expect(truncateText('')).toBe('');
      expect(truncateText(123)).toBe('');
    });
  });
});


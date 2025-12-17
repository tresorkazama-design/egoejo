import { describe, it, expect } from 'vitest';

// Fonctions utilitaires de validation
export const isValidEmail = (email) => {
  if (!email || typeof email !== 'string') return false;
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email.trim());
};

export const isValidPassword = (password) => {
  if (!password || typeof password !== 'string') return false;
  return password.length >= 10;
};

export const sanitizeInput = (input) => {
  if (typeof input !== 'string') return '';
  return input.trim().replace(/[<>]/g, '');
};

describe('Validation Utilities', () => {
  describe('isValidEmail', () => {
    it('devrait valider un email correct', () => {
      expect(isValidEmail('test@example.com')).toBe(true);
      expect(isValidEmail('user.name@domain.co.uk')).toBe(true);
      expect(isValidEmail('user+tag@example.com')).toBe(true);
    });

    it('devrait rejeter un email invalide', () => {
      expect(isValidEmail('invalid-email')).toBe(false);
      expect(isValidEmail('@example.com')).toBe(false);
      expect(isValidEmail('test@')).toBe(false);
      expect(isValidEmail('test@example')).toBe(false);
      expect(isValidEmail('')).toBe(false);
    });

    it('devrait gérer les cas limites', () => {
      expect(isValidEmail(null)).toBe(false);
      expect(isValidEmail(undefined)).toBe(false);
      expect(isValidEmail(123)).toBe(false);
      expect(isValidEmail('  test@example.com  ')).toBe(true); // trim
    });
  });

  describe('isValidPassword', () => {
    it('devrait valider un mot de passe de 10 caractères ou plus', () => {
      expect(isValidPassword('1234567890')).toBe(true);
      expect(isValidPassword('password123')).toBe(true);
      expect(isValidPassword('a'.repeat(10))).toBe(true);
      expect(isValidPassword('a'.repeat(20))).toBe(true);
    });

    it('devrait rejeter un mot de passe trop court', () => {
      expect(isValidPassword('123456789')).toBe(false); // 9 caractères
      expect(isValidPassword('short')).toBe(false);
      expect(isValidPassword('')).toBe(false);
    });

    it('devrait gérer les cas limites', () => {
      expect(isValidPassword(null)).toBe(false);
      expect(isValidPassword(undefined)).toBe(false);
      expect(isValidPassword(1234567890)).toBe(false); // nombre
    });
  });

  describe('sanitizeInput', () => {
    it('devrait nettoyer les entrées utilisateur', () => {
      expect(sanitizeInput('  hello world  ')).toBe('hello world');
      expect(sanitizeInput('<script>alert("xss")</script>')).toBe('scriptalert("xss")/script');
      expect(sanitizeInput('normal text')).toBe('normal text');
    });

    it('devrait gérer les cas limites', () => {
      expect(sanitizeInput('')).toBe('');
      expect(sanitizeInput(null)).toBe('');
      expect(sanitizeInput(undefined)).toBe('');
      expect(sanitizeInput(123)).toBe('');
    });
  });
});


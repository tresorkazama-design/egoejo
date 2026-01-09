import { describe, it, expect } from 'vitest';
import { formatSaka, isSakaFormatValid } from '../saka';
import { formatMoney } from '../money';

describe('Protection Philosophique SAKA/EUR - Frontend', () => {
  it('SAKA ne doit jamais être formaté comme une monnaie', () => {
    const sakaAmount = 150;
    const formatted = formatSaka(sakaAmount);
    
    // Vérifier qu'il n'y a pas de symbole monétaire
    expect(formatted).not.toContain('€');
    expect(formatted).not.toContain('EUR');
    expect(formatted).not.toContain('euro');
    
    // Vérifier que c'est bien formaté comme "grains SAKA"
    expect(formatted).toContain('grains SAKA');
    expect(formatted).toBe('150 grains SAKA');
  });
  
  it('formatMoney ne doit pas être utilisé pour SAKA', () => {
    // Ce test vérifie que formatMoney n'est pas utilisé pour SAKA
    const sakaAmount = 150;
    
    // Vérifier que formatSaka ne produit pas de format monétaire
    const sakaFormatted = formatSaka(sakaAmount);
    const moneyFormatted = formatMoney('150', 'EUR');
    
    // Les formats doivent être différents
    expect(sakaFormatted).not.toBe(moneyFormatted);
    expect(sakaFormatted).not.toMatch(/\d+[,\s]\d+\s*€/);
    
    // Vérifier que formatSaka ne contient pas de format monétaire
    expect(isSakaFormatValid(sakaFormatted)).toBe(true);
    expect(isSakaFormatValid(moneyFormatted)).toBe(false);
  });
  
  it('isSakaFormatValid doit détecter les violations', () => {
    // Format valide (grains SAKA)
    expect(isSakaFormatValid('150 grains SAKA')).toBe(true);
    expect(isSakaFormatValid('1 grain SAKA')).toBe(true);
    
    // Formats invalides (contiennent des symboles monétaires)
    expect(isSakaFormatValid('150 €')).toBe(false);
    expect(isSakaFormatValid('150 EUR')).toBe(false);
    expect(isSakaFormatValid('150,00 €')).toBe(false);
    expect(isSakaFormatValid('150 grains SAKA (150 €)')).toBe(false);
  });
});


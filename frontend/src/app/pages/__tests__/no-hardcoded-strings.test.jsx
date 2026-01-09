import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Tests BLOQUANTS - Détection de strings hardcodées en français
 * 
 * Vérifie que les fichiers critiques n'ont pas de strings hardcodées en français.
 * Toutes les strings doivent utiliser i18n via t().
 */

// Patterns de détection de strings hardcodées en français
const FRENCH_PATTERNS = [
  /["']Aller au contenu principal["']/i,
  /["']Aller au contenu["']/i,
  /["']Passer au contenu["']/i,
  /["']Contenu principal["']/i,
  /aria-label=["']Contenu principal["']/i,
  /aria-label=["']Aller au contenu["']/i,
  // Patterns pour "100% des dons" sans i18n
  /100\s*%\s*des?\s*dons?[^"]*["']/i,
  // Patterns pour principes/glossaire/disclaimer hardcodés
  /["']Principes fondamentaux["']/i,
  /["']Glossaire["']/i,
  /["']Disclaimer["']/i,
  /["']Citations autochtones["']/i,
];

// Fichiers à scanner
const FILES_TO_SCAN = [
  join(__dirname, '../Home.jsx'),
  join(__dirname, '../Vision.jsx'),
  join(__dirname, '../../../components/Layout.jsx'),
];

describe('Détection de strings hardcodées en français (BLOQUANT)', () => {
  FILES_TO_SCAN.forEach((filePath) => {
    const fileName = filePath.split('/').pop() || filePath.split('\\').pop();
    
    describe(`Fichier: ${fileName}`, () => {
      it('ne devrait PAS contenir de strings hardcodées en français', () => {
        let content;
        try {
          content = readFileSync(filePath, 'utf-8');
        } catch (error) {
          throw new Error(`Impossible de lire le fichier ${filePath}: ${error.message}`);
        }

        const violations = [];
        
        // Vérifier chaque pattern
        FRENCH_PATTERNS.forEach((pattern, index) => {
          const matches = content.match(new RegExp(pattern.source, 'g'));
          if (matches) {
            matches.forEach(match => {
              // Ignorer si c'est dans un commentaire
              const lines = content.split('\n');
              const matchIndex = content.indexOf(match);
              const lineNumber = content.substring(0, matchIndex).split('\n').length;
              const line = lines[lineNumber - 1];
              
              // Vérifier si c'est dans un commentaire
              const isInComment = line.trim().startsWith('//') || 
                                  line.trim().startsWith('/*') ||
                                  line.includes('//') && line.indexOf('//') < line.indexOf(match);
              
              if (!isInComment) {
                violations.push({
                  pattern: pattern.source,
                  match: match.trim(),
                  line: lineNumber,
                  lineContent: line.trim(),
                });
              }
            });
          }
        });

        // Vérifier les strings critiques spécifiques
        const criticalStrings = [
          { pattern: /100\s*%\s*des?\s*dons?/i, name: '"100% des dons"', context: 'home.soutenir_desc' },
          { pattern: /SAKA.*EUR|EUR.*SAKA/i, name: 'SAKA/EUR', context: 'home.saka_eur_note' },
          { pattern: /Principes fondamentaux/i, name: '"Principes fondamentaux"', context: 'vision.principles_title' },
          { pattern: /Glossaire/i, name: '"Glossaire"', context: 'vision.glossary_title' },
          { pattern: /Citations autochtones|autochtone/i, name: 'Citations autochtones', context: 'vision.citations_disclaimer' },
        ];

        criticalStrings.forEach(({ pattern, name, context }) => {
          // Vérifier si la string est présente mais pas via t()
          const hasString = pattern.test(content);
          if (hasString) {
            // Vérifier si elle est utilisée via t() ou si elle est hardcodée
            const lines = content.split('\n');
            lines.forEach((line, index) => {
              if (pattern.test(line)) {
                // Ignorer si c'est dans un commentaire, un test, ou un attribut technique
                if (line.trim().startsWith('//') || 
                    line.trim().startsWith('/*') ||
                    line.includes('__tests__') ||
                    line.includes('.test.') ||
                    line.includes('.spec.') ||
                    line.includes('data-testid') ||
                    line.includes('aria-label') && line.includes('t(') ||
                    line.includes('className') ||
                    line.includes('id=') ||
                    line.includes('role=')) {
                  return;
                }
                
                // Vérifier si elle utilise t() ou si elle est hardcodée
                const hasI18n = line.includes('t(') || line.includes('i18n');
                // Vérifier si c'est une string hardcodée (entre guillemets mais pas via t())
                const isHardcodedString = /["']([^"']*)/.test(line) && 
                                         !hasI18n && 
                                         !line.includes('data-testid') &&
                                         !line.includes('className') &&
                                         !line.includes('id=') &&
                                         !line.includes('role=');
                
                if (isHardcodedString) {
                  const match = line.match(/["']([^"']*)/);
                  if (match && pattern.test(match[1])) {
                    violations.push({
                      pattern: pattern.source,
                      match: line.trim(),
                      line: index + 1,
                      lineContent: line.trim(),
                      context: `Devrait utiliser t("${context}")`,
                    });
                  }
                }
              }
            });
          }
        });

        if (violations.length > 0) {
          const violationReport = violations.map(v => 
            `  Ligne ${v.line}: ${v.lineContent}\n    → ${v.match}\n    → ${v.context || 'String hardcodée détectée'}`
          ).join('\n\n');
          
          throw new Error(
            `BLOQUANT : Strings hardcodées en français détectées dans ${fileName}\n\n` +
            `Violations (${violations.length}):\n\n${violationReport}\n\n` +
            `Exigence : Toutes les strings doivent utiliser i18n via t().`
          );
        }

        expect(violations.length).toBe(0);
      });

      it('devrait utiliser t() pour toutes les strings critiques', () => {
        let content;
        try {
          content = readFileSync(filePath, 'utf-8');
        } catch (error) {
          throw new Error(`Impossible de lire le fichier ${filePath}: ${error.message}`);
        }

        // Vérifier que les clés i18n critiques sont utilisées
        const requiredI18nKeys = {
          'Layout.jsx': ['accessibility.skip_to_main'],
          'Home.jsx': ['home.soutenir_desc', 'home.saka_eur_note'],
          'Vision.jsx': ['vision.principles_title', 'vision.glossary_title', 'vision.citations_disclaimer'],
        };

        const fileName = filePath.split('/').pop() || filePath.split('\\').pop();
        const requiredKeys = requiredI18nKeys[fileName] || [];

        const missingKeys = requiredKeys.filter(key => {
          // Vérifier si la clé est utilisée via t()
          const keyPattern = new RegExp(`t\\(["']${key.replace('.', '\\.')}["']`, 'i');
          return !keyPattern.test(content);
        });

        if (missingKeys.length > 0) {
          throw new Error(
            `BLOQUANT : Clés i18n manquantes dans ${fileName}\n\n` +
            `Clés requises non utilisées :\n${missingKeys.map(k => `  - ${k}`).join('\n')}\n\n` +
            `Exigence : Toutes les strings critiques doivent utiliser t() avec les clés i18n appropriées.`
          );
        }

        expect(missingKeys.length).toBe(0);
      });
    });
  });
});


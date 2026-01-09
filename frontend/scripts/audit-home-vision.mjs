#!/usr/bin/env node

/**
 * Script d'audit BLOQUANT pour les pages Accueil et Vision
 * 
 * Vérifie les règles de conformité EGOEJO et échoue (exit 1) si violations détectées.
 * 
 * Usage:
 *   npm run audit:home-vision
 *   npm run audit:home-vision -- --json
 * 
 * Règles vérifiées:
 * 1. "100% des dons" doit contenir "nets" ou mention de frais (HelloAsso/Stripe/frais de plateforme)
 * 2. Le skip-link ne doit pas être hardcodé en français dans Layout.jsx
 * 3. Les clés i18n minimales doivent exister
 */

import { readFileSync, readdirSync, statSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Chemins
const ROOT_DIR = join(__dirname, '..');
const SRC_DIR = join(ROOT_DIR, 'src');
const LOCALES_DIR = join(SRC_DIR, 'locales');
const LAYOUT_FILE = join(SRC_DIR, 'components', 'Layout.jsx');

// Options
const args = process.argv.slice(2);
const JSON_OUTPUT = args.includes('--json');

// Violations détectées
const violations = [];

/**
 * Trouve tous les fichiers JSON dans un répertoire
 */
function findJsonFiles(dir) {
  const files = [];
  try {
    const entries = readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.isFile() && entry.name.endsWith('.json')) {
        files.push(join(dir, entry.name));
      }
    }
  } catch (error) {
    // Ignorer si le répertoire n'existe pas
  }
  return files;
}

/**
 * Lit un fichier et retourne son contenu
 */
function readFile(filePath) {
  try {
    return readFileSync(filePath, 'utf-8');
  } catch (error) {
    return null;
  }
}

/**
 * Trouve toutes les occurrences d'un pattern dans un fichier
 */
function findPatternInFile(filePath, pattern, description) {
  const content = readFile(filePath);
  if (!content) return [];

  const matches = [];
  const lines = content.split('\n');
  
  lines.forEach((line, index) => {
    if (pattern.test(line)) {
      matches.push({
        file: filePath,
        line: index + 1,
        content: line.trim(),
        description
      });
    }
  });
  
  return matches;
}

/**
 * Règle 1: Détecter "100% des dons" sans "nets" ou mention de frais
 */
function checkDonationText() {
  const localeFiles = findJsonFiles(LOCALES_DIR);
  const violations = [];

  for (const localeFile of localeFiles) {
    const content = readFile(localeFile);
    if (!content) continue;

    try {
      const data = JSON.parse(content);
      
      // Rechercher dans toutes les clés du JSON
      const searchInObject = (obj, path = '') => {
        for (const [key, value] of Object.entries(obj)) {
          const currentPath = path ? `${path}.${key}` : key;
          
          if (typeof value === 'string') {
            // Pattern: "100% des dons" ou "100 % des dons" (avec ou sans espace)
            const pattern100Dons = /100\s*%\s*des?\s*dons?/i;
            
            if (pattern100Dons.test(value)) {
              // Vérifier qu'il contient "nets" ou mention de frais
              const hasNets = /\bnets?\b/i.test(value);
              const hasFees = /(?:frais|fees|helloasso|stripe|plateforme|platform)/i.test(value);
              
              if (!hasNets && !hasFees) {
                violations.push({
                  rule: 'DONATION_TEXT_MISSING_NETS',
                  file: localeFile,
                  key: currentPath,
                  line: findLineNumber(content, value),
                  content: value.substring(0, 150),
                  description: `"100% des dons" trouvé sans "nets" ou mention de frais dans ${currentPath}`
                });
              }
            }
          } else if (typeof value === 'object' && value !== null) {
            searchInObject(value, currentPath);
          }
        }
      };
      
      searchInObject(data);
    } catch (error) {
      // Ignorer les erreurs de parsing JSON
    }
  }

  return violations;
}

/**
 * Trouve le numéro de ligne d'une valeur dans un fichier JSON
 */
function findLineNumber(content, searchValue) {
  const lines = content.split('\n');
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes(searchValue.substring(0, 50))) {
      return i + 1;
    }
  }
  return 0;
}

/**
 * Règle 2: Détecter skip-link hardcodé en français dans Layout.jsx
 */
function checkSkipLinkHardcoded() {
  const violations = [];
  const content = readFile(LAYOUT_FILE);
  
  if (!content) {
    violations.push({
      rule: 'LAYOUT_FILE_MISSING',
      file: LAYOUT_FILE,
      line: 0,
      content: '',
      description: `Le fichier Layout.jsx est introuvable`
    });
    return violations;
  }

  // Patterns de skip-link hardcodé en français
  const hardcodedPatterns = [
    /["']Aller au contenu principal["']/i,
    /["']Aller au contenu["']/i,
    /["']Passer au contenu["']/i,
    /skip.*navigation.*français/i,
  ];

  const lines = content.split('\n');
  lines.forEach((line, index) => {
    // Ignorer les lignes qui utilisent t() ou i18n
    if (line.includes('t(') || line.includes('i18n') || line.includes('useLanguage')) {
      return;
    }

    hardcodedPatterns.forEach(pattern => {
      if (pattern.test(line)) {
        violations.push({
          rule: 'SKIP_LINK_HARDCODED_FR',
          file: LAYOUT_FILE,
          line: index + 1,
          content: line.trim(),
          description: `Skip-link hardcodé en français détecté (doit utiliser i18n)`
        });
      }
    });
  });

  return violations;
}

/**
 * Règle 3: Vérifier l'existence des clés i18n minimales
 */
function checkI18nKeys() {
  const violations = [];
  const localeFiles = findJsonFiles(LOCALES_DIR);
  
  // Clés i18n minimales requises
  const requiredKeys = [
    'accessibility.skip_to_main',
    'vision.principles_title',
    'vision.glossary_title',
    'vision.citations_disclaimer',
    'home.saka_eur_note',
    'home.soutenir_desc',
  ];

  // Alternatives acceptables pour certaines clés
  const keyAlternatives = {
    'vision.citations_disclaimer': ['vision.citations_disclaimer', 'vision.disclaimer', 'vision.citations_note'],
    'home.saka_eur_note': ['home.saka_eur_note', 'home.saka_eur_note_title', 'home.saka_eur_separation'],
  };

  for (const localeFile of localeFiles) {
    const content = readFile(localeFile);
    if (!content) continue;

    try {
      const data = JSON.parse(content);
      
      for (const key of requiredKeys) {
        const keyParts = key.split('.');
        let value = data;
        let found = true;

        // Naviguer dans l'objet JSON
        for (const part of keyParts) {
          if (value && typeof value === 'object' && part in value) {
            value = value[part];
          } else {
            found = false;
            break;
          }
        }

        // Vérifier les alternatives si la clé principale n'existe pas
        if (!found && keyAlternatives[key]) {
          for (const altKey of keyAlternatives[key]) {
            const altParts = altKey.split('.');
            let altValue = data;
            found = true;

            for (const part of altParts) {
              if (altValue && typeof altValue === 'object' && part in altValue) {
                altValue = altValue[part];
              } else {
                found = false;
                break;
              }
            }

            if (found) break;
          }
        }

        if (!found) {
          violations.push({
            rule: 'I18N_KEY_MISSING',
            file: localeFile,
            key: key,
            line: findKeyLineNumber(content, key),
            content: '',
            description: `Clé i18n manquante: ${key}`
          });
        }
      }
    } catch (error) {
      violations.push({
        rule: 'I18N_FILE_INVALID',
        file: localeFile,
        key: '',
        line: 0,
        content: '',
        description: `Erreur de parsing JSON: ${error.message}`
      });
    }
  }

  return violations;
}

/**
 * Trouve le numéro de ligne d'une clé dans un fichier JSON
 */
function findKeyLineNumber(content, key) {
  const keyParts = key.split('.');
  const lastKey = keyParts[keyParts.length - 1];
  const lines = content.split('\n');
  
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes(`"${lastKey}"`)) {
      return i + 1;
    }
  }
  return 0;
}

/**
 * Affiche un rapport textuel
 */
function printTextReport(violations) {
  if (violations.length === 0) {
    console.log('✅ Aucune violation détectée. Conformité OK.');
    return;
  }

  console.log('\n❌ VIOLATIONS DÉTECTÉES\n');
  console.log('='.repeat(80));

  // Grouper par règle
  const byRule = {};
  violations.forEach(v => {
    if (!byRule[v.rule]) {
      byRule[v.rule] = [];
    }
    byRule[v.rule].push(v);
  });

  Object.entries(byRule).forEach(([rule, vs]) => {
    console.log(`\n🔴 Règle: ${rule}`);
    console.log('-'.repeat(80));
    
    vs.forEach((v, index) => {
      console.log(`\n  Violation ${index + 1}:`);
      console.log(`  Fichier: ${v.file}`);
      if (v.line > 0) {
        console.log(`  Ligne: ${v.line}`);
      }
      if (v.key) {
        console.log(`  Clé: ${v.key}`);
      }
      if (v.content) {
        console.log(`  Extrait: ${v.content}`);
      }
      console.log(`  Description: ${v.description}`);
    });
  });

  console.log('\n' + '='.repeat(80));
  console.log(`\n❌ Total: ${violations.length} violation(s) détectée(s)\n`);
}

/**
 * Génère un rapport JSON
 */
function generateJsonReport(violations) {
  const report = {
    status: violations.length === 0 ? 'compliant' : 'non-compliant',
    violations_count: violations.length,
    violations: violations.map(v => ({
      rule: v.rule,
      file: v.file,
      line: v.line,
      key: v.key || null,
      content: v.content || null,
      description: v.description
    })),
    timestamp: new Date().toISOString()
  };

  console.log(JSON.stringify(report, null, 2));
}

// ============================================================================
// EXÉCUTION PRINCIPALE
// ============================================================================

console.log('🔍 Audit BLOQUANT Home/Vision - EGOEJO Compliance\n');

// Exécuter les vérifications
const donationViolations = checkDonationText();
const skipLinkViolations = checkSkipLinkHardcoded();
const i18nViolations = checkI18nKeys();

// Agréger toutes les violations
const allViolations = [
  ...donationViolations,
  ...skipLinkViolations,
  ...i18nViolations
];

// Générer le rapport
if (JSON_OUTPUT) {
  generateJsonReport(allViolations);
} else {
  printTextReport(allViolations);
}

// Exit avec code d'erreur si violations
if (allViolations.length > 0) {
  process.exit(1);
} else {
  process.exit(0);
}


#!/usr/bin/env node

/**
 * Script d'audit BLOQUANT GLOBAL pour TOUT le projet EGOEJO
 * 
 * Scanne frontend/src ET backend/ à la recherche de mots interdits
 * qui violent la Constitution EGOEJO.
 * 
 * Usage:
 *   npm run audit:global
 *   npm run audit:global -- --json
 * 
 * Règles vérifiées:
 * 1. Mots interdits : "Rendement", "ROI", "Dividende", "Spéculation", "1 SAKA = X EUR"
 * 2. Conversions SAKA ↔ EUR interdites
 * 3. Promesses financières interdites
 */

import { readFileSync, readdirSync, statSync } from 'fs';
import { join, dirname, relative } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Chemins
const ROOT_DIR = join(__dirname, '..', '..', '..'); // Remonter à la racine du projet
const FRONTEND_SRC = join(ROOT_DIR, 'frontend', 'frontend', 'src');
const BACKEND_DIR = join(ROOT_DIR, 'backend');

// Options
const args = process.argv.slice(2);
const JSON_OUTPUT = args.includes('--json');

// Violations détectées
const violations = [];

// ============================================================================
// PATTERNS INTERDITS
// ============================================================================

/**
 * Patterns interdits (mots-clés qui violent la Constitution EGOEJO)
 */
const FORBIDDEN_PATTERNS = [
  // Conversions SAKA ↔ EUR
  {
    pattern: /1\s*saka\s*=\s*\d+\s*eur/gi,
    description: 'Conversion SAKA ↔ EUR interdite (ex: "1 SAKA = X EUR")',
    rule: 'SAKA_EUR_CONVERSION'
  },
  {
    pattern: /saka\s*=\s*\d+\s*eur/gi,
    description: 'Équivalence SAKA ↔ EUR interdite',
    rule: 'SAKA_EUR_CONVERSION'
  },
  {
    pattern: /convert.*saka.*eur|convert.*eur.*saka/gi,
    description: 'Fonction de conversion SAKA ↔ EUR interdite',
    rule: 'SAKA_EUR_CONVERSION'
  },
  {
    pattern: /exchange.*saka|saka.*exchange/gi,
    description: 'Échange SAKA interdit',
    rule: 'SAKA_EUR_CONVERSION'
  },
  
  // Mots financiers interdits
  {
    pattern: /\bRendement\b/gi,
    description: 'Mot "Rendement" interdit (promesse financière)',
    rule: 'FORBIDDEN_FINANCIAL_TERM'
  },
  {
    pattern: /\bROI\b/gi,
    description: 'Acronyme "ROI" interdit (Return On Investment)',
    rule: 'FORBIDDEN_FINANCIAL_TERM'
  },
  {
    pattern: /\bDividende\b/gi,
    description: 'Mot "Dividende" interdit (promesse financière)',
    rule: 'FORBIDDEN_FINANCIAL_TERM'
  },
  {
    pattern: /\bSpéculation\b/gi,
    description: 'Mot "Spéculation" interdit',
    rule: 'FORBIDDEN_FINANCIAL_TERM'
  },
  {
    pattern: /\bSpeculation\b/gi,
    description: 'Mot "Speculation" interdit (anglais)',
    rule: 'FORBIDDEN_FINANCIAL_TERM'
  },
  {
    pattern: /\bRente\b/gi,
    description: 'Mot "Rente" interdit (accumulation passive)',
    rule: 'FORBIDDEN_FINANCIAL_TERM'
  },
  {
    pattern: /\bIntérêt\b.*\bsaka\b|\bsaka\b.*\bintérêt\b/gi,
    description: 'Intérêt sur SAKA interdit',
    rule: 'FORBIDDEN_FINANCIAL_TERM'
  },
  
  // Promesses de valeur monétaire
  {
    pattern: /saka.*vaut.*eur|saka.*worth.*eur/gi,
    description: 'Valeur monétaire du SAKA interdite',
    rule: 'MONETARY_VALUE_SAKA'
  },
  {
    pattern: /saka.*prix|saka.*price/gi,
    description: 'Prix du SAKA interdit',
    rule: 'MONETARY_VALUE_SAKA'
  },
  {
    pattern: /saka.*taux.*change|saka.*exchange.*rate/gi,
    description: 'Taux de change SAKA interdit',
    rule: 'MONETARY_VALUE_SAKA'
  },
];

/**
 * Fichiers à exclure (commentaires, tests de conformité, etc.)
 */
const EXCLUDED_PATHS = [
  /node_modules/,
  /\.git/,
  /__pycache__/,
  /\.pytest_cache/,
  /venv/,
  /\.venv/,
  /dist/,
  /build/,
  /coverage/,
  /playwright-report/,
  /test-results/,
  /\.next/,
  /\.cache/,
  /staticfiles/,
  /migrations\/.*\.pyc$/,
  // Exclure les tests de conformité qui contiennent les patterns interdits
  /test.*conversion.*saka.*eur/,
  /test.*saka.*eur.*separation/,
  /test.*no.*saka.*eur/,
  /audit.*global/,
  /audit.*home.*vision/,
];

/**
 * Extensions de fichiers à scanner
 */
const SCANNABLE_EXTENSIONS = [
  '.js', '.jsx', '.ts', '.tsx',  // Frontend
  '.py',                          // Backend
  '.json',                        // Config
  '.md',                          // Documentation (peut contenir des exemples)
];

/**
 * Extensions à exclure (binaires, etc.)
 */
const EXCLUDED_EXTENSIONS = [
  '.png', '.jpg', '.jpeg', '.gif', '.svg',
  '.woff', '.woff2', '.ttf', '.eot',
  '.mp4', '.webm', '.mp3', '.wav',
  '.zip', '.tar', '.gz',
  '.pdf',
];

// ============================================================================
// FONCTIONS UTILITAIRES
// ============================================================================

/**
 * Vérifie si un chemin doit être exclu
 */
function shouldExcludePath(filePath) {
  return EXCLUDED_PATHS.some(pattern => pattern.test(filePath));
}

/**
 * Vérifie si un fichier doit être scanné
 */
function shouldScanFile(filePath) {
  const ext = filePath.toLowerCase();
  return SCANNABLE_EXTENSIONS.some(e => ext.endsWith(e)) &&
         !EXCLUDED_EXTENSIONS.some(e => ext.endsWith(e));
}

/**
 * Trouve tous les fichiers à scanner dans un répertoire
 */
function findScannableFiles(dir, baseDir = dir) {
  const files = [];
  
  try {
    const entries = readdirSync(dir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = join(dir, entry.name);
      const relativePath = relative(baseDir, fullPath);
      
      // Exclure les chemins interdits
      if (shouldExcludePath(relativePath)) {
        continue;
      }
      
      if (entry.isDirectory()) {
        // Récursion
        files.push(...findScannableFiles(fullPath, baseDir));
      } else if (entry.isFile() && shouldScanFile(fullPath)) {
        files.push(fullPath);
      }
    }
  } catch (error) {
    // Ignorer les erreurs (permissions, etc.)
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
 * Scanne un fichier pour les patterns interdits
 */
function scanFile(filePath) {
  const content = readFile(filePath);
  if (!content) return [];
  
  const fileViolations = [];
  const lines = content.split('\n');
  
  FORBIDDEN_PATTERNS.forEach(({ pattern, description, rule }) => {
    lines.forEach((line, index) => {
      const matches = line.match(pattern);
      if (matches) {
        // Vérifier si c'est dans un commentaire (à ignorer pour certains patterns)
        const isComment = /^\s*(\/\/|#|\*|<!--)/.test(line.trim());
        
        // Pour les patterns critiques (conversion SAKA/EUR), même dans les commentaires c'est interdit
        if (rule === 'SAKA_EUR_CONVERSION' || !isComment) {
          fileViolations.push({
            rule,
            file: filePath,
            line: index + 1,
            content: line.trim(),
            description,
            match: matches[0]
          });
        }
      }
    });
  });
  
  return fileViolations;
}

// ============================================================================
// EXÉCUTION PRINCIPALE
// ============================================================================

console.log('🔍 Audit BLOQUANT GLOBAL - EGOEJO Compliance\n');
console.log('Scanning frontend/src et backend/...\n');

// Scanner frontend/src
let frontendFiles = [];
if (statSync(FRONTEND_SRC, { throwIfNoEntry: false })) {
  console.log(`📁 Scanning ${FRONTEND_SRC}...`);
  frontendFiles = findScannableFiles(FRONTEND_SRC, FRONTEND_SRC);
  console.log(`   Found ${frontendFiles.length} files`);
}

// Scanner backend/
let backendFiles = [];
if (statSync(BACKEND_DIR, { throwIfNoEntry: false })) {
  console.log(`📁 Scanning ${BACKEND_DIR}...`);
  backendFiles = findScannableFiles(BACKEND_DIR, BACKEND_DIR);
  console.log(`   Found ${backendFiles.length} files`);
}

// Scanner tous les fichiers
const allFiles = [...frontendFiles, ...backendFiles];
console.log(`\n🔍 Scanning ${allFiles.length} files for forbidden patterns...\n`);

allFiles.forEach((filePath, index) => {
  if ((index + 1) % 100 === 0) {
    process.stdout.write(`   Progress: ${index + 1}/${allFiles.length}\r`);
  }
  
  const fileViolations = scanFile(filePath);
  violations.push(...fileViolations);
});

console.log(`\n✅ Scan complete. Found ${violations.length} violation(s).\n`);

// ============================================================================
// GÉNÉRATION DU RAPPORT
// ============================================================================

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
      console.log(`  Ligne: ${v.line}`);
      if (v.match) {
        console.log(`  Match: "${v.match}"`);
      }
      if (v.content) {
        console.log(`  Extrait: ${v.content.substring(0, 100)}${v.content.length > 100 ? '...' : ''}`);
      }
      console.log(`  Description: ${v.description}`);
    });
  });

  console.log('\n' + '='.repeat(80));
  console.log(`\n❌ Total: ${violations.length} violation(s) détectée(s)\n`);
  console.log('⚠️  ACTION REQUISE : Corriger toutes les violations avant de merger.\n');
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
      match: v.match || null,
      content: v.content ? v.content.substring(0, 200) : null,
      description: v.description
    })),
    timestamp: new Date().toISOString()
  };

  console.log(JSON.stringify(report, null, 2));
}

// Générer le rapport
if (JSON_OUTPUT) {
  generateJsonReport(violations);
} else {
  printTextReport(violations);
}

// Exit avec code d'erreur si violations
if (violations.length > 0) {
  process.exit(1);
} else {
  process.exit(0);
}


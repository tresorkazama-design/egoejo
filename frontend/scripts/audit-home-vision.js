#!/usr/bin/env node

/**
 * Script d'audit statique pour les pages Accueil et Vision
 * 
 * Vérifie les règles de conformité EGOEJO et génère un JSON de statut.
 * 
 * Usage: npm run audit:home-vision
 * 
 * Sortie JSON:
 * {
 *   status: "compliant" | "conditional" | "non-compliant",
 *   checks: [{id, ok, details}]
 * }
 */

import { readFileSync, readdirSync, statSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Chemins des fichiers à scanner
const ROOT_DIR = join(__dirname, '..');
const SRC_DIR = join(ROOT_DIR, 'src');
const LOCALES_DIR = join(SRC_DIR, 'locales');

// Fonction pour trouver tous les fichiers correspondant à un pattern
function findFiles(pattern, baseDir) {
  const files = [];
  try {
    const entries = readdirSync(baseDir, { withFileTypes: true, recursive: true });
    for (const entry of entries) {
      if (entry.isFile() && pattern.test(entry.name)) {
        const filePath = join(entry.path || baseDir, entry.name);
        // Exclure les fichiers de test (__tests__, *.test.jsx, *.spec.jsx)
        if (!filePath.includes('__tests__') && 
            !filePath.includes('.test.') && 
            !filePath.includes('.spec.')) {
          files.push(filePath);
        }
      }
    }
  } catch (error) {
    // Si erreur, on retourne les fichiers par défaut
  }
  return files;
}

// Fichiers à scanner : Home*.jsx, Vision*.jsx, Layout*.jsx
const PAGES_DIR = join(SRC_DIR, 'app', 'pages');
const COMPONENTS_DIR = join(SRC_DIR, 'components');

const FILES_TO_SCAN = [
  ...findFiles(/^Home.*\.jsx$/i, PAGES_DIR),
  ...findFiles(/^Vision.*\.jsx$/i, PAGES_DIR),
  ...findFiles(/^Layout.*\.jsx$/i, COMPONENTS_DIR),
].filter(file => {
  try {
    return statSync(file).isFile();
  } catch {
    return false;
  }
});

// Fichiers de traduction à vérifier
const LOCALE_FILES = [
  join(LOCALES_DIR, 'fr.json'),
  join(LOCALES_DIR, 'en.json'),
  join(LOCALES_DIR, 'es.json'),
  join(LOCALES_DIR, 'de.json'),
  join(LOCALES_DIR, 'ar.json'),
  join(LOCALES_DIR, 'sw.json'),
].filter(file => {
  try {
    return statSync(file).isFile();
  } catch {
    return false;
  }
});

// Clés i18n requises pour Vision
const REQUIRED_VISION_I18N_KEYS = {
  principles: [
    'vision.principles_title',
    'vision.principle_relational_title',
    'vision.principle_relational_desc',
    'vision.principle_anti_accumulation_title',
    'vision.principle_anti_accumulation_desc',
    'vision.principle_cycle_title',
    'vision.principle_cycle_desc',
  ],
  glossary: [
    'vision.glossary_title',
    'vision.glossary_vivant_term',
    'vision.glossary_vivant_def',
    'vision.glossary_gardiens_term',
    'vision.glossary_gardiens_def',
    'vision.glossary_alliance_term',
    'vision.glossary_alliance_def',
  ],
};

// Violations détectées
const violations = [];

// Résultats des checks (pour JSON)
const checks = [];

// Charger les règles depuis le fichier JSON
const RULES_FILE = join(__dirname, '..', '..', '..', 'docs', 'egoejo_compliance', 'home-vision.rules.json');
let rules = null;
try {
  rules = JSON.parse(readFileSync(RULES_FILE, 'utf-8'));
} catch (error) {
  console.error(`❌ Erreur : Impossible de charger les règles depuis ${RULES_FILE}`);
  console.error(`   ${error.message}`);
  process.exit(1);
}

/**
 * Lit un fichier et retourne son contenu
 */
function readFile(filePath) {
  try {
    return readFileSync(filePath, 'utf-8');
  } catch (error) {
    violations.push({
      file: filePath,
      line: 0,
      rule: 'FICHIER_INACCESSIBLE',
      message: `Impossible de lire le fichier : ${error.message}`,
    });
    return null;
  }
}

/**
 * Trouve le numéro de ligne d'une correspondance dans un fichier
 */
function getLineNumber(content, matchIndex) {
  return content.substring(0, matchIndex).split('\n').length;
}

/**
 * Vérifie "100 % des dons" sans "nets" ou mention de frais
 */
function checkDonationText() {
  const ruleId = 'donation_text_nets';
  const rule = rules.rules.find(r => r.id === ruleId);
  if (!rule) {
    checks.push({ id: ruleId, ok: false, details: 'Règle non trouvée dans rules.json' });
    return;
  }
  
  console.log('🔍 Vérification : "100 % des dons" sans "nets" ou mention de frais...');
  let hasViolation = false;
  const violationDetails = [];
  
  // Pattern pour détecter "100 % des dons" ou "100% des dons"
  const donationPattern = /100\s*%\s*des?\s*dons?/gi;
  
  // Patterns acceptables (avec "nets" ou mention de frais)
  const acceptablePatterns = [
    /100\s*%\s*des?\s*dons?\s*nets?/i,
    /100\s*%\s*des?\s*dons?\s*après\s*frais/i,
    /100\s*%\s*des?\s*dons?\s*net/i,
    /100\s*%\s*des?\s*dons?\s*after\s*fees/i,
    /100\s*%\s*des?\s*dons?\s*frais\s*plateforme/i,
    /100\s*%\s*des?\s*dons?\s*platform\s*fees/i,
  ];
  
  for (const filePath of FILES_TO_SCAN) {
    const content = readFile(filePath);
    if (!content) continue;
    
    // Chercher toutes les occurrences de "100 % des dons"
    let match;
    while ((match = donationPattern.exec(content)) !== null) {
      const matchText = match[0];
      const matchIndex = match.index;
      const lineNumber = getLineNumber(content, matchIndex);
      
      // Vérifier si c'est acceptable (contient "nets" ou mention de frais)
      const isAcceptable = acceptablePatterns.some(pattern => {
        // Vérifier dans un contexte plus large (50 caractères avant et après)
        const contextStart = Math.max(0, matchIndex - 50);
        const contextEnd = Math.min(content.length, matchIndex + matchText.length + 50);
        const context = content.substring(contextStart, contextEnd);
        return pattern.test(context);
      });
      
      if (!isAcceptable) {
        hasViolation = true;
        const relativePath = filePath.replace(ROOT_DIR + '/', '');
        violationDetails.push(`${relativePath}:${lineNumber} - "${matchText}" trouvé sans "nets" ou mention de frais`);
        violations.push({
          file: filePath,
          line: lineNumber,
          rule: 'DONATION_TEXT_MISSING_NETS',
          message: `"${matchText}" trouvé sans "nets" ou mention de frais. Le texte doit être "100% des dons nets (après frais de plateforme)" ou formulation équivalente.`,
        });
      }
    }
  }
  
  // Vérifier aussi dans les fichiers de traduction
  for (const localeFile of LOCALE_FILES) {
    const content = readFile(localeFile);
    if (!content) continue;
    
    // Parser le JSON pour vérifier la clé "home.soutenir_desc"
    try {
      const localeData = JSON.parse(content);
      if (localeData.home && localeData.home.soutenir_desc) {
        const soutenirDesc = localeData.home.soutenir_desc;
        
        // Vérifier si contient "100 % des dons" ou "100% des dons"
        const has100PercentDons = /100\s*%\s*des?\s*dons?/i.test(soutenirDesc);
        
        if (has100PercentDons) {
          // Vérifier si c'est acceptable
          const isAcceptable = acceptablePatterns.some(pattern => pattern.test(soutenirDesc));
          
          if (!isAcceptable) {
            hasViolation = true;
            const lineNumber = getLineNumber(content, content.indexOf(soutenirDesc));
            const relativePath = localeFile.replace(ROOT_DIR + '/', '');
            violationDetails.push(`${relativePath}:${lineNumber} - "100% des dons" dans home.soutenir_desc sans "nets" ou mention de frais`);
            violations.push({
              file: localeFile,
              line: lineNumber,
              rule: 'DONATION_TEXT_MISSING_NETS',
              message: `"100% des dons" trouvé dans home.soutenir_desc sans "nets" ou mention de frais. Le texte doit être "100% des dons nets (après frais de plateforme)" ou formulation équivalente.`,
            });
          }
        }
      }
    } catch (error) {
      // Erreur de parsing JSON, on ignore pour cette vérification
    }
  }
  
  checks.push({
    id: ruleId,
    ok: !hasViolation,
    details: hasViolation ? violationDetails.join('; ') : 'Aucune violation détectée',
    severity: rule.severity
  });
}

/**
 * Vérifie les clés i18n vision.principles_* et vision.glossary_*
 */
function checkVisionI18nKeys() {
  console.log('🔍 Vérification : Clés i18n vision.principles_* et vision.glossary_*...');
  
  // Vérifier les principes
  const principlesRule = rules.rules.find(r => r.id === 'vision_i18n_principles');
  if (principlesRule) {
    checkI18nKeysForRule(principlesRule);
  }
  
  // Vérifier le glossaire
  const glossaryRule = rules.rules.find(r => r.id === 'vision_i18n_glossary');
  if (glossaryRule) {
    checkI18nKeysForRule(glossaryRule);
  }
}

/**
 * Vérifie les clés i18n pour une règle donnée
 */
function checkI18nKeysForRule(rule) {
  const allRequiredKeys = rule.keys || [];
  let hasViolation = false;
  const violationDetails = [];
  
  for (const localeFile of LOCALE_FILES) {
    const content = readFile(localeFile);
    if (!content) continue;
    
    let localeData;
    try {
      localeData = JSON.parse(content);
    } catch (error) {
      violations.push({
        file: localeFile,
        line: 0,
        rule: 'INVALID_JSON',
        message: `Fichier JSON invalide : ${error.message}`,
      });
      continue;
    }
    
    // Vérifier chaque clé requise
    for (const key of allRequiredKeys) {
      const keys = key.split('.');
      let value = localeData;
      
      for (const k of keys) {
        if (value && typeof value === 'object' && k in value) {
          value = value[k];
        } else {
          value = null;
          break;
        }
      }
      
      if (!value || (typeof value === 'string' && value.trim() === '')) {
        hasViolation = true;
        const relativePath = localeFile.replace(ROOT_DIR + '/', '');
        violationDetails.push(`${relativePath} - Clé manquante: "${key}"`);
        violations.push({
          file: localeFile,
          line: 0, // JSON n'a pas de numéros de ligne précis
          rule: 'MISSING_I18N_KEY',
          message: `Clé i18n manquante : "${key}". Cette clé est requise pour la conformité éditoriale.`,
        });
      }
    }
  }
  
  checks.push({
    id: rule.id,
    ok: !hasViolation,
    details: hasViolation ? `${violationDetails.length} clé(s) manquante(s): ${violationDetails.slice(0, 3).join('; ')}${violationDetails.length > 3 ? '...' : ''}` : 'Toutes les clés i18n sont présentes',
    severity: rule.severity
  });
}

/**
 * Vérifie que le skip-link n'est pas hardcodé en FR dans Layout.jsx
 */
function checkSkipLinkHardcoded() {
  const ruleId = 'skip_link_i18n';
  const rule = rules.rules.find(r => r.id === ruleId);
  if (!rule) {
    checks.push({ id: ruleId, ok: false, details: 'Règle non trouvée dans rules.json' });
    return;
  }
  
  console.log('🔍 Vérification : Skip-link hardcodé en FR dans Layout.jsx...');
  
  const layoutPath = join(SRC_DIR, 'components', 'Layout.jsx');
  const content = readFile(layoutPath);
  if (!content) {
    checks.push({ id: ruleId, ok: false, details: 'Impossible de lire Layout.jsx', severity: rule.severity });
    return;
  }
  
  let hasViolation = false;
  const violationDetails = [];
  
  // Pattern pour détecter "Aller au contenu principal" hardcodé
  // On cherche le texte en dehors d'un appel à t() ou dans un JSX direct
  const hardcodedPattern = />\s*Aller au contenu principal\s*</;
  
  // Vérifier si le skip-link utilise t("accessibility.skip_to_main", language)
  const usesTranslation = /t\(["']accessibility\.skip_to_main["']/i.test(content);
  
  // Si le texte hardcodé est présent ET que la traduction n'est pas utilisée
  if (hardcodedPattern.test(content) && !usesTranslation) {
    hasViolation = true;
    const match = content.match(hardcodedPattern);
    if (match) {
      const matchIndex = content.indexOf(match[0]);
      const lineNumber = getLineNumber(content, matchIndex);
      const relativePath = layoutPath.replace(ROOT_DIR + '/', '');
      violationDetails.push(`${relativePath}:${lineNumber} - Skip-link hardcodé en FR sans traduction`);
      
      violations.push({
        file: layoutPath,
        line: lineNumber,
        rule: 'SKIP_LINK_HARDCODED_FR',
        message: 'Le skip-link est hardcodé en français "Aller au contenu principal" au lieu d\'utiliser t("accessibility.skip_to_main", language).',
      });
    }
  }
  
  // Vérifier aussi si le texte hardcodé existe même si la traduction est utilisée (doublon)
  if (hardcodedPattern.test(content) && usesTranslation) {
    hasViolation = true;
    const match = content.match(hardcodedPattern);
    if (match) {
      const matchIndex = content.indexOf(match[0]);
      const lineNumber = getLineNumber(content, matchIndex);
      const relativePath = layoutPath.replace(ROOT_DIR + '/', '');
      violationDetails.push(`${relativePath}:${lineNumber} - Skip-link contient texte hardcodé même avec traduction`);
      
      violations.push({
        file: layoutPath,
        line: lineNumber,
        rule: 'SKIP_LINK_HARDCODED_FR_DUPLICATE',
        message: 'Le skip-link contient du texte hardcodé "Aller au contenu principal" même si la traduction est utilisée. Supprimez le texte hardcodé.',
      });
    }
  }
  
  checks.push({
    id: ruleId,
    ok: !hasViolation,
    details: hasViolation ? violationDetails.join('; ') : 'Skip-link utilise correctement la traduction i18n',
    severity: rule.severity
  });
}

/**
 * Détermine le statut de conformité
 */
function determineStatus() {
  const criticalChecks = checks.filter(c => c.severity === 'critical');
  const highChecks = checks.filter(c => c.severity === 'high');
  
  // Si au moins une règle critical échoue → non-compliant
  if (criticalChecks.some(c => !c.ok)) {
    return 'non-compliant';
  }
  
  // Si toutes les règles critical passent mais certaines high/medium échouent → conditional
  if (highChecks.some(c => !c.ok)) {
    return 'conditional';
  }
  
  // Si toutes les règles critical et high passent → compliant
  return 'compliant';
}

/**
 * Génère un rapport des violations
 */
function generateReport() {
  console.log('\n' + '='.repeat(80));
  console.log('📊 RAPPORT D\'AUDIT - Pages Accueil & Vision');
  console.log('='.repeat(80) + '\n');
  
  if (violations.length === 0) {
    console.log('✅ Aucune violation détectée. Toutes les règles sont respectées.\n');
    return true;
  }
  
  console.log(`❌ ${violations.length} violation(s) détectée(s) :\n`);
  
  // Grouper par règle
  const violationsByRule = {};
  for (const violation of violations) {
    if (!violationsByRule[violation.rule]) {
      violationsByRule[violation.rule] = [];
    }
    violationsByRule[violation.rule].push(violation);
  }
  
  // Afficher par règle
  for (const [rule, ruleViolations] of Object.entries(violationsByRule)) {
    console.log(`\n🔴 Règle violée : ${rule}`);
    console.log(`   Nombre de violations : ${ruleViolations.length}\n`);
    
    for (const violation of ruleViolations) {
      const relativePath = violation.file.replace(ROOT_DIR + '/', '');
      console.log(`   📄 Fichier : ${relativePath}`);
      if (violation.line > 0) {
        console.log(`   📍 Ligne   : ${violation.line}`);
      }
      console.log(`   ⚠️  Message : ${violation.message}`);
      console.log('');
    }
  }
  
  console.log('='.repeat(80));
  console.log(`\n❌ ÉCHEC : ${violations.length} violation(s) détectée(s).`);
  console.log('Corrigez ces violations avant de continuer.\n');
  
  return false;
}

/**
 * Génère le JSON de statut
 */
function generateStatusJSON() {
  const status = determineStatus();
  const statusJSON = {
    status: status,
    checks: checks,
    timestamp: new Date().toISOString(),
    version: rules.version
  };
  
  // Écrire le JSON dans un fichier
  const statusFile = join(ROOT_DIR, 'compliance-status.json');
  writeFileSync(statusFile, JSON.stringify(statusJSON, null, 2), 'utf-8');
  
  // Afficher le JSON sur stdout (pour CI)
  console.log('\n📋 STATUT DE CONFORMITÉ (JSON):');
  console.log(JSON.stringify(statusJSON, null, 2));
  
  return statusJSON;
}

/**
 * Fonction principale
 */
function main() {
  console.log('🛡️  Audit Compliance - Pages Accueil & Vision\n');
  console.log('Vérification des règles de conformité...\n');
  
  // Exécuter toutes les vérifications
  checkDonationText();
  checkVisionI18nKeys();
  checkSkipLinkHardcoded();
  
  // Générer le JSON de statut
  const statusJSON = generateStatusJSON();
  
  // Générer le rapport
  const success = generateReport();
  
  // Afficher le statut final
  console.log('\n' + '='.repeat(80));
  console.log(`📊 STATUT FINAL : ${statusJSON.status.toUpperCase()}`);
  console.log('='.repeat(80));
  
  // Exit avec code d'erreur si non-compliant
  if (statusJSON.status === 'non-compliant') {
    console.log('\n❌ ÉCHEC : Statut non-compliant. Au moins une règle critical a échoué.\n');
    process.exit(1);
  }
  
  if (statusJSON.status === 'conditional') {
    console.log('\n⚠️  ATTENTION : Statut conditional. Toutes les règles critical passent, mais certaines règles high/medium échouent.\n');
    // En mode CI, on peut choisir de bloquer aussi sur conditional
    if (process.env.CI && process.env.FAIL_ON_CONDITIONAL === 'true') {
      process.exit(1);
    }
  }
  
  if (statusJSON.status === 'compliant') {
    console.log('\n✅ SUCCÈS : Statut compliant. Toutes les règles critical et high sont respectées.\n');
  }
  
  process.exit(0);
}

// Exécuter le script
main();


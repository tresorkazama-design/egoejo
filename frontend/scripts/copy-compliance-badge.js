#!/usr/bin/env node

/**
 * Script pour copier le badge de conformité approprié selon le statut
 * 
 * Usage: node scripts/copy-compliance-badge.js
 */

import { readFileSync, copyFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const ROOT_DIR = join(__dirname, '..');
const STATUS_FILE = join(ROOT_DIR, 'compliance-status.json');
const BADGES_DIR = join(ROOT_DIR, 'public', 'badges');
const CURRENT_BADGE = join(BADGES_DIR, 'egoejo-compliant-current.svg');

try {
  const statusData = JSON.parse(readFileSync(STATUS_FILE, 'utf-8'));
  const status = statusData.status;
  
  let sourceBadge;
  if (status === 'compliant') {
    sourceBadge = join(BADGES_DIR, 'egoejo-compliant.svg');
  } else if (status === 'conditional') {
    sourceBadge = join(BADGES_DIR, 'egoejo-conditional.svg');
  } else {
    sourceBadge = join(BADGES_DIR, 'egoejo-non-compliant.svg');
  }
  
  copyFileSync(sourceBadge, CURRENT_BADGE);
  console.log(`✅ Badge copié : ${status} → egoejo-compliant-current.svg`);
} catch (error) {
  console.error(`❌ Erreur : ${error.message}`);
  process.exit(1);
}


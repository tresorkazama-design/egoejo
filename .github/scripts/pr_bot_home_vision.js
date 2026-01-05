#!/usr/bin/env node

/**
 * PR Bot GitHub - EGOEJO Compliant (Home/Vision)
 * 
 * Commente la PR et ajoute un label selon le statut de conformité.
 * Gestion idempotente : met à jour le commentaire existant au lieu d'en créer plusieurs.
 * 
 * Usage: node .github/scripts/pr_bot_home_vision.js
 * 
 * Variables d'environnement requises:
 * - GITHUB_TOKEN: Token GitHub avec permissions pull-requests:write, issues:write
 * - PR_NUMBER: Numéro de la PR
 * - STATUS: Statut de conformité (compliant, conditional, non-compliant)
 */

import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Variables d'environnement
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const PR_NUMBER = process.env.PR_NUMBER;
const STATUS = process.env.STATUS || 'non-compliant';

// Repository info
const REPO_OWNER = process.env.GITHUB_REPOSITORY?.split('/')[0] || 'egoejo';
const REPO_NAME = process.env.GITHUB_REPOSITORY?.split('/')[1] || 'egoejo';

// API GitHub
const GITHUB_API = 'https://api.github.com';

// Chemins
const ROOT_DIR = join(__dirname, '..', '..');
const AUDIT_RESULT_FILE = join(ROOT_DIR, 'frontend', 'frontend', 'audit-result.json');

/**
 * Lit le fichier audit-result.json
 */
function readAuditResult() {
  try {
    let content = readFileSync(AUDIT_RESULT_FILE, 'utf-8');
    
    // Supprimer le BOM UTF-8 si présent
    if (content.charCodeAt(0) === 0xFEFF) {
      content = content.slice(1);
    }
    
    // Nettoyer le contenu (supprimer les lignes avant le premier {)
    const jsonStart = content.indexOf('{');
    if (jsonStart > 0) {
      content = content.substring(jsonStart);
    }
    
    // Trouver le dernier } pour extraire uniquement le JSON valide
    const jsonEnd = content.lastIndexOf('}');
    if (jsonEnd > 0) {
      content = content.substring(0, jsonEnd + 1);
    }
    
    return JSON.parse(content);
  } catch (error) {
    console.error(`⚠️  Impossible de lire ${AUDIT_RESULT_FILE}`);
    console.error(`   ${error.message}`);
    return null;
  }
}

/**
 * Détermine le statut final (compliant, conditional, non-compliant)
 */
function determineStatus(auditData) {
  if (!auditData) {
    return 'non-compliant';
  }
  
  const status = auditData.status || STATUS;
  const violations = auditData.violations || [];
  
  // Si pas de violations → compliant
  if (violations.length === 0) {
    return 'compliant';
  }
  
  // Si violations → non-compliant (le script audit-home-vision.mjs ne distingue pas conditional)
  // Pour l'instant, on considère que toute violation est non-compliant
  // TODO: Améliorer pour distinguer critical vs high/medium si nécessaire
  return 'non-compliant';
}

/**
 * Génère le commentaire pour la PR
 */
function generateComment(auditData, finalStatus) {
  const violations = auditData?.violations || [];
  const violationsCount = violations.length;
  
  let emoji = '🔴';
  let label = 'EGOEJO Non Compliant';
  let title = '❌ Non Conforme';
  let description = 'Au moins une violation a été détectée.';
  
  if (finalStatus === 'compliant') {
    emoji = '🟢';
    label = 'EGOEJO Compliant';
    title = '✅ Conforme';
    description = 'Toutes les vérifications sont passées. Les pages Accueil et Vision respectent les exigences de conformité EGOEJO.';
  } else if (finalStatus === 'conditional') {
    emoji = '🟡';
    label = 'EGOEJO Conditional';
    title = '⚠️ Conditionnel';
    description = 'Toutes les vérifications critiques passent, mais certaines vérifications non-critiques échouent.';
  }
  
  let comment = `## ${emoji} Statut EGOEJO Compliant - Pages Accueil/Vision\n\n`;
  comment += `**${title}**\n\n`;
  comment += `${description}\n\n`;
  comment += `---\n\n`;
  comment += `### 📊 Résumé des Vérifications\n\n`;
  comment += `- **Statut** : \`${finalStatus}\`\n`;
  comment += `- **Violations détectées** : ${violationsCount}\n\n`;
  
  // Détails des violations
  if (violations.length > 0) {
    comment += `### ❌ Violations Détectées\n\n`;
    
    // Grouper par règle
    const violationsByRule = {};
    violations.forEach(v => {
      if (!violationsByRule[v.rule]) {
        violationsByRule[v.rule] = [];
      }
      violationsByRule[v.rule].push(v);
    });
    
    for (const [rule, ruleViolations] of Object.entries(violationsByRule)) {
      comment += `#### 🔴 ${rule}\n\n`;
      comment += `**${ruleViolations.length} violation(s)**\n\n`;
      
      ruleViolations.forEach((v, index) => {
        comment += `${index + 1}. **Fichier** : \`${v.file}\`\n`;
        if (v.line > 0) {
          comment += `   - Ligne : ${v.line}\n`;
        }
        if (v.key) {
          comment += `   - Clé i18n : \`${v.key}\`\n`;
        }
        if (v.content) {
          comment += `   - Extrait : \`${v.content.substring(0, 100)}${v.content.length > 100 ? '...' : ''}\`\n`;
        }
        comment += `   - Description : ${v.description}\n\n`;
      });
    }
  } else {
    comment += `### ✅ Toutes les Vérifications Sont Conformes\n\n`;
    comment += `Les pages Accueil et Vision respectent toutes les exigences de l'audit de conformité EGOEJO.\n\n`;
  }
  
  comment += `---\n\n`;
  comment += `**Timestamp** : ${auditData?.timestamp || new Date().toISOString()}\n`;
  comment += `**Bot** : 🤖 EGOEJO PR Bot (Home/Vision)\n`;
  
  return { comment, label };
}

/**
 * Trouve ou crée un commentaire existant du bot
 */
async function findOrCreateComment(commentBody) {
  const commentsUrl = `${GITHUB_API}/repos/${REPO_OWNER}/${REPO_NAME}/issues/${PR_NUMBER}/comments`;
  
  // Récupérer tous les commentaires
  const commentsResponse = await fetch(commentsUrl, {
    headers: {
      'Authorization': `token ${GITHUB_TOKEN}`,
      'Accept': 'application/vnd.github.v3+json',
    },
  });
  
  if (!commentsResponse.ok) {
    console.error(`❌ Erreur : Impossible de récupérer les commentaires (${commentsResponse.status})`);
    return null;
  }
  
  const comments = await commentsResponse.json();
  
  // Chercher un commentaire existant du bot (identifié par le titre)
  const botComment = comments.find(c => 
    c.body.includes('Statut EGOEJO Compliant - Pages Accueil/Vision') ||
    c.body.includes('🤖 EGOEJO PR Bot (Home/Vision)')
  );
  
  if (botComment) {
    // Mettre à jour le commentaire existant
    const updateUrl = `${GITHUB_API}/repos/${REPO_OWNER}/${REPO_NAME}/issues/comments/${botComment.id}`;
    const updateResponse = await fetch(updateUrl, {
      method: 'PATCH',
      headers: {
        'Authorization': `token ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ body: commentBody }),
    });
    
    if (updateResponse.ok) {
      console.log('✅ Commentaire mis à jour sur la PR');
      return botComment.id;
    } else {
      const errorText = await updateResponse.text();
      console.error(`❌ Erreur : Impossible de mettre à jour le commentaire (${updateResponse.status})`);
      console.error(`   ${errorText}`);
      return null;
    }
  } else {
    // Créer un nouveau commentaire
    const createResponse = await fetch(commentsUrl, {
      method: 'POST',
      headers: {
        'Authorization': `token ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ body: commentBody }),
    });
    
    if (createResponse.ok) {
      const newComment = await createResponse.json();
      console.log('✅ Commentaire ajouté sur la PR');
      return newComment.id;
    } else {
      const errorText = await createResponse.text();
      console.error(`❌ Erreur : Impossible de créer le commentaire (${createResponse.status})`);
      console.error(`   ${errorText}`);
      return null;
    }
  }
}

/**
 * Crée le label s'il n'existe pas
 */
async function ensureLabelExists(labelName, labelColor, labelDescription) {
  const labelsUrl = `${GITHUB_API}/repos/${REPO_OWNER}/${REPO_NAME}/labels`;
  
  // Vérifier si le label existe
  const labelsResponse = await fetch(labelsUrl, {
    headers: {
      'Authorization': `token ${GITHUB_TOKEN}`,
      'Accept': 'application/vnd.github.v3+json',
    },
  });
  
  if (!labelsResponse.ok) {
    console.error(`⚠️  Impossible de récupérer les labels (${labelsResponse.status})`);
    return false;
  }
  
  const labels = await labelsResponse.json();
  const labelExists = labels.find(l => l.name === labelName);
  
  if (!labelExists) {
    // Créer le label
    const createLabelResponse = await fetch(labelsUrl, {
      method: 'POST',
      headers: {
        'Authorization': `token ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: labelName,
        color: labelColor,
        description: labelDescription,
      }),
    });
    
    if (createLabelResponse.ok) {
      console.log(`✅ Label créé : ${labelName}`);
      return true;
    } else {
      const errorText = await createLabelResponse.text();
      console.error(`⚠️  Impossible de créer le label (${createLabelResponse.status})`);
      console.error(`   ${errorText}`);
      return false;
    }
  }
  
  return true;
}

/**
 * Met à jour les labels de la PR
 */
async function updatePRLabels(targetLabel) {
  // Labels de conformité à gérer
  const complianceLabels = [
    'EGOEJO Compliant',
    'EGOEJO Conditional',
    'EGOEJO Non Compliant'
  ];
  
  // Couleurs et descriptions pour chaque label
  const labelConfig = {
    'EGOEJO Compliant': {
      color: '28a745',
      description: 'Pages Accueil/Vision conformes aux exigences EGOEJO'
    },
    'EGOEJO Conditional': {
      color: 'fbca04',
      description: 'Pages Accueil/Vision conditionnellement conformes (vérifications non-critiques en échec)'
    },
    'EGOEJO Non Compliant': {
      color: 'd73a4a',
      description: 'Pages Accueil/Vision non conformes (violations détectées)'
    }
  };
  
  // Créer le label s'il n'existe pas
  const config = labelConfig[targetLabel];
  if (config) {
    await ensureLabelExists(targetLabel, config.color, config.description);
  }
  
  // Récupérer les labels actuels de la PR
  const issueUrl = `${GITHUB_API}/repos/${REPO_OWNER}/${REPO_NAME}/issues/${PR_NUMBER}`;
  const issueResponse = await fetch(issueUrl, {
    headers: {
      'Authorization': `token ${GITHUB_TOKEN}`,
      'Accept': 'application/vnd.github.v3+json',
    },
  });
  
  if (!issueResponse.ok) {
    console.error(`❌ Erreur : Impossible de récupérer la PR (${issueResponse.status})`);
    return;
  }
  
  const issue = await issueResponse.json();
  const currentLabels = issue.labels.map(l => l.name);
  
  // Retirer les anciens labels de conformité
  const labelsToSet = currentLabels.filter(l => !complianceLabels.includes(l));
  
  // Ajouter le nouveau label
  if (!labelsToSet.includes(targetLabel)) {
    labelsToSet.push(targetLabel);
  }
  
  // Mettre à jour les labels
  const updateLabelsUrl = `${GITHUB_API}/repos/${REPO_OWNER}/${REPO_NAME}/issues/${PR_NUMBER}`;
  const updateLabelsResponse = await fetch(updateLabelsUrl, {
    method: 'PATCH',
    headers: {
      'Authorization': `token ${GITHUB_TOKEN}`,
      'Accept': 'application/vnd.github.v3+json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ labels: labelsToSet }),
  });
  
  if (updateLabelsResponse.ok) {
    console.log(`✅ Label mis à jour : ${targetLabel}`);
  } else {
    const errorText = await updateLabelsResponse.text();
    console.error(`❌ Erreur : Impossible de mettre à jour le label (${updateLabelsResponse.status})`);
    console.error(`   ${errorText}`);
  }
}

/**
 * Fonction principale
 */
async function main() {
  console.log('🤖 PR Bot - EGOEJO Compliant (Home/Vision)\n');
  
  // Vérifier les variables d'environnement
  if (!GITHUB_TOKEN) {
    console.error('❌ Erreur : GITHUB_TOKEN non défini');
    process.exit(1);
  }
  
  if (!PR_NUMBER) {
    console.error('❌ Erreur : PR_NUMBER non défini');
    process.exit(1);
  }
  
  console.log(`📋 PR #${PR_NUMBER}`);
  console.log(`📊 Statut initial : ${STATUS}\n`);
  
  // Lire le fichier de résultat d'audit
  const auditData = readAuditResult();
  const finalStatus = determineStatus(auditData);
  
  console.log(`🔍 Statut final : ${finalStatus}\n`);
  
  // Générer le commentaire
  const { comment, label } = generateComment(auditData || { violations: [] }, finalStatus);
  
  // Commenter la PR (idempotent : met à jour si existe, crée sinon)
  await findOrCreateComment(comment);
  
  // Mettre à jour le label
  await updatePRLabels(label);
  
  console.log('\n✅ PR Bot terminé');
}

// Exécuter le script
main().catch(error => {
  console.error('❌ Erreur fatale :', error);
  process.exit(1);
});

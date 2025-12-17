/**
 * Script pour exécuter Lighthouse CI et vérifier les métriques de performance
 */
import { execSync } from 'child_process';
import { logger } from '../src/utils/logger.js';

const LIGHTHOUSE_THRESHOLDS = {
  performance: 90,
  accessibility: 95,
  'best-practices': 90,
  seo: 90,
};

async function runLighthouse() {
  try {
    logger.info('Démarrage de Lighthouse CI...');
    
    // Vérifier si Lighthouse CI est installé
    try {
      execSync('which lhci', { stdio: 'ignore' });
    } catch {
      logger.warn('Lighthouse CI n\'est pas installé. Installation...');
      execSync('npm install -g @lhci/cli', { stdio: 'inherit' });
    }
    
    // Exécuter Lighthouse
    const result = execSync('lhci autorun', { 
      encoding: 'utf-8',
      stdio: 'pipe',
    });
    
    logger.info('Lighthouse CI terminé avec succès');
    console.log(result);
    
    return true;
  } catch (error) {
    logger.error('Erreur lors de l\'exécution de Lighthouse CI:', error);
    return false;
  }
}

// Exécuter seulement si appelé directement
if (import.meta.url === `file://${process.argv[1]}`) {
  runLighthouse();
}

export { runLighthouse, LIGHTHOUSE_THRESHOLDS };


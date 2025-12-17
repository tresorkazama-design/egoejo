#!/usr/bin/env node

/**
 * Script de test de performance
 * Analyse le bundle et les métriques de performance
 */

import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(__dirname, '..');

console.log('🔍 Analyse de Performance - EGOEJO\n');
console.log('═══════════════════════════════════════════════════════════════\n');

// Vérifier si le build existe
const distPath = join(projectRoot, 'dist');
if (!existsSync(distPath)) {
  console.log('⚠️  Le dossier dist/ n\'existe pas.');
  console.log('   Lancez d\'abord: npm run build\n');
  process.exit(1);
}

// Analyser les fichiers du build
import { readdirSync, statSync } from 'fs';

const analyzeBundle = () => {
  console.log('📦 Analyse du Bundle\n');
  
  const files = [];
  const walkDir = (dir, basePath = '') => {
    const entries = readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = join(dir, entry.name);
      const relativePath = join(basePath, entry.name);
      
      if (entry.isDirectory()) {
        walkDir(fullPath, relativePath);
      } else {
        const stats = statSync(fullPath);
        files.push({
          path: relativePath,
          size: stats.size,
          sizeKB: (stats.size / 1024).toFixed(2),
          sizeMB: (stats.size / (1024 * 1024)).toFixed(2),
        });
      }
    }
  };
  
  walkDir(distPath);
  
  // Grouper par type
  const jsFiles = files.filter(f => f.path.endsWith('.js'));
  const cssFiles = files.filter(f => f.path.endsWith('.css'));
  const imageFiles = files.filter(f => /\.(png|jpg|jpeg|svg|gif|webp)$/i.test(f.path));
  const otherFiles = files.filter(f => 
    !f.path.endsWith('.js') && 
    !f.path.endsWith('.css') && 
    !/\.(png|jpg|jpeg|svg|gif|webp)$/i.test(f.path)
  );
  
  const totalSize = files.reduce((sum, f) => sum + f.size, 0);
  const totalSizeKB = (totalSize / 1024).toFixed(2);
  const totalSizeMB = (totalSize / (1024 * 1024)).toFixed(2);
  
  console.log(`📊 Taille totale: ${totalSizeMB} MB (${totalSizeKB} KB)\n`);
  
  // JavaScript
  const jsTotal = jsFiles.reduce((sum, f) => sum + f.size, 0);
  const jsTotalKB = (jsTotal / 1024).toFixed(2);
  console.log(`📜 JavaScript:`);
  console.log(`   Total: ${jsTotalKB} KB`);
  console.log(`   Fichiers: ${jsFiles.length}`);
  if (jsFiles.length > 0) {
    const largest = jsFiles.sort((a, b) => b.size - a.size).slice(0, 5);
    console.log(`   Plus gros fichiers:`);
    largest.forEach(f => {
      console.log(`     - ${f.path}: ${f.sizeKB} KB`);
    });
  }
  console.log();
  
  // CSS
  const cssTotal = cssFiles.reduce((sum, f) => sum + f.size, 0);
  const cssTotalKB = (cssTotal / 1024).toFixed(2);
  console.log(`🎨 CSS:`);
  console.log(`   Total: ${cssTotalKB} KB`);
  console.log(`   Fichiers: ${cssFiles.length}`);
  console.log();
  
  // Images
  const imgTotal = imageFiles.reduce((sum, f) => sum + f.size, 0);
  const imgTotalKB = (imgTotal / 1024).toFixed(2);
  console.log(`🖼️  Images:`);
  console.log(`   Total: ${imgTotalKB} KB`);
  console.log(`   Fichiers: ${imageFiles.length}`);
  console.log();
  
  // Autres
  const otherTotal = otherFiles.reduce((sum, f) => sum + f.size, 0);
  const otherTotalKB = (otherTotal / 1024).toFixed(2);
  if (otherFiles.length > 0) {
    console.log(`📄 Autres:`);
    console.log(`   Total: ${otherTotalKB} KB`);
    console.log(`   Fichiers: ${otherFiles.length}`);
    console.log();
  }
  
  // Vérifier le code splitting
  const vendorChunks = jsFiles.filter(f => 
    f.path.includes('vendor') || 
    f.path.includes('react') || 
    f.path.includes('three') || 
    f.path.includes('gsap')
  );
  
  if (vendorChunks.length > 0) {
    console.log(`✅ Code Splitting détecté:`);
    vendorChunks.forEach(f => {
      console.log(`   - ${f.path}: ${f.sizeKB} KB`);
    });
    console.log();
  }
  
  // Recommandations
  console.log('💡 Recommandations:\n');
  
  if (jsTotal > 500 * 1024) {
    console.log('   ⚠️  Le bundle JS est > 500KB. Considérez:');
    console.log('      - Lazy loading supplémentaire');
    console.log('      - Tree shaking plus agressif');
    console.log('      - Compression Brotli');
  } else {
    console.log('   ✅ Bundle JS optimisé (< 500KB)');
  }
  
  if (imgTotal > 1000 * 1024) {
    console.log('   ⚠️  Les images sont > 1MB. Considérez:');
    console.log('      - Conversion en WebP');
    console.log('      - Compression des images');
    console.log('      - Lazy loading des images');
  } else {
    console.log('   ✅ Images optimisées');
  }
  
  console.log();
};

// Vérifier le service worker
const checkServiceWorker = () => {
  console.log('🔧 Vérification du Service Worker\n');
  
  const swPath = join(distPath, 'sw.js');
  const swManifest = join(distPath, 'manifest.webmanifest');
  
  if (existsSync(swPath)) {
    const swSize = statSync(swPath).size;
    console.log(`   ✅ Service Worker trouvé: ${(swSize / 1024).toFixed(2)} KB`);
  } else {
    console.log('   ⚠️  Service Worker non trouvé');
    console.log('      Le service worker est généré lors du build avec vite-plugin-pwa');
  }
  
  if (existsSync(swManifest)) {
    console.log(`   ✅ Manifest trouvé`);
  } else {
    console.log('   ⚠️  Manifest non trouvé');
  }
  
  console.log();
};

// Vérifier les optimisations
const checkOptimizations = () => {
  console.log('⚡ Vérification des Optimisations\n');
  
  const indexHtml = join(distPath, 'index.html');
  if (existsSync(indexHtml)) {
    const content = readFileSync(indexHtml, 'utf-8');
    
    // Vérifier preload
    if (content.includes('rel="preload"')) {
      console.log('   ✅ Preload détecté');
    } else {
      console.log('   ⚠️  Preload non détecté dans index.html');
    }
    
    // Vérifier modulepreload
    if (content.includes('rel="modulepreload"')) {
      console.log('   ✅ Modulepreload détecté');
    }
    
    // Vérifier preconnect
    if (content.includes('rel="preconnect"')) {
      console.log('   ✅ Preconnect détecté');
    }
  }
  
  console.log();
};

// Exécuter les analyses
try {
  analyzeBundle();
  checkServiceWorker();
  checkOptimizations();
  
  console.log('✅ Analyse terminée!\n');
  console.log('💡 Pour un audit complet, utilisez:');
  console.log('   - Lighthouse (Chrome DevTools)');
  console.log('   - npm run build -- --mode analyze (si configuré)');
  console.log('   - WebPageTest (https://www.webpagetest.org/)\n');
} catch (error) {
  console.error('❌ Erreur lors de l\'analyse:', error.message);
  process.exit(1);
}


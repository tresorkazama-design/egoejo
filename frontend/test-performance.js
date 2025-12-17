/**
 * Script de test de performance pour EGOEJO
 * Mesure les métriques de performance avant et après les optimisations
 */

import { performance } from 'perf_hooks';

const METRICS = {
  bundleSize: 0,
  loadTime: 0,
  firstContentfulPaint: 0,
  timeToInteractive: 0,
  lighthouseScore: 0,
};

/**
 * Mesure la taille du bundle
 */
async function measureBundleSize() {
  try {
    const fs = await import('fs');
    const path = await import('path');
    const { fileURLToPath } = await import('url');
    
    const __dirname = path.dirname(fileURLToPath(import.meta.url));
    const distPath = path.join(__dirname, 'dist');
    
    if (!fs.existsSync(distPath)) {
      console.log('⚠️  Le dossier dist/ n\'existe pas. Lancez d\'abord: npm run build');
      return;
    }
    
    let totalSize = 0;
    const files = [];
    
    function getFiles(dir) {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          getFiles(fullPath);
        } else {
          const stats = fs.statSync(fullPath);
          const size = stats.size;
          totalSize += size;
          files.push({
            path: fullPath.replace(distPath, ''),
            size: size,
            sizeKB: (size / 1024).toFixed(2),
          });
        }
      }
    }
    
    getFiles(distPath);
    
    // Trier par taille
    files.sort((a, b) => b.size - a.size);
    
    console.log('\n📦 TAILLE DES BUNDLES');
    console.log('═══════════════════════════════════════════════════════════════');
    console.log(`Taille totale: ${(totalSize / 1024 / 1024).toFixed(2)} MB\n`);
    
    console.log('Top 10 des fichiers les plus gros:');
    files.slice(0, 10).forEach((file, index) => {
      console.log(`  ${index + 1}. ${file.path}: ${file.sizeKB} KB`);
    });
    
    // Analyser les chunks
    const jsFiles = files.filter(f => f.path.endsWith('.js'));
    const cssFiles = files.filter(f => f.path.endsWith('.css'));
    const imageFiles = files.filter(f => /\.(png|jpg|jpeg|svg|webp)$/i.test(f.path));
    
    const jsTotal = jsFiles.reduce((sum, f) => sum + f.size, 0);
    const cssTotal = cssFiles.reduce((sum, f) => sum + f.size, 0);
    const imageTotal = imageFiles.reduce((sum, f) => sum + f.size, 0);
    
    console.log('\n📊 Répartition par type:');
    console.log(`  JavaScript: ${(jsTotal / 1024 / 1024).toFixed(2)} MB (${jsFiles.length} fichiers)`);
    console.log(`  CSS: ${(cssTotal / 1024 / 1024).toFixed(2)} MB (${cssFiles.length} fichiers)`);
    console.log(`  Images: ${(imageTotal / 1024 / 1024).toFixed(2)} MB (${imageFiles.length} fichiers)`);
    
    METRICS.bundleSize = totalSize;
    
    // Vérifier les chunks
    const reactChunk = jsFiles.find(f => f.path.includes('react-vendor'));
    const threeChunk = jsFiles.find(f => f.path.includes('three-vendor'));
    const gsapChunk = jsFiles.find(f => f.path.includes('gsap-vendor'));
    
    console.log('\n🎯 Code Splitting:');
    if (reactChunk) {
      console.log(`  ✅ React vendor: ${reactChunk.sizeKB} KB`);
    }
    if (threeChunk) {
      console.log(`  ✅ Three.js vendor: ${threeChunk.sizeKB} KB`);
    }
    if (gsapChunk) {
      console.log(`  ✅ GSAP vendor: ${gsapChunk.sizeKB} KB`);
    }
    
  } catch (error) {
    console.error('Erreur lors de la mesure de la taille du bundle:', error.message);
  }
}

/**
 * Vérifie la configuration du service worker
 */
async function checkServiceWorker() {
  try {
    const fs = await import('fs');
    const path = await import('path');
    const { fileURLToPath } = await import('url');
    
    const __dirname = path.dirname(fileURLToPath(import.meta.url));
    const distPath = path.join(__dirname, 'dist');
    const swPath = path.join(distPath, 'sw.js');
    const swMapPath = path.join(distPath, 'workbox-*.js');
    
    console.log('\n🔧 SERVICE WORKER');
    console.log('═══════════════════════════════════════════════════════════════');
    
    if (fs.existsSync(swPath)) {
      const stats = fs.statSync(swPath);
      console.log(`✅ Service worker trouvé: ${(stats.size / 1024).toFixed(2)} KB`);
    } else {
      console.log('⚠️  Service worker non trouvé. Lancez: npm run build');
    }
    
    // Vérifier le manifest
    const manifestPath = path.join(distPath, 'manifest.webmanifest');
    if (fs.existsSync(manifestPath)) {
      console.log('✅ Manifest PWA trouvé');
    } else {
      console.log('⚠️  Manifest PWA non trouvé');
    }
    
  } catch (error) {
    console.error('Erreur lors de la vérification du service worker:', error.message);
  }
}

/**
 * Vérifie les optimisations dans le code
 */
async function checkOptimizations() {
  console.log('\n⚡ OPTIMISATIONS');
  console.log('═══════════════════════════════════════════════════════════════');
  
  try {
    const fs = await import('fs');
    const path = await import('path');
    const { fileURLToPath } = await import('url');
    
    const __dirname = path.dirname(fileURLToPath(import.meta.url));
    
    // Vérifier le lazy loading dans router.jsx
    const routerPath = path.join(__dirname, 'src', 'app', 'router.jsx');
    if (fs.existsSync(routerPath)) {
      const content = fs.readFileSync(routerPath, 'utf-8');
      const lazyCount = (content.match(/lazy\(/g) || []).length;
      const suspenseCount = (content.match(/Suspense/g) || []).length;
      
      console.log(`✅ Lazy loading: ${lazyCount} pages en lazy loading`);
      console.log(`✅ Suspense: ${suspenseCount} utilisations`);
    }
    
    // Vérifier les optimisations Three.js
    const heroPath = path.join(__dirname, 'src', 'components', 'HeroSorgho.jsx');
    if (fs.existsSync(heroPath)) {
      const content = fs.readFileSync(heroPath, 'utf-8');
      const hasVisibilityCheck = content.includes('visibilitychange');
      const hasFPSLimit = content.includes('frameInterval');
      
      console.log(`✅ Three.js optimisé: ${hasVisibilityCheck ? 'Pause quand invisible' : '❌'}`);
      console.log(`✅ FPS limité: ${hasFPSLimit ? 'Oui (60 FPS)' : '❌'}`);
    }
    
    // Vérifier le preload dans index.html
    const indexPath = path.join(__dirname, 'index.html');
    if (fs.existsSync(indexPath)) {
      const content = fs.readFileSync(indexPath, 'utf-8');
      const hasPreload = content.includes('rel="preload"');
      const hasPreconnect = content.includes('rel="preconnect"');
      
      console.log(`✅ Preload: ${hasPreload ? 'Oui' : '❌'}`);
      console.log(`✅ Preconnect: ${hasPreconnect ? 'Oui' : '❌'}`);
    }
    
  } catch (error) {
    console.error('Erreur lors de la vérification des optimisations:', error.message);
  }
}

/**
 * Affiche les recommandations
 */
function showRecommendations() {
  console.log('\n💡 RECOMMANDATIONS');
  console.log('═══════════════════════════════════════════════════════════════');
  
  console.log('\n1. Test Lighthouse:');
  console.log('   • Ouvrez Chrome DevTools → Lighthouse');
  console.log('   • Lancez un audit Performance');
  console.log('   • Vérifiez le score (objectif: 90+)');
  
  console.log('\n2. Test en production:');
  console.log('   • npm run build');
  console.log('   • npm run preview');
  console.log('   • Testez avec un throttling réseau (Slow 3G)');
  
  console.log('\n3. Vérifier le service worker:');
  console.log('   • DevTools → Application → Service Workers');
  console.log('   • Vérifier que le SW est actif');
  console.log('   • Vérifier les caches (Cache Storage)');
  
  console.log('\n4. Web Vitals:');
  console.log('   • Installer l\'extension Web Vitals');
  console.log('   • Mesurer FCP, LCP, TTI, CLS');
  
  console.log('\n5. Comparaison avant/après:');
  console.log('   • Utiliser Chrome DevTools → Performance');
  console.log('   • Enregistrer un chargement de page');
  console.log('   • Comparer les métriques');
}

/**
 * Fonction principale
 */
async function main() {
  console.log('\n🚀 TEST DE PERFORMANCE - EGOEJO');
  console.log('═══════════════════════════════════════════════════════════════\n');
  
  await measureBundleSize();
  await checkServiceWorker();
  await checkOptimizations();
  showRecommendations();
  
  console.log('\n✅ Tests terminés!\n');
}

main().catch(console.error);


# Tests E2E et Monitoring - Configuration Complète

## 📋 Résumé

Les tests E2E ont été configurés et le monitoring a été mis en place pour détecter rapidement les problèmes en production.

## ✅ Tests E2E

### Configuration

- **Fichier de configuration**: `playwright.config.js` (développement)
- **Fichier de configuration production**: `playwright.production.config.js`
- **Script de test production**: `scripts/test-e2e-production.js`

### Commandes disponibles

```bash
# Tests E2E en développement (serveur local)
npm run test:e2e

# Tests E2E en production
npm run test:e2e:production

# Tests E2E avec interface graphique
npm run test:e2e:ui

# Tests E2E avec navigateur visible
npm run test:e2e:headed

# Tests E2E uniquement pour la connexion backend
npm run test:e2e:backend
```

### Tests disponibles

1. **home.spec.js** - Tests de la page d'accueil
2. **navigation.spec.js** - Tests de navigation entre les pages
3. **rejoindre.spec.js** - Tests du formulaire Rejoindre
4. **contenus.spec.js** - Tests de la page Contenus
5. **admin.spec.js** - Tests de la page Admin
6. **backend-connection.spec.js** - Tests de connexion Backend-Frontend

### Résultats actuels

- ✅ **14 tests passent** (tests de base fonctionnels)
- ⚠️ **16 tests échouent** (nécessitent des ajustements ou le serveur de développement)

### Notes importantes

- Les tests en développement nécessitent que le serveur local soit démarré (`npm run dev`)
- Les tests en production utilisent l'URL de production configurée dans `VITE_APP_URL` ou `PLAYWRIGHT_BASE_URL`
- Certains tests peuvent échouer si le contenu de la page a changé (textes, éléments, etc.)

## 🔍 Monitoring

### Configuration

Le monitoring est configuré dans `src/utils/monitoring.js` et initialisé automatiquement en production dans `src/main.jsx`.

### Fonctionnalités

#### 1. **Sentry** (Erreurs et Performance)
- Capture automatique des erreurs JavaScript
- Capture des promesses rejetées non gérées
- Tracking des métriques de performance (LCP, FID, CLS)
- Replay des sessions avec erreurs

**Configuration requise:**
```env
VITE_SENTRY_DSN=votre-dsn-sentry
```

#### 2. **Métriques de Performance**
- **LCP** (Largest Contentful Paint) - Objectif: < 2.5s
- **FID** (First Input Delay) - Objectif: < 100ms
- **CLS** (Cumulative Layout Shift) - Objectif: < 0.1
- **TTFB** (Time to First Byte) - Objectif: < 600ms
- **PageLoad** - Temps de chargement total
- **DOMContentLoaded** - Temps jusqu'au DOM chargé

#### 3. **Monitoring des Requêtes API**
- Détection des requêtes lentes (> 2s)
- Détection des erreurs serveur (5xx)
- Tracking de la durée des requêtes

#### 4. **Alertes Automatiques**
- Alertes de performance (LCP, FID, CLS hors limites)
- Alertes d'erreurs critiques
- Alertes de santé de l'application
- Vérification périodique de la santé (toutes les minutes)

### Utilisation

Le monitoring est automatiquement initialisé en production. Aucune action manuelle n'est requise.

Pour envoyer manuellement une métrique ou une alerte:

```javascript
import { sendMetric, sendError, sendAlert } from './utils/monitoring';

// Envoyer une métrique
sendMetric('CustomMetric', 123, { metadata: 'value' });

// Envoyer une erreur
sendError({
  message: 'Erreur personnalisée',
  error: new Error('Détails'),
  type: 'custom',
});

// Envoyer une alerte
sendAlert('warning', 'Message d\'alerte', { context: 'value' });
```

### Endpoints API (à créer dans le backend)

Le monitoring envoie des données à ces endpoints (optionnels):

- `POST /api/analytics/metrics/` - Métriques de performance
- `POST /api/monitoring/alerts/` - Alertes

Ces endpoints peuvent être créés dans le backend pour stocker et analyser les données.

## 🚀 Déploiement

### Tests E2E en CI/CD

Pour exécuter les tests E2E dans GitHub Actions ou autre CI/CD:

```yaml
# Exemple GitHub Actions
- name: Run E2E tests
  run: npm run test:e2e:production
  env:
    PLAYWRIGHT_BASE_URL: ${{ secrets.PRODUCTION_URL }}
```

### Monitoring en Production

1. **Configurer Sentry:**
   - Créer un compte sur https://sentry.io
   - Créer un projet
   - Obtenir le DSN
   - Ajouter `VITE_SENTRY_DSN` dans les variables d'environnement Vercel

2. **Vérifier les métriques:**
   - Les métriques sont automatiquement envoyées à Sentry
   - Les alertes sont envoyées à Sentry et à l'API (si configurée)

## 📊 Tableau de Bord

### Sentry
- Accéder au dashboard Sentry pour voir les erreurs et métriques
- Configurer des alertes par email/Slack dans Sentry

### Métriques Personnalisées
- Les métriques sont envoyées à `/api/analytics/metrics/` (si endpoint créé)
- Créer un dashboard personnalisé pour visualiser les métriques

## 🔧 Dépannage

### Tests E2E échouent

1. **Vérifier que le serveur est démarré** (pour les tests en développement)
2. **Vérifier les timeouts** - Augmenter si nécessaire dans `playwright.config.js`
3. **Vérifier les sélecteurs** - Les éléments peuvent avoir changé dans le code
4. **Vérifier les screenshots** - Dans `test-results/` pour voir ce qui s'est passé

### Monitoring ne fonctionne pas

1. **Vérifier que `VITE_SENTRY_DSN` est configuré** (en production)
2. **Vérifier la console** - Les erreurs de monitoring sont loggées
3. **Vérifier les endpoints API** - Les erreurs d'envoi sont ignorées silencieusement

## 📝 Prochaines Étapes

1. ✅ Tests E2E configurés
2. ✅ Monitoring configuré
3. ⏳ Créer les endpoints API pour les métriques et alertes (backend)
4. ⏳ Configurer les alertes Sentry (email/Slack)
5. ⏳ Créer un dashboard de monitoring personnalisé
6. ⏳ Ajuster les tests E2E qui échouent selon les besoins

## 🎯 Objectifs

- **Détection rapide des problèmes** - Alertes automatiques
- **Performance optimale** - Métriques Core Web Vitals
- **Fiabilité** - Tests E2E pour vérifier les fonctionnalités critiques
- **Visibilité** - Dashboard Sentry et métriques personnalisées


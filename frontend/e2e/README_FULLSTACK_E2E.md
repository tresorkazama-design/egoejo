# Tests E2E Full-Stack

Ce document décrit les tests E2E full-stack qui nécessitent un backend Django réel.

## 📋 Tests Disponibles

### 1. `flux-complet-saka-vote.spec.js`
**Flux testé :**
- Register/Login utilisateur
- Crédit SAKA (via endpoint test-only `/api/saka/grant/`)
- Aller sur la page Votes
- Voter avec intensité
- Vérifier que SAKA diminue et que le vote est enregistré

### 2. `flux-complet-projet-financement.spec.js`
**Flux testé :**
- Créer un projet
- Publier le projet
- Effectuer financement EUR (mock ou endpoint test-only)
- Vérifier statut et trace côté UI

## 🚀 Exécution Locale

### Prérequis

1. **Backend Django démarré** :
   ```bash
   cd backend
   # Activer l'environnement virtuel si nécessaire
   export E2E_TEST_MODE=1  # ou DEBUG=1
   export ENABLE_SAKA=1
   python manage.py migrate
   python manage.py runserver
   ```

2. **Frontend démarré** :
   ```bash
   cd frontend/frontend
   npm install
   npm run dev
   ```

### Exécuter les tests

```bash
cd frontend/frontend

# Variable d'environnement pour pointer vers le backend
export BACKEND_URL=http://localhost:8000
export PLAYWRIGHT_BASE_URL=http://localhost:5173

# Exécuter un test spécifique
npm run test:e2e -- e2e/flux-complet-saka-vote.spec.js
npm run test:e2e -- e2e/flux-complet-projet-financement.spec.js

# Exécuter tous les tests full-stack
npm run test:e2e -- e2e/flux-complet-*.spec.js
```

## 🔧 Configuration Backend

Pour que les tests fonctionnent, le backend doit avoir :

1. **Variable d'environnement `E2E_TEST_MODE=1`** (ou `DEBUG=1`) pour activer l'endpoint `/api/saka/grant/`
2. **Variable d'environnement `ENABLE_SAKA=1`** pour activer le protocole SAKA
3. **Base de données de test** (SQLite par défaut, ou PostgreSQL pour la CI)

### Endpoint Test-Only : `/api/saka/grant/`

Cet endpoint est disponible uniquement si `E2E_TEST_MODE=True` ou `DEBUG=True`.

**POST /api/saka/grant/**
```json
{
  "amount": 100,
  "reason": "e2e_test"
}
```

**Réponse :**
```json
{
  "ok": true,
  "amount": 100,
  "new_balance": 100,
  "transaction_id": 123
}
```

**Limites :**
- Montant maximum : 500 SAKA (pour éviter l'erreur de double validation)
- Disponible uniquement en mode test

## 🎭 Helpers Utilisés

Les tests utilisent les helpers suivants (définis dans `e2e/utils/test-helpers.js`) :

- `waitForElementInViewport(page, selector, options)` : Attend qu'un élément soit visible dans le viewport
- `waitForApiIdle(page, options)` : Attend que toutes les requêtes API soient terminées

**Aucun `waitForTimeout` fixe n'est utilisé** - tous les waits sont actifs avec polling.

## 📊 Logs Diagnostics

En cas d'échec, les tests affichent des logs détaillés :
- `[E2E]` : Logs généraux du test
- Messages d'erreur explicites avec status HTTP et texte d'erreur
- Vérifications étape par étape du flux

## 🔄 CI/CD

Les tests sont exécutés dans `.github/workflows/e2e-fullstack.yml` :

1. Démarre PostgreSQL et Redis (services)
2. Configure et démarre le backend Django
3. Démarre le frontend
4. Exécute les tests E2E full-stack
5. Génère un résumé et upload le rapport Playwright

## ⚠️ Notes Importantes

1. **Isolation** : Chaque test crée un utilisateur unique avec un timestamp pour éviter les conflits
2. **Idempotence** : Les tests peuvent être exécutés plusieurs fois sans pollution
3. **Mode séquentiel** : Les tests dans un même fichier sont exécutés séquentiellement (`mode: 'serial'`)
4. **Backend requis** : Ces tests nécessitent un backend réel - ils ne fonctionnent pas en mode mock-only

## 🐛 Dépannage

### Backend non accessible
```
Error: Backend non accessible à http://localhost:8000
```
**Solution :** Vérifiez que le backend Django est démarré et accessible sur le port 8000.

### Endpoint `/api/saka/grant/` retourne 403
```
Error: Endpoint disponible uniquement en mode test
```
**Solution :** Définissez `E2E_TEST_MODE=1` ou `DEBUG=1` dans les variables d'environnement du backend.

### Tests échouent avec "SAKA_PROTOCOL_DISABLED"
**Solution :** Définissez `ENABLE_SAKA=1` dans les variables d'environnement du backend.


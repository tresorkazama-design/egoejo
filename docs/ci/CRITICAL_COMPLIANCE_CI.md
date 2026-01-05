# 🚨 Critical Compliance CI - Guide d'Exécution

## 📋 Vue d'Ensemble

Le workflow `audit-global.yml` exécute **6 jobs séparés** pour garantir que toutes les protections P0/P1 sont respectées avant un merge :

1. **Audit Statique** : Détection des mots interdits (ROI, rendement, etc.)
2. **Backend Compliance** : Tests de conformité EGOEJO (`@egoejo_compliance`)
3. **Backend Permissions** : Tests de permissions critiques (`@critical`)
4. **Frontend Unit** : Tests unitaires Vitest
5. **Frontend E2E Critical** : Tests E2E full-stack critiques
6. **Critical Compliance** : Job de synthèse qui échoue si un job précédent échoue

## 🎯 Jobs P0/P1 BLOQUANTS

### ✅ Job 1: Audit Statique
- **Commande** : `npm run audit:global`
- **Objectif** : Détecter les mots interdits (ROI, rendement, dividende, etc.)
- **Échec** : BLOQUE le merge

### ✅ Job 2: Backend Compliance
- **Commande** : `pytest tests/compliance/ -m egoejo_compliance`
- **Objectif** : Vérifier la conformité EGOEJO (SAKA/EUR séparation, anti-accumulation, etc.)
- **Échec** : BLOQUE le merge

### ✅ Job 3: Backend Permissions
- **Commande** : `pytest core/tests/api/test_*_permissions.py -m critical`
- **Objectif** : Vérifier que les permissions sont correctement appliquées
- **Échec** : BLOQUE le merge

### ✅ Job 4: Frontend Unit
- **Commande** : `npm test -- --run`
- **Objectif** : Vérifier que tous les tests unitaires passent
- **Échec** : BLOQUE le merge

### ✅ Job 5: Frontend E2E Critical
- **Commande** : `npm run test:e2e -- e2e/flux-complet-*.spec.js`
- **Objectif** : Vérifier les flux critiques (SAKA→Vote, Projet→Financement)
- **Échec** : BLOQUE le merge

### ✅ Job 6: Critical Compliance (Synthèse)
- **Objectif** : Synthétiser les résultats et échouer si un job précédent a échoué
- **Échec** : BLOQUE le merge

## 🚀 Exécution Locale

### Prérequis

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend/frontend
npm ci
npx playwright install --with-deps chromium
```

### 1. Audit Statique

```bash
cd frontend/frontend
npm run audit:global
```

### 2. Backend Compliance

```bash
cd backend
pytest tests/compliance/ -v -m egoejo_compliance
```

### 3. Backend Permissions

```bash
cd backend
pytest core/tests/api/test_*_permissions.py -v -m critical
```

### 4. Frontend Unit

```bash
cd frontend/frontend
npm test -- --run
```

### 5. Frontend E2E Critical

**Prérequis** : PostgreSQL et Redis doivent être démarrés.

```bash
# Terminal 1: Démarrer PostgreSQL et Redis (via Docker)
docker-compose up -d postgres redis

# Terminal 2: Démarrer le backend Django
cd backend
export DATABASE_URL="postgres://test_user:test_password@localhost:5432/test_db"
export REDIS_URL="redis://localhost:6379/0"
export E2E_TEST_MODE=1
export ENABLE_SAKA=1
export SAKA_COMPOST_ENABLED=1
export SAKA_SILO_REDIS_ENABLED=1
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

# Terminal 3: Démarrer le frontend
cd frontend/frontend
npm run dev

# Terminal 4: Exécuter les tests E2E critiques
cd frontend/frontend
export BACKEND_URL="http://localhost:8000"
export PLAYWRIGHT_BASE_URL="http://localhost:5173"
export E2E_MODE="full-stack"
npm run test:e2e -- e2e/flux-complet-saka-vote.spec.js e2e/flux-complet-projet-financement.spec.js
```

### 6. Exécuter Tous les Tests (Simulation CI)

```bash
#!/bin/bash
# Script: scripts/run-critical-compliance.sh

set -e  # Arrêter en cas d'erreur

echo "🚨 Exécution des tests Critical Compliance (P0/P1)"

# 1. Audit Statique
echo "📋 1/5: Audit Statique..."
cd frontend/frontend
npm run audit:global || exit 1

# 2. Backend Compliance
echo "📋 2/5: Backend Compliance..."
cd ../../backend
pytest tests/compliance/ -v -m egoejo_compliance || exit 1

# 3. Backend Permissions
echo "📋 3/5: Backend Permissions..."
pytest core/tests/api/test_*_permissions.py -v -m critical || exit 1

# 4. Frontend Unit
echo "📋 4/5: Frontend Unit..."
cd ../frontend/frontend
npm test -- --run || exit 1

# 5. Frontend E2E Critical (nécessite backend + frontend démarrés)
echo "📋 5/5: Frontend E2E Critical..."
echo "⚠️  Note: Assurez-vous que le backend et le frontend sont démarrés"
npm run test:e2e -- e2e/flux-complet-saka-vote.spec.js e2e/flux-complet-projet-financement.spec.js || exit 1

echo "✅ Tous les tests Critical Compliance sont passés !"
```

## 🔧 Configuration GitHub Actions

### Déclencheurs

Le workflow se déclenche automatiquement sur :
- **Pull Request** vers `main` ou `develop`
- **Push** sur `main` ou `develop`

### Cache

- **npm** : Cache des dépendances frontend (`package-lock.json`)
- **pip** : Cache des dépendances backend (`requirements.txt`)

### Timeouts

- **Audit Statique** : 10 minutes
- **Backend Compliance** : 15 minutes
- **Backend Permissions** : 15 minutes
- **Frontend Unit** : 10 minutes
- **Frontend E2E Critical** : 20 minutes
- **Critical Compliance** : 5 minutes

### Artifacts

Les rapports suivants sont uploadés :
- `backend-compliance-reports` : JUnit XML des tests compliance
- `backend-permissions-reports` : JUnit XML des tests permissions
- `frontend-unit-coverage` : Coverage des tests unitaires
- `playwright-report-critical` : Rapport Playwright des tests E2E

## 🚫 Blocage du Merge

Le workflow **BLOQUE** le merge si :
- ❌ Un mot interdit est détecté
- ❌ Un test de compliance échoue
- ❌ Un test de permission échoue
- ❌ Un test unitaire échoue
- ❌ Un test E2E critique échoue

## 📊 Diagnostic Rapide

Les jobs sont **séparés** pour permettre un diagnostic rapide :

1. Si **Audit Statique** échoue → Vérifier les mots interdits
2. Si **Backend Compliance** échoue → Vérifier les tests `tests/compliance/`
3. Si **Backend Permissions** échoue → Vérifier les tests `core/tests/api/test_*_permissions.py`
4. Si **Frontend Unit** échoue → Vérifier les tests unitaires Vitest
5. Si **Frontend E2E Critical** échoue → Vérifier les tests E2E full-stack

## 🔍 Vérification des Résultats

### Dans GitHub Actions

1. Aller sur l'onglet **Actions**
2. Sélectionner le workflow **🛡️ Audit BLOQUANT GLOBAL - EGOEJO Compliance**
3. Cliquer sur le run en échec
4. Voir les logs de chaque job pour identifier le problème

### Localement

```bash
# Voir les logs détaillés
pytest tests/compliance/ -v -m egoejo_compliance --tb=long
pytest core/tests/api/test_*_permissions.py -v -m critical --tb=long
npm test -- --run --reporter=verbose
npm run test:e2e -- e2e/flux-complet-*.spec.js --reporter=list
```

## 🎯 Prochaines Étapes

1. ✅ Vérifier que tous les jobs passent en local
2. ✅ Pousser les changements sur une branche
3. ✅ Créer une Pull Request
4. ✅ Vérifier que le workflow passe dans GitHub Actions
5. ✅ Merger si tous les jobs sont verts

## 📚 Documentation Associée

- [Tests Compliance Backend](../tests/compliance/README.md)
- [Tests Permissions Backend](../tests/api/README.md)
- [Tests E2E Full-Stack](../../frontend/frontend/e2e/README_FULLSTACK_E2E.md)
- [Guide d'Audit Global](../../frontend/frontend/scripts/README_AUDIT_GLOBAL.md)


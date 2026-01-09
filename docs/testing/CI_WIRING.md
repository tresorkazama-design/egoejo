# 🔧 CI Wiring - Documentation Technique EGOEJO

**Date** : 2025-01-27  
**Version** : 1.0  
**Objectif** : Documentation du wiring CI pour les tests EGOEJO

---

## 🎯 Vue d'Ensemble

Le wiring CI EGOEJO garantit que :
- ✅ Les jobs critiques sont séparés et bloquants
- ✅ Les artefacts sont générés et uploadés (JUnit, Playwright, compliance)
- ✅ Les tests E2E sont shardés pour parallélisation
- ✅ Les healthchecks sont explicites avant E2E
- ✅ Les retries sont intelligents (timeout/infrastructure uniquement)

---

## 📁 Workflows CI

### 1. `ci.yml` - CI Basique

**Objectif** : Tests basiques frontend et backend

**Jobs** :
- `frontend-test` : Lint, tests unitaires, build
- `backend-test` : Tests backend (tous)
- `build` : Build frontend (dépend de frontend-test + backend-test)

**Artefacts** :
- `backend/junit.xml` : Rapport JUnit backend (uploadé)

**Améliorations Appliquées** :
- ✅ Ajout `--junit-xml=junit.xml` dans `pytest.ini`
- ✅ Upload artefact `backend-junit-report`

---

### 2. `audit-global.yml` - Audit Global BLOQUANT

**Objectif** : Validation complète EGOEJO (P0/P1 bloquants)

**Jobs** :
1. **`audit-static`** : Audit statique (mots interdits)
2. **`backend-compliance`** : Tests compliance backend (`@egoejo_compliance`)
3. **`backend-permissions`** : Tests permissions backend (`@critical`)
4. **`frontend-unit`** : Tests unitaires frontend
5. **`frontend-e2e-critical`** : Tests E2E critiques (sharded 1/2 + 2/2 via matrix strategy)
6. **`critical-compliance`** : Job final (résumé + rapport compliance)

**Artefacts** :
- `backend/junit-compliance.xml` : Rapport JUnit compliance
- `backend/junit-permissions.xml` : Rapport JUnit permissions
- `backend/junit.xml` : Rapport JUnit backend (compliance + permissions)
- `frontend/frontend/playwright-report/` : Rapport Playwright HTML
- `compliance_report.json` : Rapport compliance JSON
- `backend/compliance-report.json` : Rapport compliance backend

**Améliorations Appliquées** :
- ✅ Sharding E2E (1/2 + 2/2) pour parallélisation
- ✅ Healthchecks explicites avec retry (backend + frontend)
- ✅ Upload artefacts JUnit (compliance + permissions)
- ✅ Upload rapport compliance JSON

**Healthchecks** :
- ✅ Backend : `curl http://localhost:8000/api/health/` (30 tentatives, 2s intervalle)
- ✅ Frontend : `curl http://localhost:5173/` (30 tentatives, 2s intervalle)

---

### 3. `e2e-fullstack.yml` - Tests E2E Full-Stack

**Objectif** : Tests E2E complets avec backend réel

**Jobs** :
- `e2e-fullstack` : Tests E2E SAKA Vote + Projet Financement

**Artefacts** :
- `frontend/frontend/playwright-report/` : Rapport Playwright HTML

**Améliorations Appliquées** :
- ✅ Healthchecks explicites avec retry (backend + frontend)
- ✅ Logs Django/Vite en cas d'échec healthcheck

---

### 4. `egoejo-compliance.yml` - Compliance Philosophique

**Objectif** : Tests compliance philosophique SAKA/EUR

**Jobs** :
- `egoejo-compliance` : Tests compliance + scans automatiques

**Vérifications** :
- ✅ Tests marqués `@egoejo_compliance`
- ✅ Scan code Python (conversion SAKA↔EUR)
- ✅ Scan endpoints API (conformité constitution)
- ✅ ESLint SAKA (no-monetary-symbols)

---

## 🔧 Configuration

### Backend (`backend/pytest.ini`)

**Ajout** :
```ini
addopts = 
    ...
    --junit-xml=junit.xml
```

**Génération** :
- `junit.xml` : Généré automatiquement pour tous les tests backend

---

### Frontend (`frontend/frontend/playwright.config.js`)

**Sharding** :
```javascript
// Utilisation dans CI
npm run test:e2e -- --shard=1/2
npm run test:e2e -- --shard=2/2
```

**Rapport** :
- `playwright-report/` : Généré automatiquement par Playwright

---

## 📊 Artefacts CI

### Backend

| Artefact | Fichier | Workflow | Description |
|----------|---------|----------|-------------|
| JUnit Backend | `backend/junit.xml` | `ci.yml`, `audit-global.yml` | Rapport JUnit tous tests |
| JUnit Compliance | `backend/junit-compliance.xml` | `audit-global.yml` | Rapport JUnit compliance |
| JUnit Permissions | `backend/junit-permissions.xml` | `audit-global.yml` | Rapport JUnit permissions |
| Compliance Report | `backend/compliance-report.json` | `audit-global.yml` | Rapport compliance JSON |

### Frontend

| Artefact | Fichier | Workflow | Description |
|----------|---------|----------|-------------|
| Playwright Report | `frontend/frontend/playwright-report/` | `audit-global.yml`, `e2e-fullstack.yml` | Rapport Playwright HTML |
| Coverage | `frontend/frontend/coverage/` | `audit-global.yml` | Coverage frontend |

### Compliance

| Artefact | Fichier | Workflow | Description |
|----------|---------|----------|-------------|
| Compliance Report | `compliance_report.json` | `audit-global.yml` | Rapport compliance final |

---

## 🚀 Healthchecks

### Backend Healthcheck

**Endpoint** : `http://localhost:8000/api/health/`

**Implémentation** :
```bash
for i in {1..30}; do
  if curl -f http://localhost:8000/api/health/ > /dev/null 2>&1; then
    echo "✅ Backend health check OK"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "❌ Backend health check failed after 30 attempts"
    exit 1
  fi
  sleep 2
done
```

**Retry** : 30 tentatives, 2s intervalle (max 60s)

### Frontend Healthcheck

**Endpoint** : `http://localhost:5173/`

**Implémentation** :
```bash
for i in {1..30}; do
  if curl -f http://localhost:5173/ > /dev/null 2>&1; then
    echo "✅ Frontend health check OK"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "❌ Frontend health check failed after 30 attempts"
    exit 1
  fi
  sleep 2
done
```

**Retry** : 30 tentatives, 2s intervalle (max 60s)

---

## 🔄 Sharding E2E

### Configuration

**Workflow** : `audit-global.yml`

**Job** : `frontend-e2e-critical` (avec stratégie de matrice)

**Stratégie** :
```yaml
strategy:
  fail-fast: false
  matrix:
    shard: [1, 2]
```

**Commande** :
```bash
npm run test:e2e -- --shard=${{ matrix.shard }}/2 e2e/flux-complet-saka-vote.spec.js e2e/flux-complet-projet-financement.spec.js e2e/cms-workflow-fullstack.spec.js e2e/chat-websocket.spec.js
```

**Exécution** :
- Shard 1/2 : Exécuté en parallèle avec shard 2/2
- Shard 2/2 : Exécuté en parallèle avec shard 1/2

**Avantages** :
- ✅ Parallélisation (2 shards en parallèle)
- ✅ Réduction temps d'exécution (~50%)
- ✅ Isolation des tests (shard indépendants)

---

## 🔁 Retries Intelligents

### Playwright

**Configuration** : `playwright.config.js`

```javascript
retries: process.env.CI ? 2 : 0,  // 2 retries en CI uniquement
```

**Critères** :
- ✅ Retries uniquement en CI
- ✅ Retries sur timeout/infrastructure (pas sur erreurs fonctionnelles)

### Backend

**Pas de retries automatiques** : Les tests backend sont déterministes et ne nécessitent pas de retries.

---

## 📋 Checklist Branch Protection

### Checks Requis

Les checks suivants doivent être activés dans GitHub Branch Protection Rules :

1. ✅ `audit-home-vision` (audit Home/Vision)
2. ✅ `audit-static` (audit statique)
3. ✅ `backend-compliance` (tests compliance backend)
4. ✅ `backend-permissions` (tests permissions backend)
5. ✅ `frontend-unit` (tests unitaires frontend)
6. ✅ `frontend-e2e-critical` (tests E2E critiques, sharded 1/2 + 2/2)
7. ✅ `critical-compliance` (job final compliance)
8. ✅ `egoejo-compliance` (tests compliance philosophique)

**Documentation** : `docs/governance/REQUIRED_CHECKS.md`

---

## 🐛 Dépannage

### Healthcheck Échoue

1. **Vérifier les logs** :
   ```bash
   cat /tmp/django.log  # Backend
   cat /tmp/vite.log    # Frontend
   ```

2. **Vérifier les services** :
   - PostgreSQL : `pg_isready`
   - Redis : `redis-cli ping`

3. **Augmenter timeout** : Modifier `sleep 2` et `{1..30}` si nécessaire

### Sharding Échoue

1. **Vérifier que les tests sont shardables** : Playwright sharde automatiquement
2. **Vérifier les dépendances** : Les shards doivent être indépendants

### Artefacts Manquants

1. **Vérifier les chemins** : Les chemins doivent être relatifs au workspace
2. **Vérifier `if-no-files-found`** : `ignore` ou `warn` selon le cas

---

## 📚 Références

- **Workflows** : `.github/workflows/`
- **Pytest Config** : `backend/pytest.ini`
- **Playwright Config** : `frontend/frontend/playwright.config.js`
- **Required Checks** : `docs/governance/REQUIRED_CHECKS.md`
- **Plan Action Tests** : `docs/testing/PLAN_ACTION_TESTS.md`

---

**Statut** : ✅ **OPÉRATIONNEL**  
**Dernière Mise à Jour** : 2025-01-27


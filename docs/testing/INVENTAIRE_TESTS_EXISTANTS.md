# 📋 Inventaire Complet des Tests EGOEJO

**Date** : 2025-01-XX  
**Objectif** : Cartographier l'existant avant d'ajouter les tests manquants

---

## 🎯 Résumé Exécutif

| Catégorie | Nombre | Statut Bloquant | Couverture |
|-----------|--------|-----------------|------------|
| Backend Unit | ~50+ | Partiel | Bonne |
| Backend Compliance | ~30+ | ✅ **BLOQUANT** | Excellente |
| Backend Permissions | ~15+ | ✅ **BLOQUANT** | Bonne |
| Frontend Unit | ~17 | Non bloquant | Moyenne |
| Frontend E2E | ~24 | Partiel | Bonne |
| CI Workflows | 15 | Mixte | Bonne |
| Scripts Audit | 3 | ✅ **BLOQUANT** | Bonne |

---

## 🔧 BACKEND - Tests Python (pytest)

### Marqueurs pytest

**Défini dans `backend/pytest.ini`** :
- `@pytest.mark.egoejo_compliance` : Tests de compliance philosophique (BLOQUANT en CI)
- `@pytest.mark.critical` : Tests critiques (utilisé mais non défini formellement)

### Structure des tests

```
backend/
├── tests/
│   ├── compliance/          # ~30 tests de compliance (BLOQUANT)
│   │   ├── content/          # Compliance éditoriale
│   │   ├── finance/          # Séparation SAKA/EUR
│   │   ├── governance/       # Feature flags, transparence
│   │   ├── philosophy/       # Anti-accumulation, double structure
│   │   └── structure/        # Séparation modèles
│   └── infrastructure/      # Redis resilience
│
└── core/tests/
    ├── admin/                # Admin readonly SAKA
    ├── api/                  # Permissions API (BLOQUANT)
    │   ├── test_contract_cms_actions.py  # Contract tests CMS (publish/reject/archive/export)
    │   └── ...
    ├── cms/                  # Permissions CMS, workflow
    │   ├── test_content_permissions.py  # Permissions CMS
    │   ├── test_content_workflow_transitions.py  # Workflow transitions
    │   └── test_xss_sanitization.py  # XSS sanitization (P0)
    ├── models/               # Intégrité modèles SAKA
    ├── services/             # Services manuels
    └── utils/                # Utilitaires (alerts)
```

### Suites de tests existantes

#### 1. Compliance Philosophique (`tests/compliance/`)

**Commande** : `pytest -m egoejo_compliance -v`  
**Durée estimée** : ~5-10 min  
**Fiabilité** : ✅ Excellente  
**Statut** : ✅ **BLOQUANT** (workflow `egoejo-compliance.yml`)

**Tests inclus** :
- `test_saka_eur_separation.py` : Séparation stricte SAKA/EUR
- `test_no_saka_eur_conversion.py` : Scan récursif code Python (BLOQUANT)
- `test_api_endpoints_protection.py` : Scan endpoints API (BLOQUANT)
- `test_anti_accumulation.py` : Anti-accumulation SAKA
- `test_saka_cycle_incompressible.py` : Cycle SAKA incompressible
- `test_saka_compost_depreciation_effective.py` : Compostage effectif
- `test_silo_redistribution.py` : Redistribution silo
- `test_banque_dormante_strict.py` : Banque dormante
- `test_content_editorial_compliance.py` : Compliance éditoriale contenu
- `test_settings_failfast.py` : Validation settings (18 tests)
- `test_meta_compliance.py` : Vérifie que tous les tests compliance sont tagués

**Gaps identifiés** :
- ❌ Pas de tests contract API (OpenAPI/schéma)
- ❌ Pas de tests E2E backend (DB + Redis réels)
- ⚠️ Tests de scan récursif peuvent être lents

#### 2. Permissions API (`core/tests/api/`)

**Commande** : `pytest core/tests/api/ -v`  
**Durée estimée** : ~2-3 min  
**Fiabilité** : ✅ Excellente  
**Statut** : ✅ **BLOQUANT** (marqueur `@pytest.mark.critical`)

**Tests inclus** :
- `test_saka_permissions.py` : Permissions endpoints SAKA (9 tests)
- `test_projects_permissions.py` : Permissions projets (3 tests)
- `test_polls_permissions.py` : Permissions votes (4 tests)
- `test_public_constitution.py` : Endpoint public constitution

**Gaps identifiés** :
- ✅ Tests permissions CMS existants (`test_content_permissions.py`)
- ✅ Tests workflow transitions existants (`test_content_workflow_transitions.py`)
- ✅ Tests XSS sanitization ajoutés (`test_xss_sanitization.py`)
- ✅ Contract tests CMS actions ajoutés (`test_contract_cms_actions.py`)
- ✅ E2E workflow complet ajouté (`cms-workflow-fullstack.spec.js`)
- ❌ Pas de tests permissions pour endpoints finance
- ⚠️ Pas de tests contract (schéma réponse)

#### 3. Modèles SAKA (`core/tests/models/`)

**Commande** : `pytest core/tests/models/ -v`  
**Durée estimée** : ~3-5 min  
**Fiabilité** : ✅ Excellente  
**Statut** : ✅ **BLOQUANT** (marqueurs `@pytest.mark.critical` + `@pytest.mark.egoejo_compliance`)

**Tests inclus** :
- `test_saka_wallet_protection.py` : Protection wallet SAKA
- `test_saka_wallet_raw_sql.py` : Détection bypass raw SQL (BLOQUANT)
- `test_saka_wallet_alerting.py` : Alertes critiques wallet
- `test_saka_wallet_update_prevention.py` : Prévention updates directs
- `test_transaction_type_integrity.py` : Intégrité transaction_type (BLOQUANT)
- `test_critical_alert_event.py` : Modèle alertes critiques

**Gaps identifiés** :
- ✅ Couverture excellente, pas de gaps majeurs

#### 4. CMS (`core/tests/cms/`)

**Commande** : `pytest core/tests/cms/ -v`  
**Durée estimée** : ~2-3 min  
**Fiabilité** : ✅ Bonne  
**Statut** : ✅ **BLOQUANT** (marqueur `@pytest.mark.critical`)

**Tests inclus** :
- `test_content_permissions.py` : Permissions CMS (6 tests)
- `test_content_workflow_transitions.py` : Workflow transitions (15+ tests)
- `test_xss_sanitization.py` : XSS sanitization (7+ tests) 🔴 **P0**
- `test_content_workflow_transitions.py` : Transitions workflow (draft/pending/published/archived)

**Gaps identifiés** :
- ❌ Pas de tests XSS sanitization
- ❌ Pas de tests pagination
- ❌ Pas de tests cache

#### 5. Finance (`finance/tests/`)

**Commande** : `pytest finance/tests/ -v`  
**Durée estimée** : ~3-5 min  
**Fiabilité** : ✅ Bonne  
**Statut** : ⚠️ Partiel (pas de marqueur `critical`)

**Tests inclus** :
- `test_stripe_segregation.py` : Ségrégation Stripe (BLOQUANT)
- `test_ledger_fee_allocation.py` : Allocation frais
- `test_views_permissions.py` : Permissions vues finance (3 tests)
- `test_deadlock_allocate_deposit.py` : Deadlock allocation
- `test_race_condition_release_escrow.py` : Race condition escrow
- `test_race_condition_pledge.py` : Race condition pledge

**Gaps identifiés** :
- ❌ Pas de tests contract webhooks Stripe
- ❌ Pas de tests traçabilité complète (UI + API)
- ❌ Pas de tests promesses "dons nets" (validation texte)

#### 6. Infrastructure (`tests/infrastructure/`)

**Commande** : `pytest tests/infrastructure/ -v`  
**Durée estimée** : ~1-2 min  
**Fiabilité** : ✅ Bonne  
**Statut** : ⚠️ Non bloquant

**Tests inclus** :
- `test_redis_resilience.py` : Résilience Redis

**Gaps identifiés** :
- ❌ Pas de tests résilience Postgres
- ❌ Pas de tests migrations rollback

---

## 🎨 FRONTEND - Tests JavaScript/TypeScript

### Framework de tests

- **Unit** : Vitest (remplace Jest)
- **E2E** : Playwright
- **Lint** : ESLint (règle custom `egoejo/no-monetary-symbols` désactivée, remplacée par script audit)

### Structure des tests

```
frontend/frontend/
├── src/
│   ├── __tests__/            # Tests unitaires
│   │   └── performance/      # Tests performance
│   ├── hooks/__tests__/      # Tests hooks React
│   └── utils/__tests__/      # Tests utilitaires
│
└── e2e/                      # Tests E2E Playwright
    ├── fixtures/             # Fixtures auth
    └── utils/                # Helpers E2E
```

### Suites de tests existantes

#### 1. Tests Unitaires (Vitest)

**Commande** : `npm test -- --run`  
**Durée estimée** : ~30-60s  
**Fiabilité** : ✅ Bonne  
**Statut** : ⚠️ Non bloquant (workflow `ci.yml`)

**Tests inclus** (~17 fichiers) :
- `src/utils/__tests__/backend-connection.test.js` : Connexion backend (mock)
- `src/utils/__tests__/integration-backend.test.js` : Intégration backend (réel, optionnel)
- `src/utils/__tests__/api.test.js` : Utilitaires API
- `src/utils/__tests__/format.test.js` : Formatage
- `src/utils/__tests__/validation.test.js` : Validation
- `src/utils/__tests__/content.test.js` : Contenu
- `src/utils/__tests__/performance.test.js` : Performance
- `src/utils/security.test.js` : Sécurité
- `src/utils/__tests__/saka-protection.test.ts` : Protection SAKA
- `src/hooks/__tests__/useFetch.test.js` : Hook useFetch
- `src/hooks/__tests__/useLocalStorage.test.js` : Hook localStorage
- `src/hooks/__tests__/useDebounce.test.js` : Hook debounce
- `src/hooks/__tests__/useMediaQuery.test.js` : Hook media query
- `src/hooks/__tests__/useToggle.test.js` : Hook toggle
- `src/__tests__/performance/lighthouse.test.js` : Lighthouse
- `src/__tests__/performance/automated.test.js` : Performance automatisée
- `src/__tests__/performance/metrics.test.js` : Métriques

**Gaps identifiés** :
- ❌ Pas de tests accessibilité automatisés (axe-core)
- ❌ Pas de tests XSS sanitization
- ❌ Pas de tests retry/backoff useFetch
- ⚠️ Couverture partielle des composants

#### 2. Tests E2E (Playwright)

**Commande** : `npm run test:e2e`  
**Durée estimée** : ~5-10 min (mock-only) / ~15-20 min (full-stack)  
**Fiabilité** : ✅ Bonne (retries en CI)  
**Statut** : ⚠️ Partiel (workflow `e2e-fullstack.yml` pour 2 tests seulement)

**Configuration** (`playwright.config.js`) :
- Mode `mock-only` (par défaut) : Tous les tests sauf `backend-connection.spec.js`
- Mode `full-stack` : Nécessite backend réel
- Retries : 2 en CI, 0 en local
- Workers : 1 en CI, parallèle en local

**Tests inclus** (~24 fichiers) :
- `e2e/home.spec.js` : Page d'accueil
- `e2e/navigation.spec.js` : Navigation
- `e2e/navigation-sections.spec.js` : Navigation sections (skip links)
- `e2e/auth.spec.js` : Authentification
- `e2e/admin.spec.js` : Admin
- `e2e/contenus.spec.js` : Contenus
- `e2e/contenus-offline.spec.js` : Contenus offline
- `e2e/cms-workflow-fullstack.spec.js` : Workflow CMS complet (full-stack) 🔴 **P0**
- `e2e/rejoindre.spec.js` : Formulaire rejoindre
- `e2e/votes.spec.js` : Votes
- `e2e/votes-quadratic.spec.js` : Votes quadratiques
- `e2e/saka-flow.spec.js` : Flux SAKA
- `e2e/saka-lifecycle.spec.js` : Cycle de vie SAKA
- `e2e/saka-cycle-complet.spec.js` : Cycle SAKA complet
- `e2e/saka-cycle-fullstack.spec.js` : Cycle SAKA full-stack
- `e2e/saka-cycle-visibility.spec.js` : Visibilité SAKA
- `e2e/projects-saka-boost.spec.js` : Projets SAKA boost
- `e2e/flux-complet-saka-vote.spec.js` : Flux complet SAKA vote (full-stack, BLOQUANT)
- `e2e/flux-complet-projet-financement.spec.js` : Flux complet projet financement (full-stack, BLOQUANT)
- `e2e/backend-connection.spec.js` : Connexion backend (full-stack)
- `e2e/home-vision-compliance.spec.js` : Compliance accueil/vision
- `e2e/home-vision-audit.spec.js` : Audit accueil/vision
- `e2e/audit-compliance-accueil-vision.spec.js` : Audit compliance accueil/vision

**Gaps identifiés** :
- ❌ Pas de tests E2E "onboarding -> login -> dashboard" complet
- ❌ Pas de tests E2E "cycle contenu -> SAKA reward" complet
- ❌ Pas de tests E2E "cycle projet -> financement EUR -> traçabilité" complet
- ⚠️ Seulement 2 tests full-stack en CI (autres en mock-only)
- ❌ Pas de tests accessibilité E2E (axe-core)

#### 3. Lint & Audit

**Commande** : `npm run lint`  
**Durée estimée** : ~10-30s  
**Fiabilité** : ✅ Bonne  
**Statut** : ⚠️ Partiel (workflow `egoejo-compliance.yml` vérifie ESLint SAKA)

**Règles ESLint** :
- `egoejo/no-monetary-symbols` : Désactivée (problème compatibilité ESLint 8.x)
- Remplacée par script `audit-home-vision.mjs` (workflow `audit-home-vision.yml`)

**Scripts audit** :
- `scripts/audit-home-vision.mjs` : Audit accueil/vision (BLOQUANT)
- `scripts/audit-global.mjs` : Audit global

**Gaps identifiés** :
- ⚠️ Règle ESLint custom désactivée (workaround via script)
- ❌ Pas de lint TypeScript strict

---

## 🔄 CI/CD - Workflows GitHub Actions

### Workflows existants

| Workflow | Déclencheur | Jobs | Statut Bloquant |
|----------|-------------|------|-----------------|
| `ci.yml` | Push/PR | frontend-test, backend-test, build | ✅ Bloquant |
| `test.yml` | Push/PR | test (matrix investment_features) | ✅ Bloquant |
| `compliance.yml` | Push/PR | compliance-tests | ✅ **BLOQUANT** |
| `egoejo-compliance.yml` | Push/PR | egoejo-compliance (multi-scans) | ✅ **BLOQUANT** |
| `e2e-fullstack.yml` | Push/PR | e2e-fullstack (2 tests) | ✅ Bloquant |
| `cd.yml` | Push main | deploy-frontend, deploy-backend, performance-check | ⚠️ Conditionnel |
| `audit-global.yml` | Push/PR | audit-global | ✅ Bloquant |
| `audit-home-vision.yml` | Push/PR | audit-home-vision | ✅ Bloquant |
| `security-audit.yml` | Push/PR | security-audit | ⚠️ Partiel |
| `egoejo-pr-bot.yml` | PR | PR bot | ⚠️ Informatif |
| `egoejo-guardian.yml` | PR | Guardian checks | ⚠️ Informatif |
| `pr-bot-egoejo-guardian.yml` | PR | PR bot guardian | ⚠️ Informatif |
| `pr-bot-home-vision.yml` | PR | PR bot home/vision | ⚠️ Informatif |
| `nightly-investment-check.yml` | Schedule | Investment check | ⚠️ Informatif |

### Services CI

**Postgres** : ✅ Configuré (health checks)  
**Redis** : ✅ Configuré (health checks)  
**Artefacts** : ⚠️ Partiel (Playwright report upload dans `e2e-fullstack.yml`)

**Gaps identifiés** :
- ❌ Pas d'artefacts JUnit pour backend
- ❌ Pas d'artefacts JSON compliance
- ❌ Pas de sharding E2E
- ❌ Pas de healthchecks explicites avant E2E
- ❌ Pas de retries intelligents (seulement Playwright retries)

---

## 📜 SCRIPTS AUDIT

### Scripts existants

1. **`scripts/audit_content.py`** (Backend)
   - **Objectif** : Police des mots (blacklist/whitelist)
   - **Commande** : `python scripts/audit_content.py`
   - **Durée** : ~10-30s
   - **Statut** : ✅ **BLOQUANT** (workflow `audit-global.yml`)
   - **Exclusions** : `docs/`, `tests/compliance/`

2. **`scripts/generate_compliance_report.py`** (Backend)
   - **Objectif** : Générer rapport compliance
   - **Statut** : ⚠️ Non utilisé en CI

3. **`frontend/frontend/scripts/audit-home-vision.mjs`** (Frontend)
   - **Objectif** : Audit accueil/vision (promesses financières, mentions SAKA/EUR)
   - **Commande** : `npm run audit:home-vision`
   - **Durée** : ~5-10s
   - **Statut** : ✅ **BLOQUANT** (workflow `audit-home-vision.yml`)

4. **`frontend/frontend/scripts/audit-global.mjs`** (Frontend)
   - **Objectif** : Audit global frontend
   - **Commande** : `npm run audit:global`
   - **Statut** : ⚠️ Non utilisé en CI

**Gaps identifiés** :
- ✅ Couverture bonne, pas de gaps majeurs

---

## 📊 RÉSUMÉ DES GAPS PAR PRIORITÉ

### P0 - BLOQUANTS (Protection Constitution + Prod)

1. **Contract tests API** : Aucun test contract (OpenAPI/schéma)
2. **Permissions complètes** : Permissions manquantes pour CMS/finance
3. **E2E full-stack critiques** : Seulement 2 tests full-stack en CI
4. **Tests anti-dérive** : Scan code SAKA<->EUR existe, mais pas de tests promesses financières
5. **Data integrity** : Tests transaction_type existent, mais pas de tests cohérence complète
6. **Artefacts CI** : Pas de JUnit backend, pas de JSON compliance

### P1 - IMPORTANTS (Qualité + Sécurité)

1. **Accessibilité** : Pas de tests a11y automatisés (axe-core)
2. **XSS** : Pas de tests sanitization contenu
3. **Pagination/perf** : Pas de tests pagination, perf light
4. **Retry/backoff** : Pas de tests retry useFetch
5. **Rate-limit** : Pas de tests rate-limit endpoints sensibles
6. **Websocket/chat** : Pas de tests smoke (si existant)

### P2 - AMÉLIORATION (Optimisation)

1. **Sharding E2E** : Pas de sharding pour parallélisation
2. **Healthchecks CI** : Pas de healthchecks explicites avant E2E
3. **Retries intelligents** : Seulement retries Playwright, pas de retries backend
4. **Coverage thresholds** : Pas de seuils coverage stricts
5. **TypeScript strict** : Pas de lint TypeScript strict

---

## ✅ PROCHAINES ÉTAPES

1. **ÉTAPE 1** : Créer matrice de couverture détaillée (domaines x niveaux)
2. **ÉTAPE 2** : Implémenter tests P0 bloquants
3. **ÉTAPE 3** : Implémenter tests P1 importants
4. **ÉTAPE 4** : Wiring CI (jobs, sharding, artefacts, retries)
5. **ÉTAPE 5** : Documentation (test plan, checklist auto)


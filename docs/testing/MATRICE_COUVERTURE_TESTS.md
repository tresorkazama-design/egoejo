# 📊 Matrice de Couverture Tests EGOEJO

**Date** : 2025-01-XX  
**Objectif** : Mapper les domaines fonctionnels aux niveaux de tests et identifier les gaps

**Légende** :
- ✅ **EXISTE** : Test existant et fonctionnel
- ⚠️ **PARTIEL** : Test existant mais incomplet
- ❌ **MANQUE** : Test manquant (gap)
- 🔴 **P0** : Priorité bloquante (Constitution + Prod)
- 🟡 **P1** : Priorité importante (Qualité + Sécurité)
- 🟢 **P2** : Priorité amélioration (Optimisation)

---

## 📋 Domaines Fonctionnels

### 1. Accueil/Vision

| Niveau de Test | Unit | Integration | Contract | E2E | Security | Performance |
|----------------|------|-------------|----------|-----|----------|-------------|
| **i18n (FR/EN)** | ❌ | ❌ | ❌ | ✅ `home.spec.js` | ❌ | ❌ |
| **Accessibilité (a11y)** | ❌ | ❌ | ❌ | ⚠️ Partiel (skip links) | ❌ | ❌ |
| **Promesses financières** | ❌ | ❌ | ❌ | ✅ `audit-compliance-accueil-vision.spec.js` | ❌ | ❌ |
| **Mention SAKA/EUR** | ❌ | ❌ | ❌ | ✅ `home-vision-compliance.spec.js` | ❌ | ❌ |
| **Disclaimers** | ❌ | ❌ | ❌ | ✅ `home-vision-audit.spec.js` | ❌ | ❌ |

**Gaps P0** :
- ❌ Tests contract API accueil/vision
- ❌ Tests accessibilité automatisés (axe-core)

**Gaps P1** :
- ❌ Tests i18n unitaires
- ❌ Tests performance chargement accueil

**Fichiers existants** :
- `frontend/frontend/e2e/home.spec.js`
- `frontend/frontend/e2e/home-vision-compliance.spec.js`
- `frontend/frontend/e2e/home-vision-audit.spec.js`
- `frontend/frontend/e2e/audit-compliance-accueil-vision.spec.js`

---

### 2. Contenus/CMS

| Niveau de Test | Unit | Integration | Contract | E2E | Security | Performance |
|----------------|------|-------------|----------|-----|----------|-------------|
| **Workflow (draft/pending/published/archived)** | ✅ `test_content_workflow_transitions.py` | ❌ | ✅ `test_contract_cms_actions.py` | ✅ `cms-workflow-fullstack.spec.js` | ❌ | ❌ |
| **Permissions (create/edit/delete)** | ✅ `test_content_permissions.py` | ❌ | ✅ `test_contract_cms_actions.py` | ✅ `admin.spec.js` | ❌ | ❌ |
| **XSS sanitization** | ✅ `test_xss_sanitization.py` | ❌ | ❌ | ❌ | ✅ **P0** | ❌ |
| **Export JSON/CSV** | ❌ | ❌ | ✅ `test_contract_cms_actions.py` | ✅ `cms-workflow-fullstack.spec.js` | ❌ | ❌ |
| **Pagination** | ❌ | ❌ | ❌ | ✅ `cms-workflow-fullstack.spec.js` | ❌ | ❌ |
| **Pagination** | ❌ | ❌ | ❌ | ❌ | ❌ | 🟡 **P1** |
| **Cache** | ❌ | ❌ | ❌ | ❌ | ❌ | 🟡 **P1** |
| **Transitions workflow** | ✅ `test_content_workflow_transitions.py` | ❌ | ❌ | ⚠️ Partiel | ❌ | ❌ |

**Gaps P0** :
- 🔴 Tests XSS sanitization (description contenu)
- 🔴 Tests contract API CMS (publish/reject/archive)

**Gaps P1** :
- 🟡 Tests pagination (ne doit pas charger "tout")
- 🟡 Tests cache (invalidation)

**Fichiers existants** :
- `backend/core/tests/cms/test_content_permissions.py`
- `backend/core/tests/cms/test_content_workflow_transitions.py`
- `frontend/frontend/e2e/contenus.spec.js`
- `frontend/frontend/e2e/admin.spec.js`

---

### 3. Projets

| Niveau de Test | Unit | Integration | Contract | E2E | Security | Performance |
|----------------|------|-------------|----------|-----|----------|-------------|
| **Création projet** | ❌ | ❌ | ❌ | ⚠️ Partiel | ✅ `test_projects_permissions.py` | ❌ |
| **Publication projet** | ❌ | ❌ | ❌ | ⚠️ Partiel | ✅ `test_projects_permissions.py` | ❌ |
| **Financement EUR** | ❌ | ❌ | ❌ | ✅ `flux-complet-projet-financement.spec.js` | ✅ `test_stripe_segregation.py` | ❌ |
| **Affichage projet** | ❌ | ❌ | ❌ | ✅ `projects-saka-boost.spec.js` | ❌ | ❌ |
| **Permissions** | ✅ `test_projects_permissions.py` | ❌ | ❌ | ⚠️ Partiel | ❌ | ❌ |
| **Traçabilité (UI + API)** | ❌ | ❌ | ❌ | ❌ | 🔴 **P0** | ❌ |

**Gaps P0** :
- 🔴 Tests contract API projets (create/publish/list)
- 🔴 Tests traçabilité complète (financement EUR -> UI + API)

**Gaps P1** :
- 🟡 Tests pagination projets
- 🟡 Tests performance liste projets

**Fichiers existants** :
- `backend/core/tests/api/test_projects_permissions.py`
- `backend/finance/tests/test_stripe_segregation.py`
- `frontend/frontend/e2e/flux-complet-projet-financement.spec.js`
- `frontend/frontend/e2e/projects-saka-boost.spec.js`

---

### 4. SAKA

| Niveau de Test | Unit | Integration | Contract | E2E | Security | Performance |
|----------------|------|-------------|----------|-----|----------|-------------|
| **Grant** | ✅ `test_saka_wallet_protection.py` | ❌ | ❌ | ✅ `saka-flow.spec.js` | ✅ `test_saka_permissions.py` | ❌ |
| **Transactions** | ✅ `test_transaction_type_integrity.py` | ❌ | ❌ | ✅ `saka-lifecycle.spec.js` | ✅ `test_saka_wallet_raw_sql.py` | ❌ |
| **Compostage** | ✅ `test_saka_compost_depreciation_effective.py` | ❌ | ❌ | ✅ `saka-cycle-complet.spec.js` | ✅ Compliance | ❌ |
| **Silo/Redistribution** | ✅ `test_silo_redistribution.py` | ❌ | ❌ | ✅ `saka-cycle-fullstack.spec.js` | ✅ Compliance | ❌ |
| **Anti-accumulation** | ✅ `test_anti_accumulation.py` | ❌ | ❌ | ✅ `saka-cycle-visibility.spec.js` | ✅ Compliance | ❌ |
| **Non-convertibilité** | ✅ `test_no_saka_eur_conversion.py` | ❌ | ❌ | ✅ `saka-flow.spec.js` | ✅ Compliance | ❌ |
| **Vote** | ✅ `test_polls_permissions.py` | ❌ | ❌ | ✅ `votes.spec.js`, `votes-quadratic.spec.js` | ✅ `test_polls_permissions.py` | ❌ |

**Gaps P0** :
- 🔴 Tests contract API SAKA (grant/transactions/vote)
- 🔴 Tests E2E full-stack complets (seulement 2 en CI)

**Gaps P1** :
- 🟡 Tests performance grant/transactions (volume)

**Fichiers existants** :
- `backend/core/tests/models/test_saka_wallet_protection.py`
- `backend/core/tests/models/test_transaction_type_integrity.py`
- `backend/core/tests/api/test_saka_permissions.py`
- `backend/core/tests/api/test_polls_permissions.py`
- `backend/tests/compliance/test_anti_accumulation.py`
- `backend/tests/compliance/test_saka_compost_depreciation_effective.py`
- `backend/tests/compliance/test_silo_redistribution.py`
- `backend/tests/compliance/test_no_saka_eur_conversion.py`
- `frontend/frontend/e2e/saka-flow.spec.js`
- `frontend/frontend/e2e/saka-lifecycle.spec.js`
- `frontend/frontend/e2e/saka-cycle-complet.spec.js`
- `frontend/frontend/e2e/saka-cycle-fullstack.spec.js`
- `frontend/frontend/e2e/saka-cycle-visibility.spec.js`
- `frontend/frontend/e2e/votes.spec.js`
- `frontend/frontend/e2e/votes-quadratic.spec.js`
- `frontend/frontend/e2e/flux-complet-saka-vote.spec.js`

---

### 5. Euros/Finance

| Niveau de Test | Unit | Integration | Contract | E2E | Security | Performance |
|----------------|------|-------------|----------|-----|----------|-------------|
| **Paiement** | ✅ `test_stripe_segregation.py` | ❌ | ❌ | ✅ `flux-complet-projet-financement.spec.js` | ✅ `test_views_permissions.py` | ❌ |
| **Traçabilité** | ✅ `test_ledger_fee_allocation.py` | ❌ | ❌ | ⚠️ Partiel | ❌ | ❌ |
| **Promesse "dons nets"** | ❌ | ❌ | ❌ | ✅ `audit-compliance-accueil-vision.spec.js` | 🔴 **P0** | ❌ |
| **Webhooks Stripe** | ❌ | ❌ | 🔴 **P0** | ❌ | ❌ | ❌ |
| **Race conditions** | ✅ `test_race_condition_pledge.py` | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Deadlocks** | ✅ `test_deadlock_allocate_deposit.py` | ❌ | ❌ | ❌ | ❌ | ❌ |

**Gaps P0** :
- 🔴 Tests contract webhooks Stripe (payload, signature)
- 🔴 Tests validation promesses "dons nets" (texte doit contenir "nets après frais")

**Gaps P1** :
- 🟡 Tests traçabilité complète (paiement -> ledger -> UI)

**Fichiers existants** :
- `backend/finance/tests/test_stripe_segregation.py`
- `backend/finance/tests/test_ledger_fee_allocation.py`
- `backend/finance/tests/test_views_permissions.py`
- `backend/finance/tests/test_race_condition_pledge.py`
- `backend/finance/tests/test_deadlock_allocate_deposit.py`
- `backend/finance/tests/test_race_condition_release_escrow.py`
- `frontend/frontend/e2e/flux-complet-projet-financement.spec.js`

---

### 6. Chats/Communautés

| Niveau de Test | Unit | Integration | Contract | E2E | Security | Performance |
|----------------|------|-------------|----------|-----|----------|-------------|
| **Modération** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Permissions** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Anti-abus** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Rate limit** | ❌ | ❌ | ❌ | ❌ | 🟡 **P1** | ❌ |
| **PII** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Websocket/chat** | ❌ | ❌ | ❌ | ❌ | 🟡 **P1** | ❌ |

**Gaps P1** :
- 🟡 Tests rate-limit endpoints sensibles (si présent)
- 🟡 Tests smoke websocket/chat (connect/disconnect + auth)

**Fichiers existants** :
- Aucun (feature peut-être non implémentée)

---

### 7. Gouvernance/Label

| Niveau de Test | Unit | Integration | Contract | E2E | Security | Performance |
|----------------|------|-------------|----------|-----|----------|-------------|
| **Audit statique** | ✅ `scripts/audit_content.py` | ❌ | ❌ | ✅ `audit-compliance-accueil-vision.spec.js` | ✅ Compliance | ❌ |
| **Tests constitution** | ✅ `tests/compliance/` | ❌ | ❌ | ✅ `home-vision-compliance.spec.js` | ✅ Compliance | ❌ |
| **PR bot** | ✅ Workflow `egoejo-pr-bot.yml` | ❌ | ❌ | ❌ | ✅ Compliance | ❌ |
| **Branch protection** | ✅ Workflow `egoejo-guardian.yml` | ❌ | ❌ | ❌ | ✅ Compliance | ❌ |

**Gaps** :
- ✅ Couverture excellente, pas de gaps majeurs

**Fichiers existants** :
- `scripts/audit_content.py`
- `backend/tests/compliance/` (tous les tests)
- `.github/workflows/egoejo-pr-bot.yml`
- `.github/workflows/egoejo-guardian.yml`
- `frontend/frontend/e2e/home-vision-compliance.spec.js`

---

### 8. Observabilité/Alerting

| Niveau de Test | Unit | Integration | Contract | E2E | Security | Performance |
|----------------|------|-------------|----------|-----|----------|-------------|
| **Email alerts** | ✅ `test_alerts.py` | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Slack/Webhook alerts** | ✅ `test_alerts.py` | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Compteur alertes/mois** | ✅ `test_critical_alert_event.py` | ❌ | ✅ `test_critical_alert_metrics.py` | ❌ | ❌ | ❌ |
| **Endpoint métriques** | ✅ `test_critical_alert_metrics.py` | ❌ | ✅ `test_critical_alert_metrics.py` | ❌ | ❌ | ❌ |

**Gaps** :
- ✅ Couverture bonne, pas de gaps majeurs

**Fichiers existants** :
- `backend/core/tests/utils/test_alerts.py`
- `backend/core/tests/models/test_critical_alert_event.py`
- `backend/core/tests/api/test_critical_alert_metrics.py`

---

### 9. Sécurité Globale

| Niveau de Test | Unit | Integration | Contract | E2E | Security | Performance |
|----------------|------|-------------|----------|-----|----------|-------------|
| **Auth** | ✅ `test_saka_permissions.py` | ❌ | ❌ | ✅ `auth.spec.js` | ✅ `test_saka_permissions.py` | ❌ |
| **CORS/CSRF** | ❌ | ❌ | ❌ | ⚠️ Partiel (`backend-connection.spec.js`) | 🔴 **P0** | ❌ |
| **CSP** | ❌ | ❌ | ❌ | ❌ | 🔴 **P0** | ❌ |
| **Secrets** | ✅ `test_settings_failfast.py` | ❌ | ❌ | ❌ | ✅ Compliance | ❌ |
| **Injection** | ❌ | ❌ | ❌ | ❌ | 🔴 **P0** | ❌ |
| **SSRF** | ❌ | ❌ | ❌ | ❌ | 🔴 **P0** | ❌ |
| **IDOR** | ✅ `test_projects_permissions.py` | ❌ | ❌ | ⚠️ Partiel | ✅ `test_projects_permissions.py` | ❌ |

**Gaps P0** :
- 🔴 Tests CORS/CSRF (headers, tokens)
- 🔴 Tests CSP (Content-Security-Policy)
- 🔴 Tests injection (SQL, XSS)
- 🔴 Tests SSRF (endpoints externes)

**Fichiers existants** :
- `backend/core/tests/api/test_saka_permissions.py`
- `backend/core/tests/api/test_projects_permissions.py`
- `backend/tests/compliance/test_settings_failfast.py`
- `frontend/frontend/e2e/auth.spec.js`
- `frontend/frontend/e2e/backend-connection.spec.js`

---

### 10. Data Migrations & Résilience

| Niveau de Test | Unit | Integration | Contract | E2E | Security | Performance |
|----------------|------|-------------|----------|-----|----------|-------------|
| **Redis resilience** | ✅ `test_redis_resilience.py` | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Postgres resilience** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Migrations rollback** | ❌ | ❌ | ❌ | ❌ | ❌ | 🟡 **P1** |

**Gaps P1** :
- 🟡 Tests résilience Postgres (timeout, reconnexion)
- 🟡 Tests migrations rollback (rollback minimal)

**Fichiers existants** :
- `backend/tests/infrastructure/test_redis_resilience.py`

---

## 📊 RÉSUMÉ DES GAPS PAR PRIORITÉ

### 🔴 P0 - BLOQUANTS (Protection Constitution + Prod)

1. **Contract tests API** :
   - `/api/health` (❌)
   - Endpoints SAKA critiques (grant/transactions/vote) (❌)
   - Endpoints CMS (publish/reject/archive) (❌)
   - Endpoints projets (create/publish/list) (❌)
   - Webhooks Stripe (❌)

2. **Permissions complètes** :
   - Permissions CMS (✅ partiel)
   - Permissions finance (✅ partiel)
   - Permissions tous endpoints sensibles (⚠️ partiel)

3. **E2E full-stack critiques** :
   - Onboarding -> login -> dashboard (❌)
   - Cycle contenu -> SAKA reward (❌)
   - Cycle projet -> financement EUR -> traçabilité (⚠️ partiel)

4. **Tests anti-dérive** :
   - Scan code SAKA<->EUR (✅)
   - Tests promesses financières (validation "dons nets") (❌)

5. **Sécurité globale** :
   - Tests CORS/CSRF (❌)
   - Tests CSP (❌)
   - Tests injection (SQL, XSS) (❌)
   - Tests SSRF (❌)
   - Tests XSS sanitization contenu (❌)

6. **Artefacts CI** :
   - JUnit backend (❌)
   - JSON compliance (❌)

### 🟡 P1 - IMPORTANTS (Qualité + Sécurité)

1. **Accessibilité** :
   - Tests a11y automatisés (axe-core) (❌)

2. **Performance** :
   - Tests pagination (contenus/projets) (❌)
   - Tests perf light (❌)

3. **Retry/backoff** :
   - Tests retry useFetch (❌)

4. **Rate-limit** :
   - Tests rate-limit endpoints sensibles (❌)

5. **Websocket/chat** :
   - Tests smoke (connect/disconnect + auth) (❌)

6. **Résilience** :
   - Tests résilience Postgres (❌)
   - Tests migrations rollback (❌)

### 🟢 P2 - AMÉLIORATION (Optimisation)

1. **CI** :
   - Sharding E2E (❌)
   - Healthchecks explicites avant E2E (❌)
   - Retries intelligents backend (❌)

2. **Coverage** :
   - Seuils coverage stricts (❌)

3. **TypeScript** :
   - Lint TypeScript strict (❌)

---

## ✅ PROCHAINES ÉTAPES

1. **ÉTAPE 2** : Implémenter tests P0 bloquants
2. **ÉTAPE 3** : Implémenter tests P1 importants
3. **ÉTAPE 4** : Wiring CI (jobs, sharding, artefacts, retries)
4. **ÉTAPE 5** : Documentation (test plan, checklist auto)


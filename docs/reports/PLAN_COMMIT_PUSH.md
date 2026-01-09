# PLAN DE COMMIT/PUSH - AUDIT-READY

**Date de génération:** 2026-01-09  
**Basé sur:** État Git actuel (26 modified unstaged + 54 untracked + submodule frontend modifié)

---

## 1. CLASSIFICATION DES FICHIERS EN 4 CATÉGORIES

### A. CODE BACKEND (API/models/services/migrations)

#### **Fichiers MODIFIÉS (non-staged):**
- `backend/config/settings.py`
- `backend/core/api/__init__.py`
- `backend/core/api/compliance_views.py`
- `backend/core/api/content_views.py`
- `backend/core/api/polls.py`
- `backend/core/models/__init__.py`
- `backend/core/permissions.py`
- `backend/core/security/sanitization.py`
- `backend/core/serializers/content.py`
- `backend/core/urls.py`
- `backend/finance/views.py`
- `backend/requirements.txt`
- `backend/pytest.ini`

#### **Fichiers UNTRACKED (nouveaux):**
- `backend/core/migrations/0032_add_transaction_type_to_sakatransaction.py` ⚠️ **MIGRATION**
- `backend/core/api/chat_moderation.py`
- `backend/core/api/institutional_exports.py`
- `backend/core/models/chat_moderation.py`
- `backend/finance/helloasso_client.py`
- `backend/finance/ledger_services/helloasso_ledger.py`
- `backend/finance/stripe_utils.py`

**Total:** 20 fichiers (13 modifiés + 7 nouveaux)

---

### B. CI/WORKFLOWS/SCRIPTS (GitHub Actions + scripts/)

#### **Fichiers MODIFIÉS (non-staged):**
- `.github/workflows/audit-global.yml`
- `.github/workflows/ci.yml`
- `.github/workflows/e2e-fullstack.yml`
- `scripts/audit_content.py`

#### **Fichiers UNTRACKED (nouveaux):**
- `.github/workflows/monthly-auto-audit.yml`
- `.github/workflows/verify-critical-tests.yml`
- `scripts/generate_monthly_audit_report.py`
- `scripts/simulate_webhook_helloasso.py`
- `scripts/simulate_webhook_stripe.py`
- `scripts/verify_critical_markers.py`
- `scripts/__tests__/` (dossier)

**Total:** 11 fichiers (4 modifiés + 7 nouveaux)

---

### C. TESTS (backend + frontend + E2E)

#### **Fichiers MODIFIÉS (non-staged):**
- `backend/core/api/__tests__/test_compliance_badge.py`
- `backend/core/api/__tests__/test_compliance_views.py`
- `backend/core/tests/api/test_polls_permissions.py`
- `backend/core/tests/api/test_projects_permissions.py`
- `backend/core/tests/cms/test_content_permissions.py`
- `backend/finance/tests/test_stripe_segregation.py`
- `backend/tests/compliance/test_settings_failfast.py`

#### **Fichiers UNTRACKED (nouveaux):**
- `backend/core/tests/api/test_contract_cms.py`
- `backend/core/tests/api/test_contract_cms_actions.py`
- `backend/core/tests/api/test_contract_cms_export.py`
- `backend/core/tests/api/test_contract_cms_pagination.py`
- `backend/core/tests/api/test_contract_cms_workflow.py`
- `backend/core/tests/api/test_contract_health.py`
- `backend/core/tests/api/test_contract_projects.py`
- `backend/core/tests/api/test_contract_saka.py`
- `backend/core/tests/api/test_critical_alert_metrics.py`
- `backend/core/tests/api/test_institutional_exports.py`
- `backend/core/tests/cms/test_content_crud.py`
- `backend/core/tests/cms/test_content_i18n.py`
- `backend/core/tests/cms/test_content_security_external.py`
- `backend/core/tests/cms/test_content_versioning.py`
- `backend/core/tests/cms/test_content_xss.py`
- `backend/core/tests/cms/test_xss_sanitization.py`
- `backend/core/tests/models/test_transaction_type_integrity.py`
- `backend/core/tests/websocket/` (dossier)
- `backend/finance/tests/test_contract_webhooks_stripe.py`
- `backend/finance/tests/test_helloasso_contract.py`
- `backend/finance/tests/test_payments_kyc.py`
- `backend/finance/tests/test_payments_saka_segregation.py`
- `backend/finance/tests/test_payments_security.py`
- `backend/tests/compliance/governance/test_constitution_documents.py`

**Total:** 31 fichiers (7 modifiés + 24 nouveaux)

---

### D. DOCUMENTATION (docs/*)

#### **Fichiers MODIFIÉS (non-staged):**
- `docs/governance/REQUIRED_CHECKS.md`
- `docs/institutionnel/NOTE_CONCEPTUELLE_FONDATIONS.md`
- `docs/institutionnel/NOTE_CONCEPTUELLE_ONU.md`
- `docs/security/ALERTING_EMAIL.md`

#### **Fichiers UNTRACKED (nouveaux):**
- `docs/MANUEL_OFFICIEL_EGOEJO.md`
- `docs/chat/WEBSOCKET_CHAT.md`
- `docs/cms/CMS_WORKFLOW.md`
- `docs/compliance/EXPORTS_INSTITUTIONNELS.md`
- `docs/finance/` (dossier - vérifier contenu)
- `docs/observability/CRITICAL_ALERT_METRICS.md`
- `docs/reports/AUDIT_GLOBAL_CHANGEMENTS_EGOEJO.md`
- `docs/reports/GIT_SYNC_REPORT.md` ✅ (déjà créé)
- `docs/reports/MONTHLY_AUTO_AUDIT.md`
- `docs/security/ALERTING_SLACK.md`
- `docs/testing/` (dossier - 14 fichiers)

**Total:** 18 fichiers (4 modifiés + 14 nouveaux/dossiers)

---

## 2. FICHIERS À IGNORER (.gitignore)

### Fichiers à ajouter à `.gitignore`:

| Fichier/Dossier | Raison |
|-----------------|--------|
| `backend/junit.xml` | Artefact de test généré automatiquement |
| `test_protocol.ps1` | Script de test temporaire (si non destiné au repo) |
| `frontend/audit-result.json` | Artefact d'audit généré |
| `frontend/playwright-results.txt` | Artefact Playwright |

### Fichiers à VERSIONNER (ne PAS ignorer):

Tous les autres fichiers untracked doivent être versionnés car ils sont:
- Code source (API, models, services)
- Tests unitaires/intégration
- Migrations Django (critiques)
- Documentation normative
- Scripts utilitaires
- Workflows CI/CD

**Action:** Mettre à jour `.gitignore` avec les fichiers ci-dessus.

---

## 3. PLAN DE COMMITS PAR CATÉGORIE

### ORDRE RECOMMANDÉ (cohérence fonctionnelle)

1. **Migrations** (prérequis pour tout le reste)
2. **Code backend** (API, models, services)
3. **Tests backend** (validation du code)
4. **CI/Workflows/Scripts** (automatisation)
5. **Documentation** (finalisation)
6. **Submodule frontend** (séparé)

---

### COMMIT 1: Migration transaction_type SAKA

**Type:** `feat(backend)`  
**Message:** `feat(backend): Ajout champ transaction_type à SakaTransaction avec migration`

**Fichiers à ajouter:**
```bash
git add backend/core/migrations/0032_add_transaction_type_to_sakatransaction.py
```

**Check de cohérence:**
- ✅ Migration dépend de `0031_add_critical_alert_event` (vérifié)
- ✅ Migration inclut RunPython pour données existantes
- ⚠️ **VÉRIFIER:** Le modèle `SakaTransaction` dans `backend/core/models/__init__.py` est cohérent

**Commande exacte:**
```bash
git add backend/core/migrations/0032_add_transaction_type_to_sakatransaction.py
git commit -m "feat(backend): Ajout champ transaction_type à SakaTransaction avec migration

- Migration 0032: Ajout transaction_type (HARVEST, SPEND, COMPOST, REDISTRIBUTION)
- Migration des données existantes (EARN -> HARVEST, SPEND -> SPEND)
- Champ non-nullable après migration"
```

---

### COMMIT 2: API Chat Moderation + Institutional Exports

**Type:** `feat(backend)`  
**Message:** `feat(backend): API chat moderation et exports institutionnels`

**Fichiers à ajouter:**
```bash
git add backend/core/api/chat_moderation.py
git add backend/core/api/institutional_exports.py
git add backend/core/models/chat_moderation.py
```

**Commande exacte:**
```bash
git add backend/core/api/chat_moderation.py \
       backend/core/api/institutional_exports.py \
       backend/core/models/chat_moderation.py
git commit -m "feat(backend): API chat moderation et exports institutionnels

- API chat_moderation: Modération des messages chat
- API institutional_exports: Exports JSON/Markdown pour ONU/Fondations/États
- Modèle ChatModeration pour tracking des modérations"
```

---

### COMMIT 3: Finance - HelloAsso + Stripe Utils

**Type:** `feat(finance)`  
**Message:** `feat(finance): Clients HelloAsso et utilitaires Stripe`

**Fichiers à ajouter:**
```bash
git add backend/finance/helloasso_client.py
git add backend/finance/ledger_services/helloasso_ledger.py
git add backend/finance/stripe_utils.py
```

**Commande exacte:**
```bash
git add backend/finance/helloasso_client.py \
       backend/finance/ledger_services/helloasso_ledger.py \
       backend/finance/stripe_utils.py
git commit -m "feat(finance): Clients HelloAsso et utilitaires Stripe

- helloasso_client: Client API HelloAsso
- helloasso_ledger: Service ledger pour HelloAsso
- stripe_utils: Utilitaires pour intégration Stripe"
```

---

### COMMIT 4: Modifications API/Models/Services existants

**Type:** `refactor(backend)` ou `fix(backend)` selon les changements  
**Message:** `refactor(backend): Améliorations API, permissions et sécurité`

**Fichiers à ajouter:**
```bash
git add backend/config/settings.py
git add backend/core/api/__init__.py
git add backend/core/api/compliance_views.py
git add backend/core/api/content_views.py
git add backend/core/api/polls.py
git add backend/core/models/__init__.py
git add backend/core/permissions.py
git add backend/core/security/sanitization.py
git add backend/core/serializers/content.py
git add backend/core/urls.py
git add backend/finance/views.py
git add backend/requirements.txt
git add backend/pytest.ini
```

**⚠️ AVANT COMMIT:** Examiner les diffs pour déterminer si `refactor`, `fix`, ou `feat`:
```bash
git diff backend/config/settings.py
git diff backend/core/urls.py
git diff backend/requirements.txt
```

**Commande exacte (exemple refactor):**
```bash
git add backend/config/settings.py \
       backend/core/api/__init__.py \
       backend/core/api/compliance_views.py \
       backend/core/api/content_views.py \
       backend/core/api/polls.py \
       backend/core/models/__init__.py \
       backend/core/permissions.py \
       backend/core/security/sanitization.py \
       backend/core/serializers/content.py \
       backend/core/urls.py \
       backend/finance/views.py \
       backend/requirements.txt \
       backend/pytest.ini
git commit -m "refactor(backend): Améliorations API, permissions et sécurité

- Mise à jour settings.py
- Améliorations compliance_views et content_views
- Renforcement sanitization et permissions
- Mise à jour requirements.txt et pytest.ini"
```

---

### COMMIT 5: Tests CMS Contract (nouveaux)

**Type:** `test(backend)`  
**Message:** `test(backend): Tests contract CMS (CRUD, workflow, pagination, export)`

**Fichiers à ajouter:**
```bash
git add backend/core/tests/api/test_contract_cms.py
git add backend/core/tests/api/test_contract_cms_actions.py
git add backend/core/tests/api/test_contract_cms_export.py
git add backend/core/tests/api/test_contract_cms_pagination.py
git add backend/core/tests/api/test_contract_cms_workflow.py
```

**Commande exacte:**
```bash
git add backend/core/tests/api/test_contract_cms*.py
git commit -m "test(backend): Tests contract CMS (CRUD, workflow, pagination, export)

- Tests CRUD CMS complet
- Tests workflow CMS
- Tests pagination CMS
- Tests export CMS
- Tests actions CMS"
```

---

### COMMIT 6: Tests Contract Health + Projects + SAKA

**Type:** `test(backend)`  
**Message:** `test(backend): Tests contract health, projects et SAKA`

**Fichiers à ajouter:**
```bash
git add backend/core/tests/api/test_contract_health.py
git add backend/core/tests/api/test_contract_projects.py
git add backend/core/tests/api/test_contract_saka.py
```

**Commande exacte:**
```bash
git add backend/core/tests/api/test_contract_health.py \
       backend/core/tests/api/test_contract_projects.py \
       backend/core/tests/api/test_contract_saka.py
git commit -m "test(backend): Tests contract health, projects et SAKA

- Tests contract health endpoints
- Tests contract projects API
- Tests contract SAKA transactions"
```

---

### COMMIT 7: Tests Critical Metrics + Institutional Exports

**Type:** `test(backend)`  
**Message:** `test(backend): Tests critical alert metrics et exports institutionnels`

**Fichiers à ajouter:**
```bash
git add backend/core/tests/api/test_critical_alert_metrics.py
git add backend/core/tests/api/test_institutional_exports.py
```

**Commande exacte:**
```bash
git add backend/core/tests/api/test_critical_alert_metrics.py \
       backend/core/tests/api/test_institutional_exports.py
git commit -m "test(backend): Tests critical alert metrics et exports institutionnels

- Tests critical alert metrics
- Tests exports institutionnels API"
```

---

### COMMIT 8: Tests CMS Content (CRUD, i18n, sécurité, versioning, XSS)

**Type:** `test(backend)`  
**Message:** `test(backend): Tests CMS content (CRUD, i18n, sécurité, versioning, XSS)`

**Fichiers à ajouter:**
```bash
git add backend/core/tests/cms/test_content_crud.py
git add backend/core/tests/cms/test_content_i18n.py
git add backend/core/tests/cms/test_content_security_external.py
git add backend/core/tests/cms/test_content_versioning.py
git add backend/core/tests/cms/test_content_xss.py
git add backend/core/tests/cms/test_xss_sanitization.py
```

**Commande exacte:**
```bash
git add backend/core/tests/cms/test_content_*.py \
       backend/core/tests/cms/test_xss_sanitization.py
git commit -m "test(backend): Tests CMS content (CRUD, i18n, sécurité, versioning, XSS)

- Tests CRUD contenu CMS
- Tests i18n contenu CMS
- Tests sécurité externe contenu CMS
- Tests versioning contenu CMS
- Tests XSS et sanitization contenu CMS"
```

---

### COMMIT 9: Tests Transaction Type + WebSocket + Finance

**Type:** `test(backend)`  
**Message:** `test(backend): Tests transaction type integrity, WebSocket et finance`

**Fichiers à ajouter:**
```bash
git add backend/core/tests/models/test_transaction_type_integrity.py
git add backend/core/tests/websocket/
git add backend/finance/tests/test_contract_webhooks_stripe.py
git add backend/finance/tests/test_helloasso_contract.py
git add backend/finance/tests/test_payments_kyc.py
git add backend/finance/tests/test_payments_saka_segregation.py
git add backend/finance/tests/test_payments_security.py
git add backend/tests/compliance/governance/test_constitution_documents.py
```

**Commande exacte:**
```bash
git add backend/core/tests/models/test_transaction_type_integrity.py \
       backend/core/tests/websocket/ \
       backend/finance/tests/test_contract_webhooks_stripe.py \
       backend/finance/tests/test_helloasso_contract.py \
       backend/finance/tests/test_payments_kyc.py \
       backend/finance/tests/test_payments_saka_segregation.py \
       backend/finance/tests/test_payments_security.py \
       backend/tests/compliance/governance/test_constitution_documents.py
git commit -m "test(backend): Tests transaction type integrity, WebSocket et finance

- Tests intégrité transaction_type
- Tests WebSocket
- Tests webhooks Stripe contracts
- Tests HelloAsso contracts
- Tests KYC payments
- Tests ségrégation SAKA payments
- Tests sécurité payments
- Tests gouvernance constitution documents"
```

---

### COMMIT 10: Modifications tests existants

**Type:** `test(backend)`  
**Message:** `test(backend): Améliorations tests existants (compliance, permissions, finance)`

**Fichiers à ajouter:**
```bash
git add backend/core/api/__tests__/test_compliance_badge.py
git add backend/core/api/__tests__/test_compliance_views.py
git add backend/core/tests/api/test_polls_permissions.py
git add backend/core/tests/api/test_projects_permissions.py
git add backend/core/tests/cms/test_content_permissions.py
git add backend/finance/tests/test_stripe_segregation.py
git add backend/tests/compliance/test_settings_failfast.py
```

**Commande exacte:**
```bash
git add backend/core/api/__tests__/test_compliance_badge.py \
       backend/core/api/__tests__/test_compliance_views.py \
       backend/core/tests/api/test_polls_permissions.py \
       backend/core/tests/api/test_projects_permissions.py \
       backend/core/tests/cms/test_content_permissions.py \
       backend/finance/tests/test_stripe_segregation.py \
       backend/tests/compliance/test_settings_failfast.py
git commit -m "test(backend): Améliorations tests existants (compliance, permissions, finance)

- Améliorations tests compliance badge et views
- Améliorations tests permissions polls, projects, content
- Améliorations tests ségrégation Stripe
- Améliorations tests settings failfast"
```

---

### COMMIT 11: CI Workflows - Monthly Audit + Critical Tests

**Type:** `ci`  
**Message:** `ci: Ajout workflows monthly auto-audit et verify critical tests`

**Fichiers à ajouter:**
```bash
git add .github/workflows/monthly-auto-audit.yml
git add .github/workflows/verify-critical-tests.yml
```

**Commande exacte:**
```bash
git add .github/workflows/monthly-auto-audit.yml \
       .github/workflows/verify-critical-tests.yml
git commit -m "ci: Ajout workflows monthly auto-audit et verify critical tests

- Monthly auto-audit: Audit mensuel automatisé (cron 1er du mois)
- Verify critical tests: Vérification marqueurs tests critiques en PR"
```

---

### COMMIT 12: Modifications CI Workflows existants

**Type:** `ci`  
**Message:** `ci: Améliorations workflows audit-global, ci et e2e-fullstack`

**Fichiers à ajouter:**
```bash
git add .github/workflows/audit-global.yml
git add .github/workflows/ci.yml
git add .github/workflows/e2e-fullstack.yml
```

**⚠️ AVANT COMMIT:** Examiner les diffs:
```bash
git diff .github/workflows/audit-global.yml
git diff .github/workflows/ci.yml
git diff .github/workflows/e2e-fullstack.yml
```

**Commande exacte:**
```bash
git add .github/workflows/audit-global.yml \
       .github/workflows/ci.yml \
       .github/workflows/e2e-fullstack.yml
git commit -m "ci: Améliorations workflows audit-global, ci et e2e-fullstack

- Améliorations workflow audit-global
- Améliorations workflow CI
- Améliorations workflow E2E fullstack"
```

---

### COMMIT 13: Scripts utilitaires (audit, webhooks, vérification)

**Type:** `chore(scripts)`  
**Message:** `chore(scripts): Scripts audit mensuel, webhooks et vérification marqueurs`

**Fichiers à ajouter:**
```bash
git add scripts/audit_content.py
git add scripts/generate_monthly_audit_report.py
git add scripts/simulate_webhook_helloasso.py
git add scripts/simulate_webhook_stripe.py
git add scripts/verify_critical_markers.py
git add scripts/__tests__/
```

**Commande exacte:**
```bash
git add scripts/audit_content.py \
       scripts/generate_monthly_audit_report.py \
       scripts/simulate_webhook_helloasso.py \
       scripts/simulate_webhook_stripe.py \
       scripts/verify_critical_markers.py \
       scripts/__tests__/
git commit -m "chore(scripts): Scripts audit mensuel, webhooks et vérification marqueurs

- Script audit_content: Audit de contenu
- Script generate_monthly_audit_report: Génération rapport audit mensuel
- Scripts simulate_webhook_*: Simulation webhooks HelloAsso et Stripe
- Script verify_critical_markers: Vérification marqueurs tests critiques
- Tests scripts"
```

---

### COMMIT 14: Documentation - Chat + CMS + Compliance + Finance

**Type:** `docs`  
**Message:** `docs: Documentation chat, CMS, exports institutionnels et finance`

**Fichiers à ajouter:**
```bash
git add docs/chat/
git add docs/cms/
git add docs/compliance/EXPORTS_INSTITUTIONNELS.md
git add docs/finance/
```

**⚠️ VÉRIFIER:** Contenu du dossier `docs/finance/` avant commit:
```bash
ls docs/finance/
```

**Commande exacte:**
```bash
git add docs/chat/ \
       docs/cms/ \
       docs/compliance/EXPORTS_INSTITUTIONNELS.md \
       docs/finance/
git commit -m "docs: Documentation chat, CMS, exports institutionnels et finance

- Documentation WebSocket chat
- Documentation workflow CMS
- Documentation exports institutionnels
- Documentation finance"
```

---

### COMMIT 15: Documentation - Observability + Security + Reports

**Type:** `docs`  
**Message:** `docs: Documentation observability, security alerting et rapports`

**Fichiers à ajouter:**
```bash
git add docs/observability/CRITICAL_ALERT_METRICS.md
git add docs/security/ALERTING_SLACK.md
git add docs/reports/AUDIT_GLOBAL_CHANGEMENTS_EGOEJO.md
git add docs/reports/MONTHLY_AUTO_AUDIT.md
git add docs/reports/GIT_SYNC_REPORT.md
```

**Commande exacte:**
```bash
git add docs/observability/CRITICAL_ALERT_METRICS.md \
       docs/security/ALERTING_SLACK.md \
       docs/reports/AUDIT_GLOBAL_CHANGEMENTS_EGOEJO.md \
       docs/reports/MONTHLY_AUTO_AUDIT.md \
       docs/reports/GIT_SYNC_REPORT.md
git commit -m "docs: Documentation observability, security alerting et rapports

- Documentation critical alert metrics
- Documentation alerting Slack
- Rapports audit global et monthly auto-audit
- Rapport état Git sync"
```

---

### COMMIT 16: Documentation - Testing + Manuel Officiel + Modifications

**Type:** `docs`  
**Message:** `docs: Documentation testing, manuel officiel et mises à jour`

**Fichiers à ajouter:**
```bash
git add docs/testing/
git add docs/MANUEL_OFFICIEL_EGOEJO.md
git add docs/governance/REQUIRED_CHECKS.md
git add docs/institutionnel/NOTE_CONCEPTUELLE_FONDATIONS.md
git add docs/institutionnel/NOTE_CONCEPTUELLE_ONU.md
git add docs/security/ALERTING_EMAIL.md
```

**Commande exacte:**
```bash
git add docs/testing/ \
       docs/MANUEL_OFFICIEL_EGOEJO.md \
       docs/governance/REQUIRED_CHECKS.md \
       docs/institutionnel/NOTE_CONCEPTUELLE_FONDATIONS.md \
       docs/institutionnel/NOTE_CONCEPTUELLE_ONU.md \
       docs/security/ALERTING_EMAIL.md
git commit -m "docs: Documentation testing, manuel officiel et mises à jour

- Documentation complète testing (14 fichiers)
- Manuel officiel EGOEJO
- Mise à jour REQUIRED_CHECKS
- Mise à jour notes conceptuelles Fondations et ONU
- Mise à jour documentation alerting email"
```

---

### COMMIT 17: Mise à jour .gitignore

**Type:** `chore`  
**Message:** `chore: Mise à jour .gitignore (artefacts tests, fichiers temporaires)`

**Fichiers à modifier:**
- `.gitignore` (ajouter les patterns)

**Action:** Ajouter à `.gitignore`:
```
# Artefacts de tests
backend/junit.xml
frontend/audit-result.json
frontend/playwright-results.txt

# Scripts temporaires
test_protocol.ps1
```

**Commande exacte:**
```bash
# Éditer .gitignore manuellement, puis:
git add .gitignore
git commit -m "chore: Mise à jour .gitignore (artefacts tests, fichiers temporaires)

- Ignorer junit.xml (artefact de test)
- Ignorer audit-result.json et playwright-results.txt (artefacts Playwright)
- Ignorer test_protocol.ps1 (script temporaire)"
```

---

### COMMIT 18: Submodule frontend (SÉPARÉ - voir section 4)

**Type:** `chore(frontend)`  
**Message:** `chore(frontend): Mise à jour submodule frontend (fix/hash-navigation-scroll)`

**Procédure:** Voir section 4 ci-dessous.

---

## 4. GESTION SUBMODULE `frontend`

### État actuel:
- Submodule sur branche: `fix/hash-navigation-scroll`
- Statut: Modifié (beaucoup de fichiers)

### Procédure correcte:

#### **Étape 1: Vérifier le commit référencé dans le submodule**
```bash
cd frontend
git status -sb
git log --oneline -5
cd ..
```

#### **Étape 2: Décision stratégique**

**Option A: Les modifications frontend sont liées aux changements backend (cohérence)**
- Commiter le submodule dans le même commit/PR que les changements backend associés
- **Recommandé si:** Les changements frontend sont nécessaires pour utiliser les nouvelles API backend

**Option B: Les modifications frontend sont indépendantes (frontend autonome)**
- Créer une PR séparée uniquement pour le submodule frontend
- **Recommandé si:** Les changements frontend sont isolés (UX, navigation, UI)

#### **Étape 3: Commiter le submodule**

**Si Option A (intégré):**
```bash
cd frontend
git add .
git commit -m "fix(frontend): Fix hash navigation scroll

- Corrections navigation avec hash
- Améliorations scroll behavior
- ... (voir git status pour détails)"
git push origin fix/hash-navigation-scroll  # Pousser d'abord le submodule
cd ..
git add frontend  # Mettre à jour le pointeur du submodule
git commit -m "chore(frontend): Mise à jour submodule frontend (fix hash navigation scroll)"
```

**Si Option B (séparé):**
```bash
cd frontend
git add .
git commit -m "fix(frontend): Fix hash navigation scroll"
git push origin fix/hash-navigation-scroll
# Créer une PR frontend séparée
cd ..
# Plus tard, après merge de la PR frontend:
git add frontend
git commit -m "chore(frontend): Mise à jour submodule frontend"
```

### ⚠️ **RECOMMANDATION:**

**Option B (séparé)** car:
- Le submodule a une branche spécifique `fix/hash-navigation-scroll`
- Beaucoup de modifications (navigation, scroll, UI)
- Permet de revoir et merger le frontend indépendamment

**Procédure recommandée:**
1. Commiter et pousser le submodule frontend dans sa branche
2. Créer une PR frontend `fix/hash-navigation-scroll` → `main` (du submodule)
3. Après merge, mettre à jour le pointeur du submodule dans le repo principal

---

## 5. CONFIGURATION LINE ENDINGS (LF/CRLF)

### Problème identifié:
Plusieurs fichiers Python génèrent des avertissements `LF will be replaced by CRLF`:
- `backend/config/settings.py`
- `backend/core/api/content_views.py`
- `backend/core/api/polls.py`
- `backend/core/models/__init__.py`
- `backend/core/permissions.py`
- Etc.

### Solution recommandée:

#### **Créer `.gitattributes`** (à la racine du repo):

```gitattributes
# Configuration automatique des line endings

# Text files - normaliser en LF
* text=auto eol=lf

# Fichiers spécifiques qui doivent être CRLF (si nécessaire)
*.ps1 text eol=crlf
*.bat text eol=crlf
*.cmd text eol=crlf

# Fichiers binaires - ne pas modifier
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.ico binary
*.pdf binary
*.zip binary
*.tar.gz binary
*.mp4 binary
*.mov binary
```

#### **Configuration Git locale:**

```bash
# Normaliser les line endings pour ce repo
git config core.autocrlf false
git config core.eol lf

# Appliquer .gitattributes
git add .gitattributes
git commit -m "chore: Configuration line endings (LF) via .gitattributes"
```

#### **Normaliser les fichiers existants:**

⚠️ **ATTENTION:** Cette opération peut créer beaucoup de diffs. À faire **AVANT** les autres commits.

```bash
# Sauvegarde
git stash

# Normaliser tous les fichiers
git add --renormalize .

# Vérifier les changements
git status

# Si OK, commiter
git commit -m "chore: Normalisation line endings (LF) fichiers existants"
```

**Recommandation:** Faire cette normalisation **AVANT** le commit 1 (migrations).

---

## 6. STRATÉGIE FINALE: PR UNIQUE OU MULTIPLES PR?

### Option A: 1 PR UNIQUE (tous les commits)

**Avantages:**
- ✅ Revue complète en une fois
- ✅ Merge atomique
- ✅ CI exécutée une seule fois sur l'ensemble

**Inconvénients:**
- ❌ PR très volumineuse (80+ fichiers)
- ❌ Difficile à revoir
- ❌ Risque de conflit élevé
- ❌ Bloque le merge si un seul commit pose problème

### Option B: 3 PR SÉPARÉES (par domaine fonctionnel)

#### **PR 1: Backend Core + Migrations + Tests Backend**
- Commits 1-10 (migrations, API, models, tests backend)
- **Raison:** Cohérence fonctionnelle (migrations → code → tests)
- **Taille:** ~40 fichiers

#### **PR 2: CI/Workflows + Scripts + Documentation**
- Commits 11-16 (CI, scripts, docs)
- **Raison:** Infrastructure et documentation
- **Taille:** ~30 fichiers

#### **PR 3: Submodule Frontend** (si Option B section 4)
- Commit 18 (submodule frontend)
- **Raison:** Frontend indépendant
- **Taille:** Variables (beaucoup de fichiers dans submodule)

**Avantages:**
- ✅ PRs plus petites et faciles à revoir
- ✅ CI par domaine fonctionnel
- ✅ Merge progressif
- ✅ Moins de conflits

**Inconvénients:**
- ❌ Plus de PRs à gérer
- ❌ Ordre de merge important (PR1 avant PR2)

### Option C: 5 PR SPÉCIALISÉES (granularité fine)

1. **PR: Migrations + Models** (Commit 1)
2. **PR: API Backend** (Commits 2-4)
3. **PR: Tests Backend** (Commits 5-10)
4. **PR: CI + Scripts + Docs** (Commits 11-16)
5. **PR: Frontend** (Commit 18)

**Avantages:**
- ✅ PRs très ciblées
- ✅ Revue ultra-facile

**Inconvénients:**
- ❌ Beaucoup de PRs
- ❌ Dépendances entre PRs (ordre critique)

---

### ⭐ **RECOMMANDATION: Option B (3 PR)**

**Justification:**
1. **PR 1 (Backend)** contient migrations + code + tests = cohérence fonctionnelle
2. **PR 2 (CI/Docs)** est indépendante et peut être mergée après PR 1
3. **PR 3 (Frontend)** est isolée et peut être mergée indépendamment

**Ordre de merge recommandé:**
1. PR 1: Backend Core + Migrations + Tests
2. PR 3: Frontend (peut être en parallèle)
3. PR 2: CI + Scripts + Docs (après PR 1 validée)

---

## 7. CHECKLIST PRÉ-COMMIT

Avant d'exécuter les commandes:

- [ ] **Normaliser line endings** (section 5)
- [ ] **Mettre à jour .gitignore** (section 2)
- [ ] **Vérifier migrations:** Cohérence avec models
- [ ] **Vérifier tests:** Tous les nouveaux tests passent
- [ ] **Vérifier submodule:** Décision Option A ou B (section 4)
- [ ] **Examiner diffs critiques:** `settings.py`, `requirements.txt`, `urls.py`
- [ ] **Vérifier cohérence:** Tests liés aux APIs ajoutées existent

---

## 8. COMMANDES GIT EXACTES (RÉSUMÉ)

### Phase 1: Préparation
```bash
# 1. Normaliser line endings
git config core.autocrlf false
git config core.eol lf
# Créer .gitattributes (contenu section 5)
git add .gitattributes
git commit -m "chore: Configuration line endings (LF) via .gitattributes"
git add --renormalize .
git commit -m "chore: Normalisation line endings (LF) fichiers existants"

# 2. Mettre à jour .gitignore
# Éditer .gitignore (ajouter patterns section 2)
git add .gitignore
git commit -m "chore: Mise à jour .gitignore (artefacts tests, fichiers temporaires)"
```

### Phase 2: Backend (PR 1)
```bash
# Commits 1-10 (voir section 3)
# ... (exécuter dans l'ordre)
```

### Phase 3: CI/Docs (PR 2)
```bash
# Commits 11-16 (voir section 3)
# ... (exécuter dans l'ordre)
```

### Phase 4: Frontend (PR 3)
```bash
# Commit 18 (voir section 4)
```

### Phase 5: Push
```bash
# Pour chaque PR:
git push origin main  # ou branche feature spécifique
```

---

**Plan validé:** ✅  
**Prêt pour exécution:** Après validation de la stratégie PR (Option B recommandée)


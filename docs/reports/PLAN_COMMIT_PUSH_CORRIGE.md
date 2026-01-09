# PLAN DE COMMIT/PUSH CORRIGÉ - AUDIT-READY (Build-Safe)

**Date de génération:** 2026-01-09  
**Méthodologie:** Reconstruit selon règles strictes (migration+modèle+test, API+wiring, submodule sécurisé)

---

## RÈGLES STRICTES APPLIQUÉES

1. ✅ **Migration Django** = migration + modèle + test d'intégrité (MÊME COMMIT)
2. ✅ **Nouvelle API** = fichier API + wiring (urls.py, api/__init__.py, permissions) (MÊME COMMIT)
3. ✅ **Tests** arrivent après le code qu'ils testent
4. ✅ **Submodule frontend** : ne pointer que vers un commit pushé et mergé
5. ✅ **CI Workflows** : après que la base de tests passe localement

---

## FICHIERS À IGNORER (.gitignore mis à jour)

### Patterns recommandés (à ajouter):

```gitattributes
# Test artifacts
backend/junit.xml
**/junit.xml
**/playwright-report/
**/playwright-results*
**/test-results/
**/.pytest_cache/
**/coverage.xml
**/.coverage

# Scripts temporaires (si vraiment local)
test_protocol.ps1
```

**Note:** `test_protocol.ps1` - à ignorer UNIQUEMENT si vraiment local. Sinon versionner dans `scripts/` ou `tools/`.

---

## PLAN DE COMMITS PAR PR

### PR0 (Optionnelle) – Hygiène

#### **COMMIT 0.1: Configuration Git (line endings + ignore)**

**Type:** `chore`  
**Message:** `chore: Configuration Git (.gitattributes + .gitignore patterns)`

**Fichiers:**
```bash
git add .gitattributes  # Déjà committé
git add .gitignore      # À mettre à jour avec patterns ci-dessus
```

**Build safety:** ✅ Pas de risque (configuration)

**Check:** Aucun test requis

---

### PR1 – BACKEND FONCTIONNEL (Cohérent, Build-Safe)

#### **COMMIT 1.1: Migration transaction_type SAKA + Modèle + Test Intégrité**

**Type:** `feat(backend)`  
**Message:** `feat(backend): Ajout transaction_type à SakaTransaction (migration + modèle + test intégrité)`

**Fichiers:**
```bash
git add backend/core/migrations/0032_add_transaction_type_to_sakatransaction.py
git add backend/core/models/__init__.py  # Modifié (si import SakaTransaction affecté)
git add backend/core/models/saka.py      # Modifié (si champ transaction_type modifié)
git add backend/core/tests/models/test_transaction_type_integrity.py  # Test intégrité
```

**Raison:** Migration doit voyager avec le modèle modifié et un test d'intégrité pour garantir la cohérence.

**Build safety:**
- ✅ Migration dépend de `0031_add_critical_alert_event` (vérifié)
- ✅ Modèle SakaTransaction a déjà `transaction_type` dans le code (lignes 376-381, 401-405)
- ⚠️ **Check requis:** `pytest backend/core/tests/models/test_transaction_type_integrity.py -v`

**Risques:**
- ⚠️ Si `backend/core/models/saka.py` n'est PAS modifié, vérifier que le modèle correspond à la migration
- ⚠️ Test doit passer avant commit

---

#### **COMMIT 1.2: Chat Moderation API + Wiring + Tests**

**Type:** `feat(backend)`  
**Message:** `feat(backend): API chat moderation (viewset + wiring + permissions + tests)`

**Fichiers:**
```bash
git add backend/core/api/chat_moderation.py              # Nouveau fichier API
git add backend/core/models/chat_moderation.py           # Modèle (si nouveau)
git add backend/core/api/__init__.py                     # Modifié (import ChatMessageReportViewSet - ligne 12)
git add backend/core/urls.py                             # Modifié (import ligne 15 + routing)
git add backend/core/permissions.py                      # Modifié (si permissions chat ajoutées)
git add backend/core/tests/websocket/                    # Tests websocket/modération (si pertinents)
```

**Raison:** Nouvelle API doit inclure son wiring complet (urls, __init__, permissions) + tests dans le même commit.

**Build safety:**
- ✅ Wiring déjà présent dans `urls.py` (ligne 15: `ChatMessageReportViewSet`)
- ✅ Wiring déjà présent dans `api/__init__.py` (ligne 12)
- ⚠️ **Check requis:** Vérifier que `urls.py` a bien le routing pour `ChatMessageReportViewSet`
- ⚠️ **Check requis:** `pytest backend/core/tests/websocket/ -v` (si tests websocket/modération existent)

**Risques:**
- ⚠️ Si `permissions.py` n'est pas modifié, vérifier que les permissions par défaut suffisent
- ⚠️ Si wiring incomplet, le commit casse le build

---

#### **COMMIT 1.3: Institutional Exports API + Wiring + Tests**

**Type:** `feat(backend)`  
**Message:** `feat(backend): API exports institutionnels (ONU/Fondations + wiring + tests)`

**Fichiers:**
```bash
git add backend/core/api/institutional_exports.py        # Nouveau fichier API
git add backend/core/urls.py                             # Modifié (import ligne 58 + routing lignes 195-196)
git add backend/core/api/__tests__/test_compliance_views.py  # Tests compliance (si exports testés ici)
git add backend/core/tests/api/test_institutional_exports.py # Tests exports dédiés
```

**Raison:** Nouvelle API doit inclure son wiring (urls) + tests dans le même commit.

**Build safety:**
- ✅ Wiring déjà présent dans `urls.py` (ligne 58: imports, lignes 195-196: routing)
- ⚠️ **Check requis:** `pytest backend/core/tests/api/test_institutional_exports.py -v`

**Risques:**
- ⚠️ Si `api/__init__.py` doit exporter les fonctions mais n'est pas modifié, vérifier que l'import direct suffit

---

#### **COMMIT 1.4: Finance HelloAsso + Stripe Utils + Views + Settings + Tests**

**Type:** `feat(finance)`  
**Message:** `feat(finance): Clients HelloAsso/Stripe + views + settings + tests`

**Fichiers:**
```bash
git add backend/finance/helloasso_client.py
git add backend/finance/ledger_services/helloasso_ledger.py
git add backend/finance/stripe_utils.py
git add backend/finance/views.py                         # Modifié (+293 lignes - wiring existant)
git add backend/config/settings.py                       # Modifié (si config HelloAsso/Stripe)
git add backend/finance/tests/test_contract_webhooks_stripe.py
git add backend/finance/tests/test_helloasso_contract.py
git add backend/finance/tests/test_payments_kyc.py
git add backend/finance/tests/test_payments_saka_segregation.py
git add backend/finance/tests/test_payments_security.py
git add backend/finance/tests/test_stripe_segregation.py  # Modifié
```

**Raison:** Nouveaux services financiers + views + settings + tests dans un commit cohérent.

**Build safety:**
- ⚠️ **Check requis:** Vérifier que `views.py` utilise bien `helloasso_client.py` et `stripe_utils.py`
- ⚠️ **Check requis:** `pytest backend/finance/tests/ -v` (tous les tests finance)
- ⚠️ **Check requis:** Vérifier que `settings.py` a les clés API nécessaires (exemples ou documentation)

**Risques:**
- ⚠️ Si settings incomplet, le code peut crasher au runtime (mais tests doivent échouer)

---

#### **COMMIT 1.5: Modifications API/Models/Services existants (refactor/improvements)**

**Type:** `refactor(backend)` ou `fix(backend)` selon diffs  
**Message:** `refactor(backend): Améliorations API, permissions, sécurité et serializers`

**Fichiers:**
```bash
git add backend/core/api/__init__.py                     # Modifié (si autres imports)
git add backend/core/api/compliance_views.py             # Modifié
git add backend/core/api/content_views.py                # Modifié
git add backend/core/api/polls.py                        # Modifié
git add backend/core/models/__init__.py                  # Modifié (si autres imports)
git add backend/core/permissions.py                      # Modifié
git add backend/core/security/sanitization.py            # Modifié
git add backend/core/serializers/content.py              # Modifié
git add backend/core/urls.py                             # Modifié (si autres changements)
```

**⚠️ AVANT COMMIT:** Examiner les diffs pour déterminer si `refactor`, `fix`, ou `feat`:
```bash
git diff backend/core/api/compliance_views.py
git diff backend/core/security/sanitization.py
git diff backend/core/permissions.py
```

**Build safety:**
- ⚠️ **Check requis:** `pytest backend/core/tests/api/ -v` (tests API)
- ⚠️ **Check requis:** `pytest backend/core/tests/cms/ -v` (tests CMS)

**Risques:**
- ⚠️ Changements dans `permissions.py` peuvent affecter les tests de permissions
- ⚠️ Changements dans `sanitization.py` peuvent affecter les tests XSS

---

#### **COMMIT 1.6: Tests CMS Contract (nouveaux)**

**Type:** `test(backend)`  
**Message:** `test(backend): Tests contract CMS (CRUD, workflow, pagination, export)`

**Fichiers:**
```bash
git add backend/core/tests/api/test_contract_cms.py
git add backend/core/tests/api/test_contract_cms_actions.py
git add backend/core/tests/api/test_contract_cms_export.py
git add backend/core/tests/api/test_contract_cms_pagination.py
git add backend/core/tests/api/test_contract_cms_workflow.py
```

**Raison:** Tests arrivent après le code (commits 1.4-1.5 ont le code CMS).

**Build safety:**
- ✅ Tests nouveaux, ne cassent pas le build existant
- ⚠️ **Check requis:** `pytest backend/core/tests/api/test_contract_cms*.py -v`

---

#### **COMMIT 1.7: Tests Contract Health + Projects + SAKA**

**Type:** `test(backend)`  
**Message:** `test(backend): Tests contract health, projects et SAKA`

**Fichiers:**
```bash
git add backend/core/tests/api/test_contract_health.py
git add backend/core/tests/api/test_contract_projects.py
git add backend/core/tests/api/test_contract_saka.py
```

**Build safety:**
- ✅ Tests nouveaux
- ⚠️ **Check requis:** `pytest backend/core/tests/api/test_contract_health.py backend/core/tests/api/test_contract_projects.py backend/core/tests/api/test_contract_saka.py -v`

---

#### **COMMIT 1.8: Tests Critical Metrics**

**Type:** `test(backend)`  
**Message:** `test(backend): Tests critical alert metrics`

**Fichiers:**
```bash
git add backend/core/tests/api/test_critical_alert_metrics.py
```

**Build safety:**
- ✅ Test nouveau
- ⚠️ **Check requis:** `pytest backend/core/tests/api/test_critical_alert_metrics.py -v`

---

#### **COMMIT 1.9: Tests CMS Content (CRUD, i18n, sécurité, versioning, XSS)**

**Type:** `test(backend)`  
**Message:** `test(backend): Tests CMS content (CRUD, i18n, sécurité, versioning, XSS)`

**Fichiers:**
```bash
git add backend/core/tests/cms/test_content_crud.py
git add backend/core/tests/cms/test_content_i18n.py
git add backend/core/tests/cms/test_content_security_external.py
git add backend/core/tests/cms/test_content_versioning.py
git add backend/core/tests/cms/test_content_xss.py
git add backend/core/tests/cms/test_xss_sanitization.py
```

**Build safety:**
- ✅ Tests nouveaux
- ⚠️ **Check requis:** `pytest backend/core/tests/cms/ -v`

---

#### **COMMIT 1.10: Tests Transaction Type + WebSocket + Governance**

**Type:** `test(backend)`  
**Message:** `test(backend): Tests transaction type integrity, WebSocket et gouvernance`

**Fichiers:**
```bash
git add backend/core/tests/models/test_transaction_type_integrity.py  # Déjà dans commit 1.1 si présent
git add backend/core/tests/websocket/                                 # Déjà dans commit 1.2 si pertinent
git add backend/tests/compliance/governance/test_constitution_documents.py
```

**Note:** `test_transaction_type_integrity.py` devrait être dans le commit 1.1, mais si oublié, le mettre ici.

**Build safety:**
- ✅ Tests nouveaux
- ⚠️ **Check requis:** `pytest backend/core/tests/models/test_transaction_type_integrity.py backend/tests/compliance/governance/test_constitution_documents.py -v`

---

#### **COMMIT 1.11: Modifications tests existants**

**Type:** `test(backend)`  
**Message:** `test(backend): Améliorations tests existants (compliance, permissions, settings)`

**Fichiers:**
```bash
git add backend/core/api/__tests__/test_compliance_badge.py      # Modifié
git add backend/core/api/__tests__/test_compliance_views.py      # Modifié
git add backend/core/tests/api/test_polls_permissions.py         # Modifié
git add backend/core/tests/api/test_projects_permissions.py      # Modifié
git add backend/core/tests/cms/test_content_permissions.py       # Modifié
git add backend/tests/compliance/test_settings_failfast.py       # Modifié
```

**Build safety:**
- ⚠️ **Check requis:** `pytest backend/core/api/__tests__/ backend/core/tests/api/test_polls_permissions.py backend/core/tests/api/test_projects_permissions.py backend/core/tests/cms/test_content_permissions.py backend/tests/compliance/test_settings_failfast.py -v`

---

#### **COMMIT 1.12: Requirements + Pytest Config**

**Type:** `chore(backend)`  
**Message:** `chore(backend): Mise à jour requirements.txt et pytest.ini`

**Fichiers:**
```bash
git add backend/requirements.txt    # Modifié
git add backend/pytest.ini          # Modifié
```

**Raison:** Dépendances et config doivent être cohérentes avec le code committé.

**Build safety:**
- ⚠️ **Check requis:** `pip install -r backend/requirements.txt` (vérifier que ça installe)
- ⚠️ **Check requis:** `pytest backend/ --collect-only` (vérifier config pytest)

---

### PR2 – CI/WORKFLOWS + SCRIPTS + DOCS

#### **COMMIT 2.1: CI Workflows - Monthly Audit + Critical Tests**

**Type:** `ci`  
**Message:** `ci: Ajout workflows monthly auto-audit et verify critical tests`

**Fichiers:**
```bash
git add .github/workflows/monthly-auto-audit.yml
git add .github/workflows/verify-critical-tests.yml
```

**Raison:** Workflows CI après que la base de tests passe (PR1 validée).

**Build safety:**
- ✅ Workflows nouveaux, ne cassent pas le build immédiatement
- ⚠️ **Check requis:** Vérifier que les workflows ne référencent pas des fichiers/tests qui n'existent pas encore

---

#### **COMMIT 2.2: Modifications CI Workflows existants**

**Type:** `ci`  
**Message:** `ci: Améliorations workflows audit-global, ci et e2e-fullstack`

**Fichiers:**
```bash
git add .github/workflows/audit-global.yml    # Modifié
git add .github/workflows/ci.yml              # Modifié
git add .github/workflows/e2e-fullstack.yml   # Modifié
```

**⚠️ AVANT COMMIT:** Examiner les diffs:
```bash
git diff .github/workflows/audit-global.yml
git diff .github/workflows/ci.yml
git diff .github/workflows/e2e-fullstack.yml
```

**Build safety:**
- ⚠️ **Check requis:** Vérifier que les workflows modifiés ne cassent pas le CI existant

---

#### **COMMIT 2.3: Scripts utilitaires**

**Type:** `chore(scripts)`  
**Message:** `chore(scripts): Scripts audit mensuel, webhooks et vérification marqueurs`

**Fichiers:**
```bash
git add scripts/audit_content.py                    # Modifié
git add scripts/generate_monthly_audit_report.py
git add scripts/simulate_webhook_helloasso.py
git add scripts/simulate_webhook_stripe.py
git add scripts/verify_critical_markers.py
git add scripts/__tests__/
```

**Build safety:**
- ✅ Scripts utilitaires, ne cassent pas le build backend/frontend

---

#### **COMMIT 2.4: Documentation - Chat + CMS + Compliance + Finance**

**Type:** `docs`  
**Message:** `docs: Documentation chat, CMS, exports institutionnels et finance`

**Fichiers:**
```bash
git add docs/chat/
git add docs/cms/
git add docs/compliance/EXPORTS_INSTITUTIONNELS.md
git add docs/finance/
```

**Build safety:**
- ✅ Documentation, aucun risque build

---

#### **COMMIT 2.5: Documentation - Observability + Security + Reports**

**Type:** `docs`  
**Message:** `docs: Documentation observability, security alerting et rapports`

**Fichiers:**
```bash
git add docs/observability/CRITICAL_ALERT_METRICS.md
git add docs/security/ALERTING_SLACK.md
git add docs/reports/AUDIT_GLOBAL_CHANGEMENTS_EGOEJO.md
git add docs/reports/MONTHLY_AUTO_AUDIT.md
git add docs/reports/GIT_SYNC_REPORT.md
git add docs/reports/PLAN_COMMIT_PUSH.md
```

**Build safety:**
- ✅ Documentation, aucun risque build

---

#### **COMMIT 2.6: Documentation - Testing + Manuel Officiel + Modifications**

**Type:** `docs`  
**Message:** `docs: Documentation testing, manuel officiel et mises à jour`

**Fichiers:**
```bash
git add docs/testing/
git add docs/MANUEL_OFFICIEL_EGOEJO.md
git add docs/governance/REQUIRED_CHECKS.md              # Modifié
git add docs/institutionnel/NOTE_CONCEPTUELLE_FONDATIONS.md  # Modifié
git add docs/institutionnel/NOTE_CONCEPTUELLE_ONU.md    # Modifié
git add docs/security/ALERTING_EMAIL.md                 # Modifié
```

**Build safety:**
- ✅ Documentation, aucun risque build

---

### PR3 – SUBMODULE FRONTEND

#### **COMMIT 3.1: Mise à jour submodule frontend**

**Type:** `chore(frontend)`  
**Message:** `chore(frontend): Mise à jour submodule frontend (fix/hash-navigation-scroll)`

**⚠️ PROCÉDURE STRICTE:**

1. **Dans le submodule frontend:**
   ```bash
   cd frontend
   git status -sb  # Vérifier branche et modifications
   git add .
   git commit -m "fix(frontend): Fix hash navigation scroll"
   git push origin fix/hash-navigation-scroll  # PUSH OBLIGATOIRE AVANT SUITE
   ```

2. **Créer PR dans le repo submodule:**
   - `fix/hash-navigation-scroll` → `main` (du submodule)
   - Attendre merge de la PR (ou au minimum validation code review)

3. **Dans le repo principal:**
   ```bash
   cd ..  # Retour au repo principal
   git add frontend  # Mettre à jour le pointeur du submodule
   git commit -m "chore(frontend): Mise à jour submodule frontend (fix hash navigation scroll)"
   ```

**⚠️ RÈGLE ABSOLUE:** Ne jamais pointer vers un commit du submodule qui n'est pas pushé sur le remote.

**Build safety:**
- ✅ Submodule indépendant, ne casse pas le build backend
- ⚠️ **Check requis:** Vérifier que le commit référencé existe sur `origin/fix/hash-navigation-scroll`

---

## RÉSUMÉ DES 3 PR

### PR0 (Optionnelle): Hygiène
- **Commits:** 1 (gitignore)
- **Risque:** Aucun
- **Action:** Optionnelle, peut être mergée immédiatement

### PR1: Backend Fonctionnel
- **Commits:** 12 (migrations+modèles+tests, APIs+wiring, finance, tests)
- **Risque:** Élevé si migrations/APIs mal câblées
- **Action:** Requiert validation tests complets avant merge

### PR2: CI/Scripts/Docs
- **Commits:** 6 (workflows, scripts, documentation)
- **Risque:** Faible (sauf si workflows cassent le CI)
- **Action:** Peut être mergée après PR1

### PR3: Submodule Frontend
- **Commits:** 1 (update submodule pointer)
- **Risque:** Faible si procédure respectée
- **Action:** Après PR merge dans le repo submodule

---

## CHECKLIST BUILD SAFETY PAR COMMIT

| Commit | Fichiers | Build Safety Check | Risque |
|--------|----------|-------------------|--------|
| 0.1 | .gitignore | Aucun | ✅ Aucun |
| 1.1 | Migration + Modèle + Test | `pytest backend/core/tests/models/test_transaction_type_integrity.py` | ⚠️ Moyen |
| 1.2 | Chat API + Wiring + Tests | `pytest backend/core/tests/websocket/` + vérifier urls.py | ⚠️ Élevé |
| 1.3 | Institutional Exports + Wiring + Tests | `pytest backend/core/tests/api/test_institutional_exports.py` | ⚠️ Moyen |
| 1.4 | Finance HelloAsso/Stripe + Views + Tests | `pytest backend/finance/tests/` + vérifier settings.py | ⚠️ Élevé |
| 1.5 | Refactor API/Models/Services | `pytest backend/core/tests/api/ backend/core/tests/cms/` | ⚠️ Élevé |
| 1.6-1.11 | Tests (nouveaux/modifiés) | `pytest <fichiers tests>` | ✅ Faible |
| 1.12 | Requirements + Pytest | `pip install -r requirements.txt` + `pytest --collect-only` | ⚠️ Moyen |
| 2.1-2.2 | CI Workflows | Vérifier syntaxe YAML + références fichiers | ⚠️ Moyen |
| 2.3-2.6 | Scripts + Docs | Aucun (pas de code backend/frontend) | ✅ Aucun |
| 3.1 | Submodule Frontend | Vérifier commit référencé existe sur remote | ⚠️ Faible |

---

## COMMANDES GIT EXACTES (RÉSUMÉ)

### Phase 1: PR0 (Optionnelle)
```bash
# Mise à jour .gitignore
# Éditer .gitignore (ajouter patterns section 2)
git add .gitignore
git commit -m "chore: Mise à jour .gitignore (patterns artefacts tests)"
git push origin main
```

### Phase 2: PR1 (Backend)
```bash
# Créer branche feature
git checkout -b feat/backend-transaction-type-migration-chat-finance

# Commits 1.1 à 1.12 (voir détail ci-dessus)
# ... (exécuter dans l'ordre avec checks build safety)

# Push
git push origin feat/backend-transaction-type-migration-chat-finance

# Créer PR sur GitHub
```

### Phase 3: PR2 (CI/Docs)
```bash
# Créer branche feature
git checkout -b feat/ci-workflows-scripts-docs

# Commits 2.1 à 2.6 (voir détail ci-dessus)

# Push
git push origin feat/ci-workflows-scripts-docs

# Créer PR sur GitHub
```

### Phase 4: PR3 (Frontend)
```bash
# Dans submodule (voir procédure section 3.1)
# Puis dans repo principal:
git add frontend
git commit -m "chore(frontend): Mise à jour submodule frontend"
git push origin main  # ou branche feature selon workflow
```

---

**Plan validé:** ✅  
**Build-safe:** ✅ (avec checks requis respectés)  
**Prêt pour exécution:** Après validation des checks build safety


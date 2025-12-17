# 📊 Audit Complet des Tests Backend - EGOEJO

**Date** : 2025-12-16  
**Objectif** : Cartographier la couverture de tests et proposer un plan structuré

---

## 📈 État Actuel des Tests

### Statistiques Globales

- **Total tests collectés** : 41 tests (pytest)
- **Fichiers de tests** : 11 fichiers
- **Couverture estimée** : ~17-29% (selon les modules)

### Fichiers de Tests Existants

1. **`core/tests.py`** (27 tests)
   - `IntentTestCase` : Intentions (création, admin, export, suppression)
   - `ProjetCagnotteTestCase` : Projets et Cagnottes (création basique)
   - `ProjectImpact4PTestCase` : Scores 4P (création, service, API)
   - `MessagingVoteTestCase` : Chat et votes (création thread, messages)
   - `GlobalAssetsTestCase` : Endpoint global-assets

2. **`core/tests_saka.py`** (27 tests)
   - `SakaWalletTestCase` : Création automatique des wallets
   - `SakaHarvestTestCase` : Récolte SAKA (content_read, vote, etc.)
   - `SakaSpendTestCase` : Dépense SAKA (vote, boost)
   - `SakaVoteQuadraticTestCase` : Vote quadratique avec SAKA
   - `SakaProjectBoostTestCase` : Boost de projets avec SAKA
   - `SakaGlobalAssetsTestCase` : Intégration SAKA dans global-assets
   - `SakaRaceConditionTestCase` : Conditions de course
   - `SakaConcurrencyTestCase` : Concurrence (TransactionTestCase)
   - `SakaCycleTestCase` : Cycles SAKA et stats

3. **`core/tests_auth.py`** (15 tests)
   - `AuthTestCase` : Login, register, refresh token, current user
   - Couverture : succès, erreurs, validation, rotation tokens

4. **`core/tests_saka_public.py`** (5 tests)
   - `SakaPublicEndpointsTestCase` : Endpoints publics SAKA (cycles, silo)
   - Authentification requise, structure des réponses

5. **`core/tests_saka_celery.py`** (4 tests)
   - `SakaCompostCeleryTestCase` : Tâche Celery de compostage SAKA
   - Mode eager, respect des règles, association aux cycles

6. **`core/tests_saka_celery_redistribution.py`** (3 tests)
   - `SakaSiloRedistributionCeleryTestCase` : Tâche Celery de redistribution
   - Wallets éligibles, désactivation, silo vide

7. **`core/tests_saka_redistribution.py`** (9 tests)
   - `SakaRedistributionTestCase` : Redistribution du Silo SAKA
   - Atomicité, balances négatives, API admin

8. **`core/tests_communities.py`** (8 tests)
   - `CommunityTestCase` : Modèle Community et API
   - Création, slug auto, association projets, API list/detail

9. **`core/tests_content.py`** (13 tests) ⭐ NOUVEAU
   - `EducationalContentTestCase` : Endpoints Content
   - Liste, détail, création, publication, mark-consumed (SAKA)

10. **`core/tests_engagement.py`** (8 tests) ⭐ NOUVEAU
    - `EngagementTestCase` : Endpoints Engagement
    - Liste, création, filtrage par help_request

11. **`finance/tests_finance.py`** (10 tests)
    - `EscrowContractTestCase` : Création escrow via pledge_funds
    - `EscrowReleaseTestCase` : Libération escrow (commission, fees)
    - `EscrowRefundTestCase` : Remboursement escrow
    - `EscrowMultipleTestCase` : Multiples escrows sur un projet

12. **`finance/tests.py`** (3 tests)
    - `UserWalletTestCase` : Création automatique, balance
    - `WalletTransactionTestCase` : Transactions, idempotency
    - `EscrowContractTestCase` : Statut par défaut
    - `WalletPocketTestCase` : Pockets, allocation, validation

13. **`investment/tests.py`** : Vide (pas de tests)

---

## ✅ Domaines Métier Testés

### Bien Couverts

1. **SAKA Protocol** ✅
   - Récolte, dépense, vote quadratique, boost projets
   - Cycles, compostage, redistribution, Silo commun
   - Concurrence et conditions de course
   - Tâches Celery (compost, redistribution)
   - Endpoints publics (cycles, silo)

2. **Authentification** ✅
   - Login, register, refresh token, rotation
   - Validation, erreurs, current user

3. **Finance/Escrow** ✅
   - Création escrow, libération, remboursement
   - Commission, fees, idempotency
   - Multiples escrows

4. **Intent** ✅
   - Création, admin, export, suppression
   - Honeypot anti-spam, filtres

5. **4P (Performance Partagée)** ✅
   - Création, service update_project_4p
   - API exposure, structure stable

6. **Communities** ✅
   - Modèle, API list/detail, association projets

7. **Content** ✅ (nouveau)
   - Liste, détail, création, publication, mark-consumed

8. **Engagement** ✅ (nouveau)
   - Liste, création, filtrage

### Partiellement Couverts

1. **Projets** ⚠️
   - Tests basiques (création projet, cagnotte)
   - **Manque** : API endpoints (list, detail, update, delete, boost, search)
   - **Manque** : Permissions, validation

2. **Chat** ⚠️
   - Tests basiques (création thread, messages)
   - **Manque** : ViewSet complet, permissions, WebSocket
   - **Manque** : Concierge support

3. **Polls/Votes** ⚠️
   - Tests basiques (vote avec SAKA)
   - **Manque** : API endpoints complets, différents types de votes
   - **Manque** : Permissions, résultats

### Non Testés (Critiques)

1. **Health/Readiness/Liveness Checks** ❌
   - `HealthCheckView`, `ReadinessCheckView`, `LivenessCheckView`
   - Endpoints critiques pour Kubernetes/monitoring

2. **Monitoring** ❌
   - `MetricsView`, `AlertsView`, `MetricsStatsView`, `AlertsListView`
   - Endpoints admin pour métriques et alertes

3. **Security Views** ❌
   - `SecurityAuditView`, `SecurityMetricsView`
   - Endpoints admin pour audit de sécurité

4. **GDPR/RGPD** ❌
   - `DataExportView`, `DataDeleteView`
   - Droits utilisateurs (portabilité, suppression)

5. **Help Requests** ❌
   - `HelpRequestViewSet` : Liste, création, mark-as-project
   - Filtres (status, mine)

6. **Chat Support (Concierge)** ❌
   - `ConciergeThreadView`, `ConciergeEligibilityView`, `SupportContactView`
   - Éligibilité, création thread, contact support

7. **Search** ❌
   - `ProjetSearchView` : Recherche textuelle
   - `SemanticSearchView`, `SemanticSuggestionsView` : Recherche sémantique

8. **Mycelium (3D)** ❌
   - `MyceliumDataView`, `MyceliumReduceView`
   - Visualisation 3D, réduction de données

9. **Config** ❌
   - `FeaturesConfigView` : Feature flags

10. **Impact Dashboard** ❌
    - `ImpactDashboardView` : Dashboard utilisateur

11. **Moderation** ❌
    - `ModerationReportViewSet` : Signalements

12. **Audit Logs** ❌
    - `AuditLogViewSet` : Logs d'audit

13. **Fundraising** ❌
    - `CagnotteListCreate` : API cagnottes
    - `contribute` : Endpoint désactivé mais présent

14. **Investment (V2.0)** ❌
    - `ShareholderRegisterViewSet` : Dormant mais présent
    - Tests vides

15. **Tâches Celery** ⚠️
    - SAKA compost ✅, SAKA redistribution ✅
    - **Manque** : Audio generation, embeddings, security scans, mycelium
    - **Manque** : Tâches générales (impact dashboard, etc.)

16. **Channels/WebSocket** ❌
    - Pas de tests pour les consumers WebSocket
    - Chat en temps réel, notifications

17. **Rate Limiting** ❌
    - Pas de tests pour le throttling DRF
    - Protection contre les abus

18. **Permissions Avancées** ❌
    - `IsFounderOrReadOnly`, `IsInvestmentFeatureEnabled`
    - Groupes, permissions custom

---

## 📋 Plan de Tests Structuré par Priorité

### 🔴 P0 - Critique (Sécurité & Stabilité)

#### 1. `core/tests_health.py` - Health Checks
**Objectif** : Vérifier que les endpoints de monitoring fonctionnent

**Scénarios** :
- `test_health_check_healthy` : DB et cache OK → 200, status="healthy"
- `test_health_check_database_error` : DB inaccessible → 503, status="unhealthy"
- `test_health_check_cache_error` : Cache inaccessible → 503, status="degraded"
- `test_readiness_check_ready` : DB accessible → 200, status="ready"
- `test_readiness_check_not_ready` : DB inaccessible → 503
- `test_liveness_check` : Toujours 200, status="alive"

**Impact** : Kubernetes, monitoring, alertes

---

#### 2. `core/tests_security_views.py` - Security Audit
**Objectif** : Vérifier les endpoints d'audit de sécurité (admin)

**Scénarios** :
- `test_security_audit_admin_only` : Non-admin → 403
- `test_security_audit_weak_passwords` : Détecte mots de passe faibles
- `test_security_audit_inactive_users` : Liste utilisateurs inactifs >90j
- `test_security_metrics_admin_only` : Non-admin → 403
- `test_security_metrics_structure` : Structure de réponse correcte

**Impact** : Sécurité, conformité, audit

---

#### 3. `core/tests_gdpr.py` - GDPR/RGPD
**Objectif** : Vérifier les droits utilisateurs (portabilité, suppression)

**Scénarios** :
- `test_data_export_authenticated` : Export JSON complet des données utilisateur
- `test_data_export_unauthenticated` : 401 Unauthorized
- `test_data_export_includes_intents` : Intentions incluses dans l'export
- `test_data_delete_authenticated` : Suppression complète des données
- `test_data_delete_unauthenticated` : 401 Unauthorized
- `test_data_delete_cascade` : Vérifier suppression en cascade (intents, etc.)

**Impact** : Conformité RGPD, droits utilisateurs

---

#### 4. `core/tests_projects_api.py` - API Projets (Complet)
**Objectif** : Tester tous les endpoints projets (list, detail, update, delete, boost, search)

**Scénarios** :
- `test_list_projects_public` : GET /api/projets/ → 200, liste
- `test_list_projects_filtered` : Filtres (categorie, status, etc.)
- `test_create_project_authenticated` : POST /api/projets/ → 201
- `test_create_project_unauthenticated` : POST → 401 ou 403
- `test_retrieve_project_detail` : GET /api/projets/{id}/ → 200
- `test_update_project_owner` : PUT/PATCH par le créateur → 200
- `test_update_project_not_owner` : PUT/PATCH par autre → 403
- `test_delete_project_owner` : DELETE par le créateur → 204
- `test_delete_project_not_owner` : DELETE par autre → 403
- `test_boost_project_with_saka` : POST /api/projets/{id}/boost/ avec SAKA
- `test_boost_project_insufficient_saka` : Solde insuffisant → 400
- `test_search_projects` : GET /api/projets/search/?q=... → résultats

**Impact** : Fonctionnalité core, permissions, SAKA

---

#### 5. `core/tests_polls_api.py` - API Polls/Votes (Complet)
**Objectif** : Tester tous les endpoints de votes (list, detail, vote, résultats)

**Scénarios** :
- `test_list_polls_public` : GET /api/polls/ → 200
- `test_retrieve_poll_detail` : GET /api/polls/{id}/ → 200
- `test_vote_binary` : Vote binaire (oui/non)
- `test_vote_quadratic_with_saka` : Vote quadratique avec SAKA
- `test_vote_quadratic_insufficient_saka` : Solde insuffisant → 400
- `test_vote_majority` : Vote majoritaire
- `test_vote_unauthenticated` : 401 Unauthorized
- `test_poll_results` : Calcul des résultats (différents types)
- `test_poll_permissions` : Permissions (authentifié, owner, etc.)

**Impact** : Démocratie participative, SAKA

---

### 🟡 P1 - Important (Fonctionnalités Majeures)

#### 6. `core/tests_help_requests.py` - Help Requests API
**Objectif** : Tester les endpoints de demandes d'aide

**Scénarios** :
- `test_list_help_requests_public` : GET /api/help-requests/ → 200
- `test_list_help_requests_filtered_by_status` : ?status=accepted
- `test_list_help_requests_mine` : ?mine=1 (authentifié) → mes demandes
- `test_create_help_request_authenticated` : POST → 201, user attaché
- `test_create_help_request_unauthenticated` : POST → 201, user=null
- `test_mark_as_project` : POST /api/help-requests/{id}/mark-as-project/ → status=accepted

**Impact** : Aide mutuelle, transformation en projets

---

#### 7. `core/tests_chat_support.py` - Concierge Support
**Objectif** : Tester les endpoints de support concierge

**Scénarios** :
- `test_concierge_eligibility_premium` : Utilisateur Premium → eligible=True
- `test_concierge_eligibility_donations` : 500€+ de dons → eligible=True
- `test_concierge_eligibility_investments` : 1000€+ d'investissements → eligible=True
- `test_concierge_eligibility_not_eligible` : Aucune condition → eligible=False, 403
- `test_concierge_thread_get_or_create` : GET /api/support/concierge/ → thread créé/récupéré
- `test_concierge_thread_unauthenticated` : 401 Unauthorized
- `test_support_contact` : POST /api/support/contact/ → message envoyé

**Impact** : Support premium, expérience utilisateur

---

#### 8. `core/tests_monitoring.py` - Monitoring & Analytics
**Objectif** : Tester les endpoints de monitoring (admin)

**Scénarios** :
- `test_metrics_post_public` : POST /api/analytics/metrics/ → métrique enregistrée
- `test_metrics_post_invalid_data` : Données invalides → 400
- `test_alerts_list_admin_only` : GET /api/monitoring/alerts/list/ → admin only
- `test_alerts_create` : Création d'alerte
- `test_metrics_stats_admin_only` : GET /api/monitoring/metrics/stats/ → admin only
- `test_metrics_stats_structure` : Structure de réponse correcte

**Impact** : Observabilité, performance, alertes

---

#### 9. `core/tests_search.py` - Search & Semantic Search
**Objectif** : Tester les endpoints de recherche

**Scénarios** :
- `test_projet_search_textual` : GET /api/projets/search/?q=... → résultats
- `test_projet_search_empty_query` : Query vide → 400 ou tous les projets
- `test_semantic_search` : POST /api/projets/semantic-search/ → recherche par embedding
- `test_semantic_search_no_embedding` : Projet sans embedding → ignoré
- `test_semantic_suggestions` : GET /api/projets/semantic-suggestions/?q=... → suggestions

**Impact** : Découvrabilité, UX

---

#### 10. `core/tests_chat_api.py` - Chat API (Complet)
**Objectif** : Tester tous les endpoints de chat (threads, messages, permissions)

**Scénarios** :
- `test_list_threads_authenticated` : GET /api/chat/threads/ → mes threads
- `test_list_threads_unauthenticated` : 401
- `test_create_thread` : POST /api/chat/threads/ → thread créé
- `test_create_thread_with_project` : Thread lié à un projet
- `test_delete_thread_owner` : DELETE par le créateur → 204
- `test_delete_thread_not_owner` : DELETE par autre → 403
- `test_list_messages` : GET /api/chat/messages/?thread={id} → messages
- `test_create_message` : POST /api/chat/messages/ → message créé
- `test_message_broadcast` : Vérifier broadcast WebSocket (mock)

**Impact** : Communication, collaboration

---

#### 11. `core/tests_mycelium.py` - Mycelium 3D
**Objectif** : Tester les endpoints de visualisation 3D

**Scénarios** :
- `test_mycelium_data_get` : GET /api/mycelium/data/ → données 3D
- `test_mycelium_data_structure` : Structure correcte (nodes, edges)
- `test_mycelium_reduce_post` : POST /api/mycelium/reduce/ → réduction données
- `test_mycelium_reduce_invalid_params` : Paramètres invalides → 400

**Impact** : Visualisation, performance frontend

---

#### 12. `core/tests_config.py` - Feature Flags
**Objectif** : Tester l'endpoint de configuration

**Scénarios** :
- `test_features_config_public` : GET /api/config/features/ → feature flags
- `test_features_config_structure` : Structure correcte (saka_enabled, etc.)
- `test_features_config_dynamic` : Vérifier que les flags reflètent settings

**Impact** : Feature flags, déploiement progressif

---

#### 13. `core/tests_impact_dashboard.py` - Impact Dashboard
**Objectif** : Tester l'endpoint dashboard utilisateur

**Scénarios** :
- `test_impact_dashboard_authenticated` : GET /api/impact/dashboard/ → données utilisateur
- `test_impact_dashboard_unauthenticated` : 401
- `test_impact_dashboard_structure` : Structure correcte (contributions, projets, etc.)
- `test_impact_dashboard_aggregations` : Vérifier agrégations ORM

**Impact** : Gamification, engagement utilisateur

---

#### 14. `core/tests_moderation.py` - Moderation API
**Objectif** : Tester les endpoints de modération

**Scénarios** :
- `test_create_moderation_report` : POST /api/moderation/reports/ → signalement créé
- `test_list_reports_admin_only` : GET /api/moderation/reports/ → admin only
- `test_moderation_report_structure` : Structure correcte

**Impact** : Modération, sécurité communautaire

---

#### 15. `core/tests_audit.py` - Audit Logs
**Objectif** : Tester les endpoints d'audit

**Scénarios** :
- `test_audit_logs_list_admin_only` : GET /api/audit/logs/ → admin only
- `test_audit_logs_filtered` : Filtres (user, action, date)
- `test_audit_logs_structure` : Structure correcte

**Impact** : Traçabilité, conformité

---

#### 16. `core/tests_fundraising_api.py` - Fundraising API
**Objectif** : Tester les endpoints de cagnottes

**Scénarios** :
- `test_list_cagnottes_public` : GET /api/cagnottes/ → 200
- `test_create_cagnotte_authenticated` : POST → 201
- `test_create_cagnotte_unauthenticated` : POST → 401 ou 403
- `test_contribute_endpoint_disabled` : POST /api/cagnottes/{id}/contribute/ → 404 (désactivé)

**Impact** : Financement participatif

---

### 🟢 P2 - Secondaire (Fonctionnalités Futures)

#### 17. `investment/tests_investment_api.py` - Investment API (V2.0)
**Objectif** : Tester les endpoints d'investissement (dormants)

**Scénarios** :
- `test_shareholder_register_feature_disabled` : Feature flag désactivé → 403
- `test_shareholder_register_feature_enabled` : Feature flag activé → tests complets
- `test_shareholder_permissions` : Permissions IsInvestmentFeatureEnabled

**Impact** : V2.0, fonctionnalité future

---

#### 18. `core/tests_celery_tasks.py` - Tâches Celery (Complément)
**Objectif** : Tester les tâches Celery non-SAKA

**Scénarios** :
- `test_generate_audio_content` : Génération audio TTS
- `test_generate_embedding_task` : Génération embedding
- `test_scan_file_antivirus` : Scan antivirus
- `test_validate_file_type` : Validation type MIME
- `test_update_impact_dashboard_metrics` : Mise à jour métriques dashboard

**Impact** : Tâches asynchrones, performance

---

#### 19. `core/tests_channels.py` - WebSocket/Channels
**Objectif** : Tester les consumers WebSocket

**Scénarios** :
- `test_chat_consumer_connect` : Connexion WebSocket chat
- `test_chat_consumer_message` : Réception/envoi messages
- `test_chat_consumer_disconnect` : Déconnexion
- `test_notification_consumer` : Notifications en temps réel

**Impact** : Temps réel, UX

---

#### 20. `core/tests_rate_limiting.py` - Rate Limiting
**Objectif** : Tester le throttling DRF

**Scénarios** :
- `test_rate_limit_exceeded` : Trop de requêtes → 429
- `test_rate_limit_reset` : Reset après période
- `test_rate_limit_by_ip` : Limitation par IP
- `test_rate_limit_by_user` : Limitation par utilisateur

**Impact** : Protection contre abus, sécurité

---

#### 21. `core/tests_permissions.py` - Permissions Avancées
**Objectif** : Tester les permissions custom

**Scénarios** :
- `test_is_founder_or_read_only` : Groupe Founders_V1_Protection
- `test_is_investment_feature_enabled` : Feature flag investment
- `test_permission_combinations` : Combinaisons de permissions

**Impact** : Sécurité, contrôle d'accès

---

## 📊 Résumé par Priorité

### P0 - Critique (5 blocs)
1. Health Checks
2. Security Views
3. GDPR/RGPD
4. Projects API (complet)
5. Polls API (complet)

**Total estimé** : ~50-60 tests

### P1 - Important (11 blocs)
6. Help Requests
7. Chat Support (Concierge)
8. Monitoring
9. Search & Semantic Search
10. Chat API (complet)
11. Mycelium 3D
12. Config (Feature Flags)
13. Impact Dashboard
14. Moderation
15. Audit Logs
16. Fundraising API

**Total estimé** : ~80-100 tests

### P2 - Secondaire (5 blocs)
17. Investment API (V2.0)
18. Celery Tasks (complément)
19. Channels/WebSocket
20. Rate Limiting
21. Permissions Avancées

**Total estimé** : ~40-50 tests

---

## 🎯 Prochaines Étapes Recommandées

1. **Immédiat** : Créer les tests P0 (sécurité, health, GDPR, projets, polls)
2. **Court terme** : Compléter P1 (fonctionnalités majeures)
3. **Moyen terme** : P2 (futures fonctionnalités, optimisations)

**Objectif** : Passer de 41 tests à ~170-210 tests, couverture ~60-70%

---

## 📝 Notes Importantes

- **Respecter la structure existante** : `core/tests_*.py`, `finance/tests_*.py`
- **Utiliser pytest** : Pas Django test runner
- **Isolation** : Chaque test doit être indépendant
- **Pas de modification métier** : Tester uniquement, ne pas refactorer
- **Mock Celery** : Utiliser `CELERY_TASK_ALWAYS_EAGER=True` pour les tests
- **Mock WebSocket** : Utiliser des mocks pour Channels dans les tests unitaires


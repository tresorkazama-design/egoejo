# 🔍 Analyse Architecture Backend Django - EGOEJO

**Date** : 2025-12-16  
**Objectif** : Analyser l'architecture backend telle qu'elle est réellement codée

---

## 📋 Configuration Django (`backend/config/settings.py`)

### Stack Technique

**Version Django** : 5.x (déduit de `requirements.txt` : `Django>=5.0,<6.0`)

**Apps Installées** (`INSTALLED_APPS`) :
```python
INSTALLED_APPS = [
    'channels',                                    # WebSockets
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',                              # DRF
    'corsheaders',                                 # CORS
    'csp',                                         # Content Security Policy
    'drf_spectacular',                             # OpenAPI/Swagger
    'rest_framework_simplejwt.token_blacklist',    # JWT avec blacklist
    'core',                                        # App principale
    'finance',                                     # Système financier
    'investment',                                  # Investissement V2.0 (dormant)
]
```

**Middleware** :
- `CorsMiddleware` : CORS
- `SecurityHeadersMiddleware` : Headers sécurité personnalisés
- `DataProtectionMiddleware` : Protection données sensibles
- `CSPMiddleware` : Content Security Policy
- `WhiteNoiseMiddleware` : Servir fichiers statiques
- Middleware Django standard (sessions, CSRF, auth, messages)

### Base de Données

**Configuration** :
- **Production** : PostgreSQL (via `DATABASE_URL`)
- **Développement** : SQLite (fallback si `DATABASE_URL` absent)
- **Options PostgreSQL** : Connection pooling (keepalives, timeout)

**Extensions PostgreSQL** :
- `pg_trgm` : Recherche full-text floue (migration `0010_enable_pg_trgm.py`)
- `pgvector` : Recherche sémantique (migration `0013_migrate_to_pgvector.py`)

### Cache & Redis

**Configuration Redis** :
- **Channels** : DB 0 (WebSockets)
- **Cache** : DB 1 (TTL 300s, prefix `egoejo`)
- **Celery** : DB 2 (broker + results)

**Fallback** : `LocMemCache` si Redis non disponible

### Channels (WebSockets)

**Backend** : `channels_redis.core.RedisChannelLayer`
**Fallback** : `InMemoryChannelLayer` si Redis absent

### Celery

**Configuration** (`backend/config/celery.py`) :
- **Broker** : Redis DB 2
- **Backend** : Redis DB 2
- **Tâches périodiques** : Compost SAKA (lundi 3h UTC)

**Tâches découvertes** :
- `core/tasks.py` : Tâches principales
- `core/tasks_audio.py` : Génération audio (TTS)
- `core/tasks_embeddings.py` : Génération embeddings
- `core/tasks_mycelium.py` : Réduction Mycelium 3D
- `core/tasks_security.py` : Scan antivirus

### Sécurité

**Headers** :
- `X_FRAME_OPTIONS = 'DENY'`
- `SECURE_CONTENT_TYPE_NOSNIFF = True`
- `SECURE_PROXY_SSL_HEADER` configuré
- `SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'`

**Cookies** :
- `SESSION_COOKIE_HTTPONLY = True`
- `SESSION_COOKIE_SAMESITE = 'Lax'`
- `CSRF_COOKIE_HTTPONLY = True`
- `CSRF_COOKIE_SAMESITE = 'Lax'`
- `SESSION_COOKIE_AGE = 1800` (30 minutes)

**Production** :
- `SECURE_SSL_REDIRECT = True`
- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`
- `SECURE_HSTS_SECONDS = 31536000` (1 an)

**Passwords** :
- `Argon2PasswordHasher` (priorité)
- `PBKDF2PasswordHasher` (fallback)
- Validation : min 10 caractères, pas de mots communs, pas uniquement numériques

### REST Framework

**Authentification** :
- `SessionAuthentication`
- `BasicAuthentication`
- `JWTAuthentication` (SimpleJWT)

**JWT** :
- Access token : 60 minutes (configurable)
- Refresh token : 7 jours (configurable)
- Rotation activée
- Blacklist activée

**Throttling** :
- Anon : 10/minute
- User : 100/minute
- IP : 100/hour (optionnel)

**OpenAPI** : `drf-spectacular` configuré (`/api/schema/`, `/api/docs/`)

### Stockage

**Statique** : WhiteNoise (compression, cache headers)

**Médias** :
- **Production** : S3/R2 (Cloudflare R2 compatible S3)
- **Développement** : FileSystemStorage local
- **Activation** : `USE_S3_STORAGE` (variable d'environnement)

### Feature Flags

**V1.6/V2.0** :
- `ENABLE_INVESTMENT_FEATURES` : Active/désactive investissement V2.0
- `EGOEJO_COMMISSION_RATE` : 5% (configurable)
- `STRIPE_FEE_ESTIMATE` : 3% (configurable)
- `FOUNDER_GROUP_NAME` : `'Founders_V1_Protection'`

**SAKA Protocol** :
- `ENABLE_SAKA` : Activation globale
- `SAKA_VOTE_ENABLED` : Vote quadratique fertilisé
- `SAKA_PROJECT_BOOST_ENABLED` : Sorgho-boosting
- `SAKA_COMPOST_ENABLED` : Compostage & Silo
- `SAKA_COMPOST_INACTIVITY_DAYS` : 90 jours
- `SAKA_COMPOST_RATE` : 10%
- `SAKA_COMPOST_MIN_BALANCE` : 50 SAKA
- `SAKA_COMPOST_MIN_AMOUNT` : 10 SAKA
- `SAKA_VOTE_MAX_MULTIPLIER` : 2.0
- `SAKA_VOTE_SCALE` : 200 SAKA
- `SAKA_VOTE_COST_PER_INTENSITY` : 5 SAKA
- `SAKA_PROJECT_BOOST_COST` : 10 SAKA

---

## 🗄️ Modèles (`backend/core/models/`)

### Domaines Métier Identifiés

#### 1. **Projets** (`projects.py`)

**Modèles** :
- `Projet` : Projets du collectif
  - Champs : `titre`, `description`, `categorie`, `impact_score`, `image`, `embedding`, `coordinates_3d`
  - Financement hybride : `funding_type` (DONATION/EQUITY/HYBRID), `donation_goal`, `investment_goal`, `share_price`, `total_shares`, `valuation_pre_money`
  - SAKA : `saka_score`, `saka_supporters_count`
  - Relations : `ForeignKey` vers User (auteur), `OneToOne` vers `ProjectImpact4P`
  - QuerySet personnalisé : `ProjetQuerySet.search()` (recherche full-text avec pg_trgm)
- `Media` : Médias associés aux projets

**Relations** :
- `Projet` → `Cagnotte` (OneToMany)
- `Projet` → `Poll` (OneToMany)
- `Projet` → `ProjectImpact4P` (OneToOne)
- `Projet` → `SakaProjectSupport` (OneToMany via SAKA)

---

#### 2. **SAKA** (`saka.py`)

**Modèles** :
- `SakaWallet` : Portefeuille SAKA utilisateur
  - Champs : `balance`, `total_harvested`, `total_planted`, `total_composted`, `last_activity_date`
  - Relation : `OneToOne` vers User
- `SakaTransaction` : Historique complet des transactions
  - Champs : `direction` (EARN/SPEND), `amount`, `reason`, `metadata`, `created_at`
  - Relation : `ForeignKey` vers User
- `SakaSilo` : Silo commun (singleton)
  - Champs : `total_balance`, `total_composted`, `total_cycles`, `last_compost_at`
- `SakaCompostLog` : Logs des cycles de compostage
  - Champs : `dry_run`, `started_at`, `finished_at`, `wallets_affected`, `total_composted`, `inactivity_days`, `rate`, `min_balance`, `min_amount`, `source`
  - Relation : `ForeignKey` vers `SakaCycle` (optionnel)
- `SakaProjectSupport` : Support SAKA par projet
  - Champs : `total_saka_spent`, `first_support_at`, `last_support_at`
  - Relations : `ForeignKey` vers User et Projet
- `SakaCycle` : Cycles SAKA (saisons)
  - Champs : `name`, `start_date`, `end_date`, `is_active`
  - Relations : `OneToMany` vers `SakaCompostLog`

**Relations** :
- `SakaWallet` → User (OneToOne)
- `SakaTransaction` → User (ManyToOne)
- `SakaProjectSupport` → User + Projet (ManyToOne)
- `SakaCompostLog` → `SakaCycle` (ManyToOne, optionnel)

---

#### 3. **Sondages** (`polls.py`)

**Modèles** :
- `Poll` : Sondages participatifs
  - Champs : `title`, `question`, `description`, `status` (draft/open/closed), `voting_method` (binary/quadratic/majority), `is_anonymous`, `allow_multiple`, `quorum`, `opens_at`, `closes_at`, `max_points`
  - Relations : `ForeignKey` vers Projet (optionnel), `ForeignKey` vers User (created_by)
  - Méthodes : `get_vote_weight()`, `compute_quadratic_weight()`
- `PollOption` : Options de vote
  - Champs : `label`, `position`
  - Relation : `ForeignKey` vers Poll
- `PollBallot` : Votes individuels
  - Champs : `voter_hash`, `points`, `weight`, `saka_spent`, `metadata`
  - Relations : `ForeignKey` vers Poll et PollOption

**Relations** :
- `Poll` → `PollOption` (OneToMany)
- `Poll` → `PollBallot` (OneToMany)
- `Poll` → Projet (ManyToOne, optionnel)

---

#### 4. **Financement** (`fundraising.py`)

**Modèles** :
- `Cagnotte` : Cagnottes de financement
  - Champs : `titre`, `description`, `montant_cible`, `montant_collecte`
  - Relation : `ForeignKey` vers Projet (optionnel)
- `Contribution` : Contributions aux cagnottes
  - Champs : `montant`
  - Relations : `ForeignKey` vers Cagnotte et User

**Relations** :
- `Cagnotte` → Projet (ManyToOne, optionnel)
- `Contribution` → Cagnotte (ManyToOne)
- `Contribution` → User (ManyToOne)

---

#### 5. **Impact** (`impact.py`)

**Modèles** :
- `ImpactDashboard` : Tableau de bord d'impact utilisateur
  - Champs : `total_contributions`, `projects_supported`, `cagnottes_contributed`, `intentions_submitted`, `last_updated`
  - Relation : `OneToOne` vers User
  - Méthode : `update_metrics()`
- `ProjectImpact4P` : Scores 4P par projet
  - Champs : `financial_score`, `saka_score`, `social_score`, `purpose_score`, `updated_at`
  - Relation : `OneToOne` vers Projet

**Relations** :
- `ImpactDashboard` → User (OneToOne)
- `ProjectImpact4P` → Projet (OneToOne)

---

#### 6. **Intentions** (`intents.py`)

**Modèles** :
- `Intent` : Intentions de rejoindre le collectif
  - Champs : `nom`, `email`, `profil`, `message`, `ip`, `user_agent`, `document_url`, `created_at`
  - Pas de relation directe vers User (email uniquement)

---

#### 7. **Chat** (`chat.py`)

**Modèles** :
- `ChatThread` : Threads de discussion
  - Champs : `title`, `thread_type`, `created_at`
  - Relations : `ForeignKey` vers User (created_by)
- `ChatMembership` : Membres des threads
  - Relations : `ForeignKey` vers ChatThread et User
- `ChatMessage` : Messages
  - Champs : `content`, `created_at`
  - Relations : `ForeignKey` vers ChatThread et User (sender)

**Relations** :
- `ChatThread` → User (ManyToOne, created_by)
- `ChatMembership` → ChatThread + User (ManyToMany via table)
- `ChatMessage` → ChatThread + User (ManyToOne)

---

#### 8. **Contenus Éducatifs** (`content.py`)

**Modèles** :
- `EducationalContent` : Contenus éducatifs
  - Champs : `title`, `content`, `category`, `tags`, `embedding`, `audio_file`, `audio_source_hash`
  - Relations : `ForeignKey` vers User (author)
- `ContentLike` : Likes sur contenus
  - Relations : `ForeignKey` vers EducationalContent et User
- `ContentComment` : Commentaires sur contenus
  - Champs : `content`, `created_at`
  - Relations : `ForeignKey` vers EducationalContent et User (author)

---

#### 9. **Autres Domaines**

- **Accounts** (`accounts.py`) : `Profile` (profil utilisateur)
- **Moderation** (`moderation.py`) : `ModerationReport` (signalements)
- **Audit** (`audit.py`) : `AuditLog` (logs d'audit)
- **Monitoring** (`monitoring.py`) : `PerformanceMetric`, `MonitoringAlert`
- **Engagement** (`engagement.py`) : `Engagement`
- **Help** (`help.py`) : `HelpRequest`

---

## 🔌 API Endpoints (`backend/core/api/`)

### Fichiers API Identifiés (25 fichiers)

#### 1. **Projets** (`projects.py`)

**Endpoints** :
- `GET/POST /api/projets/` : `ProjetListCreate` (ViewSet)
  - GET : Liste des projets (cache 5 min, tri par `saka_score` si SAKA activé)
  - POST : Créer un projet (scan antivirus + embedding en arrière-plan)
- `GET/PUT/PATCH/DELETE /api/projets/<id>/` : `ProjetRetrieveUpdateDestroy` (ViewSet)
- `POST /api/projets/<id>/boost/` : `boost_project()` (fonction)
  - Sorgho-boosting SAKA
  - Transaction atomique avec `select_for_update()`
  - Vérifie `ENABLE_SAKA` et `SAKA_PROJECT_BOOST_ENABLED`
  - Met à jour `ProjectImpact4P` après boost

**Logique métier** :
- **Dans la vue** : Validation HTTP, vérification feature flags, transaction atomique
- **Services appelés** : `spend_saka()`, `update_project_4p()`

---

#### 2. **SAKA** (`saka_views.py`)

**Endpoints** :
- `GET /api/saka/silo/` : `saka_silo_view()` - État du Silo Commun
- `GET /api/saka/compost-preview/` : `saka_compost_preview_view()` - Prévisualisation compost
- `POST /api/saka/compost-trigger/` : `saka_compost_trigger_view()` - Déclencher compost (admin)
- `POST /api/saka/compost-run/` : `saka_compost_run_view()` - Dry-run compost (admin)
- `GET /api/saka/stats/` : `saka_stats_view()` - Statistiques globales (admin)
- `GET /api/saka/compost-logs/` : `saka_compost_logs_view()` - Logs compost (admin)
- `GET /api/saka/cycles/` : `saka_cycles_view()` - Liste cycles avec stats

**Logique métier** :
- **Dans la vue** : Validation permissions, vérification feature flags
- **Services appelés** : `get_saka_global_stats()`, `get_cycle_stats()`, `run_saka_compost_cycle()`

---

#### 3. **Sondages** (`polls.py`)

**Endpoints** :
- `GET/POST /api/polls/` : `PollViewSet` (ViewSet)
  - GET : Liste des sondages
  - POST : Créer un sondage
- `GET/PUT/PATCH/DELETE /api/polls/<id>/` : `PollViewSet` (ViewSet)
- `POST /api/polls/<id>/vote/` : `vote()` (action)
  - Vote avec méthodes : binary, quadratic, majority
  - Intégration SAKA : vote quadratique fertilisé
  - Vérifie `ENABLE_SAKA` et `SAKA_VOTE_ENABLED`
  - Appelle `spend_saka()` si activé
- `POST /api/polls/<id>/open/` : `open()` (action)
- `POST /api/polls/<id>/close/` : `close()` (action)

**Logique métier** :
- **Dans la vue** : Validation vote, calcul poids quadratique, intégration SAKA
- **Services appelés** : `spend_saka()`, `compute_quadratic_weight()` (modèle)

---

#### 4. **Intentions** (`intents.py`)

**Endpoints** :
- `POST /api/intents/rejoindre/` : `rejoindre()` - Formulaire "Rejoindre"
  - Validation email, honeypot, longueur message
  - Création `Intent`
- `GET /api/intents/admin/` : `admin_data()` - Liste intentions (admin)
  - Pagination, filtres (profil, email)
  - Requiert token admin
- `GET /api/intents/export/` : `export_intents()` - Export CSV (admin)
- `DELETE /api/intents/<id>/delete/` : `delete_intent()` - Supprimer intention (admin)

**Logique métier** :
- **Dans la vue** : Validation payload, honeypot, création modèle
- **Pas de service** : Logique simple dans la vue

---

#### 5. **Impact** (`impact_views.py`)

**Endpoints** :
- `GET /api/impact/dashboard/` : `ImpactDashboardView` (APIView)
  - Tableau de bord impact utilisateur
  - Met à jour métriques via Celery (non-bloquant)
- `GET /api/impact/global-assets/` : `GlobalAssetsView` (APIView)
  - Patrimoine global utilisateur
  - Retourne : `cash_balance`, `pockets`, `donations`, `equity_portfolio`, `social_dividend`, `saka`
  - Vérifie `ENABLE_SAKA` avant d'exposer données SAKA

**Logique métier** :
- **Dans la vue** : Agrégations ORM, calculs simples
- **Services appelés** : `get_saka_balance()` (si SAKA activé)

---

#### 6. **Autres Endpoints**

- **Chat** (`chat.py`) : ViewSets pour threads et messages
- **Contenus** (`content_views.py`) : ViewSet pour contenus éducatifs
- **Recherche** (`search_views.py`) : Recherche full-text projets
- **Recherche sémantique** (`semantic_search_views.py`) : Recherche avec embeddings
- **Mycelium** (`mycelium_views.py`) : Visualisation 3D
- **Monitoring** (`monitoring_views.py`) : Métriques et alertes
- **Config** (`config_views.py`) : Feature flags
- **Auth** (`auth_views.py`) : Register, login, me
- **GDPR** (`gdpr_views.py`) : Export/suppression données
- **Security** (`security_views.py`) : Audit sécurité
- **Help** (`help_views.py`) : Demandes d'aide
- **Engagement** (`engagement_views.py`) : Engagements
- **Moderation** (`moderation.py`) : Signalements
- **Audit** (`audit.py`) : Logs d'audit
- **Fundraising** (`fundraising.py`) : Cagnottes, contributions

---

## ⚙️ Services (`backend/core/services/`)

### Services Identifiés (4 fichiers)

#### 1. **SAKA** (`saka.py`)

**Fonctions principales** :
- `is_saka_enabled()` : Vérifie si SAKA est activé
- `get_or_create_wallet(user)` : Récupère/crée wallet SAKA
- `harvest_saka(user, reason, amount, metadata)` : Récolte SAKA
  - Anti-farming : limites quotidiennes par raison
  - Transaction atomique
  - Crée `SakaTransaction` (EARN)
  - Met à jour `SakaWallet`
- `spend_saka(user, amount, reason, metadata)` : Dépense SAKA
  - Vérifie solde
  - Verrouillage `select_for_update()`
  - Transaction atomique
  - Crée `SakaTransaction` (SPEND)
  - Met à jour `SakaWallet`
- `get_saka_balance(user)` : Retourne balance et stats
- `run_saka_compost_cycle(dry_run)` : Cycle de compostage
  - Identifie wallets inactifs
  - Calcule montant à composter
  - Met à jour `SakaSilo`
  - Crée `SakaCompostLog`
  - Associe au `SakaCycle` actif si disponible

**Logique métier** : ✅ **Dans le service** (logique lourde isolée)

---

#### 2. **Stats SAKA** (`saka_stats.py`)

**Fonctions principales** :
- `get_saka_global_stats()` : Statistiques globales SAKA
- `get_saka_daily_stats(days)` : Série temporelle par jour
- `get_top_saka_users(limit)` : Top utilisateurs par balance
- `get_top_saka_projects(limit)` : Top projets par SAKA
- `get_cycle_stats(cycle)` : Stats par cycle (récolté, planté, composté)

**Logique métier** : ✅ **Dans le service** (agrégations ORM)

---

#### 3. **Impact 4P** (`impact_4p.py`)

**Fonctions principales** :
- `update_project_4p(project)` : Calcule et met à jour scores 4P
  - P1 : Somme contributions + escrows
  - P2 : `project.saka_score`
  - P3 : `project.impact_score`
  - P4 : Formule basée sur supporters SAKA + cagnottes
  - Crée/met à jour `ProjectImpact4P`

**Logique métier** : ✅ **Dans le service** (calculs complexes)

---

#### 4. **Concierge** (`concierge.py`)

**Fonctions principales** :
- `is_user_concierge_eligible(user)` : Vérifie éligibilité
- `get_or_create_concierge_thread(user)` : Récupère/crée thread concierge

**Logique métier** : ✅ **Dans le service** (règles métier)

---

## 📊 Analyse : Séparation des Responsabilités

### ✅ Points Forts

1. **Service Layer bien utilisé** :
   - Logique métier lourde dans `core/services/`
   - Exemples : `saka.py`, `saka_stats.py`, `impact_4p.py`
   - Services réutilisables (appelables depuis vues, tâches Celery, management commands)

2. **Vues légères** :
   - Vues API se contentent de validation HTTP et orchestration
   - Exemples : `projects.py`, `saka_views.py`, `polls.py`
   - Appellent les services pour la logique métier

3. **Modèles propres** :
   - Modèles contiennent uniquement données et logique bas niveau
   - Exemples : `ProjetQuerySet.search()`, `Poll.get_vote_weight()`
   - Pas de logique métier complexe dans les modèles

4. **Transactions atomiques** :
   - Utilisation correcte de `@transaction.atomic`
   - Verrous pessimistes avec `select_for_update()`
   - Exemples : `boost_project()`, `spend_saka()`

5. **Feature flags cohérents** :
   - Vérification des flags dans les vues
   - Services respectent les flags (`is_saka_enabled()`)

---

### ⚠️ Points Fragiles/Confus

1. **Mélange logique dans certaines vues** :
   - **Fichier** : `backend/core/api/polls.py` (ligne 150-195)
   - **Problème** : Calcul poids quadratique et intégration SAKA directement dans la vue
   - **Impact** : Logique métier difficile à tester isolément
   - **Recommandation** : Extraire dans `core/services/polls.py` (ex: `compute_vote_with_saka()`)

2. **Agrégations ORM dans les vues** :
   - **Fichier** : `backend/core/api/impact_views.py` (ligne 87-205)
   - **Problème** : Calculs d'agrégation directement dans `GlobalAssetsView.get()`
   - **Impact** : Vue longue, difficile à tester
   - **Recommandation** : Extraire dans `core/services/assets.py` (ex: `get_user_global_assets()`)

3. **Validation métier dans les vues** :
   - **Fichier** : `backend/core/api/intents.py` (ligne 31-51)
   - **Problème** : Fonctions de validation (`_validate_payload()`, `_has_honeypot()`) dans la vue
   - **Impact** : Pas réutilisable, difficile à tester
   - **Recommandation** : Déplacer dans `core/services/intents.py` ou créer un validator DRF

4. **Gestion d'erreurs incohérente** :
   - **Fichier** : `backend/core/services/impact_4p.py` (ligne 100-105)
   - **Problème** : `try/except` silencieux qui retourne `None` en cas d'erreur
   - **Impact** : Erreurs masquées, difficile à déboguer
   - **Recommandation** : Logger l'erreur ET la propager ou utiliser un système d'alertes

5. **Dépendances circulaires potentielles** :
   - **Fichier** : `backend/core/services/impact_4p.py` (ligne 17)
   - **Problème** : Import `finance.models.EscrowContract` dans `core.services`
   - **Impact** : Couplage entre apps, risque de dépendances circulaires
   - **Recommandation** : Utiliser des interfaces ou déplacer la logique 4P dans `finance`

6. **Tests de concurrence limités** :
   - **Fichier** : `backend/core/tests_saka.py`
   - **Problème** : `SakaConcurrencyTestCase` gère les limitations SQLite mais pourrait être plus robuste
   - **Impact** : Tests peuvent échouer sur SQLite mais passer sur PostgreSQL
   - **Recommandation** : Ajouter des tests spécifiques PostgreSQL ou utiliser `pytest-postgresql`

---

## 🎯 Conclusion

### Architecture Backend Détectée

**Type** : **Monolithe Django structuré avec Service Layer**

**Patterns** :
- **Service Layer** : Logique métier isolée dans `core/services/`
- **View Layer** : Vues API légères (validation HTTP, orchestration)
- **Model Layer** : Modèles propres (données + logique bas niveau)
- **Feature Flags** : Architecture "Sleeping Giant" (V1.6/V2.0/SAKA)

**Stack** :
- Django 5 + DRF + Celery + Redis + Channels
- PostgreSQL (pg_trgm, pgvector)
- S3/R2 pour médias
- JWT avec rotation
- OpenAPI/Swagger

### Points Forts

1. ✅ **Séparation claire** : Service Layer bien utilisé pour logique métier lourde
2. ✅ **Sécurité** : Verrous pessimistes, transactions atomiques, tests de concurrence
3. ✅ **Feature flags** : Architecture hybride V1.6/V2.0/SAKA bien implémentée
4. ✅ **Documentation** : OpenAPI/Swagger configuré
5. ✅ **Tests** : Tests unitaires et de concurrence présents

### Points Fragiles/Confus

1. ⚠️ **Mélange logique dans certaines vues** : `polls.py`, `impact_views.py`
2. ⚠️ **Validation métier dans les vues** : `intents.py`
3. ⚠️ **Gestion d'erreurs silencieuse** : `impact_4p.py`
4. ⚠️ **Dépendances inter-apps** : `core.services` → `finance.models`
5. ⚠️ **Tests de concurrence** : Limitations SQLite non complètement gérées

**Recommandation globale** : Architecture solide avec quelques améliorations possibles (extraction logique métier, gestion d'erreurs, tests PostgreSQL).

---

**Dernière mise à jour** : 2025-12-16


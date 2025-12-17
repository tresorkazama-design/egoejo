# 📋 Synthèse d'Audit - EGOEJO (Basée Uniquement sur le Code)

**Date** : 2025-12-16  
**Auteur** : Analyse basée uniquement sur le code (backend, frontend, tests, config)  
**Objectif** : Rapport pour quelqu'un qui ne connaît pas le projet  
**Méthodologie** : Observation directe du code, sans référence aux documents marketing

---

## 🎯 Ce que le Code Dit qu'EGOEJO Est

**EGOEJO est une plateforme web de financement participatif hybride** qui permet à des utilisateurs de financer et soutenir des projets sociaux/écologiques via deux systèmes de valeur complémentaires et strictement séparés :

### 1. Système Financier (Euros) - V1.6 Actif + V2.0 Dormant

Le code révèle un système financier sophistiqué avec deux modes :

**V1.6 (Actif)** : Les projets peuvent recevoir des **dons** via des cagnottes (`Cagnotte`, `Contribution`). Les engagements financiers sont gérés via des contrats d'escrow (`EscrowContract`) qui verrouillent les fonds jusqu'à libération. Le système calcule automatiquement les commissions EGOEJO (5% par défaut) et les frais Stripe estimés (3%). Les utilisateurs ont des wallets (`UserWallet`) avec des "pockets" (`WalletPocket`) pour allouer leurs fonds entre dons et investissement réservé.

**V2.0 (Dormant)** : Un système d'**investissement en actions** est présent dans le code mais désactivé par le feature flag `ENABLE_INVESTMENT_FEATURES=False`. Les modèles `ShareholderRegister`, `InvestmentContract`, et les champs `investment_goal`, `share_price` existent mais ne sont pas utilisés. C'est l'architecture "Sleeping Giant" : le code est prêt, il suffit d'activer le flag.

**Exemples concrets du code** :
- `EscrowContract` : Statuts `LOCKED`, `RELEASED`, `REFUNDED`
- `WalletTransaction` : Types `DEPOSIT`, `PLEDGE_DONATION`, `PLEDGE_EQUITY`, `REFUND`, `RELEASE`, `COMMISSION`, `POCKET_TRANSFER`
- Services `pledge_funds()`, `release_escrow()`, `refund_escrow()` avec verrous `select_for_update()` et transactions atomiques
- Tests finance : `EscrowContractTestCase`, `EscrowReleaseTestCase`, `EscrowRefundTestCase` (créés récemment)

### 2. Système SAKA (Engagement Non Monétaire) - Protocole Complet

Le code révèle un protocole SAKA complet et sophistiqué :

**Récolte (EARN)** : Les utilisateurs "récoltent" des grains SAKA via `harvest_saka()` en s'engageant (lecture de contenu, vote, croissance du réseau). Chaque source a une limite quotidienne (`SAKA_DAILY_LIMITS`) pour éviter le farming. Les transactions sont enregistrées dans `SakaTransaction` avec raison (`content_read`, `poll_vote`, `invite_accepted`, etc.).

**Plantation (SPEND)** : Les utilisateurs "plantent" leur SAKA via `spend_saka()` pour booster des projets (`boost_project()`) ou des votes (`PollBallot.saka_spent`). Les boosts augmentent le `saka_score` du projet et sont enregistrés dans `SakaProjectSupport` pour éviter les doublons.

**Compostage (Cycle)** : Le SAKA inactif est "composté" périodiquement via `run_saka_compost_cycle()` qui retourne les grains au Silo commun (`SakaSilo`). Le compostage est journalisé dans `SakaCompostLog` avec détails (wallet, amount, reason). Les cycles sont représentés par `SakaCycle` avec `start_date`, `end_date`, `is_active`.

**Redistribution (V1 Implémentée)** : Le code contient `redistribute_saka_silo()` qui prend un pourcentage du Silo (5% par défaut) et le distribue équitablement aux wallets éligibles (ceux avec `total_harvested >= MIN_ACTIVITY`). C'est une V1 simple mais fonctionnelle.

**Exemples concrets du code** :
- `SakaWallet` : `balance`, `total_harvested`, `total_planted`, `total_composted`, `last_activity_date`
- `SakaTransaction` : `direction` (EARN/SPEND), `amount`, `reason`, `metadata` (JSON)
- `SakaSilo` : `total_balance`, `total_composted`, `total_cycles`, `last_compost_at`
- `SakaCycle` : `name`, `start_date`, `end_date`, `is_active`
- Services : `harvest_saka()`, `spend_saka()`, `boost_project()`, `run_saka_compost_cycle()`, `redistribute_saka_silo()`, `get_cycle_stats()`
- Tests : 27 tests SAKA couvrant wallet, récolte, dépense, boost, cycles, concurrence, redistribution

### 3. Les Projets Sont au Centre

Chaque projet (`Projet`) est l'entité centrale qui peut recevoir :
- **Financement financier** : Via `Cagnotte` (V1.6) ou investissement (V2.0 dormant)
- **Support SAKA** : Via `boost_project()` qui crée `SakaProjectSupport` et augmente `saka_score`
- **Décisions collectives** : Via `Poll` lié au projet avec méthodes avancées (binaire, quadratique avec boost SAKA, jugement majoritaire)

Les projets ont des scores 4P (`ProjectImpact4P`) qui agrègent 4 dimensions :
- **P1 (financial_score)** : Euros mobilisés (somme des contributions)
- **P2 (saka_score)** : SAKA mobilisé (somme des boosts)
- **P3 (social_score)** : Impact social/écologique (utilise `project.impact_score` ou 0)
- **P4 (purpose_score)** : Purpose/Sens (formule simpliste : `(saka_supporters_count * 10) + (nombre_cagnottes * 5)`)

Le service `update_project_4p()` calcule et met à jour ces scores automatiquement après chaque boost SAKA ou contribution financière.

**Exemples concrets du code** :
- `Projet` : `titre`, `description`, `impact_score`, `funding_type` (DONATION/EQUITY/HYBRID), `donation_goal`, `investment_goal`, `community` (ForeignKey optionnel)
- `ProjectImpact4P` : `financial_score`, `saka_score`, `social_score`, `purpose_score`, `updated_at`
- API : `/api/projets/<id>/` expose `impact_4p` avec les 4 scores
- Frontend : `Impact4PCard` affiche les 4 dimensions, `FourPStrip` sur Dashboard

### 4. La Gouvernance Est Démocratique

Des sondages (`Poll`) avec méthodes avancées permettent aux membres de décider collectivement :
- **Binaire** : Oui/Non
- **Quadratique** : Distribution de points avec boost SAKA possible (`PollBallot.points`, `PollBallot.saka_spent`)
- **Jugement Majoritaire** : Classement des options (`PollBallot.ranking`)

Les votes peuvent être boostés avec SAKA pour exprimer l'intensité de l'engagement. Les sondages peuvent être liés à un projet (décision locale) ou globaux (décision collective).

**Exemples concrets du code** :
- `Poll` : `question`, `voting_method` (binary/quadratic/majority), `max_points`, `project` (ForeignKey optionnel)
- `PollBallot` : `user`, `poll`, `points`, `ranking`, `saka_spent`, `options` (ManyToMany)
- Service : `compute_quadratic_weight()` calcule le poids du vote avec boost SAKA
- API : `/api/polls/<id>/vote/` accepte `votes` (liste de dicts avec `option_id` et `points`)

### 5. L'Impact Est Mesuré Multi-Dimensionnellement

Chaque utilisateur a un tableau de bord d'impact (`ImpactDashboard`) qui agrège :
- Contributions financières (`total_contributions`)
- Projets soutenus (`projects_supported`)
- Intentions de rejoindre (`intentions_count`)
- SAKA récolté/planté/composté (via `SakaWallet`)

Chaque projet expose ses scores 4P via l'API. Le frontend affiche ces métriques dans le Dashboard (`FourPStrip`, `UserImpact4P`) et sur les pages projets (`Impact4PCard`).

**Exemples concrets du code** :
- `ImpactDashboard` : `user`, `total_contributions`, `projects_supported`, `intentions_count`
- API : `/api/impact/global-assets/` retourne `cash_balance`, `saka.balance`, `saka.total_harvested`, `donations.total_amount`
- Frontend : `useGlobalAssets()` hook, `Dashboard.jsx` avec `FourPStrip` et `UserImpact4P`

### 6. L'Architecture Technique

**Backend** : Django 5 + DRF avec PostgreSQL, Redis (cache + Celery), Channels (WebSocket). Architecture service layer avec séparation claire : modèles (`core/models/`), services (`core/services/`), API (`core/api/`), serializers (`core/serializers/`). Feature flags pour activer/désactiver fonctionnalités (`ENABLE_SAKA`, `ENABLE_INVESTMENT_FEATURES`, `SAKA_VOTE_ENABLED`, etc.).

**Frontend** : React 19 + Vite avec PWA (Service Workers, Workbox), Three.js pour visualisations 3D, lazy loading pour toutes les pages, Error Boundaries, hooks API réutilisables (`useSakaSilo()`, `useSakaCycles()`, `useGlobalAssets()`), internationalisation (6 langues).

**Tests** : Backend pytest (~53 tests) concentrés sur SAKA (27 tests), Intent (16 tests), Auth (10 tests), Finance (8 tests). Frontend Vitest pour composants, Playwright E2E (6 suites) pour flows critiques.

---

## ✅ Ce qui Semble Déjà Très Solide

### 1. Architecture Backend

**Points Forts** :
- **Service Layer bien structuré** : Logique métier SAKA encapsulée dans `core/services/saka.py` (récolte, dépense, compost, silo, redistribution). Séparation claire entre modèles, services, et API. Chaque service est testable isolément.
- **Sécurité concurrence** : Utilisation systématique de `select_for_update()` pour verrouiller wallets et projets lors des opérations SAKA critiques. Tests de concurrence robustes (`SakaConcurrencyTestCase`) qui prouvent la prévention de double dépense avec `threading.Thread`.
- **Transactions atomiques** : Toutes les opérations SAKA critiques sont dans `@transaction.atomic()`. Utilisation de `F()` expressions pour mises à jour atomiques (`SakaWallet.objects.update(balance=F("balance") + amount)`).
- **Anti-farming SAKA** : Limites quotidiennes par raison (`SAKA_DAILY_LIMITS`) pour éviter l'exploitation du système. Vérification dans `harvest_saka()` avant création transaction.
- **Feature Flags** : Configuration flexible via `ENABLE_SAKA`, `SAKA_VOTE_ENABLED`, `SAKA_PROJECT_BOOST_ENABLED`, `ENABLE_INVESTMENT_FEATURES` pour activer/désactiver des fonctionnalités sans déploiement.

**Exemples Concrets** :
- `spend_saka()` : Verrouillage wallet avec `select_for_update()`, vérification solde après verrouillage (pas avant), mise à jour atomique avec `F()` expressions, création transaction dans la même transaction atomique.
- `boost_project()` : Transaction atomique globale avec verrouillage projet + wallet, gestion `SakaProjectSupport` pour éviter doublons, mise à jour `saka_score` avec `F()` expressions, appel `update_project_4p()` après boost.
- Tests de concurrence : `test_concurrent_boost_double_spend_prevention` simule 2 boosts simultanés avec `threading.Thread`, prouve qu'un seul réussit, solde correct, score projet cohérent.

### 2. Architecture Frontend

**Points Forts** :
- **Lazy Loading** : Toutes les pages chargées à la demande (`lazy()` imports) pour optimiser le bundle initial. Chaque page est wrappée dans `LazyPage` avec `Suspense` et `ErrorBoundary`.
- **Error Boundaries** : Gestion erreurs par page avec `ErrorBoundary` pour éviter les crashes globaux. Chaque page lazy a son propre boundary.
- **Hooks API réutilisables** : Pattern `useGlobalAssets()`, `useSakaSilo()`, `useSakaCycles()` qui encapsulent `fetchAPI()` avec gestion loading/error centralisée. Chaque hook retourne `{ data, loading, error, refetch }`.
- **PWA** : Service Workers configurés avec stratégies de cache (NetworkFirst pour API, CacheFirst pour images/fonts). Workbox pour runtime caching des endpoints critiques (`/api/contents/`, `/api/chat/`).
- **Code Splitting** : Chunks optimisés (react-vendor, three-vendor, gsap-vendor) pour réduire la taille du bundle. Terser pour minification.
- **Internationalisation** : Support 6 langues (fr, en, es, de, ar, sw) via `utils/i18n.js` avec `t()` function. `LanguageProvider` context pour gestion langue globale.

**Exemples Concrets** :
- `router.jsx` : Toutes les pages en lazy loading avec Suspense et ErrorBoundary. 23 routes définies.
- `useSakaSilo()` : Hook TypeScript qui gère loading, error, refetch automatiquement. Interface `SakaSiloData` pour type safety.
- `vite.config.js` : Configuration PWA avec Workbox, runtime caching pour API/contents/chat, manifest.json pour installation.

### 3. Intégrité SAKA

**Points Forts** :
- **Modèles complets** : `SakaWallet`, `SakaTransaction`, `SakaSilo`, `SakaCycle`, `SakaCompostLog`, `SakaProjectSupport` couvrent tous les aspects du protocole. Chaque modèle a des docstrings claires et des `help_text`.
- **Services robustes** : `harvest_saka()`, `spend_saka()`, `boost_project()`, `run_saka_compost_cycle()`, `redistribute_saka_silo()`, `get_cycle_stats()` avec anti-farming, verrous, transactions atomiques, gestion erreurs.
- **Tests exhaustifs** : 27 tests SAKA couvrent wallet, récolte, dépense, boost, cycles, concurrence, limites quotidiennes, redistribution. Tests utilisent `TransactionTestCase` pour isolation DB.
- **API complète** : Endpoints `/api/saka/silo/`, `/api/saka/compost-preview/`, `/api/saka/stats/`, `/api/saka/cycles/`, `/api/saka/compost-logs/`, `/api/saka/compost-run/`, `/api/saka/silo/redistribute/` (admin-only). Tous protégés par `IsAuthenticated` ou `IsAdminUser`.
- **Intégration 4P** : SAKA intégré dans les scores 4P (`ProjectImpact4P.saka_score`). Service `update_project_4p()` appelé après chaque boost.

**Exemples Concrets** :
- `harvest_saka()` : Vérification limite quotidienne avec `SAKA_DAILY_LIMITS[reason]`, verrouillage wallet avec `select_for_update()`, création transaction EARN, mise à jour `total_harvested` avec `F()` expressions.
- `run_saka_compost_cycle()` : Filtrage wallets éligibles (inactivité > 90 jours, balance >= 10), compostage avec audit complet via `SakaCompostLog`, mise à jour `SakaSilo.total_balance` et `total_composted`.
- Tests : `test_concurrent_boost_double_spend_prevention` prouve qu'un seul boost réussit sur 2 simultanés, solde final correct, score projet cohérent.

### 4. Qualité des Tests

**Points Forts** :
- **Tests SAKA exhaustifs** : 27 tests couvrent tous les aspects (wallet, récolte, dépense, boost, cycles, concurrence, redistribution). Tests utilisent `TransactionTestCase` pour isolation DB et `threading.Thread` pour concurrence.
- **Tests Intent complets** : 16 tests couvrent création, validation, admin, export, suppression. Tests vérifient pagination, filtres, honeypot anti-spam.
- **Tests Auth récents** : 10 tests couvrent login, register, refresh token, rotation, current user. Tests vérifient validation, erreurs, sécurité (pas de leak password hash).
- **Tests Finance récents** : 8 tests couvrent escrow creation, release, refund, idempotency, multiple escrows. Tests vérifient commissions, fees, system wallet.
- **Tests de concurrence** : `SakaConcurrencyTestCase` simule 2 boosts simultanés et prouve la prévention de double dépense. Utilise `threading.Thread` et vérifie état final DB.
- **Tests frontend accessibilité** : 5 tests a11y (ARIA, contrast, keyboard, enhanced). Tests vérifient labels, roles, navigation clavier.
- **Tests frontend performance** : 3 tests performance (metrics, automated, lighthouse). Tests vérifient LCP, FID, CLS.

**Exemples Concrets** :
- `test_concurrent_boost_double_spend_prevention` : Utilise `threading.Thread` pour simuler 2 boosts simultanés, vérifie qu'un seul réussit, solde correct, score projet cohérent. Gère exceptions threads pour SQLite limitations.
- `test_harvest_daily_limit` : Vérifie que la limite quotidienne est respectée même sous charge. Crée plusieurs transactions, vérifie que seule la première réussit.
- Tests a11y : `aria.test.jsx`, `contrast.test.jsx`, `keyboard.test.jsx` pour accessibilité. Tests vérifient labels, roles, navigation clavier, contrast ratios.

### 5. Organisation du Code

**Points Forts** :
- **Séparation des responsabilités** : Modèles (`core/models/`), Services (`core/services/`), API (`core/api/`), Serializers (`core/serializers/`). Chaque couche a un rôle clair.
- **Modularité** : Apps Django séparées (`core`, `finance`, `investment`). Chaque app a ses modèles, services, API.
- **Documentation inline** : Docstrings dans les modèles, services, API. `help_text` dans les champs de modèles. Commentaires pour logique complexe.
- **Configuration centralisée** : `config/settings.py` avec feature flags, `pytest.ini` pour tests, `vite.config.js` pour frontend.
- **Type Safety** : TypeScript pour hooks frontend (`useSakaSilo.ts`, `useSakaCycles.ts`) avec interfaces explicites.

**Exemples Concrets** :
- `core/services/saka.py` : Logique métier SAKA isolée, réutilisable, testable. Fonctions pures avec paramètres explicites.
- `core/api/projects.py` : Orchestration HTTP, appelle les services. Validation via serializers DRF.
- `core/models/saka.py` : Modèles avec docstrings claires, `help_text`, `Meta` classes avec `verbose_name`, `ordering`, `indexes`.

---

## ⚠️ Ce qui Est Partiellement Aligné avec la Vision Docs

### 1. Scores 4P (Performance Partagée)

**Vision Docs** : Les 4 dimensions (P1: Financier, P2: SAKA, P3: Social/Écologique, P4: Purpose/Sens) sont documentées comme un pilier du système.

**Code Réalité** :
- ✅ Modèle `ProjectImpact4P` existe avec les 4 champs (`financial_score`, `saka_score`, `social_score`, `purpose_score`)
- ✅ Service `update_project_4p()` calcule les scores automatiquement
- ✅ API expose `impact_4p` dans `/api/projets/<id>/` avec structure uniforme (`p1_financier`, `p2_saka`, `p3_social`, `p4_sens`)
- ✅ Frontend affiche les scores (`Impact4PCard`, `FourPStrip`, `UserImpact4P`)
- ⚠️ **P3 (social_score)** : Utilise simplement `project.impact_score` (ou 0 si non défini). Pas de calcul d'impact réel basé sur indicateurs qualitatifs (émissions CO2 évitées, emplois créés, etc.).
- ⚠️ **P4 (purpose_score)** : Formule simpliste `(saka_supporters_count * 10) + (nombre_cagnottes * 5)`. Pas d'indicateur qualitatif réel de "sens" ou "purpose" (cohérence mission, alignement valeurs, etc.).
- ⚠️ **Dashboard utilisateur** : `ImpactDashboard` existe mais n'expose pas de vue 4P pour l'utilisateur (seulement métriques agrégées classiques : `total_contributions`, `projects_supported`).

**Écart** : Les scores 4P sont présents techniquement mais les calculs P3 et P4 sont des placeholders simplistes, pas de vrais indicateurs d'impact social/écologique ou de purpose. Le dashboard utilisateur n'expose pas les 4 dimensions.

### 2. Cycles SAKA (Saisons)

**Vision Docs** : Les cycles SAKA représentent le temps cyclique, avec agrégation des chiffres (récolté, planté, composté) par période.

**Code Réalité** :
- ✅ Modèle `SakaCycle` existe avec `start_date`, `end_date`, `is_active`, `name`
- ✅ Service `get_cycle_stats()` calcule récolté, planté, composté par cycle (filtre `SakaTransaction` par dates, `SakaCompostLog` par cycle)
- ✅ API `/api/saka/cycles/` expose les cycles avec stats (`saka_harvested`, `saka_planted`, `saka_composted`)
- ✅ `SakaCompostLog` lié à `SakaCycle` (ForeignKey optionnel)
- ✅ Frontend : Page `SakaSeasons.tsx` créée récemment avec hooks `useSakaCycles()` et `useSakaSilo()`
- ⚠️ **Création automatique cycles** : Pas de mécanisme automatique pour créer/activer des cycles. Probablement manuel via admin Django.
- ⚠️ **Redistribution Silo** : Le service `redistribute_saka_silo()` existe mais n'est pas lié aux cycles. Redistribution manuelle (admin-only endpoint) ou tâche Celery optionnelle.

**Écart** : Les cycles existent techniquement et sont maintenant visibles dans le frontend, mais la création/activation est manuelle et la redistribution n'est pas automatique par cycle.

### 3. Subsidiarité (Décisions au Plus Bas Niveau)

**Vision Docs** : La subsidiarité est mentionnée comme principe de gouvernance (décisions au niveau des communautés).

**Code Réalité** :
- ✅ Modèle `Community` existe avec `name`, `slug`, `description`, `is_active`, `members` (ManyToMany), `projects` (related_name)
- ✅ `Projet` a un ForeignKey optionnel vers `Community`
- ✅ API `/api/communities/` et `/api/communities/<slug>/` exposent les communautés (read-only, `AllowAny`)
- ✅ Sondages (`Poll`) peuvent être liés à un projet (décision locale)
- ✅ Vote quadratique permet d'exprimer l'intensité
- ⚠️ **Pas de sondages par communauté** : Les sondages sont globaux ou liés à un projet, pas à une communauté. Pas de `Poll.community` ForeignKey.
- ⚠️ **Pas de budgets par communauté** : Pas de modèle `CommunityBudget` ou allocation de fonds par communauté.
- ⚠️ **Délégation** : Pas de mécanisme de délégation de vote visible.

**Écart** : Les outils de gouvernance existent (sondages, votes) et la structure `Community` existe, mais les sondages ne sont pas liés aux communautés et il n'y a pas de budgets/décisions financières par communauté.

### 4. Temps Cyclique vs Linéaire

**Vision Docs** : Le temps cyclique (saisons, compost) est opposé au temps linéaire (accumulation infinie).

**Code Réalité** :
- ✅ Compostage périodique : `run_saka_compost_cycle()` retourne SAKA inactif au Silo
- ✅ Cycles SAKA : `SakaCycle` pour agrégation temporelle
- ✅ `SakaSilo` accumule les grains compostés
- ✅ Redistribution : `redistribute_saka_silo()` distribue le Silo aux wallets éligibles (V1 implémentée)
- ⚠️ **Redistribution automatique** : Le service existe mais pas de tâche Celery automatique. Redistribution manuelle (admin-only) ou optionnelle.
- ⚠️ **Visualisation cycles** : Page `SakaSeasons.tsx` créée récemment mais pas encore intégrée dans la navigation principale (seulement liens Dashboard).

**Écart** : Le compostage existe (retour au Silo) et la redistribution existe (V1), mais la redistribution n'est pas automatique par cycle. Le cycle est presque complet mais pas entièrement automatisé.

### 5. Double Métrique (Euros / SAKA)

**Vision Docs** : Les deux systèmes (financier et SAKA) sont complémentaires et mesurent des dimensions différentes.

**Code Réalité** :
- ✅ Scores 4P : P1 (financier) et P2 (SAKA) sont calculés séparément
- ✅ API expose les deux : `/api/impact/global-assets/` retourne `cash_balance` et `saka.balance`
- ✅ Frontend : `FourPStrip` affiche capital financier et capital SAKA côte à côte
- ✅ Projets : `Impact4PCard` affiche les 4 dimensions (P1 et P2 séparés)
- ⚠️ **Dashboard utilisateur** : `ImpactDashboard` n'expose pas de vue 4P pour l'utilisateur (seulement métriques classiques). `UserImpact4P` existe mais calcule P3/P4 avec des proxies simplistes.

**Écart** : Les deux métriques existent techniquement et sont présentées ensemble dans certains composants (`FourPStrip`, `Impact4PCard`), mais le dashboard utilisateur n'a pas de vue 4P complète.

---

## ❌ Ce qui Manque ou Est Encore Théorique

### 1. Indicateurs d'Impact Réels (P3, P4)

**Vision Docs** : P3 (social/écologique) et P4 (purpose/sens) devraient être des indicateurs qualitatifs réels.

**Code Réalité** :
- ⚠️ **P3** : Utilise simplement `project.impact_score` (ou 0). Pas de calcul basé sur indicateurs réels (émissions CO2 évitées, emplois créés, hectares restaurés, etc.).
- ⚠️ **P4** : Formule simpliste basée sur supporters + cagnottes. Pas d'indicateur qualitatif réel de "sens" ou "purpose" (cohérence mission, alignement valeurs, impact systémique, etc.).

**Impact** : Les scores 4P sont présents mais P3 et P4 sont des placeholders, pas de vrais indicateurs d'impact.

### 2. Tests E2E Manquants (Frontend)

**Code Réalité** :
- ✅ 6 suites E2E Playwright (home, admin, contenus, rejoindre, navigation, backend-connection)
- ✅ Tests E2E SAKA récents (saka-flow.spec.js) : balance, season badge, silo, boost projet
- ❌ **Pages critiques non testées E2E** : Dashboard complet, Votes (vote quadratique avec boost SAKA), SakaMonitor, SakaSilo, Chat temps réel.

**Impact** : Les fonctionnalités critiques (vote quadratique avec boost SAKA) ne sont pas testées end-to-end.

### 3. Tâches Celery Non Testées

**Code Réalité** :
- ✅ Tâches existent : `tasks.py` (compost SAKA), `tasks_audio.py`, `tasks_embeddings.py`, `tasks_mycelium.py`, `tasks_security.py`
- ❌ **Aucune tâche testée** : Pas de tests pour les tâches asynchrones (compost SAKA, scan antivirus, génération embeddings). Tests unitaires des services existent mais pas de tests d'intégration Celery.

**Impact** : Les tâches critiques (compost SAKA) ne sont pas testées automatiquement en contexte Celery.

### 4. API Manquantes Non Testées

**Code Réalité** :
- ✅ Tests existent : SAKA (27), Intent (16), Auth (10), Finance (8), Projects 4P (6)
- ❌ **Endpoints non testés** : Content, Engagement, Help, Monitoring, Mycelium, Search, Security, GDPR, Moderation, Audit, Communities (API seulement, pas de tests)

**Impact** : Couverture tests incomplète pour endpoints non critiques mais importants.

### 5. Visualisation 3D Mycelium (Tests)

**Code Réalité** :
- ✅ Modèle `Projet` a `coordinates_3d` (JSON)
- ✅ API `/api/mycelium/` existe
- ✅ Frontend : Composants Three.js pour visualisation
- ❌ **Pas de tests** : Pas de tests pour la visualisation 3D (chargement, interactions, performance).

**Impact** : La visualisation 3D n'est pas testée automatiquement.

---

## 🎯 Recommandations Concrètes

### 🔴 Priorité Immédiate (Prochain Sprint)

1. **Tests E2E pour Fonctionnalités Critiques**
   - **Action** : Ajouter tests Playwright pour Dashboard complet, Votes (vote quadratique avec boost SAKA), SakaMonitor
   - **Impact** : Garantir que les fonctionnalités SAKA fonctionnent end-to-end
   - **Effort** : 2-3 jours
   - **Fichiers** : `frontend/frontend/e2e/dashboard.spec.js`, `frontend/frontend/e2e/votes.spec.js`

2. **Tests Tâches Celery (Compost SAKA)**
   - **Action** : Ajouter tests pour `run_saka_compost_cycle()` (mock Celery ou tests unitaires du service)
   - **Impact** : Garantir que le compostage fonctionne correctement
   - **Effort** : 1-2 jours
   - **Fichiers** : `backend/core/tests_celery.py` ou extension `backend/core/tests_saka.py`

3. **Documentation Code Manquante**
   - **Action** : Documenter les endpoints API non documentés (Content, Engagement, Help, etc.) avec docstrings DRF
   - **Impact** : Faciliter la maintenance et l'onboarding
   - **Effort** : 1-2 jours
   - **Fichiers** : `backend/core/api/*.py`

---

### 🟡 Prochain Sprint (2-4 Semaines)

4. **Mécanisme de Redistribution Automatique du Silo**
   - **Action** : Créer tâche Celery `run_saka_silo_redistribution()` qui s'exécute périodiquement (ex: après chaque cycle de compost) avec feature flag `SAKA_SILO_REDIS_ENABLED`
   - **Impact** : Compléter le cycle SAKA (compost → redistribution automatique)
   - **Effort** : 2-3 jours
   - **Fichiers** : `backend/core/tasks.py` (tâche existe déjà mais pas automatique), `backend/config/settings.py` (cron schedule)

5. **Dashboard Utilisateur 4P Complet**
   - **Action** : Améliorer `UserImpact4P` pour calculer P3/P4 avec des indicateurs réels (ou placeholders plus réalistes) et afficher les 4 dimensions côte à côte
   - **Impact** : Exposer les 4 dimensions d'impact pour l'utilisateur
   - **Effort** : 2-3 jours
   - **Fichiers** : `frontend/frontend/src/components/dashboard/UserImpact4P.jsx`, `backend/core/services/impact_4p.py`

6. **Tests API Manquantes**
   - **Action** : Ajouter tests pour Content, Engagement, Help, Communities (API seulement, pas de tests)
   - **Impact** : Couverture tests complète pour endpoints importants
   - **Effort** : 1 semaine
   - **Fichiers** : `backend/core/tests_content.py`, `backend/core/tests_engagement.py`, `backend/core/tests_communities.py`

7. **Intégration Navigation Saisons SAKA**
   - **Action** : Ajouter lien "Saisons SAKA" dans navigation principale (Layout) et améliorer visibilité
   - **Impact** : Rendre les cycles visibles pour les utilisateurs
   - **Effort** : 1 jour
   - **Fichiers** : `frontend/frontend/src/components/Layout.jsx`

---

### 🟢 Long Terme (1-3 Mois)

8. **Indicateurs d'Impact Réels (P3, P4)**
   - **Action** : Créer modèles `ImpactIndicator` (émissions CO2, emplois créés, hectares restaurés, etc.) et intégrer dans calcul P3/P4. Pour P4, créer système de scoring qualitatif (cohérence mission, alignement valeurs, impact systémique).
   - **Impact** : Remplacer les placeholders par de vrais indicateurs d'impact
   - **Effort** : 2-3 semaines
   - **Fichiers** : `backend/core/models/impact.py` (nouveau modèle), `backend/core/services/impact_4p.py` (calcul amélioré)

9. **Sondages par Communauté**
   - **Action** : Ajouter `Poll.community` ForeignKey et filtrer sondages par communauté. Créer budgets communautaires (`CommunityBudget`) pour allocation de fonds.
   - **Impact** : Mettre en œuvre la subsidiarité (décisions au niveau des communautés)
   - **Effort** : 1-2 semaines
   - **Fichiers** : `backend/core/models/polls.py`, `backend/core/models/communities.py`, `backend/core/api/polls.py`

10. **Tests Visualisation 3D**
    - **Action** : Ajouter tests pour la visualisation 3D (chargement, interactions, performance) avec Playwright ou tests unitaires Three.js
    - **Impact** : Garantir que la visualisation 3D fonctionne correctement
    - **Effort** : 1 semaine
    - **Fichiers** : `frontend/frontend/src/app/pages/__tests__/Mycelium.test.tsx`, `frontend/frontend/e2e/mycelium.spec.js`

11. **Tests API Complémentaires**
    - **Action** : Ajouter tests pour Monitoring, Mycelium, Search, Security, GDPR, Moderation, Audit
    - **Impact** : Couverture complète des endpoints API
    - **Effort** : 2-3 semaines
    - **Fichiers** : `backend/core/tests_monitoring.py`, `backend/core/tests_mycelium.py`, etc.

---

## 📝 Conclusion

**Points Forts** :
- Architecture backend solide (service layer, sécurité concurrence, transactions atomiques, feature flags)
- Architecture frontend moderne (lazy loading, PWA, hooks réutilisables, TypeScript)
- Intégrité SAKA très bien testée (27 tests, concurrence, anti-farming, redistribution V1)
- Tests concentrés sur fonctionnalités critiques (SAKA, Intent, Auth, Finance)
- Système 4P présent techniquement (modèles, services, API, frontend)

**Points d'Amélioration** :
- Couverture tests incomplète (Celery non testé, certains endpoints API non testés)
- Scores 4P P3/P4 sont des placeholders (pas d'indicateurs réels)
- Redistribution Silo existe mais pas automatique
- Sondages pas liés aux communautés (subsidiarité partielle)
- Visualisation 3D non testée

**Recommandation Prioritaire** : Compléter les tests E2E pour fonctionnalités critiques (Dashboard, Votes) et ajouter tests Celery (compost SAKA) avant de continuer le développement de nouvelles fonctionnalités. Améliorer les calculs P3/P4 avec des indicateurs réels (ou placeholders plus réalistes) pour rendre les scores 4P plus significatifs.

---

**Dernière mise à jour** : 2025-12-16  
**Basé sur** : Code observé dans `backend/`, `frontend/`, `docs/` (architecture uniquement)


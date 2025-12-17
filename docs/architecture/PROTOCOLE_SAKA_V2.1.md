# 🌾 Protocole SAKA V2.1 - Le Cerveau Yin

**Date** : 2025-12-16  
**Version** : 2.1.0 (Phase 1, 2 & 3 implémentées)  
**Statut** : ✅ Fondations backend complètes, Vote quadratique & Boost opérationnels, Compostage & Cycles SAKA implémentés

---

## 🎯 Vision

SAKA est une monnaie interne d'engagement (Yin) strictement séparée de l'Euro (Yang). Elle mesure la part non monétaire de la performance : l'engagement, la participation, la contribution au bien commun.

### Règles Fondamentales

1. **SAKA ne s'achète pas, il se récolte** (Proof of Care)
2. **SAKA ne sert pas à consommer, mais à influencer** (gouvernance)
3. **SAKA inactif retourne au Silo commun** (compostage)
4. **SAKA (Yin) et Euro (Yang) sont strictement séparés**

### Sémantique

- ✅ **"grains"**, **"récolter"**, **"planter"**, **"nourrir"**, **"composter"**
- ❌ **Jamais "acheter/vendre/investir"** avec SAKA

---

## 🌍 Ce que nous quittons, ce que nous installons

### Ce que nous quittons

Le système financier traditionnel repose sur une logique d'accumulation infinie dans un temps linéaire. L'argent unique (monnaie dominante) encourage la thésaurisation : tu gardes, ça grossit ou ça dort. L'usure et l'intérêt fixe créent une dynamique où l'accumulation prime sur la circulation. Cette logique ignore la pluralité des valeurs : seule la valeur financière compte.

### Ce que nous installons

SAKA installe une logique de **temps cyclique** (saisons SAKA) plutôt que linéaire. Il reconnaît la **pluralité des valeurs** : la valeur financière (euros) et la valeur d'engagement (SAKA) coexistent sans se mélanger. Le système privilégie la **circulation** (compostage) plutôt que la thésaurisation : le SAKA qui ne bouge pas retourne au Silo commun pour nourrir le bien commun.

**En 4 phrases** : Dans un système financier classique, tu gardes ton argent, il peut grossir ou dormir. Dans SAKA, tu récoltes des grains par ton engagement, tu les plantes pour influencer les décisions, ils circulent dans la communauté, et s'ils restent inactifs, ils compostent pour revenir nourrir le collectif. Le SAKA qui ne circule pas n'est pas "perdu", il est recyclé en bien commun. Cette circulation permanente crée une dynamique où l'engagement compte autant que l'argent.

---

## 🌾 Les Saisons SAKA (Cycles)

Le protocole SAKA suit un cycle naturel en trois phases, inspiré des saisons agricoles :

### 1. Semailles (Récolte)

L'utilisateur récolte du SAKA par ses actions d'engagement :
- Lecture de contenu éducatif
- Participation à un vote
- Invitation d'un nouveau membre
- Création de contenu

Chaque action est une **preuve de soin** (Proof of Care) qui génère des grains SAKA. Le système suit les montants récoltés par période, avec des limites quotidiennes pour éviter le "farming" massif.

### 2. Croissance (Plantation)

L'utilisateur plante son SAKA pour influencer :
- **Vote quadratique fertilisé** : les grains SAKA multiplient le poids du vote
- **Sorgho-boosting** : nourrir un projet avec des grains SAKA augmente son score
- **Soutien communautaire** : engagement dans la gouvernance

Le SAKA planté est engagé, mais reste traçable dans le journal de transactions.

### 3. Compost (Retour au Silo)

Le SAKA inactif (non utilisé pendant une période définie) retourne au Silo commun. Ce compostage n'est pas une "perte" : c'est un recyclage qui nourrit le bien commun. Le système suit les montants compostés par cycle, permettant une redistribution équitable.

**Important** : Le SAKA qui ne bouge pas n'est pas "perdu", il est recyclé en bien commun. Cette logique de circulation permanente évite l'accumulation stérile et encourage l'engagement continu.

### Modèle technique des Cycles

Le système utilise un modèle `SakaCycle` pour représenter les saisons (ex: "Saison 2026 - Printemps"). Chaque cycle a une période définie (date de début, date de fin) et peut être marqué comme actif. Le système agrège automatiquement les montants récoltés, plantés et compostés par cycle, permettant de suivre l'évolution de l'économie SAKA sur différentes périodes. Les logs de compost sont liés aux cycles pour une traçabilité complète.

---

## 📊 SAKA et la Performance Partagée (4P)

SAKA permet de mesurer et d'afficher les **quatre dimensions de la performance** :

### P1 : Performance Financière (Euro)

Les euros mobilisés, les revenus futurs, les investissements. Mesurée via les wallets financiers (`UserWallet`, `WalletPocket`), les contributions aux cagnottes, les investissements (V2.0).

### P2 : Performance Vivante (SAKA)

L'engagement, la participation, la contribution non monétaire. Mesurée via les wallets SAKA (`SakaWallet`), les transactions de récolte/plantation, les scores de projets boostés. SAKA capture ce que l'euro ne peut pas mesurer : l'intensité de l'engagement, la qualité de la participation.

### P3 : Performance Sociale / Écologique

Les scores d'impact, les indicateurs qualitatifs (arbres plantés, heures de formation, projets soutenus). Mesurée via les métriques d'impact (`ImpactDashboard`), les contributions aux projets, les indicateurs de bien commun.

### P4 : Purpose / Sens

La cohérence avec le vivant, l'alignement avec la mission. Mesurée via la cohérence entre les actions (SAKA) et les valeurs (mission), l'engagement long terme, la contribution au collectif.

### SAKA ne remplace pas l'Euro

- **L'euro sert à financer** : payer les projets, les salaires, les infrastructures
- **SAKA mesure la part non monétaire** : l'engagement, la participation, la contribution au bien commun

L'architecture technique (wallets SAKA + scores + Silo) permet de calculer et d'afficher ces 4 dimensions simultanément, offrant une vision complète de la performance d'un projet ou d'un utilisateur.

---

## 🛡️ Garanties techniques du protocole SAKA

Le protocole SAKA garantit plusieurs invariants critiques pour assurer sa cohérence et sa sécurité :

### Invariants garantis

1. **Aucun solde SAKA ne peut devenir négatif**
   - Vérifications systématiques avant chaque dépense
   - Verrous de base de données (`select_for_update()`) pour éviter les race conditions
   - Transactions atomiques qui garantissent la cohérence

2. **Chaque opération est traçable**
   - Toute récolte, plantation, boost est enregistrée dans `SakaTransaction`
   - Journal complet avec métadonnées (raison, montant, date, utilisateur)
   - Historique consultable pour audit et transparence

3. **Les boosts de projets sont atomiques**
   - Transactions atomiques globales : soit tout passe, soit rien ne passe
   - Verrouillage simultané du wallet SAKA et du projet (`select_for_update()`)
   - Protection contre les clics répétés et les scripts malveillants
   - Tests de concurrence validant qu'un double boost simultané ne peut pas dépenser plus que le solde disponible

4. **Les cycles de compost sont contrôlés et journalisés**
   - Exécution via tâches planifiées (Celery Beat) ou déclenchement manuel (admin)
   - Chaque cycle est enregistré dans `SakaCompostLog` avec tous les paramètres
   - Mode "dry-run" disponible pour tester sans modifier les données

### Protection contre les abus

- **Limites quotidiennes** : chaque source de SAKA a une limite par jour (ex: 3 contenus, 10 votes)
- **Règles d'éligibilité** : le compostage ne s'applique qu'aux wallets inactifs depuis un certain nombre de jours
- **Vérifications de cohérence** : le système vérifie que les soldes restent cohérents après chaque opération
- **Résistance aux attaques** : le système est conçu pour résister aux clics répétés, scripts ou tentatives de "farming" massifs

---

## 💡 Conséquences pratiques

### Pour l'utilisateur

L'utilisateur n'a pas besoin de comprendre les détails techniques. Il voit surtout qu'il :
- **Récolte des grains** par son engagement (lecture, vote, participation)
- **Plante ses grains** pour influencer les décisions (boost projets, vote quadratique)
- **Voit ses grains revenir nourrir le commun** s'il ne les utilise pas (compostage)

Il a deux métriques visibles :
- **Euro** : ce qu'il met financièrement (dons, investissements)
- **SAKA** : ce qu'il donne de lui-même (engagement, participation, contribution)

Ces deux métriques coexistent sans se mélanger, offrant une vision complète de sa contribution au collectif.

### Pour l'équipe technique / produit

**Surveillance nécessaire** :
- Temps de réponse des endpoints SAKA (notamment `/api/projets/<pk>/boost/` et `/api/polls/<pk>/vote/`)
- Charge sur les transactions atomiques lors de pics d'engagement
- Performance des cycles de compost (tâches Celery périodiques)

**Tests automatisés essentiels** :
- **Cohérence des soldes** : vérifier qu'aucun solde ne devient négatif
- **Concurrence** : tester les double-boosts, votes simultanés, race conditions (tests `TransactionTestCase` avec threads)
- **Compost périodique** : vérifier que les cycles s'exécutent correctement et journalisent tout
- **Cycles SAKA** : vérifier que les statistiques par cycle sont correctement calculées

**Points d'attention en production** :
- Configuration Redis/Celery pour les tâches périodiques
- Monitoring des transactions SAKA (volume, patterns, anomalies)
- Alertes sur les soldes incohérents ou les échecs de transactions

---

## 📋 Architecture Implémentée

### Modèles (`core/models/saka.py`)

1. **`SakaWallet`** : Portefeuille SAKA par utilisateur
   - `balance` : Grains disponibles
   - `total_harvested` : Grains jamais récoltés
   - `total_planted` : Grains jamais plantés (engagés)
   - `total_composted` : Grains compostés (retournés au Silo)
   - `last_activity_date` : Date de dernière activité

2. **`SakaTransaction`** : Historique complet des transactions
   - Types : `EARN` (récolte), `SPEND` (dépense)
   - Raisons : `content_read`, `poll_vote`, `invite_accepted`, `project_boost`, etc.
   - Métadonnées JSON pour traçabilité complète

3. **`SakaSilo`** : Silo commun (compostage)
   - Singleton pour gérer le compostage des grains inactifs
   - `total_balance` : Solde actuel du Silo
   - `total_composted` : Cumul historique
   - `total_cycles` : Nombre de cycles exécutés

4. **`SakaCompostLog`** : Audit log des cycles de compost
   - Enregistre chaque exécution (manuelle ou Celery)
   - Paramètres utilisés (inactivity_days, rate, min_balance, etc.)
   - Mode dry-run vs live
   - Lié à un `SakaCycle` (optionnel) pour traçabilité

5. **`SakaCycle`** : Représentation des saisons/cycles SAKA
   - Nom du cycle (ex: "Saison 2026 / 1")
   - Période (start_date, end_date)
   - Statut actif/inactif
   - Permet d'agréger les statistiques SAKA par période

6. **`SakaProjectSupport`** : Supporters uniques d'un projet
   - Évite les doublons dans le comptage des supporters
   - Track le total SAKA dépensé par utilisateur par projet

### Services (`core/services/saka.py`)

Toute logique métier SAKA passe par ces services :

- `harvest_saka()` : Récolter des grains (Proof of Care)
- `spend_saka()` : Dépenser des grains (vote quadratique, boost projet)
- `get_saka_balance()` : Récupérer le solde utilisateur
- `run_saka_compost_cycle()` : Exécuter un cycle de compostage (Phase 3)
- `get_user_compost_preview()` : Prévisualiser le compostage pour un utilisateur

### API Endpoints (`core/api/saka_views.py`)

**Phase 1 (Fondations)** :
- `GET /api/saka/silo/` : État du Silo Commun
- `GET /api/saka/compost-preview/` : Prévisualisation du compostage utilisateur

**Phase 2 (Vote quadratique fertilisé + Boost projets)** :
- `POST /api/projets/<pk>/boost/` : Nourrir un projet avec SAKA
- `POST /api/polls/<pk>/vote/` : Voter avec intensité SAKA (vote quadratique)

**Phase 3 (Compostage & Silo Commun)** :
- `POST /api/saka/compost-trigger/` : Déclencher un cycle de compost (admin)
- `POST /api/saka/compost-run/` : Cycle de compost en dry-run (admin)
- `GET /api/saka/stats/` : Statistiques globales SAKA (admin)
- `GET /api/saka/compost-logs/` : Logs des cycles de compost (admin)
- `GET /api/saka/cycles/` : Liste des cycles SAKA avec statistiques (récolté, planté, composté par période)

**Exposition dans Global Assets** :
- `GET /api/impact/global-assets/` : Inclut les données SAKA dans la réponse

---

## ⚙️ Configuration

### Feature Flags (`settings.py`)

```python
# Activation globale du protocole SAKA
ENABLE_SAKA = os.environ.get('ENABLE_SAKA', 'False').lower() == 'true'

# Feature flags par fonctionnalité
SAKA_VOTE_ENABLED = os.environ.get('SAKA_VOTE_ENABLED', 'False').lower() == 'true'  # Phase 2
SAKA_PROJECT_BOOST_ENABLED = os.environ.get('SAKA_PROJECT_BOOST_ENABLED', 'False').lower() == 'true'  # Phase 2

# Phase 3 : Compostage & Silo Commun
SAKA_COMPOST_ENABLED = os.environ.get('SAKA_COMPOST_ENABLED', 'False').lower() == 'true'
SAKA_COMPOST_INACTIVITY_DAYS = int(os.environ.get('SAKA_COMPOST_INACTIVITY_DAYS', '90'))
SAKA_COMPOST_RATE = float(os.environ.get('SAKA_COMPOST_RATE', '0.10'))  # 10%
SAKA_COMPOST_MIN_BALANCE = int(os.environ.get('SAKA_COMPOST_MIN_BALANCE', '50'))
SAKA_COMPOST_MIN_AMOUNT = int(os.environ.get('SAKA_COMPOST_MIN_AMOUNT', '10'))

# Configuration Vote Quadratique Fertilisé (Phase 2)
SAKA_VOTE_MAX_MULTIPLIER = float(os.environ.get('SAKA_VOTE_MAX_MULTIPLIER', '2.0'))
SAKA_VOTE_SCALE = int(os.environ.get('SAKA_VOTE_SCALE', '200'))
SAKA_VOTE_COST_PER_INTENSITY = int(os.environ.get('SAKA_VOTE_COST_PER_INTENSITY', '5'))

# Configuration Sorgho-Boosting (Phase 2)
SAKA_PROJECT_BOOST_COST = int(os.environ.get('SAKA_PROJECT_BOOST_COST', '10'))
```

### Variables d'Environnement

```env
# Activer le protocole SAKA
ENABLE_SAKA=True
SAKA_VOTE_ENABLED=True
SAKA_PROJECT_BOOST_ENABLED=True

# Phase 3 (optionnel)
SAKA_COMPOST_ENABLED=False
SAKA_COMPOST_INACTIVITY_DAYS=90
SAKA_COMPOST_RATE=0.10
```

---

## 🚀 Activation

### 1. Appliquer les migrations

```bash
cd backend
python manage.py migrate
```

Les migrations SAKA sont :
- `0019_add_saka_wallet_transaction.py` : Fondations (Phase 1)
- `0020_add_saka_phase2.py` : Vote quadratique & Boost (Phase 2)
- `0021_add_saka_silo_phase3.py` : Silo Commun (Phase 3)
- `0022_add_saka_compost_log.py` : Logs de compostage (Phase 3)
- `0023_add_saka_project_support.py` : Supporters projets (Phase 2)
- `0025_sakacycle_sakacompostlog_cycle.py` : Cycles SAKA et lien avec compost logs

### 2. Activer les feature flags

Définir dans `.env` ou variables d'environnement :
```env
ENABLE_SAKA=True
SAKA_VOTE_ENABLED=True
SAKA_PROJECT_BOOST_ENABLED=True
```

### 3. Configurer Celery (Phase 3)

Pour les cycles de compost automatiques, configurer Celery Beat :
```python
# backend/config/celery.py
app.conf.beat_schedule = {
    'saka-compost-cycle': {
        'task': 'core.tasks.saka_run_compost_cycle',
        'schedule': crontab(hour=3, minute=0, day_of_week=1),  # Lundi à 3h
        'args': (False,),  # dry_run=False
    },
}
```

---

## 📊 Utilisation API

### Récupérer le solde SAKA (via Global Assets)

```bash
GET /api/impact/global-assets/
Authorization: Bearer <token>

Response:
{
  "cash_balance": "100.00",
  "pockets": [...],
  "donations": {...},
  "saka": {
    "balance": 50,
    "total_harvested": 100,
    "total_planted": 30,
    "total_composted": 20
  }
}
```

### Booster un projet avec SAKA

```bash
POST /api/projets/<pk>/boost/
Authorization: Bearer <token>
Content-Type: application/json

{
  "amount": 10
}

Response:
{
  "ok": true,
  "message": "Projet 'X' boosté avec 10 grains SAKA.",
  "saka_spent": 10,
  "saka_score": 25,
  "saka_supporters_count": 3
}
```

### Voter avec intensité SAKA (vote quadratique)

```bash
POST /api/polls/<pk>/vote/
Authorization: Bearer <token>
Content-Type: application/json

{
  "votes": [{"option_id": 1, "points": 50}],
  "intensity": 3
}

Response:
{
  "id": 123,
  "saka_info": {
    "intensity": 3,
    "saka_cost": 15,
    "saka_spent": 15,
    "weight": 1.75
  }
}
```

---

## 🔄 Phases d'Implémentation

### ✅ Phase 1 : Fondations backend + affichage simple

**Statut** : ✅ **COMPLÈTE**

- ✅ Modèles créés (`SakaWallet`, `SakaTransaction`)
- ✅ Services créés (`harvest_saka()`, `spend_saka()`, `get_saka_balance()`)
- ✅ API endpoints créés
- ✅ Routes configurées
- ✅ Migrations créées
- ✅ Admin Django configuré
- ✅ Feature flags ajoutés
- ✅ Exposition dans `/api/impact/global-assets/`

**Fonctionnalités** :
- Affichage du solde SAKA dans le Dashboard
- Historique des transactions
- Récolte automatique (lecture, vote, invitation)

### ✅ Phase 2 : Vote quadratique fertilisé + Sorgho-boosting

**Statut** : ✅ **COMPLÈTE**

- ✅ Vote quadratique avec intensité SAKA
- ✅ Boost de projets avec SAKA
- ✅ Modèle `SakaProjectSupport` pour tracker les supporters
- ✅ Transactions atomiques sécurisées
- ✅ Tests complets (race conditions, concurrence)

**Fonctionnalités** :
- Vote quadratique fertilisé (grains SAKA multiplient le poids du vote)
- Nourrir/booster des projets avec SAKA
- API `POST /api/projets/<pk>/boost/` et `POST /api/polls/<pk>/vote/` opérationnelles

### ✅ Phase 3 : Silo commun + compostage + Cycles SAKA

**Statut** : ✅ **IMPLÉMENTÉE**

- ✅ Modèle `SakaSilo` (Silo commun)
- ✅ Modèle `SakaCompostLog` (audit des cycles)
- ✅ Modèle `SakaCycle` (saisons/cycles SAKA)
- ✅ Service `run_saka_compost_cycle()` avec dry-run
- ✅ Service `get_cycle_stats()` pour statistiques par cycle
- ✅ Tâche Celery Beat configurée
- ✅ API endpoints admin pour monitoring
- ✅ API `GET /api/saka/cycles/` pour exposition des cycles avec stats

**Fonctionnalités** :
- Compostage automatique des grains SAKA inactifs (tâche Celery périodique)
- Association des compost logs aux cycles actifs
- Agrégation des statistiques SAKA par période (récolté, planté, composté)
- Prévisualisation du compostage pour l'utilisateur

---

## 🛡️ Sécurité & Contraintes

### Séparation stricte SAKA / Euro

- ✅ Aucune conversion possible entre SAKA et Euro
- ✅ Aucune logique financière dans les services SAKA
- ✅ Modèles séparés (`SakaWallet` vs `UserWallet`)
- ✅ Endpoints distincts (`/api/saka/*` vs `/api/wallet/*`)

### Protection par feature flags

- ✅ Tous les endpoints vérifient `is_saka_enabled()`
- ✅ Chaque phase vérifie son flag spécifique (`SAKA_VOTE_ENABLED`, `SAKA_PROJECT_BOOST_ENABLED`, etc.)
- ✅ Services lèvent `ValidationError` si SAKA désactivé

### Limites quotidiennes

- ✅ Chaque raison de récolte a une `daily_limit` (ex: 3 contenus, 10 votes)
- ✅ Vérification automatique dans `harvest_saka()`
- ✅ Comptage par jour et par raison pour éviter le farming

### Protection contre les race conditions

- ✅ Transactions atomiques globales
- ✅ Verrous de base de données (`select_for_update()`) sur wallets et projets
- ✅ Tests de concurrence pour valider la robustesse

---

## 📝 Notes Techniques

### Sémantique respectée

- ✅ Utilisation de "grains", "récolter", "planter", "nourrir", "composter"
- ✅ Jamais "acheter/vendre/investir" avec SAKA
- ✅ Documentation claire sur la séparation Yin/Yang

### Architecture propre

- ✅ Toute logique métier dans `core/services/saka.py`
- ✅ Pas de logique dispersée dans les vues
- ✅ Services réutilisables et testables
- ✅ Journal de transactions complet pour audit

### Compatibilité V1.6 / V2.0

- ✅ Feature flags protègent la production
- ✅ Backward compatible (SAKA peut être désactivé sans impact)
- ✅ Intégration transparente dans l'API existante (`/api/impact/global-assets/`)

---

## 🧪 Tests

Les tests unitaires et d'intégration pour le protocole SAKA sont implémentés dans `backend/core/tests_saka.py` :

- ✅ Tests de récolte (`SakaHarvestTestCase`)
- ✅ Tests de dépense (`SakaSpendTestCase`)
- ✅ Tests de vote quadratique (`SakaVoteQuadraticTestCase`)
- ✅ Tests de boost projets (`SakaProjectBoostTestCase`)
- ✅ Tests de race conditions (`SakaRaceConditionTestCase`)
- ✅ Tests de concurrence (`SakaConcurrencyTestCase`) : validation de la double dépense avec threads
- ✅ Tests de cycles SAKA (`SakaCycleTestCase`) : création, statistiques par cycle, API
- ✅ Tests d'exposition dans global-assets (`SakaGlobalAssetsTestCase`)

**Commande** : `pytest -k "Saka" -vv`

---

## 📚 Documentation Complémentaire

- **Architecture globale** : `ARCHITECTURE_SLEEPING_GIANT_V1.6_V2.0.md`
- **Feature flags** : `backend/config/settings.py` (lignes 481-512)
- **Services** : `backend/core/services/saka.py`
- **API** : `backend/core/api/saka_views.py`
- **Tests** : `backend/core/tests_saka.py`

---

**Dernière mise à jour** : 2025-12-16  
**Version** : 2.1.0 (Phase 1, 2 & 3 complètes, Cycles SAKA implémentés) 🌾

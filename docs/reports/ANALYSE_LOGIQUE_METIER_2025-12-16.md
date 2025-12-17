# 🔍 Analyse Logique Métier Réelle - EGOEJO

**Date** : 2025-12-16  
**Objectif** : Analyser la logique métier telle qu'elle ressort du code, sans supposer la vision

---

## 📊 Domaines Métier Principaux

### 1. **Projets** (`core/models/projects.py`)

#### Modèle `Projet`

**Ce qu'il représente** :
- Un projet du collectif qui peut être financé
- Supporte deux types de financement : **Dons** (actif) et **Investissement** (dormant V2.0)
- Peut être visualisé dans un espace 3D (coordonnées 3D pour "Mycélium Numérique")
- Recherche full-text avec pg_trgm (similarité trigram)

**Relations** :
- `ForeignKey` vers `User` (créateur, via `created_by` implicite)
- `OneToOne` vers `ProjectImpact4P` (scores 4P)
- `OneToMany` vers `Media` (médias associés)
- `OneToMany` vers `Poll` (sondages liés)
- `OneToMany` vers `Cagnotte` (cagnottes de financement)
- `OneToMany` vers `SakaProjectSupport` (supports SAKA)

**Champs Clés** :
- `titre`, `description`, `categorie`, `impact_score`
- `funding_type` : DONATION (actif) ou EQUITY/HYBRID (dormant)
- `donation_goal` / `investment_goal` : Objectifs financiers distincts
- `saka_score` : Score de soutien SAKA (visibilité organique)
- `saka_supporters_count` : Nombre de membres ayant boosté
- `embedding` : Vecteur pour recherche sémantique (pgvector future)
- `coordinates_3d` : Position dans visualisation 3D

**Propriétés Calculées** :
- `donation_current` : Montant collecté via EscrowContract
- `investment_current` : Montant investi (si V2.0 activé)
- `is_investment_open` : Vérifie si investissement possible ET activé

#### Modèle `Media`

**Ce qu'il représente** :
- Fichiers multimédias associés à un projet (images, vidéos, documents)

**Relations** :
- `ForeignKey` vers `Projet` (obligatoire)

---

### 2. **Sondages & Votes** (`core/models/polls.py`)

#### Modèle `Poll`

**Ce qu'il représente** :
- Un sondage avec plusieurs méthodes de vote :
  - **Binaire** (Oui/Non) : Défaut
  - **Quadratique** : Points distribués (max 100) avec boost SAKA
  - **Jugement Majoritaire** : Classement des options
- Peut être lié à un projet (optionnel)
- Peut être réservé aux actionnaires (V2.0 dormant)

**Relations** :
- `ForeignKey` vers `Projet` (optionnel, `null=True`)
- `ForeignKey` vers `User` (créateur, `created_by`)
- `OneToMany` vers `PollOption` (options de vote)
- `OneToMany` vers `PollBallot` (bulletins de vote)

**Champs Clés** :
- `status` : DRAFT, OPEN, CLOSED
- `voting_method` : binary, quadratic, majority
- `max_points` : Points max pour vote quadratique (défaut 100)
- `is_anonymous` : Vote anonyme ou non
- `is_shareholder_vote` : Vote réservé aux actionnaires (V2.0)
- `quorum` : Quorum requis (optionnel)

**Méthodes** :
- `get_vote_weight(user)` : Calcule le poids du vote (1 voix V1.6, ou x100 pour fondateurs V2.0)

#### Modèle `PollOption`

**Ce qu'il représente** :
- Une option de réponse dans un sondage

**Relations** :
- `ForeignKey` vers `Poll` (obligatoire)
- `OneToMany` vers `PollBallot` (bulletins pour cette option)

#### Modèle `PollBallot`

**Ce qu'il représente** :
- Un bulletin de vote individuel (une voix pour une option)

**Relations** :
- `ForeignKey` vers `Poll` (obligatoire)
- `ForeignKey` vers `PollOption` (obligatoire)

**Champs Clés** :
- `voter_hash` : Hash anonyme du votant (pour éviter doublons)
- `points` : Points attribués (vote quadratique)
- `ranking` : Classement (jugement majoritaire)
- `saka_spent` : SAKA plantés pour ce vote (boost)
- `weight` : Poids calculé (sqrt(intensity) * multiplier SAKA)
- `metadata` : JSON (timestamp, user_id si non anonyme)

**Fonction** :
- `compute_quadratic_weight(intensity, saka_spent)` : Calcule le poids quadratique avec boost SAKA

---

### 3. **Intentions** (`core/models/intents.py`)

#### Modèle `Intent`

**Ce qu'il représente** :
- Une intention d'engagement d'une personne qui souhaite rejoindre le collectif
- Formulaire "Rejoindre" avec profil, message, etc.

**Relations** :
- Aucune relation directe (modèle autonome)

**Champs Clés** :
- `nom`, `email`, `profil` (ex: "je-decouvre", "je-contribue")
- `message` : Message libre
- `ip`, `user_agent` : Traçabilité
- `document_url` : URL du document consulté

**Usage** :
- Panel admin pour filtrer, exporter, gérer les intentions

---

### 4. **SAKA** (`core/models/saka.py`)

#### Modèle `SakaWallet`

**Ce qu'il représente** :
- Portefeuille SAKA d'un utilisateur (monnaie interne d'engagement)

**Relations** :
- `OneToOne` vers `User` (un wallet par utilisateur)
- `OneToMany` vers `SakaTransaction` (historique)

**Champs Clés** :
- `balance` : Solde disponible (grains SAKA)
- `total_harvested` : Total jamais récolté (cumul historique)
- `total_planted` : Total jamais planté (cumul historique)
- `total_composted` : Total jamais composté (cumul historique)
- `last_activity_date` : Date dernière activité SAKA

#### Modèle `SakaTransaction`

**Ce qu'il représente** :
- Transaction SAKA individuelle (historique complet)

**Relations** :
- `ForeignKey` vers `User` (obligatoire)

**Champs Clés** :
- `direction` : EARN (récolte) ou SPEND (dépense)
- `amount` : Nombre de grains
- `reason` : Raison (ex: "content_read", "poll_boost", "project_boost")
- `metadata` : JSON (project_id, poll_id, etc.)
- `created_at` : Timestamp

#### Modèle `SakaSilo`

**Ce qu'il représente** :
- Silo commun où vont les grains compostés (modèle global, un seul en pratique)

**Relations** :
- Aucune relation directe (modèle global)

**Champs Clés** :
- `total_balance` : Solde actuel du Silo (grains compostés disponibles)
- `total_composted` : Total jamais composté (cumul historique)
- `total_cycles` : Nombre de cycles de compostage exécutés
- `last_compost_at` : Date dernier compost

#### Modèle `SakaCycle`

**Ce qu'il représente** :
- Une saison/cycle SAKA (ex: "Saison 2026 - Printemps")
- Permet d'agréger les chiffres SAKA par période

**Relations** :
- `OneToMany` vers `SakaCompostLog` (logs de compostage)

**Champs Clés** :
- `name` : Nom du cycle
- `start_date`, `end_date` : Période du cycle
- `is_active` : Cycle actuellement actif

#### Modèle `SakaCompostLog`

**Ce qu'il représente** :
- Audit log d'un cycle de compostage SAKA

**Relations** :
- `ForeignKey` vers `SakaCycle` (optionnel)

**Champs Clés** :
- `dry_run` : Simulation ou réel
- `wallets_affected` : Nombre de wallets affectés
- `total_composted` : Total composté dans ce cycle
- `inactivity_days`, `rate`, `min_balance`, `min_amount` : Paramètres utilisés
- `source` : Source du déclenchement (celery, admin, management_command)

#### Modèle `SakaProjectSupport`

**Ce qu'il représente** :
- Tracker les supporters uniques d'un projet SAKA (évite doublons)

**Relations** :
- `ForeignKey` vers `User` (obligatoire)
- `ForeignKey` vers `Projet` (obligatoire)
- `unique_together` : (user, project)

**Champs Clés** :
- `total_saka_spent` : Total SAKA dépensé par cet utilisateur pour ce projet
- `first_boost_at`, `last_boost_at` : Dates premier/dernier boost

---

### 5. **Impact** (`core/models/impact.py`)

#### Modèle `ImpactDashboard`

**Ce qu'il représente** :
- Tableau de bord d'impact personnel pour chaque utilisateur (métriques agrégées)

**Relations** :
- `OneToOne` vers `User` (un dashboard par utilisateur)

**Champs Clés** :
- `total_contributions` : Total contributions en euros
- `projects_supported` : Nombre de projets soutenus
- `cagnottes_contributed` : Nombre de cagnottes contribuées
- `intentions_submitted` : Nombre d'intentions soumises

**Méthodes** :
- `update_metrics()` : Recalcule les métriques depuis les modèles réels

#### Modèle `ProjectImpact4P`

**Ce qu'il représente** :
- Scores 4P (Performance Partagée) par projet

**Relations** :
- `OneToOne` vers `Projet` (un score 4P par projet)

**Champs Clés** :
- `financial_score` : P1 - Performance financière (euros mobilisés)
- `saka_score` : P2 - Performance vivante (SAKA mobilisé)
- `social_score` : P3 - Performance sociale/écologique (score d'impact agrégé)
- `purpose_score` : P4 - Purpose / Sens (indicateur qualitatif)

---

### 6. **Financement** (`core/models/fundraising.py`)

#### Modèle `Cagnotte`

**Ce qu'il représente** :
- Une cagnotte de financement pour un projet

**Relations** :
- `ForeignKey` vers `Projet` (optionnel, `null=True`)
- `OneToMany` vers `Contribution` (contributions)

**Champs Clés** :
- `titre`, `description`
- `montant_cible` : Objectif de collecte
- `montant_collecte` : Montant actuellement collecté

#### Modèle `Contribution`

**Ce qu'il représente** :
- Une contribution financière à une cagnotte

**Relations** :
- `ForeignKey` vers `Cagnotte` (obligatoire)
- `ForeignKey` vers `User` (optionnel, `null=True`)

**Champs Clés** :
- `montant` : Montant de la contribution (en euros)

---

## 🔄 Flots Métier Clés

### 1. **Flot "Rejoindre" (Intent)**

**Endpoint** : `POST /api/intents/rejoindre/`

**Flot** :
1. Utilisateur remplit formulaire "Rejoindre" (nom, email, profil, message)
2. Validation payload (honeypot, longueur message, email valide)
3. Création `Intent` avec :
   - `nom`, `email`, `profil`, `message`
   - `ip`, `user_agent` (traçabilité)
   - `document_url` (optionnel)
4. Retour : `{"ok": True, "id": intent.pk}`

**Modèles Créés** :
- `Intent` (nouveau)

**Modèles Mis à Jour** :
- Aucun (modèle autonome)

**Logique Métier** :
- **Localisation** : `core/api/intents.py` (fonction `rejoindre()`)
- **Pas de service** : Logique directement dans la vue
- **Sécurité** : Honeypot anti-spam, validation email, limite longueur message

---

### 2. **Flot "Créer un Projet"**

**Endpoint** : `POST /api/projets/` (via `ProjetListCreate`)

**Flot** :
1. Utilisateur authentifié crée un projet (titre, description, categorie, etc.)
2. Validation via serializer
3. Création `Projet`
4. **Tâches asynchrones** (si Celery disponible) :
   - Scan antivirus de l'image uploadée
   - Génération embedding (recherche sémantique)
5. Invalidation cache `projets_list`
6. Calcul scores 4P (`update_project_4p()`)
7. Retour : Projet créé

**Modèles Créés** :
- `Projet` (nouveau)
- `ProjectImpact4P` (via `update_project_4p()`)

**Modèles Mis à Jour** :
- Aucun (création initiale)

**Logique Métier** :
- **Localisation** : `core/api/projects.py` (`ProjetListCreate.perform_create()`)
- **Service** : `core/services/impact_4p.py` (`update_project_4p()`)
- **Tâches Celery** : `core/tasks_security.py`, `core/tasks_embeddings.py`

---

### 3. **Flot "Voter"**

**Endpoint** : `POST /api/polls/<id>/vote/`

**Flot** :

#### A. Vote Binaire (défaut)
1. Vérification : poll ouvert, dates valides
2. Calcul `voter_hash` (anonyme ou identifié)
3. Suppression anciens votes de cet utilisateur
4. Création `PollBallot` pour chaque option sélectionnée
5. Broadcast WebSocket (mise à jour temps réel)
6. Retour : Résultats du vote

#### B. Vote Quadratique
1. Vérification : poll ouvert, dates valides
2. Validation : total points ≤ max_points (défaut 100)
3. Récupération `intensity` (1-5) depuis payload
4. Calcul coût SAKA : `intensity * SAKA_VOTE_COST_PER_INTENSITY`
5. **Dépense SAKA** (si activé) : `spend_saka(user, saka_cost, "poll_boost")`
6. Calcul poids quadratique : `compute_quadratic_weight(intensity, saka_spent)`
7. Suppression anciens votes
8. Création `PollBallot` avec `points`, `weight`, `saka_spent`
9. Broadcast WebSocket
10. Retour : Résultats avec poids

#### C. Jugement Majoritaire
1. Vérification : poll ouvert, dates valides
2. Suppression anciens votes
3. Création `PollBallot` avec `ranking` pour chaque option
4. Broadcast WebSocket
5. Retour : Résultats avec classements

**Modèles Créés** :
- `PollBallot` (nouveau, un par option votée)

**Modèles Mis à Jour** :
- `SakaWallet` (si vote quadratique avec SAKA) : `balance` ↓, `total_planted` ↑
- `SakaTransaction` (si SAKA dépensé) : Nouvelle transaction SPEND

**Logique Métier** :
- **Localisation** : `core/api/polls.py` (`PollViewSet.vote()`)
- **Service** : `core/services/saka.py` (`spend_saka()`)
- **Fonction** : `core/models/polls.py` (`compute_quadratic_weight()`)

---

### 4. **Flot "SAKA - Récolter"**

**Service** : `harvest_saka(user, reason, amount, metadata)`

**Flot** :
1. Vérification : SAKA activé, utilisateur authentifié
2. Détermination montant (si `amount=None`, utilise `SAKA_BASE_REWARDS[reason]`)
3. Récupération/création `SakaWallet` avec `select_for_update()` (verrouillage)
4. **Anti-farming** : Vérification limite quotidienne par raison
   - Compte transactions EARN pour cette raison aujourd'hui
   - Si `today_count >= daily_limit` : retourne `None` (ignoré)
5. Mise à jour wallet :
   - `balance += amount`
   - `total_harvested += amount`
   - `last_activity_date = now()`
6. Création `SakaTransaction` (EARN)
7. Retour : Transaction créée ou `None`

**Raisons de Récolte** (`SakaReason`) :
- `CONTENT_READ` : Lecture de contenu
- `POLL_VOTE` : Vote dans un sondage
- `INVITE_ACCEPTED` : Invitation acceptée
- `NETWORK_GROWTH` : Croissance du réseau

**Modèles Créés** :
- `SakaTransaction` (EARN)

**Modèles Mis à Jour** :
- `SakaWallet` : `balance` ↑, `total_harvested` ↑, `last_activity_date` ↑

**Logique Métier** :
- **Localisation** : `core/services/saka.py` (`harvest_saka()`)
- **Sécurité** : Transaction atomique, verrouillage wallet, anti-farming quotidien

---

### 5. **Flot "SAKA - Dépenser"**

**Service** : `spend_saka(user, amount, reason, metadata)`

**Flot** :
1. Vérification : SAKA activé, utilisateur authentifié, `amount > 0`
2. Récupération/création `SakaWallet` avec `select_for_update()` (verrouillage)
3. Vérification solde : `if wallet.balance < amount` → retourne `False`
4. Mise à jour wallet avec `F()` expressions (atomique) :
   - `balance = F('balance') - amount`
   - `total_planted = F('total_planted') + amount`
   - `last_activity_date = now()`
5. Création `SakaTransaction` (SPEND)
6. Retour : `True` (succès) ou `False` (échec)

**Raisons de Dépense** :
- `"project_boost"` : Boost d'un projet
- `"poll_boost"` : Boost d'un vote quadratique
- Autres raisons personnalisées

**Modèles Créés** :
- `SakaTransaction` (SPEND)

**Modèles Mis à Jour** :
- `SakaWallet` : `balance` ↓, `total_planted` ↑, `last_activity_date` ↑

**Logique Métier** :
- **Localisation** : `core/services/saka.py` (`spend_saka()`)
- **Sécurité** : Transaction atomique, verrouillage wallet, vérification solde après verrouillage, `F()` expressions pour atomicité

---

### 6. **Flot "Boost Projet SAKA"**

**Endpoint** : `POST /api/projets/<id>/boost/`

**Flot** :
1. Vérification : utilisateur authentifié, projet existe
2. Récupération `amount` depuis payload (défaut : `SAKA_PROJECT_BOOST_COST`)
3. Validation : `amount > 0`
4. **Transaction atomique globale** :
   - Verrouillage projet avec `select_for_update()`
   - **Dépense SAKA** : `spend_saka(user, cost, "project_boost")`
     - Si échec (solde insuffisant) → retourne erreur 400
   - Mise à jour projet avec `F()` expressions :
     - `saka_score = F('saka_score') + cost`
   - Gestion `SakaProjectSupport` :
     - Si nouveau supporter : `saka_supporters_count += 1`
     - Mise à jour `total_saka_spent` pour cet utilisateur
5. Rechargement projet depuis DB
6. **Calcul scores 4P** : `update_project_4p(project)` (en dehors transaction)
7. Invalidation cache `projets_list`
8. Retour : `{"ok": True, "saka_spent": cost, "saka_score": ..., "saka_supporters_count": ...}`

**Modèles Créés** :
- `SakaTransaction` (SPEND, reason="project_boost")
- `SakaProjectSupport` (si nouveau supporter)

**Modèles Mis à Jour** :
- `SakaWallet` : `balance` ↓, `total_planted` ↑
- `Projet` : `saka_score` ↑, `saka_supporters_count` ↑ (si nouveau)
- `SakaProjectSupport` : `total_saka_spent` ↑ (si existant)
- `ProjectImpact4P` : Scores 4P recalculés

**Logique Métier** :
- **Localisation** : `core/api/projects.py` (`boost_project()`)
- **Service** : `core/services/saka.py` (`spend_saka()`), `core/services/impact_4p.py` (`update_project_4p()`)
- **Sécurité** : Transaction atomique globale, verrouillage projet + wallet, `F()` expressions

---

### 7. **Flot "Compost SAKA"**

**Service** : `run_saka_compost_cycle(dry_run=False, ...)`

**Flot** :
1. Récupération paramètres (inactivity_days, rate, min_balance, min_amount)
2. Récupération cycle actif (`SakaCycle` avec `is_active=True`)
3. Filtrage wallets éligibles :
   - `last_activity_date < (now - inactivity_days)`
   - `balance >= min_balance`
4. Pour chaque wallet éligible :
   - Calcul montant à composter : `amount = min(wallet.balance * rate, wallet.balance - min_balance)`
   - Si `amount >= min_amount` :
     - Si `dry_run=False` :
       - Mise à jour wallet : `balance -= amount`, `total_composted += amount`
       - Création `SakaTransaction` (SPEND, reason="compost")
       - Mise à jour `SakaSilo` : `total_balance += amount`, `total_composted += amount`
5. Création `SakaCompostLog` (audit)
6. Retour : Statistiques du cycle

**Modèles Créés** :
- `SakaTransaction` (SPEND, reason="compost", si dry_run=False)
- `SakaCompostLog` (audit)

**Modèles Mis à Jour** :
- `SakaWallet` : `balance` ↓, `total_composted` ↑ (si dry_run=False)
- `SakaSilo` : `total_balance` ↑, `total_composted` ↑, `total_cycles` ↑, `last_compost_at` ↑ (si dry_run=False)

**Logique Métier** :
- **Localisation** : `core/services/saka.py` (`run_saka_compost_cycle()`)
- **Déclenchement** : Tâche Celery périodique ou admin manuel
- **Sécurité** : Transaction atomique, audit complet via `SakaCompostLog`

---

### 8. **Flot "Calcul Scores 4P"**

**Service** : `update_project_4p(project)`

**Flot** :
1. **P1 - Performance financière** :
   - Somme contributions via `Cagnotte` → `Contribution`
   - Somme escrows via `EscrowContract` (si disponible)
2. **P2 - Performance vivante** :
   - Utilise directement `project.saka_score`
3. **P3 - Performance sociale/écologique** :
   - Utilise `project.impact_score` (ou 0 si non défini)
4. **P4 - Purpose / Sens** :
   - Formule : `(saka_supporters_count * 10) + (nombre_cagnottes * 5)`
5. Création/mise à jour `ProjectImpact4P`
6. Retour : Instance `ProjectImpact4P`

**Modèles Créés** :
- `ProjectImpact4P` (si nouveau)

**Modèles Mis à Jour** :
- `ProjectImpact4P` : Tous les scores recalculés

**Logique Métier** :
- **Localisation** : `core/services/impact_4p.py` (`update_project_4p()`)
- **Déclenchement** : Après création projet, après boost SAKA, après contribution

---

## 🏗️ Organisation de la Logique Métier

### Logique dans les Services (`core/services/`)

**Services Identifiés** :
- `saka.py` : Logique SAKA (récolte, dépense, compost, silo)
- `saka_stats.py` : Statistiques SAKA (cycle stats, etc.)
- `impact_4p.py` : Calcul scores 4P
- `concierge.py` : Support concierge (probablement)

**Avantages** :
- Logique réutilisable
- Testable indépendamment
- Séparation des responsabilités

---

### Logique dans les Views (`core/api/`)

**Views avec Logique Métier** :
- `intents.py` : Validation payload, création Intent (pas de service)
- `polls.py` : Gestion votes (appelle `spend_saka()` pour vote quadratique)
- `projects.py` : Boost projet (orchestre `spend_saka()` + `update_project_4p()`)

**Observations** :
- Certaines vues contiennent de la logique métier (ex: `intents.py`)
- D'autres orchestrent des services (ex: `projects.py`, `polls.py`)
- Pas de pattern uniforme : mélange logique dans views et services

---

## 📝 Ce que le Code Raconte comme Histoire Métier

### **EGOEJO est une plateforme de financement participatif avec deux systèmes de valeur parallèles** :

1. **Système Financier (Euros)** :
   - Projets peuvent être financés via **dons** (actif) ou **investissement** (dormant V2.0)
   - Cagnottes collectent des contributions
   - EscrowContracts gèrent les engagements financiers
   - Impact mesuré en euros mobilisés

2. **Système SAKA (Engagement Non Monétaire)** :
   - Monnaie interne d'engagement (grains SAKA)
   - Récolte : Lecture contenu, vote, invitation acceptée, croissance réseau
   - Dépense : Boost projets, boost votes quadratiques
   - Compost : SAKA inactif retourne au Silo commun (cyclique)
   - Impact mesuré en SAKA mobilisé

### **Les Projets sont au Centre** :
- Chaque projet peut recevoir :
  - Financement financier (dons/investissement)
  - Support SAKA (boosts)
  - Sondages pour décisions collectives
- Scores 4P agrègent les 4 dimensions de performance

### **La Gouvernance est Démocratique** :
- Sondages avec méthodes avancées (binaire, quadratique, jugement majoritaire)
- Votes peuvent être boostés avec SAKA (vote quadratique fertilisé)
- Votes peuvent être réservés aux actionnaires (V2.0 dormant)

### **Le Temps est Cyclique (SAKA)** :
- Cycles SAKA (saisons) agrègent les chiffres par période
- Compostage périodique : SAKA inactif retourne au Silo commun
- Le Silo commun peut être redistribué (mécanisme non implémenté visiblement)

### **L'Impact est Mesuré Multi-Dimensionnellement** :
- **P1** : Performance financière (euros)
- **P2** : Performance vivante (SAKA)
- **P3** : Performance sociale/écologique (impact_score)
- **P4** : Purpose / Sens (cohérence : supporters + cagnottes)

---

## 🎯 Donc, sans lire les docs, voilà comment je comprends EGOEJO d'après le code :

**EGOEJO est un collectif qui finance des projets sociaux/écologiques via deux systèmes complémentaires** :

1. **L'Euro (Yang)** : Financement classique (dons, investissement futur)
2. **Le SAKA (Yin)** : Monnaie d'engagement non monétaire (récolte → plante → composte)

**Les utilisateurs** :
- Rejoignent via formulaire "Intent"
- Financent des projets (euros)
- Engagent leur temps/attention (SAKA)
- Votent pour décisions collectives (avec boost SAKA possible)

**Les projets** :
- Sont financés (euros + SAKA)
- Ont des scores 4P (4 dimensions de performance)
- Peuvent avoir des sondages pour décisions
- Sont visualisables dans un espace 3D ("Mycélium Numérique")

**Le système SAKA** :
- Récompense l'engagement (lecture, vote, réseau)
- Permet de booster projets/votes
- Composte périodiquement (SAKA inactif → Silo commun)
- Suit des cycles (saisons) pour agrégation temporelle

**La gouvernance** :
- Démocratique (sondages avec méthodes avancées)
- Peut être boostée avec SAKA (vote quadratique fertilisé)
- Peut être réservée aux actionnaires (V2.0 dormant)

**L'impact** :
- Mesuré en 4 dimensions (4P)
- Agrégé par utilisateur (ImpactDashboard)
- Agrégé par projet (ProjectImpact4P)

---

**Dernière mise à jour** : 2025-12-16


# Tests Backend - EGOEJO

**Stack** : Django 5, Django REST Framework (DRF), pytest, Celery, Redis  
**Date de mise à jour** : 2025-01-16

---

## 🚀 Comment lancer les tests

### Commandes de base

```bash
# Depuis le répertoire backend/
cd backend

# Lancer tous les tests
python -m pytest

# Lancer avec verbosité
python -m pytest -vv

# Lancer un fichier spécifique
python -m pytest core/tests_saka.py -vv

# Lancer une classe de tests spécifique
python -m pytest core/tests_saka.py::SakaWalletTestCase -vv

# Lancer un test spécifique
python -m pytest core/tests_saka.py::SakaWalletTestCase::test_wallet_auto_creation -vv

# Lancer avec couverture de code
python -m pytest --cov=core --cov-report=html

# Lancer les tests en mode watch (nécessite pytest-watch)
pytest-watch
```

### Options utiles

```bash
# Afficher les print() dans les tests
python -m pytest -s

# Arrêter au premier échec
python -m pytest -x

# Afficher les tests les plus lents
python -m pytest --durations=10

# Filtrer par mot-clé
python -m pytest -k "saka" -vv

# Ignorer les warnings
python -m pytest --disable-warnings
```

### Configuration

Le fichier `pytest.ini` configure :
- `DJANGO_SETTINGS_MODULE = config.settings`
- Couverture de code pour le module `core`
- Rapports HTML dans `htmlcov/`
- Format de traceback court (`--tb=short`)

---

## 📦 Grands blocs de tests

### 1. Authentification (`core/tests_auth.py`, `core/tests_auth_api.py`)

**Fichiers** :
- `core/tests_auth.py` (15 tests) - Tests unitaires de l'authentification
- `core/tests_auth_api.py` (12 tests) - Tests API pour login/register/refresh

**Couverture** :
- ✅ Création de compte (register)
- ✅ Connexion (login)
- ✅ Refresh token
- ✅ Rotation des tokens
- ✅ Validation des champs (email, password)
- ✅ Gestion des erreurs (duplicate username/email, invalid credentials)
- ✅ Blacklist des tokens

**Exemples de tests** :
- `test_register_success` : Création de compte réussie
- `test_login_success` : Connexion réussie avec tokens
- `test_refresh_token_success` : Renouvellement de token
- `test_refresh_token_rotation` : Rotation et blacklist

---

### 2. SAKA (`core/tests_saka.py`)

**Fichier** : `core/tests_saka.py` (27 tests)

**Couverture** :
- ✅ Création automatique des wallets SAKA
- ✅ Récolte SAKA (content_read, vote, etc.)
- ✅ Dépense SAKA (vote quadratique, boost projet)
- ✅ Vote quadratique avec SAKA
- ✅ Boost de projets avec SAKA
- ✅ Intégration dans global-assets
- ✅ **Tests de concurrence** (race conditions, double spending)
- ✅ Cycles SAKA et statistiques

**Tests critiques de concurrence** :
- `SakaRaceConditionTestCase` : Conditions de course sur les wallets
- `SakaConcurrencyTestCase` : Tests de concurrence avec `TransactionTestCase` et `threading.Thread`
  - Simule deux appels simultanés de "boost" sur le même wallet
  - Vérifie que le solde ne devient jamais négatif
  - Vérifie la cohérence des transactions

**Exemples de tests** :
- `test_wallet_auto_creation` : Création automatique du wallet à la première activité
- `test_harvest_content_read` : Récolte SAKA lors de la lecture de contenu
- `test_spend_vote_quadratic` : Dépense SAKA pour un vote quadratique
- `test_boost_project_success` : Boost d'un projet avec SAKA
- `test_concurrent_boosts` : Tests de concurrence pour éviter le double spending

---

### 3. SAKA - Compostage & Silo (`core/tests_saka_celery.py`, `core/tests_saka_redistribution.py`)

**Fichiers** :
- `core/tests_saka_celery.py` (6 tests) - Tests d'intégration Celery pour le compostage
- `core/tests_saka_redistribution.py` (8 tests) - Tests de redistribution du Silo
- `core/tests_saka_celery_redistribution.py` (3 tests) - Tests Celery de redistribution

**Couverture** :
- ✅ Compostage des wallets inactifs vers le Silo Commun
- ✅ Tâche Celery `saka_run_compost_cycle`
- ✅ Redistribution du Silo vers les wallets actifs
- ✅ Tâche Celery `saka_silo_redistribution_task`
- ✅ Idempotence des cycles de compostage
- ✅ Association aux cycles SAKA (SakaCycle)

**Tests critiques** :
- `test_compost_cycle_moves_inactive_saka_to_silo` : Déplacement des SAKA inactifs vers le Silo
- `test_compost_cycle_is_idempotent_for_same_cycle` : Vérification de l'idempotence
- `test_celery_task_triggers_compost_service` : Vérification que la tâche Celery appelle le service

**Configuration** :
- Utilise `CELERY_TASK_ALWAYS_EAGER=True` pour exécuter les tâches immédiatement en tests
- Mock des services si nécessaire

---

### 4. Finance & Escrow (`finance/tests_finance.py`, `finance/tests_finance_escrow.py`)

**Fichiers** :
- `finance/tests_finance.py` (tests existants) - Tests des services financiers
- `finance/tests_finance_escrow.py` (8 tests) - Tests d'intégrité financière

**Couverture** :
- ✅ Création d'escrow via `pledge_funds`
- ✅ Libération d'escrow (`release_escrow`)
- ✅ Remboursement d'escrow (`refund_escrow`)
- ✅ **Intégrité financière** : vérification que l'argent n'est ni créé ni détruit
- ✅ Idempotence de `release_escrow`
- ✅ Calcul des commissions et frais
- ✅ Transactions wallet (PLEDGE, RELEASE, REFUND, COMMISSION)

**Tests critiques** :
- `test_pledge_funds_creates_escrow_and_transaction` : Création d'escrow et transaction
- `test_release_escrow_moves_funds_to_commission_wallet` : Libération vers wallet système
- `test_release_escrow_idempotent` : Vérification de l'idempotence
- `test_no_money_created_or_destroyed` : **Intégrité financière globale**
- `test_multiple_escrows_same_project` : Plusieurs escrows sur le même projet

**Note importante** : Les tests utilisent un mock pour le wallet système (car le service essaie de créer avec `user=None` mais le modèle nécessite un user).

---

### 5. Intentions (`core/tests.py` - `IntentTestCase`)

**Fichier** : `core/tests.py`

**Couverture** :
- ✅ Création d'intentions (rejoindre, contribuer, etc.)
- ✅ Gestion admin des intentions
- ✅ Export des intentions
- ✅ Suppression d'intentions

---

### 6. Projets & Impact 4P (`core/tests.py` - `ProjetCagnotteTestCase`, `ProjectImpact4PTestCase`)

**Fichier** : `core/tests.py`

**Couverture** :
- ✅ Création de projets et cagnottes
- ✅ Calcul des scores 4P (P1 financier, P2 SAKA, P3 social, P4 sens)
- ✅ Service `update_project_4p`
- ✅ Exposition API des scores 4P

**Note** : Les scores P3 et P4 sont des **proxies V1 internes** (non académiques), documentés dans le code.

---

### 7. Content & Engagement (`core/tests_content.py`, `core/tests_engagement.py`)

**Fichiers** :
- `core/tests_content.py` (tests existants)
- `core/tests_engagement.py` (tests existants)

**Couverture** :
- ✅ Création et gestion de contenu éducatif
- ✅ Engagements (offres d'aide)
- ✅ API endpoints

---

### 8. Communities (`core/tests_communities.py`)

**Fichier** : `core/tests_communities.py` (tests existants)

**Couverture** :
- ✅ Création de communautés
- ✅ Association de projets aux communautés
- ✅ API read-only des communautés

---

### 9. SAKA Public (`core/tests_saka_public.py`)

**Fichier** : `core/tests_saka_public.py` (5 tests)

**Couverture** :
- ✅ Endpoints publics SAKA (`/api/saka/cycles/`, `/api/saka/silo/`)
- ✅ Authentification requise
- ✅ Structure des réponses JSON

---

## 🔒 Tests critiques de sécurité et intégrité

### Tests de concurrence SAKA

**Fichier** : `core/tests_saka.py` - `SakaConcurrencyTestCase`

**Objectif** : Prévenir le double spending et les conditions de course.

**Technique** :
- Utilise `TransactionTestCase` pour isoler les transactions
- Simule deux threads simultanés avec `threading.Thread`
- Vérifie que le solde final est cohérent
- Vérifie qu'aucun solde négatif n'est créé

**Exemple** :
```python
def test_concurrent_boosts(self):
    # Simule deux boosts simultanés sur le même wallet
    # Vérifie que le solde final = solde initial - (2 * coût)
    # Vérifie qu'aucun solde négatif n'est créé
```

### Tests d'intégrité financière

**Fichier** : `finance/tests_finance_escrow.py` - `TestEscrowFinancialIntegrity`

**Objectif** : S'assurer que l'argent n'est ni créé ni détruit.

**Vérifications** :
- `test_no_money_created_or_destroyed` : Vérifie que wallet + escrow = constant
- Vérifie que commission + fees + net = amount (arrondis près)
- Vérifie la cohérence des soldes avant/après chaque opération

### Tests de compostage SAKA

**Fichier** : `core/tests_saka_celery.py`

**Objectif** : Vérifier que le compostage fonctionne correctement et est idempotent.

**Vérifications** :
- Les wallets inactifs sont compostés vers le Silo
- Les wallets actifs ne sont pas touchés
- Le même SAKA n'est pas composté deux fois
- Le Silo ne double pas le montant

---

## 📋 Règles et bonnes pratiques

### Règles strictes

1. **Ne jamais modifier la logique métier depuis les tests**
   - Les tests doivent révéler des bugs, pas les masquer
   - Si un test échoue, corriger le bug dans le code métier, pas dans le test

2. **Tests rapides et isolés**
   - Chaque test doit être indépendant
   - Utiliser `pytest.mark.django_db` pour l'accès à la base de données
   - Utiliser `TransactionTestCase` uniquement pour les tests de concurrence

3. **Utiliser les services existants**
   - Ne pas réécrire la logique dans les tests
   - Appeler les services (`pledge_funds`, `release_escrow`, `run_saka_compost_cycle`, etc.)

4. **Mocking approprié**
   - Mocker les dépendances externes (Stripe, APIs tierces)
   - Ne pas mocker les services internes sauf si nécessaire (ex: wallet système)

### Fixtures et helpers

**Fixtures pytest** :
- `test_user` : Utilisateur de test
- `test_project` : Projet de test
- `funded_wallet` : Wallet avec des fonds

**Helpers** :
- Utiliser `APIClient` pour les tests API
- Utiliser `override_settings` pour désactiver le throttling en tests

---

## 🎯 Couverture actuelle

### Modules bien couverts

- ✅ **SAKA** : Wallets, récolte, dépense, compostage, redistribution, cycles
- ✅ **Auth** : Login, register, refresh token, rotation
- ✅ **Finance/Escrow** : Pledge, release, refund, intégrité financière
- ✅ **Impact 4P** : Calcul et exposition des scores

### Modules partiellement couverts

- 🟡 **Content** : Tests basiques, manque tests API complets
- 🟡 **Engagement** : Tests basiques, manque tests API complets
- 🟡 **Communities** : Tests basiques, manque tests API complets

### Modules non couverts

- ❌ **Help Requests** : Pas de tests API
- ❌ **Monitoring** : Pas de tests
- ❌ **Search/Semantic Search** : Pas de tests
- ❌ **Chat/Concierge** : Pas de tests
- ❌ **Investment (V2.0)** : Tests basiques uniquement

---

## 📝 Plan de complétion

Voir `docs/tests/AUDIT_TESTS_BACKEND_2025-12-16.md` pour le plan détaillé.

**Priorités** :
- P0 (critique) : Auth ✅, Finance/Escrow ✅, SAKA compost ✅, Security errors
- P1 : Content/Engagement API, Monitoring, Mycelium, Search
- P2 : Investment (V2.0), secondary APIs

---

## 🔧 Dépannage

### Erreurs courantes

**`IntegrityError: NOT NULL constraint failed`** :
- Vérifier que tous les champs requis sont fournis
- Pour les wallets système, utiliser un mock ou créer un user système

**`TransactionTestCase` trop lent** :
- Utiliser `TestCase` sauf pour les tests de concurrence
- `TransactionTestCase` isole chaque test dans une transaction, plus lent

**Tests flaky (parfois passent, parfois échouent)** :
- Vérifier les conditions de course
- Utiliser `select_for_update()` dans le code métier
- Ajouter des `wait_for` dans les tests E2E

**Rate limiting (429) dans les tests** :
- Utiliser `@override_settings` pour désactiver le throttling :
```python
@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {},
    }
)
```

---

## 📚 Ressources

- **Documentation pytest-django** : https://pytest-django.readthedocs.io/
- **Documentation Django Testing** : https://docs.djangoproject.com/en/5.0/topics/testing/
- **Audit complet** : `docs/tests/AUDIT_TESTS_BACKEND_2025-12-16.md`


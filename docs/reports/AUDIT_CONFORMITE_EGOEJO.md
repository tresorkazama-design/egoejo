# 🔍 Audit de Conformité EGOEJO

**Date** : 2025-12-17  
**Rôle** : Gardien de cohérence du Manifeste EGOEJO  
**Objectif** : Vérifier que le code existant respecte les principes fondateurs

---

## 🔁 CYCLE & SAKA

### [✅] Le SAKA ne peut pas être accumulé indéfiniment sans conséquence

**Statut** : **OUI** ✅

**Fichiers concernés** :
- `backend/core/services/saka.py` : `run_saka_compost_cycle()` (lignes 299-437)
- `backend/core/tests_saka_philosophy.py` : Tests philosophiques (lignes 86-311)
- `backend/core/tests_saka_celery.py` : Tests d'intégration Celery (lignes 93-476)

**Mécanisme** :
- Compostage progressif (10% par cycle) après 90 jours d'inactivité
- Service `run_saka_compost_cycle()` avec `select_for_update()` pour atomicité
- Tests philosophiques qui vérifient que l'accumulation infinie est impossible

**Test existant** :
```python
# backend/core/tests_saka_philosophy.py
def test_compostage_progressif_empêche_thésaurisation_infinie(self):
    """PHILOSOPHIE : L'impossibilité de thésaurisation."""
    # Vérifie que même avec 10000 SAKA, le compostage progressif empêche l'accumulation infinie
```

**Test manquant** : ❌ **Aucun test manquant** - Les tests philosophiques couvrent ce point.

---

### [✅] Le compostage est effectif (tâche asynchrone, testée)

**Statut** : **OUI** ✅

**Fichiers concernés** :
- `backend/core/tasks.py` : `saka_run_compost_cycle()` (lignes 104-128)
- `backend/config/celery.py` : Configuration Celery Beat (lignes 36-49)
- `backend/core/tests_saka_celery.py` : Tests d'intégration (lignes 28-476)

**Mécanisme** :
- Tâche Celery `saka_run_compost_cycle` configurée dans Celery Beat (lundi 3h UTC)
- Service `run_saka_compost_cycle()` avec mode dry-run et logging complet
- Tests d'intégration avec `CELERY_TASK_ALWAYS_EAGER=True`

**Test existant** :
```python
# backend/core/tests_saka_celery.py
def test_compost_cycle_moves_inactive_saka_to_silo(self):
    """Test que le compostage déplace les SAKA inactifs vers le Silo."""
    # Vérifie que le compostage fonctionne via Celery
```

**Test manquant** : ❌ **Aucun test manquant** - Les tests Celery couvrent ce point.

---

### [✅] Le Silo reçoit effectivement la valeur compostée

**Statut** : **OUI** ✅

**Fichiers concernés** :
- `backend/core/services/saka.py` : `run_saka_compost_cycle()` (lignes 404-418)
- `backend/core/tests_saka_philosophy.py` : `test_collectif_bénéficie_de_inutilisation_individuelle()` (lignes 315-372)
- `backend/core/tests_saka_celery.py` : `test_compost_cycle_moves_inactive_saka_to_silo()` (lignes 93-178)

**Mécanisme** :
- Le service `run_saka_compost_cycle()` met à jour `silo.total_balance` et `silo.total_composted`
- Transactions atomiques avec `select_for_update()` sur le Silo
- Tests philosophiques qui vérifient que le Silo bénéficie du compostage

**Test existant** :
```python
# backend/core/tests_saka_philosophy.py
def test_collectif_bénéficie_de_inutilisation_individuelle(self):
    """PHILOSOPHIE : Le collectif bénéficie de l'inutilisation individuelle."""
    # Vérifie que le Silo reçoit le SAKA composté
```

**Test manquant** : ❌ **Aucun test manquant** - Les tests philosophiques couvrent ce point.

---

### [✅] Une redistribution existe ou est planifiée (même simple)

**Statut** : **OUI** ✅

**Fichiers concernés** :
- `backend/core/services/saka.py` : `redistribute_saka_silo()` (lignes 495-634)
- `backend/core/tasks.py` : `run_saka_silo_redistribution()` (lignes 183-220)
- `backend/config/celery.py` : Configuration Celery Beat (lignes 43-48)
- `backend/core/tests_saka_redistribution.py` : Tests de redistribution (lignes 22-350)
- `backend/core/tests_saka_philosophy.py` : Tests philosophiques (lignes 387-503)

**Mécanisme** :
- Service `redistribute_saka_silo()` qui redistribue équitablement le Silo aux wallets actifs
- Tâche Celery Beat configurée (1er du mois à 4h UTC) mais désactivée par défaut
- Redistribution équitable (même montant pour tous les wallets actifs)

**Test existant** :
```python
# backend/core/tests_saka_philosophy.py
def test_redistribution_du_silo_vers_collectif(self):
    """PHILOSOPHIE : Le Silo Commun est redistribué au collectif."""
    # Vérifie que la redistribution fonctionne
```

**Test manquant** : ❌ **Aucun test manquant** - Les tests de redistribution couvrent ce point.

---

### 👉 Test attendu : test Celery ou service prouvant qu'un solde inactif diminue

**Statut** : **OUI** ✅ **Test existant**

**Fichier** :
- `backend/core/tests_saka_philosophy.py` : `test_impossibilité_de_thésaurisation_à_long_terme()` (lignes 657-687)

**Assertion** :
```python
# Simule plusieurs cycles de compostage
# Assertion : Le compostage progressif DOIT réduire significativement le solde
reduction_percent = ((balance_initial - wallet.balance) / balance_initial) * 100
self.assertGreater(reduction_percent, 50)  # Au moins 50% de réduction
```

**Test manquant** : ❌ **Aucun test manquant** - Le test philosophique couvre ce point.

---

## 🏦 FINANCE

### [✅] Les flux financiers sont atomiques et testés

**Statut** : **OUI** ✅

**Fichiers concernés** :
- `backend/finance/services.py` : `pledge_funds()` (lignes 13-127), `release_escrow()` (lignes 129-267)
- `backend/finance/tests_finance.py` : Tests des services financiers (lignes 20-450)
- `backend/core/tests_auth.py` : Tests d'authentification (lignes 1-348)

**Mécanisme** :
- Toutes les opérations financières utilisent `@transaction.atomic`
- `select_for_update()` sur les wallets pour éviter les race conditions
- Tests de concurrence et d'atomicité

**Test existant** :
```python
# backend/finance/tests_finance.py
def test_create_escrow_contract_via_pledge_funds(self):
    """Test la création d'un contrat Escrow via pledge_funds (service)"""
    # Vérifie l'atomicité de la transaction
```

**Test manquant** : ❌ **Aucun test manquant** - Les tests financiers couvrent ce point.

---

### [✅] Aucun mouvement d'argent ne peut se produire sans trace

**Statut** : **OUI** ✅

**Fichiers concernés** :
- `backend/finance/models.py` : `WalletTransaction` (lignes 39-93)
- `backend/finance/services.py` : `pledge_funds()`, `release_escrow()` (créent toujours des transactions)
- `backend/finance/tests_finance.py` : Tests de traçabilité (lignes 41-72)

**Mécanisme** :
- Chaque opération financière crée une `WalletTransaction` avec type, montant, projet, utilisateur
- `idempotency_key` pour éviter les doublons
- Journal complet avec timestamps

**Test existant** :
```python
# backend/finance/tests_finance.py
def test_create_escrow_contract_via_pledge_funds(self):
    """Vérifie qu'une WalletTransaction a été créée"""
    self.assertIsNotNone(escrow.pledge_transaction)
```

**Test manquant** : ❌ **Aucun test manquant** - Les tests financiers couvrent ce point.

---

### [⚠️] Les scénarios d'échec (double appel, rollback) sont testés

**Statut** : **PARTIELLEMENT** ⚠️

**Fichiers concernés** :
- `backend/finance/services.py` : `pledge_funds()` avec `idempotency_key` (lignes 36-39)
- `backend/finance/tests_finance.py` : `test_pledge_funds_idempotency()` (lignes 93-121)

**Mécanisme** :
- Idempotence : `idempotency_key` empêche les doubles appels
- Tests d'idempotence existants

**Test existant** :
```python
# backend/finance/tests_finance.py
def test_pledge_funds_idempotency(self):
    """Test que pledge_funds respecte l'idempotency_key"""
    # Vérifie que le deuxième appel avec la même clé échoue
```

**Test manquant** : ⚠️ **Test de rollback partiel manquant**

**Test à ajouter** :
```python
# backend/finance/tests_finance.py
def test_pledge_funds_rollback_on_exception(self):
    """
    Test qu'une exception au milieu d'une transaction provoque un rollback complet.
    Vérifie que le wallet n'est pas débité si la transaction échoue.
    """
    # Simuler une exception après le débit du wallet
    # Assertion : Le wallet DOIT être restauré (rollback)
    # Assertion : Aucune WalletTransaction ne DOIT être créée
```

---

### 👉 Test attendu : test d'idempotence

**Statut** : **OUI** ✅ **Test existant**

**Fichier** :
- `backend/finance/tests_finance.py` : `test_pledge_funds_idempotency()` (lignes 93-121)
- `backend/finance/tests_finance_escrow.py` : `test_release_escrow_idempotent()` (lignes 198-220)

**Test manquant** : ❌ **Aucun test manquant** - Les tests d'idempotence existent.

---

### 👉 Test attendu : test d'échec partiel (exception au milieu d'une transaction)

**Statut** : **NON** ❌ **Test manquant**

**Fichier à créer** :
- `backend/finance/tests_finance.py` : Nouveau test `test_pledge_funds_rollback_on_exception()`

**Test à ajouter** :
```python
def test_pledge_funds_rollback_on_exception(self):
    """
    Test qu'une exception au milieu d'une transaction provoque un rollback complet.
    
    Scénario :
    1. Créer un wallet avec 1000€
    2. Simuler une exception après le débit du wallet mais avant la création de l'EscrowContract
    3. Vérifier que le wallet est restauré (rollback)
    4. Vérifier qu'aucune WalletTransaction n'a été créée
    5. Vérifier qu'aucun EscrowContract n'a été créé
    """
    # Mock pour simuler une exception
    # Assertion : Le wallet DOIT être restauré (balance = 1000€)
    # Assertion : Aucune transaction ne DOIT exister
```

---

## 🌱 IMPACT 4P

### [✅] P1 et P2 reposent sur des données réelles

**Statut** : **OUI** ✅

**Fichiers concernés** :
- `backend/core/services/impact_4p.py` : `update_project_4p()` (lignes 31-132)
- `backend/core/models/impact.py` : `ProjectImpact4P` (lignes 71-136)

**Mécanisme** :
- **P1 (financial_score)** : Agrégation réelle des contributions (`Contribution.montant`) et escrows (`EscrowContract.amount`)
- **P2 (saka_score)** : Utilise directement `project.saka_score` qui est calculé à partir des boosts SAKA réels

**Code** :
```python
# backend/core/services/impact_4p.py (lignes 58-82)
# P1 : Somme des contributions + escrows pour ce projet (en euros)
financial_score = sum(Decimal(str(c.montant)) for c in contributions)
financial_score += sum(Decimal(str(escrow.amount)) for escrow in escrows)

# P2 : Score SAKA du projet (déjà calculé)
saka_score = project.saka_score or 0
```

**Test existant** : ⚠️ **Tests partiels** - Tests dans `backend/core/tests.py` mais pas de test dédié 4P

**Test manquant** : ⚠️ **Test de cohérence API manquant**

**Test à ajouter** :
```python
# backend/core/tests_impact_4p.py (à créer)
def test_p1_p2_based_on_real_data(self):
    """
    Test que P1 et P2 reposent sur des données réelles.
    
    Scénario :
    1. Créer un projet
    2. Créer des contributions réelles (100€)
    3. Créer des escrows réels (200€)
    4. Booster le projet avec SAKA (50 grains)
    5. Appeler update_project_4p()
    6. Vérifier que P1 = 300€ (100 + 200)
    7. Vérifier que P2 = 50 (SAKA réellement mobilisé)
    """
    # Assertion : P1 DOIT être la somme réelle des contributions + escrows
    # Assertion : P2 DOIT être le SAKA réellement mobilisé
```

---

### [✅] P3 et P4 sont soit justifiés, soit explicitement déclaratifs

**Statut** : **OUI** ✅

**Fichiers concernés** :
- `backend/core/services/impact_4p.py` : `update_project_4p()` (lignes 84-97)
- `backend/core/models/impact.py` : `ProjectImpact4P` (lignes 110-117)
- `frontend/frontend/src/components/FourPStrip.tsx` : Labels "Signal social (V1 interne)" et "Signal de sens (V1 interne)"

**Mécanisme** :
- **P3 (social_score)** : PROXY V1 INTERNE - Utilise `project.impact_score` (ou 0)
- **P4 (purpose_score)** : PROXY V1 INTERNE - Formule simplifiée `(supporters_count * 10) + (cagnottes * 5)`
- Docstrings explicites dans le code : "PROXY V1 INTERNE", "non académique", "sera affiné"
- Frontend : Labels "Signal social (V1 interne)" et "Signal de sens (V1 interne)" avec tooltips

**Code** :
```python
# backend/core/services/impact_4p.py (lignes 84-97)
# P3 : PROXY V1 INTERNE : Utilise impact_score du projet (ou 0)
# ⚠️ ATTENTION : Ce score est un indicateur interne simplifié, non académique.
social_score = project.impact_score or 0

# P4 : PROXY V1 INTERNE : Score basé sur la cohérence
# ⚠️ ATTENTION : Ce score est un indicateur interne simplifié, non académique.
purpose_score = (project.saka_supporters_count * 10) + (cagnottes.count() * 5)
```

**Test existant** : ⚠️ **Tests partiels** - Pas de test dédié pour vérifier que P3/P4 sont explicitement déclaratifs

**Test manquant** : ⚠️ **Test de cohérence API manquant**

**Test à ajouter** :
```python
# backend/core/tests_impact_4p.py (à créer)
def test_p3_p4_explicitly_declarative(self):
    """
    Test que P3 et P4 sont explicitement déclaratifs (proxy V1 interne).
    
    Scénario :
    1. Créer un projet avec impact_score = 50
    2. Créer 3 supporters SAKA et 2 cagnottes
    3. Appeler update_project_4p()
    4. Vérifier que P3 = 50 (impact_score, proxy V1)
    5. Vérifier que P4 = 40 (3*10 + 2*5, proxy V1)
    6. Vérifier que l'API retourne un champ "p3_social_proxy" et "p4_purpose_proxy"
    """
    # Assertion : P3 DOIT être explicitement marqué comme "proxy V1 interne"
    # Assertion : P4 DOIT être explicitement marqué comme "proxy V1 interne"
    # Assertion : L'API DOIT retourner des métadonnées indiquant le statut proxy
```

---

### [✅] Aucun score n'est présenté comme "scientifique" sans source

**Statut** : **OUI** ✅

**Fichiers concernés** :
- `backend/core/services/impact_4p.py` : Docstrings explicites (lignes 11-19, 43-48)
- `backend/core/models/impact.py` : Docstrings dans `ProjectImpact4P` (lignes 82-90)
- `frontend/frontend/src/components/FourPStrip.tsx` : Labels "Signal social (V1 interne)" et tooltips
- `frontend/frontend/src/components/dashboard/UserImpact4P.jsx` : Labels et tooltips
- `frontend/frontend/src/components/projects/Impact4PCard.jsx` : Labels et tooltips

**Mécanisme** :
- P3/P4 sont explicitement marqués comme "PROXY V1 INTERNE" dans le code
- Frontend : Labels "Signal social (V1 interne)" et "Signal de sens (V1 interne)" avec tooltips explicatifs
- Docstrings : "non académique", "sera affiné dans les versions futures"

**Test existant** : ⚠️ **Tests partiels** - Pas de test frontend pour vérifier les tooltips

**Test manquant** : ⚠️ **Test frontend manquant**

**Test à ajouter** :
```typescript
// frontend/frontend/src/components/__tests__/FourPStrip.test.jsx (à compléter)
it('affiche des tooltips pour P3 et P4 indiquant leur statut proxy', () => {
  // Vérifier que les tooltips contiennent "V1 interne" ou "proxy"
  // Vérifier que P1 et P2 n'ont PAS de tooltip "proxy"
});
```

---

### 👉 Test attendu : test de cohérence API (valeurs expliquées / documentées)

**Statut** : **PARTIELLEMENT** ⚠️

**Fichiers concernés** :
- `backend/core/api/projects.py` : Endpoints de projets (doivent inclure `impact_4p`)
- `backend/core/services/impact_4p.py` : Service de calcul 4P

**Test manquant** : ⚠️ **Test API manquant**

**Test à ajouter** :
```python
# backend/core/tests_impact_4p.py (à créer)
def test_api_returns_4p_with_metadata(self):
    """
    Test que l'API retourne les scores 4P avec métadonnées explicatives.
    
    Scénario :
    1. Créer un projet avec impact 4P calculé
    2. Appeler GET /api/projets/<id>/
    3. Vérifier que la réponse contient un bloc "impact_4p" avec :
       - p1_financier (valeur réelle)
       - p2_saka (valeur réelle)
       - p3_social (valeur proxy, marquée comme "proxy V1 interne")
       - p4_sens (valeur proxy, marquée comme "proxy V1 interne")
       - Métadonnées : "p3_social_proxy": true, "p4_purpose_proxy": true
    """
    # Assertion : L'API DOIT retourner des métadonnées indiquant le statut proxy
```

---

### 👉 Test attendu : snapshot frontend avec disclaimer si nécessaire

**Statut** : **PARTIELLEMENT** ⚠️

**Fichiers concernés** :
- `frontend/frontend/src/components/FourPStrip.tsx` : Composant 4P
- `frontend/frontend/src/components/dashboard/UserImpact4P.jsx` : Composant utilisateur
- `frontend/frontend/src/components/projects/Impact4PCard.jsx` : Composant projet

**Test manquant** : ⚠️ **Snapshot test manquant**

**Test à ajouter** :
```typescript
// frontend/frontend/src/components/__tests__/FourPStrip.test.jsx (à compléter)
it('affiche des disclaimers pour P3 et P4', () => {
  const { container } = render(
    <FourPStrip financial={100} saka={50} impact={{ p3_social: 30, p4_sens: 20 }} />
  );
  
  // Snapshot pour vérifier que les tooltips "V1 interne" sont présents
  expect(container).toMatchSnapshot();
  
  // Assertion : Les tooltips DOIVENT contenir "V1 interne" ou "proxy"
});
```

---

## 👥 COMMUNAUTÉ & SUBSIDIARITÉ

### [✅] Les décisions peuvent être locales (community, project)

**Statut** : **OUI** ✅ (Structure préparée, fonctionnalité V1 minimale)

**Fichiers concernés** :
- `backend/core/models/communities.py` : Modèle `Community` (lignes 10-70)
- `backend/core/models/projects.py` : `Projet.community` (ForeignKey, lignes 73-80)
- `backend/core/api/communities_views.py` : Endpoints read-only (lignes 13-109)

**Mécanisme** :
- Modèle `Community` avec `members` (ManyToMany) et `projects` (via ForeignKey)
- Projets peuvent être associés à une communauté (`Projet.community`)
- API read-only pour lister et consulter les communautés

**Limitation V1** :
- Pas de votes par communauté (encore)
- Pas de budgets par communauté (encore)
- Structure minimale pour préparer la subsidiarité

**Test existant** :
```python
# backend/core/tests_communities.py
def test_project_community_association(self):
    """Test l'association d'un projet à une communauté"""
    # Vérifie que les projets peuvent être associés à une communauté
```

**Test manquant** : ⚠️ **Test de périmètre décisionnel manquant**

**Test à ajouter** :
```python
# backend/core/tests_communities.py (à compléter)
def test_community_can_make_local_decisions(self):
    """
    Test que les décisions peuvent être prises au niveau communautaire.
    
    Scénario V1 (structure préparée) :
    1. Créer une communauté avec des membres
    2. Créer un projet associé à cette communauté
    3. Vérifier que les membres de la communauté peuvent accéder au projet
    4. (V2) Vérifier que les votes peuvent être contextualisés par communauté
    
    Note : V1 prépare la structure, V2 implémentera les décisions locales
    """
    # Assertion : Les projets DOIVENT pouvoir être associés à une communauté
    # Assertion : Les membres DOIVENT pouvoir accéder aux projets de leur communauté
```

---

### [⚠️] Le global n'écrase pas les dynamiques locales

**Statut** : **PARTIELLEMENT** ⚠️ (Structure préparée, pas de mécanisme de protection)

**Fichiers concernés** :
- `backend/core/models/communities.py` : Modèle `Community`
- `backend/core/models/polls.py` : Modèle `Poll` (pas de lien avec `Community` encore)

**Mécanisme actuel** :
- Les communautés existent mais n'ont pas encore de mécanisme de gouvernance locale
- Les votes sont globaux (pas de votes par communauté)
- Structure préparée mais pas de protection contre l'écrasement global

**Test manquant** : ⚠️ **Test de protection manquant**

**Test à ajouter** :
```python
# backend/core/tests_communities.py (à créer pour V2)
def test_global_does_not_override_local_decisions(self):
    """
    Test que les décisions globales n'écrasent pas les décisions locales.
    
    Scénario V2 (à implémenter) :
    1. Créer une communauté avec un vote local
    2. Créer un vote global qui pourrait affecter cette communauté
    3. Vérifier que le vote local prime sur le vote global pour cette communauté
    
    Note : Ce test documente une fonctionnalité V2 à implémenter
    """
    # Assertion : Les décisions locales DOIVENT primer sur les décisions globales
    # Assertion : Le global NE DOIT PAS écraser les dynamiques locales
```

---

### [⚠️] Les votes ou redistributions peuvent être contextualisés

**Statut** : **NON** ❌ (Structure préparée, fonctionnalité V2)

**Fichiers concernés** :
- `backend/core/models/polls.py` : Modèle `Poll` (pas de lien avec `Community`)
- `backend/core/services/saka.py` : `redistribute_saka_silo()` (redistribution globale uniquement)

**Mécanisme actuel** :
- Les votes sont globaux (pas de votes par communauté)
- La redistribution SAKA est globale (pas de redistribution par communauté)
- Structure `Community` préparée mais pas encore utilisée pour contextualiser

**Test manquant** : ⚠️ **Test de contextualisation manquant**

**Test à ajouter** :
```python
# backend/core/tests_communities.py (à créer pour V2)
def test_votes_can_be_contextualized_by_community(self):
    """
    Test que les votes peuvent être contextualisés par communauté.
    
    Scénario V2 (à implémenter) :
    1. Créer une communauté
    2. Créer un vote associé à cette communauté
    3. Vérifier que seuls les membres de la communauté peuvent voter
    4. Vérifier que le vote n'affecte que les projets de cette communauté
    
    Note : Ce test documente une fonctionnalité V2 à implémenter
    """
    # Assertion : Les votes DOIVENT pouvoir être contextualisés par communauté
```

---

### 👉 Test attendu : test d'accès communautaire

**Statut** : **PARTIELLEMENT** ⚠️

**Fichiers concernés** :
- `backend/core/api/communities_views.py` : Endpoints read-only
- `backend/core/tests_communities.py` : Tests de base (lignes 14-227)

**Test existant** :
```python
# backend/core/tests_communities.py
def test_community_members(self):
    """Test l'ajout de membres à une communauté"""
    # Vérifie que les membres peuvent être ajoutés
```

**Test manquant** : ⚠️ **Test d'accès API manquant**

**Test à ajouter** :
```python
# backend/core/tests_communities.py (à compléter)
def test_community_api_access(self):
    """
    Test que les membres d'une communauté peuvent accéder aux projets de leur communauté.
    
    Scénario :
    1. Créer une communauté avec des membres
    2. Créer un projet associé à cette communauté
    3. Vérifier que GET /api/communities/<slug>/ retourne les projets
    4. Vérifier que les membres peuvent accéder aux projets via l'API
    """
    # Assertion : Les membres DOIVENT pouvoir accéder aux projets de leur communauté
```

---

### 👉 Test attendu : test de périmètre décisionnel

**Statut** : **NON** ❌ **Test manquant**

**Fichier à créer** :
- `backend/core/tests_communities_governance.py` (nouveau fichier pour V2)

**Test à ajouter** :
```python
# backend/core/tests_communities_governance.py (à créer pour V2)
def test_decision_scope_by_community(self):
    """
    Test que les décisions peuvent être prises au niveau communautaire.
    
    Scénario V2 (à implémenter) :
    1. Créer une communauté avec des membres
    2. Créer un vote local pour cette communauté
    3. Vérifier que seuls les membres de la communauté peuvent voter
    4. Vérifier que le vote n'affecte que les projets de cette communauté
    
    Note : Ce test documente une fonctionnalité V2 à implémenter
    """
    # Assertion : Les décisions DOIVENT pouvoir être prises au niveau communautaire
    # Assertion : Le périmètre décisionnel DOIT être respecté
```

---

## 👁️ VISIBILITÉ DES CYCLES

### [✅] Les cycles SAKA sont visibles côté frontend

**Statut** : **OUI** ✅

**Fichiers concernés** :
- `frontend/frontend/src/app/pages/SakaSeasons.tsx` : Page des saisons SAKA (lignes 1-111)
- `frontend/frontend/src/hooks/useSakaCycles.ts` : Hook pour récupérer les cycles
- `frontend/frontend/src/app/router.jsx` : Route `/saka/saisons` (ligne 135)

**Mécanisme** :
- Page dédiée `/saka/saisons` qui affiche les cycles SAKA avec statistiques (récolté, planté, composté)
- Hook `useSakaCycles()` qui appelle `/api/saka/cycles/`
- Affichage des cycles avec dates, statistiques et statut actif

**Test existant** :
```typescript
// frontend/frontend/src/app/pages/__tests__/SakaSeasons.test.tsx
it("affiche le niveau du Silo commun et les cycles SAKA", async () => {
  // Vérifie que les cycles SAKA sont affichés
});
```

**Test manquant** : ❌ **Aucun test manquant** - Les tests Vitest couvrent ce point.

---

### [✅] Le Silo n'est pas invisible pour la communauté

**Statut** : **OUI** ✅

**Fichiers concernés** :
- `frontend/frontend/src/app/pages/SakaSeasons.tsx` : Affichage du Silo (lignes 20-42)
- `frontend/frontend/src/app/pages/SakaSilo.jsx` : Page dédiée au Silo (lignes 1-224)
- `frontend/frontend/src/app/pages/Dashboard.jsx` : Widget Silo dans le Dashboard (lignes 264-308)
- `frontend/frontend/src/hooks/useSakaSilo.ts` : Hook pour récupérer le Silo

**Mécanisme** :
- Page dédiée `/saka/silo` qui affiche l'état du Silo Commun
- Widget dans le Dashboard qui affiche le niveau du Silo
- Affichage dans la page SakaSeasons avec le niveau du Silo
- Hook `useSakaSilo()` qui appelle `/api/saka/silo/`

**Test existant** :
```typescript
// frontend/frontend/src/app/pages/__tests__/SakaSeasons.test.tsx
it("affiche le niveau du Silo commun", async () => {
  // Vérifie que le Silo est affiché
});
```

**Test manquant** : ❌ **Aucun test manquant** - Les tests Vitest couvrent ce point.

---

### [✅] L'utilisateur comprend ce qui arrive à sa valeur

**Statut** : **OUI** ✅

**Fichiers concernés** :
- `frontend/frontend/src/app/pages/Dashboard.jsx` : Prévisualisation du compostage (lignes 142-195)
- `frontend/frontend/src/hooks/useSaka.js` : `useSakaCompostPreview()` (lignes 47-65)
- `frontend/frontend/src/app/pages/SakaSeasons.tsx` : Explication du cycle (lignes 15-17)

**Mécanisme** :
- Dashboard affiche une prévisualisation du compostage : "Si vous restez inactif, environ X SAKA seront compostés"
- Page SakaSeasons explique le cycle : "récolte, plantation et compostage vers le Silo commun"
- Affichage du dernier cycle de compost dans le Dashboard

**Test existant** : ⚠️ **Tests partiels** - Pas de test E2E pour vérifier la compréhension utilisateur

**Test manquant** : ⚠️ **Test E2E manquant**

**Test à ajouter** :
```javascript
// frontend/frontend/e2e/saka-cycle-visibility.spec.js (à créer)
test('l\'utilisateur comprend ce qui arrive à son SAKA inactif', async ({ page }) => {
  // 1. Se connecter
  // 2. Aller sur le Dashboard
  // 3. Vérifier que la prévisualisation du compostage est affichée
  // 4. Aller sur /saka/saisons
  // 5. Vérifier que le cycle est expliqué (récolte → plantation → compost → silo)
  // 6. Vérifier que le Silo est visible avec son niveau
});
```

---

### 👉 Test attendu : test E2E : affichage saison / cycle / silo

**Statut** : **PARTIELLEMENT** ⚠️

**Fichiers concernés** :
- `frontend/frontend/e2e/votes-quadratic.spec.js` : Tests E2E votes (existe)
- `frontend/frontend/e2e/projects-saka-boost.spec.js` : Tests E2E boost (existe)
- `frontend/frontend/e2e/saka-flow.spec.js` : Tests E2E SAKA (existe)

**Test manquant** : ⚠️ **Test E2E cycle/silo manquant**

**Test à ajouter** :
```javascript
// frontend/frontend/e2e/saka-cycle-visibility.spec.js (à créer)
test('affiche les cycles SAKA et le Silo commun', async ({ page }) => {
  // 1. Se connecter
  // 2. Aller sur /saka/saisons
  // 3. Vérifier que la page affiche :
  //    - Le niveau du Silo commun
  //    - La liste des cycles SAKA avec statistiques (récolté, planté, composté)
  //    - Les dates de début et fin de chaque cycle
  // 4. Vérifier que le dernier cycle de compost est affiché
});
```

---

## 📊 RÉSUMÉ DE CONFORMITÉ

### ✅ Conforme (OUI)

1. **SAKA ne peut pas être accumulé indéfiniment** : Tests philosophiques complets
2. **Compostage effectif** : Tâche Celery + tests d'intégration
3. **Silo reçoit la valeur compostée** : Tests philosophiques
4. **Redistribution existe** : Service + tâche Celery + tests
5. **Flux financiers atomiques** : Transactions atomiques + tests
6. **Traçabilité financière** : WalletTransaction pour chaque opération
7. **P1/P2 basés sur données réelles** : Code vérifié
8. **P3/P4 explicitement déclaratifs** : Docstrings + labels frontend
9. **Structure communautaire** : Modèle Community + API read-only
10. **Cycles SAKA visibles** : Page SakaSeasons + tests Vitest
11. **Silo visible** : Page SakaSilo + Dashboard + tests Vitest

### ⚠️ Partiellement conforme (À compléter)

1. **Tests d'échec partiel (rollback)** : Idempotence testée, rollback partiel manquant
2. **Tests API 4P** : Service existe, tests API manquants
3. **Tests frontend 4P** : Composants existent, snapshot tests manquants
4. **Tests de périmètre décisionnel** : Structure préparée, tests V2 manquants
5. **Tests E2E cycle/silo** : Tests unitaires existent, E2E manquant

### ❌ Non conforme (À implémenter)

1. **Test de rollback partiel** : À créer dans `backend/finance/tests_finance.py`
2. **Test API 4P avec métadonnées** : À créer dans `backend/core/tests_impact_4p.py`
3. **Test frontend 4P snapshot** : À compléter dans `frontend/frontend/src/components/__tests__/FourPStrip.test.jsx`
4. **Test de contextualisation communautaire** : À créer pour V2 dans `backend/core/tests_communities_governance.py`
5. **Test E2E cycle/silo** : À créer dans `frontend/frontend/e2e/saka-cycle-visibility.spec.js`

---

## 🎯 PRIORISATION DES TESTS MANQUANTS

### P0 (Critique - Violation Manifeste si absent)

1. **Test de rollback partiel financier** : Garantit l'intégrité des transactions
   - Fichier : `backend/finance/tests_finance.py`
   - Test : `test_pledge_funds_rollback_on_exception()`

2. **Test API 4P avec métadonnées** : Garantit la transparence honnête
   - Fichier : `backend/core/tests_impact_4p.py` (à créer)
   - Test : `test_api_returns_4p_with_metadata()`

### P1 (Important - Conformité Manifeste)

3. **Test frontend 4P snapshot** : Garantit que les disclaimers sont affichés
   - Fichier : `frontend/frontend/src/components/__tests__/FourPStrip.test.jsx`
   - Test : Snapshot avec tooltips "V1 interne"

4. **Test E2E cycle/silo** : Garantit la visibilité des cycles
   - Fichier : `frontend/frontend/e2e/saka-cycle-visibility.spec.js` (à créer)
   - Test : `test('affiche les cycles SAKA et le Silo commun')`

### P2 (Préparation V2 - Subsidiarité)

5. **Test de contextualisation communautaire** : Documente la fonctionnalité V2
   - Fichier : `backend/core/tests_communities_governance.py` (à créer pour V2)
   - Test : `test_votes_can_be_contextualized_by_community()`

---

## 🔒 GARANTIES PHILOSOPHIQUES

### ✅ Garanties respectées

- **Anti-accumulation** : Compostage progressif obligatoire, tests philosophiques
- **Circulation obligatoire** : Cycle complet implémenté et testé
- **Retour au commun** : Silo bénéficie du compostage, redistribution équitable
- **Non-spéculation** : Aucune conversion SAKA ↔ Euro possible
- **Transparence honnête** : P3/P4 explicitement marqués comme proxies V1

### ⚠️ Garanties partiellement respectées

- **Subsidiarité** : Structure préparée, fonctionnalité V2 à implémenter
- **Visibilité des cycles** : Cycles visibles, mais test E2E manquant

---

**Dernière mise à jour** : 2025-12-17  
**Prochaine révision** : Après implémentation des tests manquants P0


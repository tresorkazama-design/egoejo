# 🧪 Documentation - Tests Philosophiques EGOEJO

**Date** : 17 Décembre 2025  
**Objectif** : Documenter les tests qui protègent la philosophie EGOEJO

---

## 🎯 Objectif des Tests Philosophiques

Les tests philosophiques ne vérifient pas seulement que le code fonctionne, mais qu'il **respecte les principes fondamentaux d'EGOEJO** :

- ✅ La valeur ne peut pas être stockée indéfiniment
- ✅ Un utilisateur ne peut pas contourner le cycle
- ✅ Le collectif bénéficie de l'inutilisation individuelle
- ✅ L'accumulation passive est impossible

---

## 📋 Liste des Tests Philosophiques

### Fichier : `backend/core/tests_saka_philosophy.py`

**Nombre de tests** : 14 tests

### 1. Anti-Accumulation

#### `test_saka_inactif_doit_être_composté_après_inactivité`
- **Principe** : La valeur ne peut pas être stockée indéfiniment
- **Vérifie** : Un wallet inactif depuis 90+ jours est composté
- **Assertions** :
  - Le compostage a lieu
  - Le solde diminue
  - Le Silo reçoit le SAKA composté

#### `test_compostage_progressif_empêche_thésaurisation_infinie`
- **Principe** : L'accumulation infinie est impossible
- **Vérifie** : Le compostage progressif réduit le solde au fil du temps
- **Assertions** :
  - Le solde diminue progressivement
  - Après plusieurs cycles, le solde finit par être < seuil

#### `test_pas_de_limite_maximale_mais_compostage_obligatoire`
- **Principe** : Aucun plafond, mais compostage obligatoire
- **Vérifie** : Même un très gros solde est composté
- **Assertions** :
  - Le compostage s'applique même sur un gros solde
  - Le Silo reçoit le SAKA composté

### 2. Circulation de la Valeur

#### `test_saka_composté_retourne_au_silo_commun`
- **Principe** : La valeur inactive retourne au commun
- **Vérifie** : Le SAKA composté va au Silo
- **Assertions** :
  - Le Silo reçoit le SAKA composté
  - Le total_composted du Silo augmente

#### `test_redistribution_du_silo_vers_collectif`
- **Principe** : Le Silo redistribue au collectif
- **Vérifie** : La redistribution fonctionne
- **Assertions** :
  - Le Silo diminue
  - Les wallets actifs sont crédités
  - Le montant redistribué est correct

### 3. Cycle Complet

#### `test_cycle_complet_récolte_plantation_compost_silo_redistribution`
- **Principe** : Le cycle complet fonctionne
- **Vérifie** : Récolte → Plantation → Compost → Silo → Redistribution
- **Assertions** :
  - Chaque étape fonctionne
  - Le cycle est complet
  - La valeur circule correctement

### 4. Impossibilité de Contournement

#### `test_impossibilité_de_contourner_le_compostage`
- **Principe** : Un utilisateur ne peut pas contourner le cycle
- **Vérifie** : Même avec des actions, l'inactivité déclenche le compostage
- **Assertions** :
  - Le compostage s'applique malgré les tentatives
  - Le cycle ne peut pas être contourné

---

## 🔍 Comment Exécuter les Tests

### Exécuter tous les tests philosophiques

```bash
python -m pytest backend/core/tests_saka_philosophy.py -v
```

### Exécuter un test spécifique

```bash
python -m pytest backend/core/tests_saka_philosophy.py::SakaPhilosophyTestCase::test_saka_inactif_doit_être_composté_après_inactivité -v
```

### Exécuter avec couverture

```bash
python -m pytest backend/core/tests_saka_philosophy.py --cov=core.services.saka --cov-report=html
```

---

## ✅ Critères de Succès

### Tous les tests doivent passer

- ✅ **14/14 tests** doivent passer
- ✅ **0 échec** accepté
- ✅ **0 skip** accepté (sauf si explicitement documenté)

### Vérification continue

Les tests sont exécutés :
- **Avant chaque commit** (pre-commit hook recommandé)
- **Dans la CI/CD** (GitHub Actions recommandé)
- **Avant chaque déploiement** (validation obligatoire)

---

## 🚫 Tests Refusés

### Tests qui valident l'accumulation

❌ **Refusé** : Test qui vérifie qu'un utilisateur peut accumuler indéfiniment
❌ **Refusé** : Test qui vérifie qu'il n'y a pas de limite maximale sans compostage
❌ **Refusé** : Test qui vérifie qu'on peut contourner le cycle

### Tests acceptés

✅ **Accepté** : Test qui vérifie que l'accumulation est limitée
✅ **Accepté** : Test qui vérifie que le compostage est obligatoire
✅ **Accepté** : Test qui vérifie que le cycle ne peut pas être contourné

---

## 📊 Métriques des Tests

### Couverture

- **Services testés** : `core.services.saka`
- **Modèles testés** : `SakaWallet`, `SakaSilo`, `SakaCompostLog`
- **Tâches testées** : `saka_run_compost_cycle`, `run_saka_silo_redistribution`

### Performance

- **Durée moyenne** : < 5 secondes pour tous les tests
- **Base de données** : Tests isolés (TestCase avec transactions)

---

## 🔄 Maintenance

### Ajouter un nouveau test philosophique

1. Identifier le principe à protéger
2. Créer un test dans `tests_saka_philosophy.py`
3. Ajouter des assertions explicites
4. Documenter le principe protégé
5. Vérifier que le test passe

### Modifier un test existant

1. Vérifier que la modification ne viole pas un principe
2. Mettre à jour la documentation
3. Vérifier que tous les tests passent toujours

---

## 📚 Références

- **Code** : `backend/core/tests_saka_philosophy.py`
- **Services** : `backend/core/services/saka.py`
- **Philosophie** : `docs/architecture/PROTOCOLE_SAKA_PHILOSOPHIE.md`

---

**Date de création** : 17 Décembre 2025  
**Statut** : ✅ Documentation complète


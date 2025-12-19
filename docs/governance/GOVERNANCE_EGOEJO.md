# Gouvernance EGOEJO

> **Principe fondamental** : "Le code protège le Manifeste, la communauté décide de son évolution."

## Vue d'ensemble

Le système de gouvernance EGOEJO combine **protection automatique** (bot) et **décision collective** (communauté) pour garantir que le Manifeste EGOEJO est respecté tout en permettant son évolution.

---

## Ce que le bot PEUT décider

Le **EGOEJO Guardian** (bot automatique) peut **bloquer immédiatement** les violations critiques :

### Violations bloquantes automatiques

1. **Conversion SAKA ↔ EUR**
   - Détection : Pattern `convert.*saka.*eur`, `saka_to_eur`, etc.
   - Action : 🔴 NON COMPATIBLE EGOEJO → Merge bloqué

2. **Rendement financier basé sur SAKA**
   - Détection : Pattern `saka.*interest`, `saka.*yield`, etc.
   - Action : 🔴 NON COMPATIBLE EGOEJO → Merge bloqué

3. **Désactivation du compostage**
   - Détection : Pattern `disable.*compost`, `skip.*compost`, etc.
   - Action : 🔴 NON COMPATIBLE EGOEJO → Merge bloqué

4. **Affichage monétaire du SAKA**
   - Détection : Pattern `saka.*€`, `saka.*euro`, etc.
   - Action : 🟡 COMPATIBLE SOUS CONDITIONS → Merge avec conditions

5. **Tests manquants pour modifications SAKA**
   - Détection : Fichier SAKA modifié sans test associé
   - Action : 🟡 COMPATIBLE SOUS CONDITIONS → Merge avec conditions

### Décisions automatiques

Le bot peut **approuver automatiquement** les PRs qui :
- ✅ Respectent toutes les règles déterministes
- ✅ Incluent les tests nécessaires
- ✅ Ne touchent pas aux règles fondamentales

**Verdict** : 🟢 COMPATIBLE EGOEJO → Merge autorisé

---

## Ce que le bot NE PEUT PAS décider

Le bot **ne peut pas** prendre de décisions sur :

### 1. Activation de la Banque (EUR)

**Règle** : Toute PR qui active ou modifie la structure instrumentale (EUR) nécessite une validation humaine.

**Détection automatique** :
- Modification de `ENABLE_INVESTMENT_FEATURES` de `False` à `True`
- Ajout de nouvelles features financières
- Modification des règles d'escrow ou d'investissement

**Action** :
- Label `governance-required` ajouté automatiquement
- CI passe (tests techniques OK)
- **Merge bloqué** jusqu'à validation humaine

**Processus de validation** :
1. Créer une Discussion GitHub avec le template `DISCUSSION_GOUVERNANCE.md`
2. Répondre aux questions obligatoires
3. Attendre validation de la gouvernance (minimum 2 approbations)
4. Retirer le label `governance-required` après validation

### 2. Modification du cycle SAKA

**Règle** : Toute modification du cycle SAKA (Récolte → Usage → Compost → Silo → Redistribution) nécessite une validation humaine.

**Détection automatique** :
- Modification de `run_saka_compost_cycle()`
- Modification de `redistribute_saka_silo()`
- Changement des paramètres de compostage (`SAKA_COMPOST_RATE`, `SAKA_COMPOST_INACTIVITY_DAYS`)
- Modification des règles de redistribution (`SAKA_SILO_REDIS_RATE`)

**Action** :
- Label `governance-required` ajouté automatiquement
- CI passe (tests techniques OK)
- **Merge bloqué** jusqu'à validation humaine

**Processus de validation** :
1. Créer une Discussion GitHub avec le template `DISCUSSION_GOUVERNANCE.md`
2. Répondre aux questions obligatoires :
   - Quel impact sur le cycle SAKA ?
   - Y a-t-il un risque d'accumulation ?
   - Qui bénéficie / qui perd ?
3. Attendre validation de la gouvernance (minimum 2 approbations)
4. Retirer le label `governance-required` après validation

### 3. Changement des règles de redistribution

**Règle** : Toute modification des règles de redistribution du Silo nécessite une validation humaine.

**Détection automatique** :
- Modification de `SAKA_SILO_REDIS_RATE`
- Modification de `SAKA_SILO_REDIS_MIN_WALLET_ACTIVITY`
- Changement de la logique de redistribution dans `redistribute_saka_silo()`

**Action** :
- Label `governance-required` ajouté automatiquement
- CI passe (tests techniques OK)
- **Merge bloqué** jusqu'à validation humaine

**Processus de validation** :
1. Créer une Discussion GitHub avec le template `DISCUSSION_GOUVERNANCE.md`
2. Répondre aux questions obligatoires :
   - Quel impact sur la redistribution ?
   - Y a-t-il un risque d'inégalité ?
   - Qui bénéficie / qui perd ?
3. Attendre validation de la gouvernance (minimum 2 approbations)
4. Retirer le label `governance-required` après validation

---

## Cas nécessitant validation humaine

### Résumé des cas

| Cas | Détection | Label | Merge |
|-----|-----------|-------|-------|
| Activation Banque (EUR) | Modification `ENABLE_INVESTMENT_FEATURES` | `governance-required` | Bloqué |
| Modification cycle SAKA | Modification fonctions compost/redistribution | `governance-required` | Bloqué |
| Changement règles redistribution | Modification `SAKA_SILO_REDIS_*` | `governance-required` | Bloqué |
| Conversion SAKA ↔ EUR | Pattern regex | 🔴 NON COMPATIBLE | Bloqué (automatique) |
| Rendement financier SAKA | Pattern regex | 🔴 NON COMPATIBLE | Bloqué (automatique) |

### Processus de validation

1. **Détection automatique** : Le bot ajoute le label `governance-required`
2. **Discussion obligatoire** : Créer une Discussion GitHub avec le template
3. **Questions obligatoires** : Répondre aux questions du template
4. **Validation collective** : Minimum 2 approbations de membres de la gouvernance
5. **Retrait du label** : Après validation, retirer `governance-required`
6. **Merge autorisé** : Une fois le label retiré, le merge peut être effectué

---

## Principe fondamental

> **"Le code protège le Manifeste, la communauté décide de son évolution."**

### Protection automatique (Code)

Le code **protège** le Manifeste en :
- ✅ Bloquant automatiquement les violations critiques
- ✅ Vérifiant que les règles fondamentales sont respectées
- ✅ Garantissant que les tests de conformité passent

### Décision collective (Communauté)

La communauté **décide** de l'évolution en :
- ✅ Validant les modifications des règles fondamentales
- ✅ Discutant les impacts philosophiques
- ✅ Approuvant les changements via Discussion GitHub

### Séparation des responsabilités

- **Bot** : Protection immédiate contre les violations
- **Communauté** : Décision sur l'évolution du Manifeste
- **Code** : Exécution des décisions validées

---

## Gouvernance explicite

### Transparence

- ✅ Toutes les décisions sont tracées dans GitHub Discussions
- ✅ Toutes les validations sont publiques
- ✅ Historique complet des modifications

### Pas de vote caché

- ✅ Toutes les discussions sont publiques
- ✅ Toutes les approbations sont visibles
- ✅ Aucune décision prise en privé

### Historique traçable

- ✅ Chaque Discussion GitHub est liée à une PR
- ✅ Chaque validation est documentée
- ✅ Chaque modification est tracée dans les commits

---

## Rôles et responsabilités

### Développeurs

- ✅ Respecter les règles déterministes (bot)
- ✅ Créer une Discussion si `governance-required`
- ✅ Répondre aux questions obligatoires

### Gouvernance (Membres validants)

- ✅ Examiner les Discussions `governance-required`
- ✅ Valider ou rejeter les modifications
- ✅ Documenter les décisions

### Bot (EGOEJO Guardian)

- ✅ Détecter les violations critiques
- ✅ Ajouter le label `governance-required` si nécessaire
- ✅ Bloquer le merge jusqu'à validation

---

## Exemples

### Exemple 1 : Activation de la Banque

**PR** : Modification de `ENABLE_INVESTMENT_FEATURES` de `False` à `True`

**Détection** : Bot détecte la modification et ajoute `governance-required`

**Action** :
1. Créer Discussion : "Activation de la structure instrumentale (EUR)"
2. Répondre aux questions :
   - Impact sur SAKA : Aucun, SAKA reste prioritaire
   - Risque d'accumulation : Non, SAKA reste anti-accumulation
   - Qui bénéficie : Projets nécessitant investissement
3. Attendre 2 approbations
4. Retirer `governance-required`
5. Merge autorisé

### Exemple 2 : Modification du taux de compostage

**PR** : Modification de `SAKA_COMPOST_RATE` de `0.1` à `0.2`

**Détection** : Bot détecte la modification et ajoute `governance-required`

**Action** :
1. Créer Discussion : "Augmentation du taux de compostage SAKA"
2. Répondre aux questions :
   - Impact sur le cycle : Compostage plus rapide, retour au Silo plus fréquent
   - Risque d'accumulation : Non, au contraire, réduit l'accumulation
   - Qui bénéficie : Collectif (Silo alimenté plus vite)
3. Attendre 2 approbations
4. Retirer `governance-required`
5. Merge autorisé

---

## Références

- **Constitution EGOEJO** : `docs/compliance/EGOEJO_CONSTITUTION_EXECUTABLE.md`
- **Template Discussion** : `docs/governance/DISCUSSION_GOUVERNANCE.md`
- **Bot Guardian** : `.egoejo/guardian.py`
- **Tests Compliance** : `backend/tests/compliance/`

---

**Dernière mise à jour** : 2025-12-18


# Principe Fondamental EGOEJO

> **"Le code protège le Manifeste, la communauté décide de son évolution."**

## Explication

Ce principe fondamental établit la séparation claire entre **protection automatique** (code) et **décision collective** (communauté).

### Le code protège le Manifeste

Le code **protège** le Manifeste EGOEJO en :

1. **Bloquant automatiquement** les violations critiques
   - Conversion SAKA ↔ EUR
   - Rendement financier basé sur SAKA
   - Désactivation du compostage
   - Affichage monétaire du SAKA

2. **Vérifiant** que les règles fondamentales sont respectées
   - Tests de conformité automatiques
   - Détection de patterns interdits
   - Validation des feature flags

3. **Garantissant** que les tests passent
   - Tests de conformité philosophique
   - Tests fonctionnels du cycle SAKA
   - Tests de séparation SAKA/EUR

**Le code est un gardien automatique, pas un décideur.**

### La communauté décide de son évolution

La communauté **décide** de l'évolution du Manifeste en :

1. **Validant** les modifications des règles fondamentales
   - Activation de la Banque (EUR)
   - Modification du cycle SAKA
   - Changement des règles de redistribution

2. **Discutant** les impacts philosophiques
   - Impact sur le cycle SAKA
   - Risques d'accumulation
   - Bénéficiaires et impacts

3. **Approuvant** les changements via Discussion GitHub
   - Questions obligatoires
   - Validation collective (minimum 2 approbations)
   - Historique traçable

**La communauté est le décideur, pas le code.**

---

## Séparation des responsabilités

### Code (Protection)

- ✅ **Peut** bloquer les violations critiques
- ✅ **Peut** vérifier que les règles sont respectées
- ❌ **Ne peut pas** décider de l'évolution du Manifeste
- ❌ **Ne peut pas** valider les modifications fondamentales

### Communauté (Décision)

- ✅ **Peut** valider les modifications fondamentales
- ✅ **Peut** discuter les impacts philosophiques
- ✅ **Peut** approuver les changements
- ❌ **Ne peut pas** contourner les protections automatiques

---

## Exemples

### Exemple 1 : Protection automatique

**Scénario** : Un développeur tente d'ajouter une fonction `convert_saka_to_eur()`.

**Action du code** :
- ✅ Détection automatique du pattern `convert.*saka.*eur`
- ✅ Blocage immédiat : 🔴 NON COMPATIBLE EGOEJO
- ✅ Merge bloqué automatiquement

**Résultat** : La violation est bloquée sans intervention humaine.

### Exemple 2 : Décision collective

**Scénario** : Un développeur propose d'augmenter le taux de compostage de 10% à 20%.

**Action du code** :
- ✅ Détection automatique : modification de `SAKA_COMPOST_RATE`
- ✅ Ajout du label `governance-required`
- ✅ CI passe (tests techniques OK)
- ⏸️ Merge bloqué jusqu'à validation

**Action de la communauté** :
- ✅ Création d'une Discussion GitHub
- ✅ Réponses aux questions obligatoires
- ✅ Validation collective (2 approbations)
- ✅ Retrait du label `governance-required`
- ✅ Merge autorisé

**Résultat** : La modification est validée collectivement après discussion.

---

## Implications

### Pour les développeurs

- ✅ Respecter les règles déterministes (bot)
- ✅ Créer une Discussion si `governance-required`
- ✅ Répondre aux questions obligatoires
- ❌ Ne pas contourner les protections automatiques

### Pour la gouvernance

- ✅ Examiner les Discussions `governance-required`
- ✅ Valider ou rejeter les modifications
- ✅ Documenter les décisions
- ❌ Ne pas valider les violations critiques (bloquées automatiquement)

### Pour le code

- ✅ Protéger le Manifeste automatiquement
- ✅ Détecter les violations critiques
- ✅ Ajouter `governance-required` si nécessaire
- ❌ Ne pas décider de l'évolution du Manifeste

---

## Traçabilité

### Protection automatique

- ✅ Logs du bot dans GitHub Actions
- ✅ Commentaires PR automatiques
- ✅ Labels PR automatiques
- ✅ Historique des violations bloquées

### Décision collective

- ✅ Discussions GitHub publiques
- ✅ Approbations visibles
- ✅ Historique des validations
- ✅ Liens PR ↔ Discussion

---

## Références

- **Gouvernance EGOEJO** : `docs/governance/GOVERNANCE_EGOEJO.md`
- **Template Discussion** : `docs/governance/DISCUSSION_GOUVERNANCE.md`
- **Constitution EGOEJO** : `docs/compliance/EGOEJO_CONSTITUTION_EXECUTABLE.md`

---

**Dernière mise à jour** : 2025-12-18


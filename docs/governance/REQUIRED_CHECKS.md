# Checks Requis pour les Merges - EGOEJO

**Version** : 1.0  
**Date** : 2025-01-27  
**Statut** : Document Officiel

---

## 📋 Résumé Exécutif

**🚫 Merge bloqué si non conforme**

Les merges vers la branche `main` sont **automatiquement bloqués** si les checks de conformité EGOEJO échouent.

Cette protection garantit que seules les modifications conformes aux principes EGOEJO peuvent être intégrées dans la branche principale.

---

## 🛡️ Checks Requis

### 1. Audit Home/Vision (`audit-home-vision`)

**Workflow** : `.github/workflows/audit-home-vision.yml`  
**Job** : `audit-home-vision`  
**Statut** : **REQUIS** (merge bloqué si échec)

#### Description

Vérifie la conformité des pages Accueil (`/`) et Vision (`/vision`) aux exigences de l'audit quadripartite strict :

- ✅ Navigation et accessibilité (skip-links, hash navigation)
- ✅ Présence des sections requises (principes, glossaire, disclaimer)
- ✅ Conformité éditoriale (texte "100% des dons nets", note SAKA/EUR)
- ✅ Internationalisation (clés i18n présentes, pas de hardcode)

#### Vérifications Effectuées

1. **Lint** : ESLint sur le code frontend
2. **Tests unitaires** : Tests de conformité (Testing Library)
3. **Audit statique** : Script `audit:home-vision` (détection violations)
4. **Tests E2E** : Playwright (navigation, accessibilité, présence sections)

#### Critères de Succès

- ✅ Tous les tests unitaires passent
- ✅ L'audit statique ne détecte aucune violation
- ✅ Tous les tests E2E passent
- ✅ Exit code : `0`

#### Critères d'Échec (Merge Bloqué)

- ❌ Au moins un test unitaire échoue
- ❌ L'audit statique détecte des violations (ex: "100% des dons" sans "nets")
- ❌ Au moins un test E2E échoue
- ❌ Exit code : `1`

#### Impact

**Si le check échoue, le merge est bloqué automatiquement par GitHub Branch Protection Rules.**

---

### 2. PR Bot Home/Vision (`pr-bot-home-vision`)

**Workflow** : `.github/workflows/pr-bot-home-vision.yml`  
**Job** : `pr-bot-home-vision`  
**Statut** : **Informatif** (ne bloque pas le merge, mais commente la PR)

#### Description

Bot qui commente automatiquement les PRs avec le statut de conformité des pages Accueil/Vision et applique un label approprié.

#### Labels Appliqués

- 🟢 **EGOEJO Compliant** : Toutes les vérifications passent
- 🟡 **EGOEJO Conditional** : Vérifications critiques OK, certaines non-critiques échouent
- 🔴 **EGOEJO Non Compliant** : Au moins une violation détectée

#### Note

Ce check est **informatif uniquement** et ne bloque pas le merge. Le check bloquant est `audit-home-vision`.

---

## 🔒 Configuration Branch Protection Rules

### Activation du Check Requis

Pour rendre le check `audit-home-vision` **requis** et bloquer les merges en cas d'échec :

1. **Accéder aux paramètres du dépôt** :
   - GitHub → Repository → Settings → Branches

2. **Configurer la protection de la branche `main`** :
   - Cliquer sur "Add rule" ou modifier la règle existante pour `main`
   - Activer "Require status checks to pass before merging"

3. **Sélectionner le check requis** :
   - Cocher la case **`audit-home-vision`** dans la liste des checks disponibles
   - ⚠️ **Important** : Le check doit apparaître dans la liste après au moins une exécution réussie

4. **Options supplémentaires recommandées** :
   - ✅ "Require branches to be up to date before merging"
   - ✅ "Require conversation resolution before merging" (optionnel)
   - ✅ "Require signed commits" (optionnel, selon votre politique)

5. **Sauvegarder** :
   - Cliquer sur "Create" ou "Save changes"

### Vérification

Après configuration, toute tentative de merge d'une PR où le check `audit-home-vision` échoue sera **automatiquement bloquée** par GitHub.

---

## 📊 Tableau Récapitulatif

| Check | Workflow | Bloque le Merge | Description |
|-------|----------|-----------------|-------------|
| `audit-home-vision` | `.github/workflows/audit-home-vision.yml` | ✅ **OUI** | Audit complet (lint, tests, E2E, audit statique) |
| `pr-bot-home-vision` | `.github/workflows/pr-bot-home-vision.yml` | ❌ Non | Bot informatif (commentaire + label) |

---

## 🚨 Comportement en Cas d'Échec

### Check `audit-home-vision` Échoue

1. **Merge bloqué automatiquement** par GitHub Branch Protection Rules
2. **Message d'erreur** affiché sur la PR : "Required status check 'audit-home-vision' is expected"
3. **Actions requises** :
   - Corriger les violations détectées
   - Pousser les corrections (le check se relance automatiquement)
   - Attendre que le check passe avant de pouvoir merger

### Exemples de Violations Bloquantes

- ❌ Texte "100% des dons" sans mention de "nets" ou "après frais"
- ❌ Skip-link hardcodé en français (non traduit via i18n)
- ❌ Clés i18n manquantes (`accessibility.skip_to_main`, `vision.principles_title`, etc.)
- ❌ Tests unitaires échouent (sections manquantes, texte incorrect)
- ❌ Tests E2E échouent (navigation, accessibilité)

---

## 🔍 Vérification du Statut

### Sur GitHub

1. **Ouvrir une PR** : Le check `audit-home-vision` apparaît dans la liste des checks
2. **Statut** :
   - ✅ **Vert** : Check passé, merge autorisé
   - ❌ **Rouge** : Check échoué, merge bloqué
   - ⏳ **Jaune** : Check en cours d'exécution

### Localement

```bash
# Exécuter l'audit manuellement
cd frontend/frontend
npm run audit:home-vision

# Exécuter les tests
npm run test:run
npm run test:e2e -- e2e/home-vision-compliance.spec.js
```

---

## 📝 Maintenance

### Ajouter un Nouveau Check Requis

1. **Créer le workflow** dans `.github/workflows/`
2. **Documenter** dans ce fichier (`REQUIRED_CHECKS.md`)
3. **Activer** dans Branch Protection Rules (via GitHub UI)
4. **Tester** en créant une PR de test

### Modifier un Check Existant

1. **Modifier le workflow** si nécessaire
2. **Mettre à jour la documentation** dans ce fichier
3. **Vérifier** que le check apparaît toujours dans Branch Protection Rules

---

## 🔗 Références

- **Workflow audit-home-vision** : `.github/workflows/audit-home-vision.yml`
- **Workflow pr-bot-home-vision** : `.github/workflows/pr-bot-home-vision.yml`
- **Script d'audit** : `frontend/frontend/scripts/audit-home-vision.mjs`
- **Tests E2E** : `frontend/frontend/e2e/home-vision-compliance.spec.js`
- **Gouvernance EGOEJO** : `docs/governance/GOVERNANCE_EGOEJO.md`

---

## ⚠️ Notes Importantes

1. **Configuration GitHub UI** : Les Branch Protection Rules ne peuvent pas être configurées via code. La configuration doit être effectuée manuellement dans l'interface GitHub.

2. **Première exécution** : Le check `audit-home-vision` doit avoir été exécuté au moins une fois avec succès pour apparaître dans la liste des checks disponibles dans Branch Protection Rules.

3. **Branches protégées** : Par défaut, seule la branche `main` est protégée. Pour protéger d'autres branches, créer une règle similaire.

4. **Permissions** : Seuls les administrateurs du dépôt peuvent modifier les Branch Protection Rules.

---

**Document généré le** : 2025-01-27  
**Version** : 1.0  
**Statut** : Document Officiel


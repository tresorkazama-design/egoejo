# 🛡️ Branch Protection Rules - Configuration GitHub

**Date** : 2025-01-01  
**Objectif** : Rendre impossible le merge si le label EGOEJO n'est pas respecté à 100%  
**Statut** : ✅ **DOCUMENTATION CRÉÉE**

---

## 📋 Résumé

Ce document explique comment configurer les **Branch Protection Rules** dans l'interface GitHub pour garantir qu'aucun merge n'est possible si les workflows de compliance EGOEJO échouent.

**⚠️ IMPORTANT** : Ces règles doivent être configurées **manuellement** dans l'interface GitHub, car Cursor ne peut pas cliquer dans l'UI.

---

## 🎯 Objectif

**Rendre impossible le merge si le label EGOEJO n'est pas respecté à 100%.**

Toute violation de la Constitution EGOEJO doit bloquer le merge automatiquement.

---

## 📍 Accès aux Branch Protection Rules

### Étape 1 : Accéder aux Settings du Repository

1. Aller sur GitHub : `https://github.com/[OWNER]/[REPO]`
2. Cliquer sur **Settings** (en haut à droite)
3. Dans le menu de gauche, cliquer sur **Branches**

### Étape 2 : Ajouter une Rule pour `main`

1. Dans la section **Branch protection rules**, cliquer sur **Add rule** (ou **Edit** si une rule existe déjà)
2. Dans le champ **Branch name pattern**, entrer : `main`
3. Configurer les règles ci-dessous

---

## ✅ Règles à Activer

### 1. Require status checks to pass before merging

**📍 Localisation** : Section **"Require status checks to pass before merging"**

**Actions** :
1. ✅ Cocher la case **"Require status checks to pass before merging"**
2. ✅ Cocher la case **"Require branches to be up to date before merging"** (optionnel mais recommandé)

**Status checks à sélectionner** :

#### Workflow Principal : `audit-global.yml`

Sélectionner les jobs suivants :
- ✅ **`🛡️ Audit Statique (Mots Interdits)`** (job: `audit-static`)
- ✅ **`🧪 Backend Compliance Tests`** (job: `backend-compliance`)
- ✅ **`🔐 Backend Permission Tests`** (job: `backend-permissions`)
- ✅ **`🧪 Frontend Unit Tests`** (job: `frontend-unit`)
- ✅ **`🎭 Frontend E2E Critical Tests`** (job: `frontend-e2e-critical`)
- ✅ **`🚨 Critical Compliance (P0/P1 BLOQUANT)`** (job: `critical-compliance`)

**Nom exact dans GitHub** :
- `audit-static` (ou `🛡️ Audit Statique (Mots Interdits)`)
- `backend-compliance` (ou `🧪 Backend Compliance Tests`)
- `backend-permissions` (ou `🔐 Backend Permission Tests`)
- `frontend-unit` (ou `🧪 Frontend Unit Tests`)
- `frontend-e2e-critical` (ou `🎭 Frontend E2E Critical Tests`)
- `critical-compliance` (ou `🚨 Critical Compliance (P0/P1 BLOQUANT)`)

#### Workflow Compliance : `egoejo-compliance.yml`

Sélectionner le job suivant :
- ✅ **`Tests de Compliance Philosophique SAKA/EUR`** (job: `egoejo-compliance`)

**Nom exact dans GitHub** :
- `egoejo-compliance` (ou `Tests de Compliance Philosophique SAKA/EUR`)

**⚠️ NOTE** : Les noms exacts peuvent varier selon la configuration GitHub. Pour trouver les noms exacts :
1. Créer une PR de test
2. Aller dans l'onglet **Checks** de la PR
3. Noter les noms exacts des jobs qui apparaissent
4. Utiliser ces noms dans Branch Protection Rules

---

### 2. Require pull request reviews before merging

**📍 Localisation** : Section **"Require pull request reviews before merging"**

**Actions** :
1. ✅ Cocher la case **"Require pull request reviews before merging"**
2. ✅ Configurer **"Required number of approvals"** : `1` (ou plus selon votre politique)
3. ✅ Cocher **"Dismiss stale pull request approvals when new commits are pushed"** (recommandé)

**Optionnel** :
- ✅ Cocher **"Require review from Code Owners"** (si vous avez un fichier `CODEOWNERS`)

---

### 3. Require conversation resolution before merging

**📍 Localisation** : Section **"Require conversation resolution before merging"**

**Actions** :
1. ✅ Cocher la case **"Require conversation resolution before merging"**

**Avantage** : Empêche le merge si des commentaires de review ne sont pas résolus.

---

### 4. Do not allow bypassing the above settings

**📍 Localisation** : Section **"Restrict who can push to matching branches"**

**Actions** :
1. ✅ Cocher la case **"Restrict who can push to matching branches"**
2. ✅ Cocher **"Do not allow bypassing the above settings"** (si disponible)

**⚠️ CRITIQUE** : Cette option empêche même les admins de bypasser les règles.  
**Recommandation** : Activer cette option pour garantir que personne ne peut contourner les règles de compliance.

---

## 🔍 Vérification des Workflows

### Workflows à Vérifier

Les workflows suivants doivent être **BLOQUANTS** (pas de `continue-on-error: true`) :

1. ✅ **`.github/workflows/audit-global.yml`**
   - Job `audit-static` : ✅ `continue-on-error: false`
   - Job `backend-compliance` : ✅ `continue-on-error: false`
   - Job `backend-permissions` : ✅ `continue-on-error: false`
   - Job `frontend-unit` : ✅ `continue-on-error: false`
   - Job `frontend-e2e-critical` : ✅ `continue-on-error: false`
   - Job `critical-compliance` : ✅ Bloque si un job échoue

2. ✅ **`.github/workflows/egoejo-compliance.yml`**
   - Job `egoejo-compliance` : ✅ Bloque si un test échoue
   - Step ESLint : ✅ Bloque si violation détectée (pas de `set +e`)

3. ✅ **`.github/workflows/pr-bot-home-vision.yml`**
   - Step audit : ✅ Bloque si statut != "compliant"

---

## 📊 Checklist de Configuration

### Configuration GitHub (Interface)

- [ ] Accéder à **Settings** → **Branches**
- [ ] Créer/Modifier la rule pour `main`
- [ ] Activer **"Require status checks to pass before merging"**
- [ ] Sélectionner les 6 jobs de `audit-global.yml` :
  - [ ] `audit-static`
  - [ ] `backend-compliance`
  - [ ] `backend-permissions`
  - [ ] `frontend-unit`
  - [ ] `frontend-e2e-critical`
  - [ ] `critical-compliance`
- [ ] Sélectionner le job de `egoejo-compliance.yml` :
  - [ ] `egoejo-compliance`
- [ ] Activer **"Require branches to be up to date before merging"**
- [ ] Activer **"Require pull request reviews before merging"**
- [ ] Activer **"Require conversation resolution before merging"**
- [ ] Activer **"Do not allow bypassing the above settings"** (si disponible)
- [ ] Sauvegarder les modifications

### Vérification des Workflows (Code)

- [ ] Vérifier que `audit-global.yml` n'a pas de `continue-on-error: true` sur les jobs critiques
- [ ] Vérifier que `egoejo-compliance.yml` bloque sur les violations ESLint
- [ ] Vérifier que `pr-bot-home-vision.yml` bloque sur les violations Home/Vision
- [ ] Tester avec une PR de test qui viole la compliance
- [ ] Confirmer que le merge est bloqué

---

## 🧪 Test de Validation

### Test 1 : Violation Compliance Backend

1. Créer une branche de test
2. Ajouter une violation SAKA/EUR dans le code backend (ex: `convert_saka_to_eur()`)
3. Créer une PR vers `main`
4. **Résultat attendu** : Les workflows `audit-global` et `egoejo-compliance` échouent
5. **Vérifier** : Le merge est bloqué par Branch Protection Rules

### Test 2 : Violation Compliance Frontend

1. Créer une branche de test
2. Ajouter un symbole monétaire dans le code frontend (ex: `"100 €"` dans un composant SAKA)
3. Créer une PR vers `main`
4. **Résultat attendu** : Le workflow `egoejo-compliance` échoue (ESLint)
5. **Vérifier** : Le merge est bloqué par Branch Protection Rules

### Test 3 : Tests E2E Critiques Échouent

1. Créer une branche de test
2. Casser un test E2E critique (ex: supprimer `transaction_type` dans un test)
3. Créer une PR vers `main`
4. **Résultat attendu** : Le workflow `audit-global` échoue (job `frontend-e2e-critical`)
5. **Vérifier** : Le merge est bloqué par Branch Protection Rules

---

## 📝 Notes Importantes

### Nom des Status Checks dans GitHub

Les noms des status checks dans GitHub peuvent varier selon :
- Le nom du workflow (fichier `.yml`)
- Le nom du job dans le workflow
- Les emojis dans les noms (peuvent être supprimés par GitHub)

**Pour trouver les noms exacts** :
1. Créer une PR de test
2. Aller dans l'onglet **Checks**
3. Noter les noms exacts des jobs
4. Utiliser ces noms dans Branch Protection Rules

### Workflows Multiples

Si plusieurs workflows doivent être requis, GitHub permet de sélectionner plusieurs status checks.  
**Recommandation** : Sélectionner tous les jobs critiques des workflows `audit-global.yml` et `egoejo-compliance.yml`.

### Bypass des Règles

**⚠️ CRITIQUE** : Si l'option **"Do not allow bypassing the above settings"** est disponible, l'activer pour empêcher même les admins de contourner les règles.

---

## 🔗 Références

- **Documentation GitHub** : [About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- **Workflow Principal** : `.github/workflows/audit-global.yml`
- **Workflow Compliance** : `.github/workflows/egoejo-compliance.yml`
- **Audit Final** : `docs/reports/AUDIT_FINAL_2025_01.md`

---

## ✅ Résultat Attendu

Une fois les Branch Protection Rules configurées :

1. ✅ **Aucun merge possible** si `audit-global.yml` échoue
2. ✅ **Aucun merge possible** si `egoejo-compliance.yml` échoue
3. ✅ **Aucun merge possible** si les tests E2E critiques échouent
4. ✅ **Aucun merge possible** si les tests de compliance backend échouent
5. ✅ **Aucun merge possible** si les tests de permissions backend échouent
6. ✅ **Aucun merge possible** si l'audit statique (mots interdits) échoue

**Le label EGOEJO est maintenant protégé à 100%.**

---

**Document généré le** : 2025-01-01  
**Statut** : ✅ **DOCUMENTATION CRÉÉE**


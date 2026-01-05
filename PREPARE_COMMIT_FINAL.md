# 🧹 GUIDE DE PRÉPARATION DU COMMIT FINAL - EGOEJO

**Date** : 2025-01-03  
**Objectif** : Nettoyer et organiser le dépôt avant le commit final de l'infrastructure de conformité

---

## 📋 ANALYSE DE L'ÉTAT ACTUEL

### ✅ Points Positifs
- Infrastructure CI complète (workflows GitHub Actions)
- Tests de compliance backend créés
- Documentation structurée dans `docs/`

### ⚠️ Points à Corriger

1. **Frontend** : Sous-module git avec modifications non commitées
2. **Fichiers à la racine** : 5 fichiers `AUDIT_*.md`, `RESUME_*.md`, `SYNTHESE_*.md` à déplacer
3. **Complétude CI** : Vérification des fichiers critiques manquants

---

## 🚨 ÉTAPE 1 : RÉSOUDRE LE PROBLÈME FRONTEND

### Diagnostic
Le frontend est un **sous-module git** (ou dépôt git séparé) avec :
- Des fichiers modifiés non commités dans le sous-module
- Des fichiers non trackés dans le sous-module
- Une branche `fix/hash-navigation-scroll` active

### Solution

**Option A : Si frontend est un sous-module git (recommandé)**

```powershell
# 1. Aller dans le sous-module frontend
cd frontend

# 2. Vérifier l'état
git status

# 3. Ajouter tous les fichiers non trackés
git add .

# 4. Commiter les changements dans le sous-module
git commit -m "feat: Infrastructure compliance EGOEJO - Tests, CI, Docs"

# 5. Pousser les changements du sous-module (si nécessaire)
git push origin fix/hash-navigation-scroll

# 6. Revenir à la racine
cd ..

# 7. Mettre à jour la référence du sous-module dans le dépôt parent
git add frontend
```

**Option B : Si frontend n'est PAS un sous-module (simple dossier)**

```powershell
# 1. Aller dans frontend
cd frontend

# 2. Initialiser git si nécessaire (ou vérifier s'il existe déjà)
git status

# 3. Si git n'est pas initialisé, initialiser
git init

# 4. Ajouter tous les fichiers
git add .

# 5. Commiter
git commit -m "feat: Infrastructure compliance EGOEJO - Tests, CI, Docs"

# 6. Revenir à la racine
cd ..

# 7. Ajouter frontend au .gitignore du dépôt parent (si vous ne voulez pas le tracker)
# OU ajouter frontend comme sous-module
```

**Option C : Si vous voulez tracker frontend directement dans le dépôt parent (pas de sous-module)**

```powershell
# 1. Supprimer le .git dans frontend (ATTENTION : sauvegarder d'abord)
cd frontend
Remove-Item -Recurse -Force .git
cd ..

# 2. Ajouter frontend au dépôt parent
git add frontend/
```

**⚠️ RECOMMANDATION** : Utiliser l'**Option A** si frontend est déjà un sous-module. Sinon, vérifier d'abord avec `cat .gitmodules` à la racine.

---

## 🧹 ÉTAPE 2 : NETTOYER LES FICHIERS À LA RACINE

### Fichiers à Déplacer

**Fichiers `AUDIT_*.md` à la racine** (5 fichiers) :
- `AUDIT_COMPLIANCE_PHILOSOPHIQUE.md`
- `AUDIT_COMPLIANCE_TESTS.md`
- `AUDIT_FINAL_EGOEJO_2025-01-27.md`
- `AUDIT_QUADRUPLE_EGOEJO_2025.md`
- `AUDIT_STRICT_EGOEJO_2025.md`

**Fichiers `RESUME_*.md` à la racine** (3 fichiers) :
- `RESUME_ACTIONS_GARDIEN.md`
- `RESUME_AUDIT_COMPLIANCE.md`
- `RESUME_TESTS_COMPLETS.md` (et `RESUME_TESTS_COMPLETS_2025-12-10.md`)

**Fichiers `SYNTHESE_*.md` à la racine** (2 fichiers) :
- `SYNTHESE_AUDIT_COMPLIANCE.md`
- `SYNTHESE_GARDIEN_PHILOSOPHIQUE.md`

**Autres fichiers à déplacer** :
- `PUBLICATION_STATUS.md` → `docs/reports/`
- `EGOEJO_ARCHITECTURE_CONSTITUTION.md` → `docs/architecture/` ou `docs/philosophie/`
- `PLAN_ACTION_GARDIEN_PHILOSOPHIQUE.md` → `docs/governance/` ou `docs/philosophie/`
- `README_MIGRATION_INFRA.md` → `docs/infrastructure/`

### Commandes PowerShell

```powershell
# Créer les dossiers si nécessaire
New-Item -ItemType Directory -Force -Path "docs/reports"
New-Item -ItemType Directory -Force -Path "docs/audit"
New-Item -ItemType Directory -Force -Path "docs/philosophie"

# Déplacer les fichiers AUDIT_*.md
Move-Item -Path "AUDIT_COMPLIANCE_PHILOSOPHIQUE.md" -Destination "docs/audit/"
Move-Item -Path "AUDIT_COMPLIANCE_TESTS.md" -Destination "docs/audit/"
Move-Item -Path "AUDIT_FINAL_EGOEJO_2025-01-27.md" -Destination "docs/reports/"
Move-Item -Path "AUDIT_QUADRUPLE_EGOEJO_2025.md" -Destination "docs/reports/"
Move-Item -Path "AUDIT_STRICT_EGOEJO_2025.md" -Destination "docs/reports/"

# Déplacer les fichiers RESUME_*.md
Move-Item -Path "RESUME_ACTIONS_GARDIEN.md" -Destination "docs/governance/"
Move-Item -Path "RESUME_AUDIT_COMPLIANCE.md" -Destination "docs/reports/"
Move-Item -Path "RESUME_TESTS_COMPLETS.md" -Destination "docs/tests/"
Move-Item -Path "RESUME_TESTS_COMPLETS_2025-12-10.md" -Destination "docs/tests/"

# Déplacer les fichiers SYNTHESE_*.md
Move-Item -Path "SYNTHESE_AUDIT_COMPLIANCE.md" -Destination "docs/reports/"
Move-Item -Path "SYNTHESE_GARDIEN_PHILOSOPHIQUE.md" -Destination "docs/governance/"

# Déplacer les autres fichiers
Move-Item -Path "PUBLICATION_STATUS.md" -Destination "docs/reports/"
Move-Item -Path "EGOEJO_ARCHITECTURE_CONSTITUTION.md" -Destination "docs/architecture/"
Move-Item -Path "PLAN_ACTION_GARDIEN_PHILOSOPHIQUE.md" -Destination "docs/governance/"
Move-Item -Path "README_MIGRATION_INFRA.md" -Destination "docs/infrastructure/"
```

---

## ✅ ÉTAPE 3 : VÉRIFIER LA COMPLÉTUDE CI

### Fichiers Critiques à Vérifier

#### 1. Variables d'Environnement
```powershell
# Vérifier si .env.example existe
Test-Path ".env.example"

# Si non, créer un .env.example avec les variables critiques
# (DJANGO_SECRET_KEY, E2E_TEST_MODE, ENABLE_SAKA, etc.)
```

#### 2. Scripts de Migration
```powershell
# Vérifier les scripts de migration backend
Test-Path "backend/scripts/migrate.sh"
Test-Path "backend/scripts/migrate.ps1"
```

#### 3. Fichiers de Configuration CI
```powershell
# Vérifier que tous les workflows sont présents
Test-Path ".github/workflows/audit-global.yml"
Test-Path ".github/workflows/egoejo-compliance.yml"
Test-Path ".github/workflows/pr-bot-home-vision.yml"
```

#### 4. Documentation CI
```powershell
# Vérifier la documentation CI
Test-Path "docs/ci/CRITICAL_COMPLIANCE_CI.md"
Test-Path "docs/governance/BRANCH_PROTECTION.md"
Test-Path "docs/governance/REQUIRED_CHECKS.md"
```

### Commandes de Vérification

```powershell
# Vérifier tous les fichiers critiques
$criticalFiles = @(
    ".github/workflows/audit-global.yml",
    ".github/workflows/egoejo-compliance.yml",
    ".github/workflows/pr-bot-home-vision.yml",
    "docs/governance/BRANCH_PROTECTION.md",
    "docs/governance/REQUIRED_CHECKS.md",
    "backend/core/tests/models/test_saka_wallet_update_prevention.py",
    "backend/core/tests/models/test_saka_wallet_raw_sql.py"
)

foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ $file MANQUANT" -ForegroundColor Red
    }
}
```

---

## 📝 ÉTAPE 4 : PRÉPARER LE COMMIT FINAL

### Séquence Complète

```powershell
# 1. Résoudre le problème frontend (voir ÉTAPE 1)
cd frontend
git add .
git commit -m "feat: Infrastructure compliance EGOEJO - Tests, CI, Docs"
cd ..

# 2. Nettoyer les fichiers à la racine (voir ÉTAPE 2)
# Exécuter les commandes Move-Item ci-dessus

# 3. Vérifier la complétude (voir ÉTAPE 3)
# Exécuter les commandes de vérification

# 4. Ajouter tous les fichiers au staging
git add .

# 5. Vérifier ce qui sera commité
git status

# 6. Créer le commit final
git commit -m "feat: Infrastructure complète de conformité EGOEJO

- Ajout workflows CI/CD bloquants (audit-global, egoejo-compliance, pr-bot)
- Tests de compliance backend (permissions, SAKA protection, raw SQL bypass)
- Tests de compliance frontend (Home/Vision, i18n, accessibility)
- Documentation gouvernance (Branch Protection, Required Checks)
- Documentation sécurité (Limites MANUAL_ADJUST, Protection SAKA Wallet)
- Documentation institutionnelle (Statut juridique SAKA)
- Scripts d'audit automatisés (audit-global, audit-home-vision)
- Tests E2E critiques (flux SAKA, flux projet financement)

BREAKING CHANGE: Les workflows CI sont maintenant bloquants. 
Les Branch Protection Rules doivent être configurées manuellement dans GitHub."
```

---

## 🎯 CHECKLIST FINALE AVANT COMMIT

- [ ] Frontend : Modifications commitées dans le sous-module
- [ ] Fichiers à la racine : Déplacés dans `docs/`
- [ ] `.env.example` : Créé avec les variables critiques
- [ ] Scripts de migration : Vérifiés/présents
- [ ] Workflows CI : Tous présents et fonctionnels
- [ ] Documentation CI : Complète
- [ ] Tests critiques : Tous présents
- [ ] `git status` : Propre (pas de fichiers non trackés critiques)
- [ ] `git diff --staged` : Vérifié (pas de fichiers sensibles)

---

## ⚠️ AVERTISSEMENTS

1. **Frontend** : Si frontend est un sous-module, ne pas oublier de commiter dans le sous-module AVANT de commiter dans le dépôt parent.

2. **Fichiers sensibles** : Vérifier qu'aucun fichier contenant des secrets n'est inclus (`.env`, `secrets.json`, etc.).

3. **Branch Protection** : Après le commit, configurer manuellement les Branch Protection Rules dans GitHub (voir `docs/governance/BRANCH_PROTECTION.md`).

---

**Document généré le** : 2025-01-03  
**Statut** : ✅ **PRÊT POUR EXÉCUTION**


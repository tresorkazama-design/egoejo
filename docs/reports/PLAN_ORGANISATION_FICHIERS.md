# 📋 Plan d'Organisation des Fichiers Non Suivis

**Date** : 17 Décembre 2025

---

## 🎯 Recommandation : Approche en 3 catégories

### ✅ **CATÉGORIE 1 : À COMMITTER** (Documentation importante)

Ces fichiers sont utiles pour l'équipe et doivent être dans le repo :

#### Documentation d'architecture
- ✅ `docs/architecture/ARCHITECTURE_V2_SCALE.md`
- ✅ `docs/architecture/PROTOCOLE_SAKA_PHILOSOPHIE.md` (très important pour EGOEJO)
- ✅ `docs/architecture/PROTOCOLE_SAKA_V2.1.md`
- ✅ `docs/architecture/VUE_ENSEMBLE_CODE_EGOEJO.md`

#### Guides
- ✅ `docs/guides/API_CONTENT_ENGAGEMENT.md`

#### Rapports d'audit et d'analyse
- ✅ `docs/reports/ANALYSE_ARCHITECTURE_2025-12-16.md`
- ✅ `docs/reports/ANALYSE_ARCHITECTURE_BACKEND_2025-12-16.md`
- ✅ `docs/reports/ANALYSE_ARCHITECTURE_FRONTEND_2025-12-16.md`
- ✅ `docs/reports/ANALYSE_COUVERTURE_TESTS_2025-12-16.md`
- ✅ `docs/reports/ANALYSE_ECHECS_TESTS_E2E_DETAILLEE_2025-12-17.md`
- ✅ `docs/reports/ANALYSE_LOGIQUE_METIER_2025-12-16.md`
- ✅ `docs/reports/ANALYSE_TESTS_E2E_2025-12-17.md`
- ✅ `docs/reports/AUDIT_COMPLET_EGOEJO_2025-12-16.md`
- ✅ `docs/reports/AUDIT_CONFORMITE_EGOEJO.md`
- ✅ `docs/reports/AUDIT_EGOEJO_12_DECEMBRE.md`
- ✅ `docs/reports/CARTOGRAPHIE_PROJET_EGOEJO.md`
- ✅ `docs/reports/CORRECTIONS_FINALES_TESTS_E2E_2025-12-17.md`
- ✅ `docs/reports/CORRECTIONS_TESTS_E2E_APPLIQUEES_2025-12-17.md`
- ✅ `docs/reports/ETAT_GENERAL_CONSOLIDE_2025-12-17.md`
- ✅ `docs/reports/RAPPORT_FINAL_TESTS_E2E_2025-12-17.md`
- ✅ `docs/reports/RAPPORT_TESTS_P0_2025-12-17.md`
- ✅ `docs/reports/RESUME_SESSION_2025-12-16.md`
- ✅ `docs/reports/SUGGESTIONS_FINALES_TESTS_E2E_2025-12-17.md`
- ✅ `docs/reports/SYNTHESE_AUDIT_CODE_2025-12-16.md`
- ✅ `docs/reports/SYNTHESE_AUDIT_CODE_2025-12-16_V2.md`

#### Documentation de tests
- ✅ `docs/tests/AUDIT_TESTS_BACKEND_2025-12-16.md`
- ✅ `docs/tests/AUDIT_TESTS_FRONTEND_2025-01-16.md`
- ✅ `docs/tests/TESTS_BACKEND.md`
- ✅ `docs/tests/TESTS_FRONTEND.md`

---

### 🗑️ **CATÉGORIE 2 : À IGNORER/SUPPRIMER** (Fichiers temporaires)

Ces fichiers étaient pour une tâche ponctuelle (commit frontend E2E) :

#### Scripts temporaires
- ❌ `commit-frontend-e2e.ps1`
- ❌ `commit-frontend-e2e-simple.ps1`

#### Diagnostics temporaires
- ❌ `DIAGNOSTIC_FRONTEND_SUBMODULE.md`
- ❌ `PROBLEME_COMMIT_FRONTEND_E2E.md`
- ❌ `VERIFICATION_FICHIER_E2E.md`
- ❌ `GUIDE_COMMIT_FRONTEND_E2E.md`
- ❌ `GUIDE_MANUEL_COMMIT_FRONTEND_E2E.md`
- ❌ `README_COMMIT_FRONTEND_E2E.md`
- ❌ `RESUME_COMMIT_FRONTEND_E2E_REUSSI.md`

#### Fichiers de commit temporaires
- ❌ `.gitmessage_egoejo.txt`
- ❌ `COMMIT_MESSAGE.md`
- ❌ `ETAT_EGOEJO_2025-12-12.md` (peut-être à archiver dans docs/reports/)

---

## 🚀 Plan d'action recommandé

### Option A : Committer la documentation importante (Recommandé)

```powershell
# Ajouter la documentation importante
git add docs/architecture/*.md
git add docs/guides/*.md
git add docs/reports/*.md
git add docs/tests/*.md

# Committer
git commit -m "docs: Ajout documentation architecture, guides et rapports d'audit

- Documentation protocole SAKA et philosophie EGOEJO
- Guides API et architecture
- Rapports d'audit et d'analyse complets
- Documentation des tests backend et frontend"

# Pousser
git push origin main
```

### Option B : Ajouter les fichiers temporaires au .gitignore

Ajouter dans `.gitignore` :
```
# Fichiers temporaires de diagnostic
DIAGNOSTIC_*.md
PROBLEME_*.md
VERIFICATION_*.md
GUIDE_COMMIT_*.md
README_COMMIT_*.md
RESUME_COMMIT_*.md
*.gitmessage*.txt
COMMIT_MESSAGE.md

# Scripts temporaires
commit-*.ps1
```

---

## 💡 Ma recommandation finale

**Je recommande l'Option A** car :

1. ✅ La documentation d'architecture (surtout `PROTOCOLE_SAKA_PHILOSOPHIE.md`) est **cruciale** pour comprendre EGOEJO
2. ✅ Les rapports d'audit sont utiles pour l'historique et la traçabilité
3. ✅ Les guides API sont utiles pour les développeurs
4. ❌ Les fichiers temporaires de diagnostic peuvent être supprimés (ils ont servi leur but)

**Action suggérée** :
1. Committer la documentation importante (Option A)
2. Supprimer les fichiers temporaires (scripts et diagnostics)
3. Optionnel : Ajouter un pattern au `.gitignore` pour éviter les fichiers similaires à l'avenir

---

## 📊 Statistiques

- **Fichiers à committer** : ~30 fichiers de documentation
- **Fichiers à supprimer** : ~10 fichiers temporaires
- **Impact** : Documentation complète dans le repo, environnement propre


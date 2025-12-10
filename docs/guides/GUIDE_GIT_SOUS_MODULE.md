# Guide Git - Gestion du Sous-module Frontend

## 🔍 Problème identifié

Le dossier `frontend` est un **sous-module Git**, ce qui signifie qu'il a son propre dépôt Git séparé. Vous ne pouvez pas directement ajouter des fichiers du frontend depuis la racine du projet.

## ✅ Solution : Commiter séparément

### Étape 1 : Commiter les changements backend (à la racine)

```powershell
# Vous êtes déjà à la racine
cd C:\Users\treso\Downloads\egoejo

# Ajouter les fichiers backend
git add backend/
git add CONFIGURATION_SENTRY_VERCEL.md
git add backend/ENDPOINTS_MONITORING.md
git add GUIDE_ACHAT_NOM_DOMAINE.md

# Commiter
git commit -m "feat: Ajout monitoring backend, endpoints API, sécurité renforcée"

# Pousser
git push origin main
```

### Étape 2 : Commiter les changements frontend (dans le sous-module)

```powershell
# Aller dans le sous-module frontend
cd frontend

# Vérifier le statut
git status

# Ajouter les fichiers
git add .

# Commiter
git commit -m "feat: Ajout monitoring, tests E2E et corrections build Vercel"

# Pousser (créer la branche upstream si nécessaire)
git push --set-upstream origin frontend_ui_refonte
# OU si vous êtes sur main:
git push origin main
```

### Étape 3 : Mettre à jour le sous-module dans le repo principal

```powershell
# Revenir à la racine
cd ..

# Mettre à jour la référence du sous-module
git add frontend

# Commiter la mise à jour
git commit -m "chore: Mise à jour sous-module frontend"

# Pousser
git push origin main
```

## 🔧 Commandes complètes (copier-coller)

### Pour le backend (racine)

```powershell
cd C:\Users\treso\Downloads\egoejo
git add backend/ CONFIGURATION_SENTRY_VERCEL.md backend/ENDPOINTS_MONITORING.md GUIDE_ACHAT_NOM_DOMAINE.md
git commit -m "feat: Ajout monitoring backend, endpoints API, sécurité renforcée"
git push origin main
```

### Pour le frontend (sous-module)

```powershell
cd C:\Users\treso\Downloads\egoejo\frontend
git add .
git commit -m "feat: Ajout monitoring, tests E2E et corrections build Vercel"
git push --set-upstream origin frontend_ui_refonte
```

### Pour mettre à jour le sous-module (racine)

```powershell
cd C:\Users\treso\Downloads\egoejo
git add frontend
git commit -m "chore: Mise à jour sous-module frontend"
git push origin main
```

## 📋 Vérification

### Vérifier le statut du sous-module

```powershell
cd C:\Users\treso\Downloads\egoejo
git submodule status
```

### Vérifier la branche du frontend

```powershell
cd C:\Users\treso\Downloads\egoejo\frontend
git branch
git status
```

## ⚠️ Notes importantes

1. **Deux dépôts séparés** : Le frontend a son propre dépôt Git
2. **Branches différentes** : Le frontend peut être sur une branche différente (`frontend_ui_refonte`)
3. **Commits séparés** : Il faut commiter dans chaque dépôt séparément
4. **Mise à jour du sous-module** : Après avoir poussé le frontend, mettre à jour la référence dans le repo principal

## 🚀 Alternative : Fusionner les dépôts

Si vous voulez éviter la gestion des sous-modules, vous pouvez :

1. Supprimer le sous-module et intégrer le frontend directement
2. Ou continuer avec les sous-modules (recommandé si le frontend est un projet séparé)

## 📝 Commandes rapides

**Backend uniquement** :
```powershell
cd C:\Users\treso\Downloads\egoejo
git add backend/ *.md
git commit -m "feat: Backend monitoring et sécurité"
git push origin main
```

**Frontend uniquement** :
```powershell
cd C:\Users\treso\Downloads\egoejo\frontend
git add .
git commit -m "feat: Frontend monitoring et tests E2E"
git push --set-upstream origin frontend_ui_refonte
```


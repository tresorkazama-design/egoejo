# 🔐 Authentification GitHub CLI - EGOEJO

**Date** : 2025-01-27  
**Version** : 1.0.0

---

## ⚠️ Problème

Si vous voyez ce message :
```
To get started with GitHub CLI, please run:  gh auth login
```

Cela signifie que vous n'êtes pas authentifié avec GitHub CLI.

---

## ✅ Solution

### Méthode 1 : Authentification Interactive (Recommandé)

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Se connecter à GitHub
gh auth login
```

**Étapes** :
1. Choisir `GitHub.com`
2. Choisir `HTTPS` ou `SSH`
3. Choisir `Login with a web browser`
4. Appuyer sur `Enter` pour ouvrir le navigateur
5. Autoriser GitHub CLI
6. Revenir au terminal

### Méthode 2 : Token Personnel

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Se connecter avec un token
gh auth login --with-token
# Puis coller votre token GitHub
```

**Obtenir un token** :
1. Aller sur : https://github.com/settings/tokens
2. Cliquer sur "Generate new token (classic)"
3. Nommer le token (ex: `gh-cli`)
4. Sélectionner les scopes : `repo`, `workflow`, `write:packages`
5. Générer et copier le token
6. Coller dans le terminal

### Méthode 3 : Variable d'Environnement

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Définir la variable d'environnement
$env:GH_TOKEN = "votre-token-github-ici"

# Vérifier
gh auth status
```

---

## ✅ Vérification

### Vérifier la connexion

```powershell
cd C:\Users\treso\Downloads\egoejo
gh auth status
```

**Résultat attendu** :
```
✓ Logged in to github.com as [votre-username]
✓ Git operations for github.com configured to use https protocol
✓ Token: *******************
```

---

## 🚀 Après Authentification

Une fois authentifié, vous pouvez configurer les secrets :

```powershell
cd C:\Users\treso\Downloads\egoejo

# Utiliser le script automatisé
.\config-secrets.ps1

# OU configurer manuellement
gh secret set VERCEL_TOKEN --body "votre-token"
gh secret set VERCEL_ORG_ID --body "votre-org-id"
# etc...
```

---

## 📚 Documentation

- `COMMANDES_SECRETS_GITHUB.md` - Commandes pour configurer les secrets
- `CONFIGURER_SECRETS_GITHUB.md` - Guide détaillé
- `config-secrets.ps1` - Script automatisé

---

**Une fois authentifié, vous pouvez configurer tous les secrets !** ✅


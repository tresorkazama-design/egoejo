# 🔐 Commandes pour Configurer les Secrets GitHub

**Date** : 2025-01-27  
**Version** : 1.0.0

---

## 📋 Prérequis

### Installer GitHub CLI

```powershell
# Option 1 : Winget
winget install --id GitHub.cli

# Option 2 : Chocolatey
choco install gh

# Vérifier l'installation
gh --version
```

### ⚠️ IMPORTANT : Se connecter à GitHub

**AVANT de configurer les secrets, vous DEVEZ vous authentifier :**

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Se connecter à GitHub
gh auth login
```

**Suivre les instructions** :
1. Choisir `GitHub.com`
2. Choisir `HTTPS`
3. Choisir `Login with a web browser`
4. Appuyer sur `Enter`
5. Autoriser dans le navigateur
6. Revenir au terminal

**Vérifier la connexion** :
```powershell
gh auth status
```

Si vous voyez `✓ Logged in to github.com`, vous êtes prêt !

---

## 🔑 Commandes par Secret

### 1. VERCEL_TOKEN

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Configurer le secret
gh secret set VERCEL_TOKEN --body "votre-token-vercel-ici"
```

**Obtenir le token** : https://vercel.com/account/tokens

---

### 2. VERCEL_ORG_ID

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Configurer le secret
gh secret set VERCEL_ORG_ID --body "votre-org-id-ici"
```

**Obtenir l'Org ID** : https://vercel.com/[votre-org]/settings

---

### 3. VERCEL_PROJECT_ID

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Configurer le secret
gh secret set VERCEL_PROJECT_ID --body "votre-project-id-ici"
```

**Obtenir le Project ID** : https://vercel.com/[votre-org]/[votre-projet]/settings

---

### 4. RAILWAY_TOKEN

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Configurer le secret
gh secret set RAILWAY_TOKEN --body "votre-token-railway-ici"
```

**Obtenir le token** : https://railway.app/account/tokens

---

### 5. RAILWAY_SERVICE_ID

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Configurer le secret
gh secret set RAILWAY_SERVICE_ID --body "votre-service-id-ici"
```

**Obtenir le Service ID** : https://railway.app/dashboard → Projet → Service → Settings

---

### 6. DJANGO_SECRET_KEY

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Générer un secret key sécurisé
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Configurer le secret (remplacer par la valeur générée)
gh secret set DJANGO_SECRET_KEY --body "votre-secret-key-genere-ici"
```

**Exemple de secret key généré** : `hRp-RJO_MHlpD5rs4KLQRdiGX37Rz30kHNW7Wkodatv0A7rnBhQ5BgmCtIWcFw9B89c`

---

## ✅ Vérification

### Lister tous les secrets configurés

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Lister les secrets
gh secret list
```

---

## 🚀 Script Automatisé

### Utiliser le script PowerShell

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Exécuter le script
.\config-secrets.ps1
```

Le script vous guidera étape par étape pour configurer tous les secrets.

---

## 📋 Checklist

- [ ] VERCEL_TOKEN configuré
- [ ] VERCEL_ORG_ID configuré
- [ ] VERCEL_PROJECT_ID configuré
- [ ] RAILWAY_TOKEN configuré
- [ ] RAILWAY_SERVICE_ID configuré
- [ ] DJANGO_SECRET_KEY configuré
- [ ] Vérification avec `gh secret list`

---

## 📚 Documentation

- `CONFIGURER_SECRETS_GITHUB.md` - Guide détaillé
- `config-secrets.ps1` - Script automatisé
- `GUIDE_PRODUCTION.md` - Guide de production
- `VARIABLES_PRODUCTION.md` - Variables d'environnement

---

**Toutes les commandes sont prêtes !** ✅


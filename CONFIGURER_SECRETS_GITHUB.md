# 🔐 Configuration des Secrets GitHub - EGOEJO

**Date** : 2025-01-27  
**Version** : 1.0.0

---

## 📋 Prérequis

### Option 1 : GitHub CLI (Recommandé)

```powershell
# Installer GitHub CLI si nécessaire
winget install --id GitHub.cli
# OU
choco install gh

# Vérifier l'installation
gh --version

# Se connecter à GitHub
gh auth login
```

### Option 2 : Interface Web GitHub

Accéder à : `https://github.com/[votre-username]/egoejo/settings/secrets/actions`

---

## 🔑 Secrets à Configurer

### 1. VERCEL_TOKEN

#### Obtenir le Token Vercel

1. Aller sur https://vercel.com/account/tokens
2. Cliquer sur "Create Token"
3. Nommer le token (ex: `egoejo-deployment`)
4. Copier le token généré

#### Configurer via GitHub CLI

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Configurer le secret
gh secret set VERCEL_TOKEN --body "votre-token-vercel-ici"
```

#### Configurer via Interface Web

1. Aller sur : `https://github.com/[votre-username]/egoejo/settings/secrets/actions`
2. Cliquer sur "New repository secret"
3. Nom : `VERCEL_TOKEN`
4. Valeur : Coller le token Vercel
5. Cliquer sur "Add secret"

---

### 2. VERCEL_ORG_ID

#### Obtenir l'Org ID Vercel

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Installer Vercel CLI si nécessaire
npm install -g vercel

# Se connecter à Vercel
vercel login

# Lister les projets (affiche l'Org ID)
vercel projects list
```

**OU** via l'interface Vercel :
1. Aller sur https://vercel.com/[votre-org]/settings
2. L'Org ID est visible dans l'URL ou dans les paramètres

#### Configurer via GitHub CLI

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Configurer le secret
gh secret set VERCEL_ORG_ID --body "votre-org-id-ici"
```

#### Configurer via Interface Web

1. Aller sur : `https://github.com/[votre-username]/egoejo/settings/secrets/actions`
2. Cliquer sur "New repository secret"
3. Nom : `VERCEL_ORG_ID`
4. Valeur : Coller l'Org ID
5. Cliquer sur "Add secret"

---

### 3. VERCEL_PROJECT_ID

#### Obtenir le Project ID Vercel

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Si Vercel CLI est installé
cd frontend\frontend
vercel link
# OU
vercel projects list
```

**OU** via l'interface Vercel :
1. Aller sur https://vercel.com/[votre-org]/[votre-projet]/settings
2. Le Project ID est visible dans les paramètres du projet

#### Configurer via GitHub CLI

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Configurer le secret
gh secret set VERCEL_PROJECT_ID --body "votre-project-id-ici"
```

#### Configurer via Interface Web

1. Aller sur : `https://github.com/[votre-username]/egoejo/settings/secrets/actions`
2. Cliquer sur "New repository secret"
3. Nom : `VERCEL_PROJECT_ID`
4. Valeur : Coller le Project ID
5. Cliquer sur "Add secret"

---

### 4. RAILWAY_TOKEN

#### Obtenir le Token Railway

1. Aller sur https://railway.app/account/tokens
2. Cliquer sur "New Token"
3. Nommer le token (ex: `egoejo-deployment`)
4. Copier le token généré

#### Configurer via GitHub CLI

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Configurer le secret
gh secret set RAILWAY_TOKEN --body "votre-token-railway-ici"
```

#### Configurer via Interface Web

1. Aller sur : `https://github.com/[votre-username]/egoejo/settings/secrets/actions`
2. Cliquer sur "New repository secret"
3. Nom : `RAILWAY_TOKEN`
4. Valeur : Coller le token Railway
5. Cliquer sur "Add secret"

---

### 5. RAILWAY_SERVICE_ID

#### Obtenir le Service ID Railway

1. Aller sur https://railway.app/dashboard
2. Sélectionner votre projet
3. Sélectionner le service backend
4. Aller dans "Settings" → "General"
5. Le Service ID est visible (format : `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

**OU** via Railway CLI :

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Installer Railway CLI si nécessaire
npm install -g @railway/cli

# Se connecter
railway login

# Lister les services
railway service list
```

#### Configurer via GitHub CLI

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Configurer le secret
gh secret set RAILWAY_SERVICE_ID --body "votre-service-id-ici"
```

#### Configurer via Interface Web

1. Aller sur : `https://github.com/[votre-username]/egoejo/settings/secrets/actions`
2. Cliquer sur "New repository secret"
3. Nom : `RAILWAY_SERVICE_ID`
4. Valeur : Coller le Service ID
5. Cliquer sur "Add secret"

---

### 6. DJANGO_SECRET_KEY

#### Générer le Secret Key

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Générer un secret key sécurisé (50+ caractères)
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

**Exemple généré** : `hRp-RJO_MHlpD5rs4KLQRdiGX37Rz30kHNW7Wkodatv0A7rnBhQ5BgmCtIWcFw9B89c`

⚠️ **IMPORTANT** : Utilisez une clé unique et sécurisée pour la production !

#### Configurer via GitHub CLI

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Configurer le secret
gh secret set DJANGO_SECRET_KEY --body "votre-secret-key-ici"
```

#### Configurer via Interface Web

1. Aller sur : `https://github.com/[votre-username]/egoejo/settings/secrets/actions`
2. Cliquer sur "New repository secret"
3. Nom : `DJANGO_SECRET_KEY`
4. Valeur : Coller le secret key généré
5. Cliquer sur "Add secret"

---

## ✅ Vérification

### Vérifier tous les secrets configurés

```powershell
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

# Lister tous les secrets (via GitHub CLI)
gh secret list
```

### Secrets Requis

- ✅ `VERCEL_TOKEN`
- ✅ `VERCEL_ORG_ID`
- ✅ `VERCEL_PROJECT_ID`
- ✅ `RAILWAY_TOKEN`
- ✅ `RAILWAY_SERVICE_ID`
- ✅ `DJANGO_SECRET_KEY`

---

## 🚀 Script Automatisé (Optionnel)

Créer un script PowerShell pour configurer tous les secrets :

```powershell
# config-secrets.ps1
# Se placer à la racine du projet
cd C:\Users\treso\Downloads\egoejo

Write-Host "=== Configuration des Secrets GitHub ===" -ForegroundColor Cyan
Write-Host ""

# VERCEL_TOKEN
$vercelToken = Read-Host "Entrez votre VERCEL_TOKEN"
gh secret set VERCEL_TOKEN --body $vercelToken

# VERCEL_ORG_ID
$vercelOrgId = Read-Host "Entrez votre VERCEL_ORG_ID"
gh secret set VERCEL_ORG_ID --body $vercelOrgId

# VERCEL_PROJECT_ID
$vercelProjectId = Read-Host "Entrez votre VERCEL_PROJECT_ID"
gh secret set VERCEL_PROJECT_ID --body $vercelProjectId

# RAILWAY_TOKEN
$railwayToken = Read-Host "Entrez votre RAILWAY_TOKEN"
gh secret set RAILWAY_TOKEN --body $railwayToken

# RAILWAY_SERVICE_ID
$railwayServiceId = Read-Host "Entrez votre RAILWAY_SERVICE_ID"
gh secret set RAILWAY_SERVICE_ID --body $railwayServiceId

# DJANGO_SECRET_KEY
Write-Host "Génération du DJANGO_SECRET_KEY..." -ForegroundColor Yellow
$djangoSecretKey = python -c "import secrets; print(secrets.token_urlsafe(50))"
Write-Host "Secret Key généré : $djangoSecretKey" -ForegroundColor Green
gh secret set DJANGO_SECRET_KEY --body $djangoSecretKey

Write-Host ""
Write-Host "✅ Tous les secrets sont configurés !" -ForegroundColor Green
```

---

## 📚 Documentation

- `GUIDE_PRODUCTION.md` - Guide complet de production
- `VARIABLES_PRODUCTION.md` - Variables d'environnement
- `CHECKLIST_PRODUCTION.md` - Checklist de vérification

---

**Tous les secrets sont configurés !** ✅


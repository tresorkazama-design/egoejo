# 🚀 Pousser les changements sur GitHub pour Railway

## ✅ Option 1 : Si vous avez déjà un dépôt GitHub connecté à Railway

### 📋 Étape 1 : Trouver le dépôt GitHub

1. **Ouvrez Railway** dans votre navigateur : https://railway.app
2. **Allez dans votre projet** → Service **"egoego"**
3. **Cliquez sur "Settings"** (en haut)
4. **Cliquez sur "Source"** (dans la sidebar de gauche)
5. **Vous verrez votre dépôt GitHub** connecté (ex: `username/egoejo`)

### 📋 Étape 2 : Cloner le dépôt GitHub (si nécessaire)

Si vous n'avez pas le dépôt localement, ouvrez un terminal PowerShell et exécutez :

```powershell
cd C:\Users\treso\Downloads
git clone https://github.com/VOTRE_USERNAME/egoejo.git
cd egoejo
```

**Remplacez `VOTRE_USERNAME` par votre nom d'utilisateur GitHub et `egoejo` par le nom de votre dépôt.**

### 📋 Étape 3 : Copier les fichiers modifiés dans le dépôt cloné

Copiez les fichiers suivants depuis `C:\Users\treso\Downloads\egoejo` vers votre dépôt cloné :
- `backend/config/urls.py`
- `backend/config/settings.py`
- `railway.toml`

### 📋 Étape 4 : Ajouter, commiter et pousser

```powershell
git add backend/config/urls.py backend/config/settings.py railway.toml
git commit -m "fix: ajout healthcheck et optimisation connexion DB pour Railway"
git push origin main
```

---

## ✅ Option 2 : Initialiser un nouveau dépôt Git et connecter à GitHub

### 📋 Étape 1 : Initialiser Git dans le dossier actuel

```powershell
cd C:\Users\treso\Downloads\egoejo
git init
```

### 📋 Étape 2 : Créer un fichier `.gitignore` (si nécessaire)

Créez un fichier `.gitignore` avec ce contenu :

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
htmlcov/
.coverage
*.log

# Node
node_modules/
dist/
.npm

# Database
*.db
*.sqlite3

# Environment
.env
.env.local

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

### 📋 Étape 3 : Créer un dépôt sur GitHub

1. **Ouvrez GitHub** dans votre navigateur : https://github.com
2. **Cliquez sur "+"** (en haut à droite) → **"New repository"**
3. **Remplissez** :
   - **Repository name** : `egoejo`
   - **Description** : `EGOEJO Project`
   - **Visibility** : Private (ou Public, selon vos préférences)
   - **Ne cochez PAS** "Initialize this repository with a README"
4. **Cliquez sur "Create repository"**

### 📋 Étape 4 : Connecter le dépôt local à GitHub

**Remplacez `VOTRE_USERNAME` par votre nom d'utilisateur GitHub dans ces commandes :**

```powershell
git add .
git commit -m "Initial commit: EGOEJO project with healthcheck"
git branch -M main
git remote add origin https://github.com/VOTRE_USERNAME/egoejo.git
git push -u origin main
```

### 📋 Étape 5 : Connecter Railway au dépôt GitHub

1. **Ouvrez Railway** dans votre navigateur : https://railway.app
2. **Allez dans votre projet** → Service **"egoego"**
3. **Cliquez sur "Settings"** (en haut)
4. **Cliquez sur "Source"** (dans la sidebar de gauche)
5. **Cliquez sur "Connect Repo"** ou **"Change Source"**
6. **Sélectionnez votre dépôt GitHub** `username/egoejo`
7. **Cliquez sur "Deploy"** ou **"Save"**

---

## ✅ Option 3 : Déployer manuellement via Railway CLI

Si vous préférez ne pas utiliser GitHub pour le moment, vous pouvez déployer manuellement via Railway CLI.

### 📋 Étape 1 : Installer Railway CLI

```powershell
npm install -g @railway/cli
```

### 📋 Étape 2 : Se connecter à Railway

```powershell
railway login
```

### 📋 Étape 3 : Déployer le service

```powershell
cd C:\Users\treso\Downloads\egoejo
railway up
```

---

## ✅ Après avoir poussé les changements

### 📋 Vérifier que Railway redéploie automatiquement

1. **Ouvrez Railway** dans votre navigateur : https://railway.app
2. **Allez dans votre projet** → Service **"egoego"**
3. **Cliquez sur l'onglet "Deployments"** (en haut)
4. **Vérifiez que le dernier déploiement** :
   - Est en cours (icône jaune 🔄) ou terminé (icône verte ✓)
   - Utilise le dernier commit avec le message "fix: ajout healthcheck..."

### 📋 Attendre 2-5 minutes

Attendez que Railway termine le déploiement (2-5 minutes).

### 📋 Tester le healthcheck

Une fois le déploiement terminé, testez l'endpoint de healthcheck :

**Dans votre navigateur** :
```
https://egoego-production.up.railway.app/api/health/
```

**Vous devriez voir** :
```json
{"status": "ok", "database": "connected"}
```

---

## 🆘 Si vous ne savez pas quelle option choisir

**Recommandation** : Utilisez l'**Option 1** si vous avez déjà un dépôt GitHub connecté à Railway, sinon utilisez l'**Option 2** pour créer un nouveau dépôt.

---

**🚀 Dites-moi quelle option vous choisissez et je vous guiderai étape par étape !**


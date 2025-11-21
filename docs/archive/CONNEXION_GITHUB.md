# 🔗 Connexion à GitHub - Instructions

## ✅ Dépôt Git initialisé et commit créé !

Les changements ont été ajoutés et committés localement.

## 📋 Prochaines étapes : Créer un dépôt GitHub et pousser les changements

### Étape 1 : Créer un dépôt sur GitHub

1. **Ouvrez GitHub** dans votre navigateur : https://github.com
2. **Connectez-vous** à votre compte GitHub
3. **Cliquez sur "+"** (en haut à droite) → **"New repository"**
4. **Remplissez le formulaire** :
   - **Repository name** : `egoejo`
   - **Description** : `EGOEJO Project - Backend Django + Frontend React`
   - **Visibility** : 
     - ✅ **Private** (recommandé pour un projet privé)
     - ○ Public (si vous voulez le rendre public)
   - ❌ **Ne cochez PAS** "Add a README file"
   - ❌ **Ne cochez PAS** "Add .gitignore"
   - ❌ **Ne cochez PAS** "Choose a license"
5. **Cliquez sur "Create repository"**

### Étape 2 : Connecter le dépôt local à GitHub

**Après avoir créé le dépôt sur GitHub**, vous verrez une page avec des instructions.

**Remplacez `VOTRE_USERNAME` par votre nom d'utilisateur GitHub** dans ces commandes :

```powershell
git remote add origin https://github.com/VOTRE_USERNAME/egoejo.git
git push -u origin main
```

**Exemple** si votre nom d'utilisateur est `treso` :
```powershell
git remote add origin https://github.com/treso/egoejo.git
git push -u origin main
```

### Étape 3 : Vérifier que Railway est connecté au dépôt GitHub

1. **Ouvrez Railway** dans votre navigateur : https://railway.app
2. **Allez dans votre projet** → Service **"egoego"**
3. **Cliquez sur "Settings"** (en haut)
4. **Cliquez sur "Source"** (dans la sidebar de gauche)
5. **Vérifiez que** :
   - Le dépôt GitHub est connecté (ex: `username/egoejo`)
   - La branche est `main`
   - Le "Root Directory" est `backend` (ou vide si le Dockerfile est à la racine)

**Si Railway n'est pas connecté au dépôt GitHub** :
6. **Cliquez sur "Connect Repo"** ou **"Change Source"**
7. **Sélectionnez votre dépôt GitHub** `username/egoejo`
8. **Configurez** :
   - **Root Directory** : `backend` (ou vide)
   - **Branch** : `main`
9. **Cliquez sur "Deploy"** ou **"Save"**

### Étape 4 : Attendre que Railway redéploie automatiquement

Une fois que Railway est connecté au dépôt GitHub :

1. **Railway détectera automatiquement** le nouveau commit
2. **Le service redéploiera** avec les nouvelles configurations
3. **Attendez 2-5 minutes** que le déploiement se termine

### Étape 5 : Vérifier le déploiement dans Railway

1. **Dans Railway** → Service **"egoego"** → **"Deployments"**
2. **Vérifiez que le dernier déploiement** :
   - Est en cours (icône jaune 🔄) ou terminé (icône verte ✓)
   - Utilise le dernier commit avec le message "fix: ajout healthcheck..."
   - Montre "Deployed" ou "Active"

### Étape 6 : Tester le healthcheck

Une fois le déploiement terminé, testez l'endpoint de healthcheck :

**Dans votre navigateur** :
```
https://egoego-production.up.railway.app/api/health/
```

**Vous devriez voir** :
```json
{"status": "ok", "database": "connected"}
```

Si vous voyez toujours "Not Found", attendez encore 1-2 minutes et réessayez.

---

## 🆘 Si vous avez besoin d'aide

**Si vous ne savez pas comment créer un dépôt GitHub** :
1. Allez sur https://github.com
2. Connectez-vous à votre compte
3. Cliquez sur le bouton "+" en haut à droite
4. Suivez les instructions ci-dessus

**Si vous avez besoin de votre nom d'utilisateur GitHub** :
1. Allez sur https://github.com
2. Connectez-vous à votre compte
3. Votre nom d'utilisateur est visible en haut à droite (icône de profil)

**Si Railway ne se connecte pas automatiquement au dépôt** :
- Vérifiez que Railway a accès à votre compte GitHub (Settings → Connected Accounts)
- Assurez-vous que le dépôt GitHub est bien créé et accessible

---

**🚀 Une fois que vous avez créé le dépôt GitHub, dites-moi votre nom d'utilisateur et je vous donnerai les commandes exactes à exécuter !**


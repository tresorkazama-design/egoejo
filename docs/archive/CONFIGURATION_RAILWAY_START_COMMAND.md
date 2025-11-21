# 🔧 Configuration de la commande de démarrage Railway

## ❌ Problème identifié

Daphne ne démarre pas après les migrations, même si le `startCommand` est défini dans `railway.toml`.

## ✅ Solution : Configurer la commande directement dans Railway

Railway peut ignorer le `startCommand` de `railway.toml` dans certains cas. Il faut configurer la commande directement dans les paramètres Railway.

---

## 📋 Étape par étape : Configurer la commande de démarrage dans Railway

### Étape 1 : Accéder aux paramètres Railway

1. **Ouvrez Railway** : https://railway.app
2. **Allez dans votre projet** → Service **"egoejo"**
3. **Cliquez sur "Settings"** (Paramètres) en haut
4. **Cliquez sur "General"** (Général) dans la sidebar de gauche

### Étape 2 : Configurer la commande de démarrage

1. **Dans la section "Start Command"** ou **"Command"** :
   - **Cherchez un champ** qui dit "Start Command" ou "Command" ou "Run Command"
   - Si le champ existe, entrez cette commande exacte :
     ```
     python manage.py migrate && daphne -b 0.0.0.0 -p $PORT config.asgi:application
     ```
   
2. **Si le champ n'existe pas**, cherchez une section **"Deploy"** ou **"Service Settings"** :
   - Cherchez un champ "Start Command" ou "Command"
   - Entrez la commande ci-dessus

3. **Cliquez sur "Save"** ou **"Update"** pour sauvegarder

### Étape 3 : Vérifier que Railway utilise cette commande

1. **Dans Railway** → Service **"egoejo"** → **Deployments**
2. **Cliquez sur le dernier déploiement**
3. **Cliquez sur l'onglet "Deploy Logs"**
4. **Vérifiez que vous voyez** :
   - Les migrations s'exécuter
   - **Puis** Daphne démarrer avec `daphne -b 0.0.0.0 -p XXXX config.asgi:application`

---

## 🆘 Si vous ne trouvez pas le champ "Start Command"

### Option 1 : Utiliser une variable d'environnement

Railway peut utiliser une variable d'environnement `RAILWAY_START_COMMAND`. Essayez de l'ajouter :

1. **Dans Railway** → Service **"egoejo"** → **Variables**
2. **Cliquez sur "+ New Variable"**
3. **Remplissez** :
   - **Name** : `RAILWAY_START_COMMAND`
   - **Value** : `python manage.py migrate && daphne -b 0.0.0.0 -p $PORT config.asgi:application`
4. **Cliquez sur "Add"** ou **"Save"**

### Option 2 : Utiliser un script de démarrage

Créez un script de démarrage et utilisez-le dans Railway :

1. **Créez un fichier** `backend/start.sh` avec ce contenu :
   ```bash
   #!/bin/bash
   set -e
   python manage.py migrate
   daphne -b 0.0.0.0 -p ${PORT:-8000} config.asgi:application
   ```

2. **Dans le Dockerfile**, rendez-le exécutable :
   ```dockerfile
   COPY start.sh /start.sh
   RUN chmod +x /start.sh
   ```

3. **Dans Railway** → Service **"egoejo"** → **Settings** → **General** :
   - **Start Command** : `/start.sh`

### Option 3 : Utiliser le CMD du Dockerfile

Si Railway ne respecte pas le `startCommand` de `railway.toml`, utilisez le `CMD` du Dockerfile :

1. **Dans `backend/Dockerfile.railway`**, ajoutez :
   ```dockerfile
   CMD python manage.py migrate && daphne -b 0.0.0.0 -p ${PORT:-8000} config.asgi:application
   ```

2. **Commitez et poussez** les changements

---

## 📝 Checklist de vérification

Avant de tester, vérifiez que :

- ✅ La commande de démarrage est configurée dans Railway (Settings → General → Start Command)
- ✅ OU la variable `RAILWAY_START_COMMAND` est définie dans Railway → Variables
- ✅ OU le `CMD` du Dockerfile est correctement configuré

---

## 🚀 Après avoir configuré la commande

1. **Railway redéploiera automatiquement** (ou déclenchez un redéploiement manuel)
2. **Attendez 2-5 minutes** que le déploiement se termine
3. **Vérifiez les "Deploy Logs"** pour voir si Daphne démarre
4. **Testez l'endpoint** `/api/health/` pour voir si ça fonctionne

---

**🚀 Dites-moi quelle option vous choisissez et je vous guiderai !**


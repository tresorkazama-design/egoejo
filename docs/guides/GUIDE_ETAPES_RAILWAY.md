# 🎯 Guide étape par étape - Configuration Railway

## 📍 Vous êtes actuellement : Project Settings → General

Vous devez sortir de **Project Settings** et aller dans les **paramètres du SERVICE "egoejo"**.

---

## 🚀 Étape 1 : Quitter Project Settings

1. **Cliquez sur le bouton "X"** en haut à droite du panneau "Project Settings"
   - OU
2. **Cliquez sur "Architecture"** dans le menu de navigation en haut (à gauche de "Settings")

Cela vous ramènera à la vue principale du projet.

---

## 📦 Étape 2 : Accéder au service "egoejo"

Après avoir quitté Project Settings, vous devriez voir :

**Dans la sidebar gauche :**
- Postgres ✅
- egoejo ❌ (avec "Failed 16 seconds ago")

1. **Cliquez sur "egoejo"** dans la liste des services à gauche
2. Cela vous amènera à la page du service "egoejo"

---

## ⚙️ Étape 3 : Aller dans Settings du service

Une fois dans la page du service "egoejo", en haut vous verrez des onglets :

- Deployments
- Variables  
- Metrics
- **Settings** ← Cliquez ici !

1. **Cliquez sur l'onglet "Settings"** en haut

---

## 🔧 Étape 4 : Trouver "Source"

Dans le panneau Settings du service, à **droite** de l'écran, vous verrez un **menu vertical** :

- **Source** ← C'est ici !
- Networking
- Build
- Deploy
- Config-as-code
- Danger

1. **Cliquez sur "Source"** dans ce menu vertical à droite

---

## 📝 Étape 5 : Configurer Root Directory et Dockerfile

Une fois dans "Source", vous verrez :

1. **Root Directory** :
   - Champ vide ou valeur par défaut
   - 📝 **Changez en** : `backend`

2. **Dockerfile Path** :
   - Champ vide ou valeur par défaut
   - 📝 **Changez en** : `Dockerfile.railway`

3. **Repository** et **Branch** :
   - Devraient être déjà configurés (votre repo GitHub et la branche)

4. **Sauvegarder** :
   - Railway sauvegarde automatiquement
   - Un nouveau déploiement va démarrer automatiquement

---

## ✅ Étape 6 : Vérifier le déploiement

Après avoir configuré Source :

1. Allez dans l'onglet **"Deployments"** en haut
2. Surveillez le nouveau déploiement
3. Si ça échoue, cliquez sur le déploiement pour voir les logs

---

## 🆘 Si vous ne voyez toujours pas "Source"

### Alternative : Utiliser Build et Deploy

Si "Source" n'est pas disponible, essayez :

1. **Build** → Configurer la commande de build (si nécessaire)
2. **Deploy** → Configurer la commande de démarrage :
   ```
   sh -c "cd backend && python manage.py migrate && daphne -b 0.0.0.0 -p $PORT config.asgi:application"
   ```

---

## 🎯 Résumé rapide

1. ❌ Quittez **Project Settings** (cliquez sur X ou "Architecture")
2. 📦 Cliquez sur le service **"egoejo"** dans la sidebar gauche
3. ⚙️ Cliquez sur l'onglet **"Settings"** en haut
4. 🔧 Cliquez sur **"Source"** dans le menu vertical à droite
5. 📝 Configurez **Root Directory** : `backend`
6. 📝 Configurez **Dockerfile Path** : `Dockerfile.railway`
7. ✅ Attendez le nouveau déploiement

---

**Suivez ces étapes dans l'ordre et dites-moi où vous en êtes !** 🚀


# 🚨 Solution : Erreur "could not translate host name 'db'"

## ❌ Problème actuel
Django essaie de se connecter à `host="db"` (configuration Docker locale) au lieu d'utiliser `DATABASE_URL` de Railway.

**Erreur** : `django.db.utils.OperationalError: could not translate host name "db" to address`

## ✅ Solution : Créer `DATABASE_URL` dans Railway

### 📋 Étape 1 : Trouver les valeurs PostgreSQL dans Railway

1. **Ouvrez Railway** dans votre navigateur : https://railway.app
2. **Cliquez sur votre projet** (en haut à gauche)
3. **Dans la sidebar de gauche**, cliquez sur **"Postgres"** (ou "PostgreSQL")
4. **Cliquez sur l'onglet "Variables"** en haut
5. **Notez ces valeurs** (copiez-collez les) :

   ```
   PGHOST = monorail.proxy.rlwy.net  (exemple, VOS valeurs seront différentes)
   PGPORT = 5432
   PGUSER = postgres
   PGPASSWORD = abc123xyz456DEF789  (exemple, VOTRE valeur sera différente)
   PGDATABASE = railway
   ```

   ⚠️ **Important** : Ces valeurs sont uniques à VOTRE service PostgreSQL sur Railway !

---

### 📋 Étape 2 : Créer `DATABASE_URL` dans le service "egoego"

1. **Retournez à votre projet** (cliquez sur le nom du projet en haut à gauche)
2. **Dans la sidebar de gauche**, cliquez sur **"egoego"** (votre service Django)
3. **Cliquez sur l'onglet "Variables"** en haut
4. **Cherchez la variable `DATABASE_URL`** dans la liste

   **Si `DATABASE_URL` n'existe pas :**
   
5. **Cliquez sur "+ New Variable"** ou **"Add Variable"** (en haut à droite, ou au-dessus de la liste des variables)

6. **Dans le formulaire qui apparaît** :
   
   - **Name** (Nom) : Tapez exactement `DATABASE_URL` (en majuscules)
   
   - **Value** (Valeur) : Construisez avec ce format (remplacez les valeurs entre crochets par VOS valeurs du service PostgreSQL) :
     ```
     postgresql://[PGUSER]:[PGPASSWORD]@[PGHOST]:[PGPORT]/[PGDATABASE]
     ```
   
   **Exemple concret** (remplacez par VOS vraies valeurs) :
   
   Si dans PostgreSQL vous avez :
   - `PGHOST` = `monorail.proxy.rlwy.net`
   - `PGPORT` = `5432`
   - `PGUSER` = `postgres`
   - `PGPASSWORD` = `ABC123xyz456`
   - `PGDATABASE` = `railway`
   
   Alors dans "egoego", créez `DATABASE_URL` avec cette valeur exacte :
   ```
   postgresql://postgres:ABC123xyz456@monorail.proxy.rlwy.net:5432/railway
   ```
   
   ⚠️ **IMPORTANT** : 
   - Remplacez `ABC123xyz456` par votre **vraie** valeur de `PGPASSWORD` du service PostgreSQL
   - Remplacez `monorail.proxy.rlwy.net` par votre **vraie** valeur de `PGHOST` du service PostgreSQL
   - Gardez `postgres` si c'est votre `PGUSER`, sinon remplacez-le
   - Gardez `railway` si c'est votre `PGDATABASE`, sinon remplacez-le

7. **Environment** (Environnement) : Sélectionnez **"Production"** (ou cochez tous les environnements)

8. **Cliquez sur "Add"** ou **"Save"** pour créer la variable

---

### 📋 Étape 3 : Vérifier que `ALLOWED_HOSTS` existe

1. **Dans le service "egoego"** → **"Variables"**
2. **Cherchez `ALLOWED_HOSTS`** dans la liste

   **Si `ALLOWED_HOSTS` n'existe pas :**
   
3. **Cliquez sur "+ New Variable"**
4. **Remplissez** :
   - **Name** : `ALLOWED_HOSTS`
   - **Value** : Votre domaine Railway (sans `https://`) :
     ```
     egoego-production.up.railway.app,*.railway.app
     ```
   
   ⚠️ **Remplacez** `egoego-production.up.railway.app` par votre vrai domaine Railway si différent !
   
   **Pour trouver votre domaine Railway** :
   - Dans le service "egoego", cliquez sur **"Settings"** (en haut)
   - Cliquez sur **"Domains"** (dans la sidebar de gauche)
   - Vous verrez votre domaine public (ex: `egoego-production.up.railway.app`)

5. **Cliquez sur "Add"** ou **"Save"**

---

### 📋 Étape 4 : Redéploiement automatique

Après avoir créé `DATABASE_URL` (et `ALLOWED_HOSTS` si nécessaire) :

1. **Railway va automatiquement redéployer** votre service
2. **Attendez 2-3 minutes** que le redéploiement se termine
3. **Dans Railway** → Service "egoego" → **"Deployments"**, vérifiez si le nouveau déploiement réussit (icône verte ✓ au lieu de rouge ✗)

---

### 📋 Étape 5 : Vérifier que ça fonctionne

1. **Dans Railway** → Service "egoego" → **"Deployments"**, vérifiez que le dernier déploiement a réussi (icône verte ✓)
2. **Dans Railway** → Service "egoego" → **"Metrics"**, vérifiez que le service est en cours d'exécution
3. **Testez l'URL** de votre backend dans votre navigateur :
   ```
   https://egoego-production.up.railway.app/api/
   ```
   
   Vous devriez voir une réponse JSON ou une page d'API Django.

---

## 🆘 Si ça ne fonctionne toujours pas

### Vérifier les logs Railway

1. **Dans Railway** → Service "egoego" → **"Deployments"** → Cliquez sur le dernier déploiement
2. **Cliquez sur "View Logs"** ou **"Logs"**
3. **Vérifiez les dernières lignes** :
   - Si vous voyez encore `could not translate host name "db"` → `DATABASE_URL` n'est pas correctement configurée
   - Si vous voyez une autre erreur → Partagez-la avec moi

### Vérifier que `DATABASE_URL` est bien créée

1. **Dans Railway** → Service "egoego" → **"Variables"**
2. **Cherchez `DATABASE_URL`** dans la liste
3. **Cliquez dessus** pour voir sa valeur (elle devrait ressembler à `postgresql://postgres:...@...:5432/railway`)
4. **Vérifiez** que la valeur correspond bien à vos valeurs PostgreSQL

---

## 📝 Checklist finale

Dans Railway, service "egoego" → Variables, vous devez avoir :

- ✅ `DJANGO_SECRET_KEY` = `...` (déjà configuré normalement)
- ✅ `DATABASE_URL` = `postgresql://postgres:VOTRE_MOT_DE_PASSE@VOTRE_HOST:5432/railway` (à créer)
- ✅ `ALLOWED_HOSTS` = `egoego-production.up.railway.app,*.railway.app` (à créer si nécessaire)

---

## 🎯 Résumé rapide

**Le problème** : Django utilise `host='db'` (configuration Docker locale) au lieu de `DATABASE_URL` de Railway.

**La solution** : Créer `DATABASE_URL` dans Railway avec la valeur de votre service PostgreSQL :
```
postgresql://postgres:VOTRE_PGPASSWORD@VOTRE_PGHOST:5432/railway
```

---

**Dites-moi quand vous avez créé `DATABASE_URL` et je vous aiderai à vérifier !** 🚀


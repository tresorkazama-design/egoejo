# 🚨 Guide rapide - Résoudre le crash Railway

## ❌ Problème actuel
Le service "egoego" crash sur Railway.

## ✅ Solution rapide (3 étapes)

### 🔍 Étape 1 : Voir les logs d'erreur

**Dans Railway :**
1. Cliquez sur **"egoego"** (sidebar gauche)
2. Cliquez sur **"Deployments"** (en haut)
3. Cliquez sur le **dernier déploiement** (celui qui a crashé)
4. Cliquez sur **"View Logs"** ou **"Logs"**

**Cherchez l'erreur exacte** dans les logs. Elle ressemble probablement à :
- `could not translate host name "db" to address`
- `DJANGO_SECRET_KEY must be set`
- `Invalid HTTP_HOST header`
- Autre erreur ?

---

### 📝 Étape 2 : Créer `DATABASE_URL` dans Railway

#### A. Trouver les valeurs PostgreSQL

1. **Dans Railway**, cliquez sur **"Postgres"** (sidebar gauche)
2. **Cliquez sur "Variables"** (en haut)
3. **Notez ces valeurs** :
   ```
   PGHOST = monorail.proxy.rlwy.net  (exemple)
   PGPORT = 5432
   PGUSER = postgres
   PGPASSWORD = abc123xyz456  (exemple)
   PGDATABASE = railway
   ```

#### B. Créer DATABASE_URL dans "egoego"

1. **Retournez au service "egoego"** (sidebar gauche)
2. **Cliquez sur "Variables"** (en haut)
3. **Cliquez sur "+ New Variable"** (en haut à droite)
4. **Remplissez** :
   - **Name** : `DATABASE_URL`
   - **Value** : Construisez avec ce format (remplacez par VOS valeurs) :
     ```
     postgresql://[PGUSER]:[PGPASSWORD]@[PGHOST]:[PGPORT]/[PGDATABASE]
     ```
   
   **Exemple** (avec les valeurs de l'exemple ci-dessus) :
   ```
   postgresql://postgres:abc123xyz456@monorail.proxy.rlwy.net:5432/railway
   ```

5. **Cliquez sur "Add"** ou **"Save"**

⚠️ **Important** : Remplacez `abc123xyz456` par votre vrai `PGPASSWORD` du service PostgreSQL !

---

### 🌐 Étape 3 : Créer `ALLOWED_HOSTS`

1. **Dans le service "egoego"** → **"Variables"**
2. **Cliquez sur "+ New Variable"**
3. **Remplissez** :
   - **Name** : `ALLOWED_HOSTS`
   - **Value** : Votre domaine Railway (sans `https://`) :
     ```
     egoego-production.up.railway.app,*.railway.app
     ```
   
   ⚠️ **Remplacez** `egoego-production.up.railway.app` par votre vrai domaine Railway si différent !

4. **Cliquez sur "Add"** ou **"Save"**

---

## ✅ Après avoir ajouté les variables

1. **Railway va automatiquement redéployer** votre service (attendez 2-3 minutes)
2. **Vérifiez l'onglet "Deployments"** pour voir si le nouveau déploiement réussit (icône verte ✓)
3. **Vérifiez l'onglet "Metrics"** pour voir si le service est en cours d'exécution

---

## 🆘 Si ça ne fonctionne toujours pas

**Partagez-moi :**
1. **L'erreur exacte** que vous voyez dans les logs Railway
2. **La liste des variables** que vous avez dans le service "egoego" → "Variables"
3. **Le dernier message d'erreur** dans les logs du dernier déploiement

---

## 📋 Checklist rapide

Dans Railway, service "egoego" → Variables, vous devez avoir :

- ✅ `DJANGO_SECRET_KEY` = `...` (déjà configuré normalement)
- ✅ `DATABASE_URL` = `postgresql://user:pass@host:port/db` (à créer)
- ✅ `ALLOWED_HOSTS` = `egoego-production.up.railway.app,*.railway.app` (à créer)
- ❓ `REDIS_URL` = `...` (optionnel, si vous avez Redis)

---

**Dites-moi où vous êtes bloqué !** 🚀


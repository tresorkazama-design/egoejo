# 🔍 Diagnostic du Crash Railway - Guide étape par étape

## ❌ Problème actuel
Le service "egoego" crash sur Railway (voir capture d'écran).

## 🔍 Causes possibles

### 1. Variable `DATABASE_URL` manquante
Django essaie de se connecter à `host="db"` (configuration par défaut Docker) au lieu d'utiliser `DATABASE_URL` de Railway.

### 2. Variable `ALLOWED_HOSTS` manquante ou incorrecte
Django peut bloquer les requêtes si `ALLOWED_HOSTS` n'inclut pas le domaine Railway.

### 3. Variable `DJANGO_SECRET_KEY` manquante
Mais normalement déjà configurée.

---

## ✅ Solution étape par étape

### 📋 Étape 1 : Vérifier les logs Railway

1. **Dans Railway**, cliquez sur le service **"egoego"** dans la sidebar gauche
2. **Cliquez sur l'onglet "Deployments"** en haut
3. **Cliquez sur le dernier déploiement** (celui qui a crashé)
4. **Cliquez sur "View Logs"** ou **"Logs"** pour voir les erreurs exactes

**Notez l'erreur exacte** que vous voyez dans les logs !

---

### 📋 Étape 2 : Vérifier les variables d'environnement

1. **Dans Railway**, cliquez sur le service **"egoego"**
2. **Cliquez sur l'onglet "Variables"** en haut
3. **Vérifiez que ces variables existent** :

   **Variables REQUISES :**
   - ✅ `DJANGO_SECRET_KEY` (normalement déjà là)
   - ❓ `DATABASE_URL` (probablement manquante)
   - ❓ `ALLOWED_HOSTS` (probablement manquante)

---

### 📋 Étape 3 : Créer `DATABASE_URL`

#### 3.1 Trouver les valeurs PostgreSQL

1. **Dans Railway**, cliquez sur **"Postgres"** (ou "PostgreSQL") dans la sidebar gauche
2. **Cliquez sur l'onglet "Variables"**
3. **Notez ces valeurs** :
   - `PGHOST` = `...` (ex: `monorail.proxy.rlwy.net`)
   - `PGPORT` = `...` (ex: `5432`)
   - `PGUSER` = `...` (ex: `postgres`)
   - `PGPASSWORD` = `...` (ex: `abc123xyz456`)
   - `PGDATABASE` = `...` (ex: `railway`)

#### 3.2 Créer `DATABASE_URL` dans le service "egoego"

1. **Retournez au service "egoego"** (cliquez dessus dans la sidebar)
2. **Cliquez sur "Variables"**
3. **Cliquez sur "+ New Variable"** ou **"Add Variable"** (en haut à droite)
4. **Remplissez le formulaire** :
   - **Name** : `DATABASE_URL`
   - **Value** : Construisez avec ce format (remplacez les valeurs entre crochets) :
     ```
     postgresql://[PGUSER]:[PGPASSWORD]@[PGHOST]:[PGPORT]/[PGDATABASE]
     ```
   
   **Exemple concret** (remplacez par VOS valeurs) :
   ```
   postgresql://postgres:abc123xyz456@monorail.proxy.rlwy.net:5432/railway
   ```

5. **Cliquez sur "Add"** ou **"Save"**

---

### 📋 Étape 4 : Créer `ALLOWED_HOSTS`

1. **Dans le service "egoego"** → **"Variables"**
2. **Cliquez sur "+ New Variable"**
3. **Remplissez** :
   - **Name** : `ALLOWED_HOSTS`
   - **Value** : Votre domaine Railway (sans `https://`). Exemples :
     ```
     egoego-production.up.railway.app,*.railway.app
     ```
   - Ou si vous avez un domaine personnalisé :
     ```
     egoejo.vercel.app,egoego-production.up.railway.app,*.railway.app
     ```

4. **Cliquez sur "Add"** ou **"Save"**

---

### 📋 Étape 5 : Optionnel - Ajouter `REDIS_URL`

Si vous avez un service Redis dans Railway :

1. **Dans Railway**, cliquez sur **"Redis"** dans la sidebar
2. **Cliquez sur "Variables"**
3. **Notez la valeur de `REDIS_URL`** (si elle existe)
4. **Dans le service "egoego"** → **"Variables"**
5. **Ajoutez `REDIS_URL`** avec la valeur du service Redis

**Si pas de Redis :** Pas de problème, Django utilisera InMemoryChannelLayer (pour le développement).

---

### 📋 Étape 6 : Redéploiement automatique

Après avoir ajouté les variables :

1. **Railway va automatiquement redéployer** votre service
2. **Attendez 2-3 minutes** que le redéploiement se termine
3. **Vérifiez l'onglet "Deployments"** pour voir si le nouveau déploiement réussit

---

### 📋 Étape 7 : Vérifier que ça fonctionne

1. **Dans Railway**, cliquez sur le service **"egoego"**
2. **Vérifiez l'onglet "Metrics"** pour voir si le service est en cours d'exécution
3. **Vérifiez l'onglet "Deployments"** pour voir si le dernier déploiement a réussi (icône verte ✓)
4. **Cliquez sur "Settings"** → **"Domains"** pour voir l'URL publique
5. **Testez l'URL** dans votre navigateur : `https://egoego-production.up.railway.app/api/`

---

## 🆘 Si ça ne fonctionne toujours pas

### Vérifier les logs détaillés

1. **Dans Railway** → Service "egoego" → **"Deployments"** → Cliquez sur le dernier déploiement
2. **Cliquez sur "View Logs"** ou **"Logs"**
3. **Copiez-collez les dernières lignes d'erreur** et partagez-les

### Vérifier que `dj-database-url` est installé

1. Vérifiez que `backend/requirements.txt` contient `dj-database-url`
2. Si ce n'est pas le cas, ajoutez-le et poussez les changements sur GitHub

---

## 📝 Liste de vérification rapide

Dans Railway, service "egoego" → Variables, vous devez avoir :

- ✅ `DJANGO_SECRET_KEY` = `...` (valeur générée)
- ✅ `DATABASE_URL` = `postgresql://user:pass@host:port/db`
- ✅ `ALLOWED_HOSTS` = `egoego-production.up.railway.app,*.railway.app`
- ❓ `REDIS_URL` = `...` (optionnel)
- ❓ `DEBUG` = `0` (optionnel, par défaut désactivé)
- ❓ `CORS_ALLOWED_ORIGINS` = `https://votre-frontend.vercel.app` (optionnel, si besoin)

---

**📝 Dites-moi quelle étape vous pose problème et je vous aiderai !**


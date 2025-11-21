# 🔍 Guide de Diagnostic : Erreur 502 sur Railway

## ❌ Symptôme
- Erreur 502 "Application failed to respond" sur `/api/health/`
- Railway ne peut pas joindre l'application Django/Daphne

## 🔍 Diagnostic étape par étape

### Étape 1 : Vérifier les Deploy Logs

1. **Dans Railway** → Service **"egoejo"** → **Deployments** → Dernier déploiement
2. **Cliquez sur "View Logs"** ou **"Deploy Logs"**
3. **Cherchez les messages suivants** :

#### ✅ Messages positifs à chercher :
```
=== EGOEJO Backend Starting ===
Configuration:
  - PORT: 8080 (ou un autre port)
  - DATABASE_URL: set (hidden)
Running migrations...
Migrations completed successfully
Starting Daphne ASGI server...
Listening on TCP address 0.0.0.0:8080
```

#### ❌ Messages d'erreur à chercher :
```
ERROR: Migrations failed
ERROR: Django check failed
ERROR: Health check error
Daphne server exited unexpectedly
Connection refused
```

---

### Étape 2 : Vérifier que Daphne reste actif

1. **Dans les Deploy Logs**, **faites défiler jusqu'à la fin**
2. **Vérifiez** :
   - Y a-t-il des messages **après** "Listening on TCP address 0.0.0.0:8080" ?
   - Y a-t-il des erreurs Python ou Django après le démarrage ?
   - Daphne crash-t-il immédiatement après le démarrage ?

**Si Daphne crash après le démarrage**, il y a un problème dans le code Django/ASGI.
**Si Daphne reste actif** (pas d'erreurs), le problème vient du routage Railway.

---

### Étape 3 : Vérifier la configuration Railway

1. **Dans Railway** → Service **"egoejo"** → **Settings** → **Networking**
2. **Vérifiez** :
   - **Port** : Railway devrait détecter automatiquement le port via `$PORT`
   - **Public Networking** : Devrait être activé
   - **Port Mapping** : Devrait être automatique

3. **Dans Settings** → **Variables**, vérifiez :
   - `PORT` : Railway définit automatiquement cette variable (vous n'avez pas besoin de la définir manuellement)
   - `DJANGO_SECRET_KEY` : Doit être défini
   - `DATABASE_URL` : Doit être défini (fourni par le service PostgreSQL)
   - `ALLOWED_HOSTS` : Peut être vide (le code l'ajoute automatiquement)

---

### Étape 4 : Vérifier les métriques Railway

1. **Dans Railway** → Service **"egoejo"** → **Metrics**
2. **Vérifiez** :
   - **CPU** : Si 0%, l'application ne démarre peut-être pas
   - **Memory** : Si 0%, l'application ne démarre peut-être pas
   - **Requests** : Y a-t-il des requêtes ? (même des 502)
   - **Errors** : Y a-t-il des erreurs enregistrées ?

---

### Étape 5 : Tester l'endpoint directement dans le conteneur

Si Railway permet d'exécuter des commandes dans le conteneur :

1. **Dans Railway** → Service **"egoejo"** → **Connect** ou **Shell**
2. **Essayez** :
   ```bash
   curl http://localhost:${PORT}/api/health/
   # ou
   wget -O- http://localhost:${PORT}/api/health/
   ```

**Si ça fonctionne**, le problème vient du routage Railway.
**Si ça ne fonctionne pas**, Daphne ne démarre pas correctement.

---

## 🛠️ Solutions possibles

### Solution 1 : Daphne crash après le démarrage

**Symptômes** :
- Les logs montrent "Listening on TCP address" puis des erreurs
- Les métriques Railway montrent 0% CPU/Memory

**Causes possibles** :
- Erreur dans le code Django/ASGI
- Problème de connexion à la base de données
- Problème avec les migrations

**Actions** :
1. Vérifiez les erreurs dans les Deploy Logs
2. Partagez les logs avec moi pour analyse

---

### Solution 2 : Railway ne route pas vers le bon port

**Symptômes** :
- Les logs montrent "Listening on TCP address 0.0.0.0:XXXX"
- XXXX est différent du port attendu par Railway

**Causes possibles** :
- La variable `PORT` n'est pas définie
- Railway attend un port différent

**Actions** :
1. Vérifiez la valeur de `PORT` dans les logs
2. Dans Railway → Settings → Networking, vérifiez le port exposé

---

### Solution 3 : Problème de healthcheck Railway

**Symptômes** :
- Daphne démarre correctement
- Les logs montrent que tout fonctionne
- Mais Railway retourne toujours 502

**Causes possibles** :
- Le healthcheck Railway échoue
- Le chemin `/api/health/` n'est pas accessible

**Actions** :
1. Vérifiez `healthcheckPath` dans `railway.toml` (devrait être `/api/health/`)
2. Vérifiez que l'endpoint health retourne 200 (pas 503)

---

### Solution 4 : Problème ALLOWED_HOSTS

**Symptômes** :
- Daphne démarre correctement
- Mais Django refuse les requêtes

**Causes possibles** :
- `ALLOWED_HOSTS` ne contient pas le domaine Railway

**Actions** :
1. Dans Railway → Variables, ajoutez `ALLOWED_HOSTS` avec la valeur `egoejo-production.up.railway.app`
2. Ou laissez vide, le code l'ajoute automatiquement si Railway est détecté

---

## 📝 Informations à partager

Pour m'aider à diagnostiquer le problème, j'ai besoin de :

1. **Les 50 dernières lignes des Deploy Logs** (après "Listening on TCP address")
   - Y a-t-il des erreurs ?
   - Daphne reste-t-il actif ?

2. **La valeur de PORT dans les logs**
   - Quel port Daphne écoute-t-il ?

3. **Les métriques Railway**
   - CPU/Memory sont-ils à 0 ou ont-ils des valeurs ?
   - Y a-t-il des requêtes/erreurs enregistrées ?

4. **Les variables Railway**
   - `PORT` est-elle définie ? (Railway le fait automatiquement)
   - `DJANGO_SECRET_KEY` est-elle définie ?
   - `DATABASE_URL` est-elle définie ?
   - `ALLOWED_HOSTS` est-elle définie ? (peut être vide)

---

## 🚀 Prochaines étapes

1. **Vérifiez les Deploy Logs** selon les étapes ci-dessus
2. **Partagez les informations** demandées avec moi
3. **Je vous aiderai** à résoudre le problème spécifique

---

**Note importante** : Railway redéploie automatiquement après chaque push Git. Attendez 2-5 minutes après un push avant de vérifier les logs.


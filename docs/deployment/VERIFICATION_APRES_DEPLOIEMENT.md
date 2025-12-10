# ✅ Vérification après déploiement réussi

## 🎉 Félicitations ! Le déploiement a réussi !

Maintenant, vérifions que tout fonctionne correctement.

---

## 📋 Étape 1 : Vérifier l'URL exacte du service Railway

L'URL peut être différente de `egoego-production.up.railway.app`. Pour trouver l'URL exacte :

1. **Ouvrez Railway** : https://railway.app
2. **Allez dans votre projet** → Service **"egoego"**
3. **Cliquez sur "Settings"** (en haut)
4. **Cliquez sur "Domains"** (dans la sidebar de gauche)
5. **Notez l'URL publique** (ex: `egoego-production.up.railway.app` ou `egoejo-production.up.railway.app`)

**Remplacez `egoego-production.up.railway.app` par votre URL exacte** dans les tests ci-dessous.

---

## 📋 Étape 2 : Tester l'endpoint `/api/health/`

### Dans votre navigateur :

```
https://VOTRE_URL_RAILWAY/api/health/
```

**Vous devriez voir** :
```json
{"status": "ok", "database": "connected"}
```

### Avec PowerShell :

```powershell
Invoke-WebRequest -Uri "https://VOTRE_URL_RAILWAY/api/health/" -UseBasicParsing
```

**Remplacer `VOTRE_URL_RAILWAY` par votre URL exacte de Railway.**

---

## 📋 Étape 3 : Tester d'autres endpoints

### Test 1 : API racine

```
https://VOTRE_URL_RAILWAY/api/
```

Vous devriez voir une liste des endpoints disponibles ou une page DRF.

### Test 2 : Admin Django

```
https://VOTRE_URL_RAILWAY/admin/
```

Vous devriez voir la page de connexion de l'admin Django.

---

## 📋 Étape 4 : Vérifier les métriques Railway

1. **Dans Railway** → Service **"egoego"** → **"Metrics"**
2. **Vérifiez que** :
   - Le service est actif (pas de redémarrages)
   - La mémoire et le CPU sont stables
   - Les requêtes réussissent (codes 200)

---

## 📋 Étape 5 : Vérifier les logs Railway

1. **Dans Railway** → Service **"egoego"** → **"Deployments"** → Cliquez sur le dernier déploiement
2. **Cliquez sur "View Logs"** ou **"Logs"**
3. **Vérifiez que** :
   - Le service démarre correctement
   - Les migrations s'exécutent sans erreur
   - Daphne démarre sur le port `$PORT`
   - Il n'y a pas d'erreur de connexion à la base de données
   - Aucune erreur après 3 minutes (le service ne devrait plus crash)

---

## ✅ Si tout fonctionne correctement

Si l'endpoint `/api/health/` retourne `{"status": "ok", "database": "connected"}` :

1. ✅ Le service est déployé correctement
2. ✅ La connexion à la base de données fonctionne
3. ✅ Le healthcheck est configuré correctement
4. ✅ Railway peut vérifier la santé du service

---

## 🆘 Si l'endpoint retourne toujours 404

### Vérifier l'URL exacte dans Railway

1. **Dans Railway** → Service **"egoego"** → **"Settings"** → **"Domains"**
2. **Copiez l'URL exacte** de votre service
3. **Testez avec cette URL exacte**

### Vérifier que Railway a bien déployé les changements

1. **Dans Railway** → Service **"egoego"** → **"Deployments"**
2. **Vérifiez que le dernier déploiement** :
   - Utilise le commit avec le message "feat: ajout fichiers backend, frontend et configuration Railway"
   - Est terminé avec succès (icône verte ✓)
   - Montre "Deployed" ou "Active"

### Vérifier les logs Railway

1. **Dans Railway** → Service **"egoego"** → **"Deployments"** → Cliquez sur le dernier déploiement
2. **Cliquez sur "View Logs"** ou **"Logs"**
3. **Vérifiez qu'il n'y a pas d'erreur** dans les logs
4. **Vérifiez que Daphne démarre correctement** sur le port `$PORT`

---

## 📝 Prochaines étapes

Une fois que l'endpoint `/api/health/` fonctionne :

1. **Configurer le frontend** pour qu'il pointe vers l'URL Railway du backend
2. **Tester l'application complète** (frontend + backend)
3. **Configurer CORS** si nécessaire pour autoriser le frontend à communiquer avec le backend

---

**🚀 Dites-moi quelle est votre URL exacte de Railway et testons l'endpoint ensemble !**


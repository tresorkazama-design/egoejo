# 🚨 Solution : Service crash après 3 minutes

## ❌ Problème identifié

Le service démarre correctement mais crash après environ 3 minutes. Cela se produit généralement à cause de :

1. **Absence de healthcheck** : Railway ne peut pas vérifier que le service fonctionne et le redémarre
2. **Timeout de connexion à la base de données** : Les connexions PostgreSQL expirent après inactivité
3. **Configuration JWT incomplète** : Une erreur de syntaxe dans la configuration

## ✅ Corrections appliquées

### 1. Ajout d'un endpoint de healthcheck

**Fichier** : `backend/config/urls.py`

Ajout d'un endpoint `/api/health/` qui :
- Vérifie que Django fonctionne
- Vérifie la connexion à la base de données
- Retourne un statut JSON pour Railway

### 2. Configuration du healthcheck dans Railway

**Fichier** : `railway.toml`

Ajout de :
- `healthcheckPath = "/api/health/"` : Railway vérifiera ce endpoint toutes les 30 secondes
- `healthcheckTimeout = 300` : Timeout de 5 minutes pour le healthcheck

### 3. Optimisation de la connexion PostgreSQL

**Fichier** : `backend/config/settings.py`

Ajout de paramètres `keepalives` pour éviter les timeouts de connexion :
- `keepalives`: 1 - Active les keep-alives TCP
- `keepalives_idle`: 30 - Délai avant d'envoyer le premier keep-alive (30 secondes)
- `keepalives_interval`: 10 - Intervalle entre les keep-alives (10 secondes)
- `keepalives_count`: 5 - Nombre de keep-alives avant de considérer la connexion morte

### 4. Correction de la configuration JWT

**Fichier** : `backend/config/settings.py`

Correction de `ACCESS_TOKEN_LIFETIME` qui était incomplet.

---

## 📋 Prochaines étapes

### 1. Pousser les changements sur GitHub

```bash
git add backend/config/urls.py backend/config/settings.py railway.toml
git commit -m "fix: ajout healthcheck et optimisation connexion DB pour Railway"
git push origin main
```

### 2. Vérifier que Railway redéploie automatiquement

- Railway détectera automatiquement le nouveau commit
- Le service redéploiera avec les nouvelles configurations
- Attendez 2-3 minutes que le redéploiement se termine

### 3. Vérifier que le healthcheck fonctionne

Dans Railway :
1. Allez dans le service "egoego" → **"Deployments"**
2. Cliquez sur le dernier déploiement
3. Cliquez sur **"View Logs"** ou **"Logs"**
4. Vérifiez qu'il n'y a plus d'erreur après 3 minutes

Vous pouvez aussi tester le healthcheck manuellement :
```
https://egoego-production.up.railway.app/api/health/
```

Vous devriez voir :
```json
{"status": "ok", "database": "connected"}
```

### 4. Vérifier les métriques Railway

Dans Railway :
1. Allez dans le service "egoego" → **"Metrics"**
2. Vérifiez que :
   - Le service reste actif (pas de redémarrages)
   - La mémoire et le CPU sont stables
   - Les requêtes réussissent (codes 200)

---

## 🔍 Si le problème persiste

### Vérifier les logs Railway

1. **Dans Railway** → Service "egoego" → **"Deployments"** → Cliquez sur le dernier déploiement
2. **Cliquez sur "View Logs"** ou **"Logs"**
3. **Cherchez l'erreur exacte** qui se produit après 3 minutes
4. **Partagez l'erreur** avec moi pour que je puisse vous aider

### Vérifier que le healthcheck répond

Testez manuellement le healthcheck :
```bash
curl https://egoego-production.up.railway.app/api/health/
```

Ou dans votre navigateur :
```
https://egoego-production.up.railway.app/api/health/
```

Vous devriez voir :
```json
{"status": "ok", "database": "connected"}
```

Si vous voyez une erreur, c'est que le healthcheck ne fonctionne pas correctement.

### Vérifier les variables d'environnement Railway

Dans Railway, service "egoego" → **"Variables"**, vérifiez que vous avez :
- ✅ `DATABASE_URL` = `postgresql://...`
- ✅ `DJANGO_SECRET_KEY` = `...`
- ✅ `ALLOWED_HOSTS` = `egoego-production.up.railway.app,*.railway.app`

---

## 📝 Résumé des changements

1. ✅ Ajout d'un endpoint `/api/health/` pour Railway
2. ✅ Configuration du healthcheck dans `railway.toml`
3. ✅ Optimisation de la connexion PostgreSQL (keepalives)
4. ✅ Correction de la configuration JWT

Ces changements devraient résoudre le problème de crash après 3 minutes.

---

**🚀 Poussez les changements sur GitHub et dites-moi si le problème persiste !**


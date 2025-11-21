# 🔍 Comment voir les "Deploy Logs" dans Railway

## 📋 Étapes pour voir les logs de déploiement après les migrations

### Étape 1 : Accéder aux "Deploy Logs"

1. **Dans Railway** → Service **"egoejo"** → **Deployments**
2. **Cliquez sur le dernier déploiement** (celui qui est "Active")
3. **En haut de la page**, vous verrez **4 onglets** :
   - **Details** (Détails)
   - **Build Logs** (Logs de construction)
   - **Deploy Logs** ← **CLIQUEZ ICI**
   - **HTTP Logs** (Logs HTTP)

4. **Cliquez sur l'onglet "Deploy Logs"**

### Étape 2 : Voir les logs après les migrations

1. **Dans les "Deploy Logs"**, **faites défiler vers le bas** pour voir les dernières lignes

2. **Vous devriez voir** :
   - Les migrations qui se terminent avec "Applying token_blacklist.0013_alter_blacklistedtoken_options_and_more... OK"
   - **Après cette ligne**, cherchez :
     - Une ligne qui dit `daphne -b 0.0.0.0 -p $PORT config.asgi:application`
     - **Des erreurs** après cette ligne

3. **Les erreurs courantes après les migrations** :
   - `daphne: command not found`
   - `ModuleNotFoundError: No module named 'XXX'`
   - `ImportError: cannot import name 'XXX'`
   - `SyntaxError` ou `IndentationError`
   - `AttributeError: module 'XXX' has no attribute 'XXX'`
   - **Autres erreurs Python**

### Étape 3 : Partager les logs

**Pour que je puisse identifier le problème exact**, **copiez et partagez avec moi** :

1. **Les dernières lignes des "Deploy Logs"** (après les migrations)
   - En particulier les lignes **après** "Applying token_blacklist.0013_alter_blacklistedtoken_options_and_more... OK"
   - **Cherchez les lignes** qui commencent par `daphne` ou qui contiennent des **erreurs**

2. **Toute erreur** que vous voyez dans les logs

---

## 🔍 Que chercher dans les "Deploy Logs"

### Après les migrations réussies, vous devriez voir :

✅ **Si tout fonctionne** :
```
daphne -b 0.0.0.0 -p $PORT config.asgi:application
2025-11-14 13:XX:XX [INFO] Starting server at tcp:port=XXXXX:interface=0.0.0.0
2025-11-14 13:XX:XX [INFO] HTTP/2 support enabled
2025-11-14 13:XX:XX [INFO] Configuring endpoint tcp:port=XXXXX:interface=0.0.0.0
2025-11-14 13:XX:XX [INFO] Listening on TCP address 0.0.0.0:XXXXX
```

❌ **Si ça ne fonctionne pas**, vous verrez une erreur comme :
- `daphne: command not found`
- `ModuleNotFoundError: No module named 'XXX'`
- `ImportError: cannot import name 'XXX' from 'XXX'`
- `SyntaxError: invalid syntax`
- `AttributeError: module 'XXX' has no attribute 'XXX'`
- **Autres erreurs Python**

---

## 📝 Instructions précises

1. **Dans Railway** → Service **"egoejo"** → **Deployments** → Dernier déploiement
2. **Cliquez sur l'onglet "Deploy Logs"** (pas "HTTP Logs")
3. **Faites défiler vers le bas** pour voir les dernières lignes
4. **Cherchez les lignes après** "Applying token_blacklist.0013_alter_blacklistedtoken_options_and_more... OK"
5. **Sélectionnez les 20-30 dernières lignes** des logs
6. **Copiez** (Ctrl+C) et **collez ici**

---

**🚀 Dites-moi ce que vous voyez dans les "Deploy Logs" après les migrations et je vous aiderai à résoudre le problème !**


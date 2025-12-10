# 🔧 Solution - Erreur "nc: port number invalid"

## ❌ Problème identifié

L'erreur `nc: port number invalid:` vient du script `wait_for_db.sh` qui essaie d'utiliser `DATABASE_HOST` et `DATABASE_PORT`, mais Railway utilise `DATABASE_URL`.

## ✅ Solution appliquée

J'ai modifié le `Dockerfile` pour **désactiver l'attente de la base de données** sur Railway, car Railway gère automatiquement les dépendances entre services.

### Changement effectué :
- **Avant** : `CMD sh -c "/wait_for_db.sh && python manage.py migrate && daphne ..."`
- **Après** : `CMD sh -c "python manage.py migrate && daphne ..."`

---

## 🚀 Prochaines étapes

### Option A : Pousser les changements vers GitHub (si vous avez un repo Git)

```powershell
cd C:\Users\treso\Downloads\egoejo
git init
git add backend/Dockerfile backend/wait_for_db.sh backend/config/settings.py backend/requirements.txt
git commit -m "fix: adapter pour Railway (DATABASE_URL, désactiver wait_for_db)"
git remote add origin [URL-de-votre-repo-GitHub]
git push origin main
```

Railway redéploiera automatiquement après le push.

---

### Option B : Déployer directement depuis Railway

Si Railway vous permet de déployer depuis des fichiers locaux :

1. Dans Railway, allez dans votre service "egoejo"
2. Allez dans **Settings** → **Source**
3. Cherchez une option pour **"Deploy from local files"** ou **"Upload files"**

---

### Option C : Modifier directement dans GitHub

Si votre projet est sur GitHub :

1. Allez sur https://github.com
2. Ouvrez votre repository `egoejo`
3. Allez dans `backend/Dockerfile`
4. Cliquez sur "Edit" (icône crayon)
5. Modifiez la ligne `CMD` comme indiqué ci-dessus
6. Committez les changements

Railway redéploiera automatiquement.

---

## 🎯 Solution temporaire : Modifier directement dans Railway

Si vous ne pouvez pas modifier les fichiers, vous pouvez modifier la **Start Command** dans Railway :

1. Dans Railway, allez dans votre service "egoejo"
2. Allez dans **Settings** → **Deploy**
3. Dans **"Start Command"**, entrez :
   ```
   sh -c "python manage.py migrate && daphne -b 0.0.0.0 -p $PORT config.asgi:application"
   ```
4. Sauvegardez (Railway sauvegarde automatiquement)
5. Railway va redéployer automatiquement

---

## ✅ Après avoir appliqué la solution

Une fois le déploiement terminé, vérifiez les logs :

1. Dans Railway, allez dans **Deployments** → **Dernier déploiement** → **Deploy Logs**
2. Vous ne devriez **plus** voir `nc: port number invalid:`
3. Vous devriez voir :
   - ✅ `Operations to perform:`
   - ✅ `Running migrations:`
   - ✅ `Starting server...`

---

**🚀 Quelle option préférez-vous ? Je peux vous guider pour chacune d'elles.**


# ✅ Étapes finales - Configuration Backend ↔ Frontend

## 🎉 Félicitations ! Vous avez modifié la Start Command dans Railway

Le backend Railway devrait maintenant redéployer automatiquement.

---

## ⏳ Étape 1 : Attendre le redéploiement

Dans Railway :

1. **Allez dans votre service "egoejo"**
2. **Cliquez sur l'onglet "Deployments"** en haut
3. **Surveillez le dernier déploiement** :
   - ✅ Il devrait être en cours ("Building..." ou "Deploying...")
   - ✅ Ou terminé avec succès ("Ready")

4. **Vérifiez les logs** :
   - Cliquez sur le dernier déploiement
   - Allez dans **"Deploy Logs"**
   - Vous ne devriez **plus** voir `nc: port number invalid:`
   - Vous devriez voir :
     - ✅ `Operations to perform:`
     - ✅ `Running migrations:`
     - ✅ `Starting server...`
     - ✅ `Application startup complete` (ou similaire)

---

## ✅ Étape 2 : Vérifier que le backend répond

### Test dans PowerShell :
```powershell
Invoke-WebRequest -Uri "https://egoejo-production.up.railway.app/api/" -UseBasicParsing
```

### Test dans le navigateur :
Ouvrez : `https://egoejo-production.up.railway.app/api/`

**Résultat attendu** :
- ✅ Status 200, 404, ou 405 (normal si l'endpoint n'existe pas)
- ✅ Pas d'erreur 502 Bad Gateway

---

## ⚙️ Étape 3 : Configurer les variables d'environnement dans Railway

Dans Railway, service "egoejo" → onglet "Variables", ajoutez/modifiez :

### Variables obligatoires :
```bash
DJANGO_SECRET_KEY=mtOu0flMSlreGirj2T6jIxaYqysq_UVc9YY0ZIYPnGjD0jZLq2kVJQbUg_Amsivx53A
DEBUG=0
ALLOWED_HOSTS=egoejo-production.up.railway.app,*.railway.app
```

### Variables pour SSL (production) :
```bash
SECURE_SSL_REDIRECT=1
SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1
```

### Variables pour CORS (Frontend Vercel) :
```bash
CORS_ALLOWED_ORIGINS=https://frontend-bwrs98104-kazamas-projects-67d737b9.vercel.app
CSRF_TRUSTED_ORIGINS=https://frontend-bwrs98104-kazamas-projects-67d737b9.vercel.app
```

Railway redéploiera automatiquement après avoir modifié les variables.

---

## 🔗 Étape 4 : Mettre à jour le frontend Vercel

Une fois Railway redéployé avec succès et les variables configurées :

```powershell
cd C:\Users\treso\Downloads\egoejo\frontend\frontend

# Supprimer l'ancienne variable
npx vercel env rm VITE_API_URL production

# Ajouter la nouvelle URL Railway
npx vercel env add VITE_API_URL production
# Entrez : https://egoejo-production.up.railway.app

# Redéployer le frontend
npx vercel --prod
```

---

## ✅ Étape 5 : Tester la connexion complète

### Test depuis le frontend Vercel :

1. **Ouvrez votre frontend Vercel** :
   ```
   https://frontend-bwrs98104-kazamas-projects-67d737b9.vercel.app
   ```

2. **Ouvrez la console du navigateur** (F12 → Console)

3. **Testez la connexion** :
   ```javascript
   fetch('https://egoejo-production.up.railway.app/api/')
     .then(r => r.json())
     .then(console.log)
     .catch(console.error)
   ```

**Résultat attendu** :
- ✅ Pas d'erreur CORS
- ✅ Réponse du backend (même si c'est une erreur 404/405, c'est normal)

4. **Testez le formulaire "Rejoindre"** :
   - Allez sur la page "Rejoindre"
   - Remplissez le formulaire
   - Cliquez sur "Envoyer"
   - ✅ Le formulaire devrait fonctionner !

---

## 🎯 Checklist finale

- [ ] Railway redéployé avec succès (pas d'erreur `nc: port number invalid`)
- [ ] Backend Railway accessible (`https://egoejo-production.up.railway.app/api/`)
- [ ] Variables d'environnement configurées dans Railway
- [ ] `VITE_API_URL` mis à jour dans Vercel
- [ ] Frontend Vercel redéployé
- [ ] Pas d'erreur CORS dans la console du navigateur
- [ ] Le formulaire "Rejoindre" fonctionne depuis le frontend

---

**🎉 Une fois toutes ces étapes complétées, votre connexion frontend ↔ backend est complètement fonctionnelle !**


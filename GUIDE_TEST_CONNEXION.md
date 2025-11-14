# 🧪 Guide de test - Connexion Frontend ↔ Backend

## 🌐 URLs configurées

- **Backend Railway** : `https://egoejo-production.up.railway.app`
- **Frontend Vercel** : `https://frontend-bwrs98104-kazamas-projects-67d737b9.vercel.app`

---

## ✅ Test 1 : Vérifier que le backend Railway répond

### Test dans PowerShell :
```powershell
# Test endpoint principal
Invoke-WebRequest -Uri "https://egoejo-production.up.railway.app/api/" -UseBasicParsing

# Test endpoint admin
Invoke-WebRequest -Uri "https://egoejo-production.up.railway.app/admin/" -UseBasicParsing
```

### Test dans le navigateur :
Ouvrez ces URLs dans votre navigateur :
- `https://egoejo-production.up.railway.app/api/`
- `https://egoejo-production.up.railway.app/admin/`

**Résultat attendu** :
- ✅ Status 200 ou 404/405 (normal si l'endpoint n'existe pas)
- ❌ Timeout ou erreur de connexion → Vérifiez que Railway est bien déployé

---

## ✅ Test 2 : Vérifier CORS depuis le frontend

### Test dans la console du navigateur (F12) :

1. **Ouvrez votre frontend Vercel** :
   ```
   https://frontend-bwrs98104-kazamas-projects-67d737b9.vercel.app
   ```

2. **Ouvrez la console du navigateur** (F12 → Console)

3. **Exécutez ce code JavaScript** :
   ```javascript
   fetch('https://egoejo-production.up.railway.app/api/')
     .then(response => {
       console.log('✅ Backend accessible - Status:', response.status);
       return response.text();
     })
     .then(data => console.log('Réponse:', data))
     .catch(error => console.error('❌ Erreur CORS:', error));
   ```

**Résultat attendu** :
- ✅ Pas d'erreur CORS → La connexion fonctionne
- ❌ Erreur "CORS policy" → Vérifiez `CORS_ALLOWED_ORIGINS` dans Railway

---

## ✅ Test 3 : Tester un endpoint spécifique

### Test de l'endpoint `/api/intents/rejoindre/` :

Dans la console du navigateur du frontend Vercel :

```javascript
fetch('https://egoejo-production.up.railway.app/api/intents/rejoindre/', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  }
})
  .then(response => {
    console.log('✅ Status:', response.status);
    return response.json();
  })
  .then(data => console.log('✅ Données:', data))
  .catch(error => console.error('❌ Erreur:', error));
```

**Résultat attendu** :
- ✅ Status 200 ou 405 (normal pour GET sur POST endpoint)
- ❌ Erreur CORS → Vérifiez la configuration CORS dans Railway

---

## ✅ Test 4 : Test complet depuis le frontend

### Test de l'application complète :

1. **Ouvrez votre frontend Vercel** :
   ```
   https://frontend-bwrs98104-kazamas-projects-67d737b9.vercel.app
   ```

2. **Allez sur la page "Rejoindre"** :
   - Cliquez sur "Rejoindre" dans le menu
   - Ou allez directement : `https://frontend-bwrs98104-kazamas-projects-67d737b9.vercel.app/rejoindre`

3. **Remplissez le formulaire** :
   - Nom : Test
   - Email : test@example.com
   - Profil : Sélectionnez un profil
   - Cliquez sur "Envoyer"

4. **Vérifiez** :
   - ✅ Message de succès → La connexion fonctionne !
   - ❌ Erreur → Vérifiez la console du navigateur (F12) pour voir l'erreur

---

## ✅ Test 5 : Vérifier les logs Railway

Dans Railway :

1. **Allez dans votre service "egoejo"**
2. **Cliquez sur l'onglet "Deployments"**
3. **Cliquez sur le dernier déploiement**
4. **Vérifiez les logs** :
   - ✅ "Starting server..."
   - ✅ "Application startup complete"
   - ✅ Pas d'erreurs critiques

---

## ✅ Test 6 : Vérifier les logs Vercel

Dans Vercel :

1. **Allez dans votre projet frontend**
2. **Cliquez sur le dernier déploiement**
3. **Vérifiez les logs** :
   - ✅ Build réussi
   - ✅ Pas d'erreurs de connexion au backend

---

## 🐛 Résolution de problèmes courants

### Problème : Erreur CORS
**Symptôme** : `Access to fetch at '...' from origin '...' has been blocked by CORS policy`

**Solution** :
1. Vérifiez que `CORS_ALLOWED_ORIGINS` dans Railway contient exactement l'URL de votre frontend Vercel (avec `https://`)
2. Redéployez Railway après avoir modifié les variables

### Problème : Timeout ou erreur de connexion
**Symptôme** : `Failed to fetch` ou `Network request failed`

**Solution** :
1. Vérifiez que Railway est bien déployé et accessible
2. Vérifiez que `VITE_API_URL` dans Vercel contient la bonne URL (avec `https://`)
3. Redéployez Vercel après avoir modifié les variables

### Problème : 404 Not Found
**Symptôme** : L'endpoint retourne 404

**Solution** :
1. Vérifiez que les URLs des endpoints sont correctes
2. Vérifiez que le backend Django est bien configuré avec les bonnes URLs

### Problème : 500 Internal Server Error
**Symptôme** : Le backend retourne une erreur 500

**Solution** :
1. Vérifiez les logs Railway pour voir l'erreur exacte
2. Vérifiez que toutes les variables d'environnement sont configurées
3. Vérifiez que la base de données est accessible

---

## ✅ Checklist finale

- [ ] Backend Railway accessible (`https://egoejo-production.up.railway.app/api/`)
- [ ] Variables d'environnement configurées dans Railway
- [ ] CORS configuré correctement dans Railway
- [ ] `VITE_API_URL` mis à jour dans Vercel
- [ ] Frontend Vercel redéployé
- [ ] Pas d'erreur CORS dans la console du navigateur
- [ ] Le formulaire "Rejoindre" fonctionne depuis le frontend
- [ ] Les requêtes API fonctionnent correctement

---

**🎉 Une fois tous ces tests réussis, votre connexion frontend ↔ backend est complètement fonctionnelle !**


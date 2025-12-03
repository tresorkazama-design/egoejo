# 🔧 Fix : Erreur Connexion Base de Données Railway

**Erreur** : `could not translate host name "host" to address`

**Cause** : `DATABASE_URL` n'est pas configuré dans Railway pour le service backend.

---

## ✅ Solution Rapide

### Étape 1 : Configurer `DATABASE_URL` dans Railway

1. **Aller sur Railway Dashboard** : https://railway.app/dashboard
2. **Sélectionner votre projet** → Service **backend** (`egoejo`)
3. **Aller dans "Variables"** (onglet à droite)
4. **Ajouter une nouvelle variable** :
   - **Nom** : `DATABASE_URL`
   - **Valeur** : Cliquer sur **"Reference Variable"** → Sélectionner `${{Postgres.DATABASE_URL}}`
   
   **OU** copier manuellement depuis le service Postgres :
   - Aller dans le service **Postgres** → **Variables**
   - Copier la valeur de `DATABASE_URL`
   - Coller dans le service backend

### Étape 2 : Vérifier les autres variables obligatoires

Dans le service backend, assurez-vous d'avoir :

```bash
DJANGO_SECRET_KEY=<votre secret key>
DEBUG=0
ALLOWED_HOSTS=*.railway.app,egoejo-production.up.railway.app
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### Étape 3 : Redéployer

1. Dans le service backend, cliquer sur **"Redeploy"**
2. Attendre la fin du déploiement
3. Vérifier les logs

---

## 🔍 Vérification

### Vérifier que ça fonctionne

```bash
curl https://egoejo-production.up.railway.app/api/health/
```

**Résultat attendu** :
```json
{
  "status": "healthy",
  "checks": {
    "database": "ok"
  }
}
```

---

## 📋 Checklist

- [ ] Service Postgres est démarré (icône verte)
- [ ] `DATABASE_URL` est configuré dans le service backend
- [ ] `DJANGO_SECRET_KEY` est configuré
- [ ] `DEBUG=0` est configuré
- [ ] `ALLOWED_HOSTS` contient `*.railway.app`
- [ ] Service backend redéployé
- [ ] Health check fonctionne

---

**Une fois `DATABASE_URL` configuré, le problème sera résolu !** ✅


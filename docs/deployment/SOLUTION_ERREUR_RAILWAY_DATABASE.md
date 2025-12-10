# 🔧 Solution : Erreur de Connexion Base de Données Railway

**Erreur** : `could not translate host name "host" to address: No address associated with hostname`

**Cause** : Django n'arrive pas à se connecter à PostgreSQL car `DATABASE_URL` n'est pas configuré ou `dj-database-url` n'est pas installé.

---

## ✅ Solution

### Étape 1 : Vérifier que `dj-database-url` est installé

Le package `dj-database-url` doit être dans `requirements.txt` :

```txt
dj-database-url>=2.1.0
```

**Si ce n'est pas le cas**, ajoutez-le :

```powershell
cd C:\Users\treso\Downloads\egoejo\backend
echo dj-database-url>=2.1.0 >> requirements.txt
```

### Étape 2 : Configurer `DATABASE_URL` dans Railway

1. Aller sur : **https://railway.app/dashboard**
2. Sélectionner votre projet
3. Sélectionner le service **Postgres**
4. Aller dans l'onglet **"Variables"**
5. Chercher la variable **`DATABASE_URL`** ou **`POSTGRES_URL`**
6. **Copier la valeur complète** (format : `postgresql://user:password@host:port/dbname`)

### Étape 3 : Ajouter `DATABASE_URL` au service backend

1. Dans Railway, sélectionner le service **backend** (`egoejo`)
2. Aller dans **"Variables"**
3. Ajouter une nouvelle variable :
   - **Nom** : `DATABASE_URL`
   - **Valeur** : Coller la valeur copiée depuis Postgres
4. **OU** utiliser la variable de référence Railway :
   - **Nom** : `DATABASE_URL`
   - **Valeur** : Cliquer sur **"Reference Variable"** et sélectionner `${{Postgres.DATABASE_URL}}`

### Étape 4 : Vérifier les autres variables

Assurez-vous que ces variables sont configurées dans le service backend :

```bash
# Obligatoires
DJANGO_SECRET_KEY=<votre secret key>
DEBUG=0
ALLOWED_HOSTS=*.railway.app,egoejo-production.up.railway.app

# Base de données (automatique si DATABASE_URL est configuré)
DATABASE_URL=${{Postgres.DATABASE_URL}}
# OU manuellement :
# DATABASE_URL=postgresql://user:password@host:port/dbname

# CORS
CORS_ALLOWED_ORIGINS=https://egoejo.vercel.app
CSRF_TRUSTED_ORIGINS=https://egoejo.vercel.app
```

### Étape 5 : Redéployer

1. Dans Railway, aller dans le service backend
2. Cliquer sur **"Redeploy"** ou **"Deploy"**
3. Attendre que le déploiement se termine
4. Vérifier les logs

---

## 🔍 Vérification

### Vérifier que `DATABASE_URL` est bien configuré

Dans les logs de déploiement Railway, vous devriez voir :
- ✅ Pas d'erreur de connexion
- ✅ Les migrations s'exécutent correctement
- ✅ Le serveur démarre

### Tester la connexion

Une fois déployé, tester l'endpoint de health check :

```bash
curl https://egoejo-production.up.railway.app/api/health/
```

**Résultat attendu** :
```json
{
  "status": "healthy",
  "checks": {
    "database": "ok",
    "cache": "ok"
  }
}
```

---

## 🐛 Si le problème persiste

### Option 1 : Vérifier les logs Railway

1. Aller dans **"Deploy Logs"** du service backend
2. Chercher les erreurs de connexion
3. Vérifier que `DATABASE_URL` est bien affiché (masqué) dans les logs

### Option 2 : Vérifier manuellement

Dans Railway, vérifier que :
- ✅ Le service Postgres est **démarré** (icône verte)
- ✅ Le service backend a accès à Postgres (même projet)
- ✅ `DATABASE_URL` est bien défini dans les variables

### Option 3 : Utiliser les variables individuelles (non recommandé)

Si `DATABASE_URL` ne fonctionne pas, vous pouvez utiliser les variables individuelles :

```bash
DB_NAME=${{Postgres.POSTGRES_DB}}
DB_USER=${{Postgres.POSTGRES_USER}}
DB_PASSWORD=${{Postgres.POSTGRES_PASSWORD}}
DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}
```

**⚠️ Note** : Cette méthode est moins fiable que `DATABASE_URL`.

---

## 📋 Checklist

- [ ] `dj-database-url` est dans `requirements.txt`
- [ ] `DATABASE_URL` est configuré dans Railway (service backend)
- [ ] Le service Postgres est démarré
- [ ] Les variables d'environnement sont correctes
- [ ] Le service backend a été redéployé
- [ ] Les logs ne montrent plus d'erreur de connexion

---

## 📚 Documentation

- `VARIABLES_PRODUCTION.md` - Liste complète des variables
- `GUIDE_PRODUCTION.md` - Guide complet de production
- `GUIDE_TROUBLESHOOTING.md` - Guide de troubleshooting

---

**Une fois `DATABASE_URL` configuré, le problème devrait être résolu !** ✅


# 🔧 Guide de Configuration - R2 & PgBouncer

**Date** : 2025-01-27  
**Objectif** : Configurer la persistance des médias (R2) et le pooling de connexions (PgBouncer)

---

## 📦 1. Configuration Cloudflare R2 (Stockage Médias)

### Étape 1 : Créer un bucket R2

1. Aller sur [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Sélectionner **R2** dans le menu
3. Cliquer sur **Create bucket**
4. Nommer le bucket : `egoejo-media`
5. Choisir la localisation (ex: `auto`)

### Étape 2 : Créer une API Token

1. Dans R2, aller dans **Manage R2 API Tokens**
2. Cliquer sur **Create API Token**
3. Configurer :
   - **Token name** : `egoejo-media-upload`
   - **Permissions** : Object Read & Write
   - **TTL** : Sans expiration (ou selon vos besoins)
4. **Copier** l'Access Key ID et Secret Access Key

### Étape 3 : Configurer les variables d'environnement

**Railway (Backend)** :
```env
USE_S3_STORAGE=true
R2_ACCESS_KEY_ID=votre-access-key-id
R2_SECRET_ACCESS_KEY=votre-secret-access-key
R2_BUCKET_NAME=egoejo-media
R2_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com
R2_CUSTOM_DOMAIN=media.egoejo.org  # Optionnel: si vous configurez un domaine personnalisé
```

**Note** : Pour trouver l'endpoint R2 :
1. Dans le dashboard R2, cliquer sur votre bucket
2. L'endpoint est affiché dans les détails (format: `https://xxx.r2.cloudflarestorage.com`)

### Étape 4 : (Optionnel) Configurer un domaine personnalisé

1. Dans R2, aller dans **Settings** du bucket
2. Section **Public Access**
3. Ajouter un domaine personnalisé (ex: `media.egoejo.org`)
4. Configurer le DNS CNAME pointant vers le bucket R2

---

## 🔌 2. Configuration PgBouncer (Connection Pooling)

### Option A : PgBouncer sur Railway (Recommandé)

#### Étape 1 : Créer un service PgBouncer

1. Dans Railway, créer un nouveau service
2. Choisir **Deploy from GitHub** ou **Empty Service**
3. Nommer : `pgbouncer`

#### Étape 2 : Configurer PgBouncer

**Créer un fichier `Dockerfile`** :
```dockerfile
FROM pgbouncer/pgbouncer:latest

# Copier la configuration
COPY pgbouncer.ini /etc/pgbouncer/pgbouncer.ini
COPY userlist.txt /etc/pgbouncer/userlist.txt

EXPOSE 5432
```

**Créer `pgbouncer.ini`** :
```ini
[databases]
egoejo = host=${POSTGRES_HOST} port=5432 dbname=${POSTGRES_DB}

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 3
max_db_connections = 100
listen_addr = 0.0.0.0
listen_port = 5432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
logfile = /var/log/pgbouncer/pgbouncer.log
pidfile = /var/run/pgbouncer/pgbouncer.pid
admin_users = admin
stats_users = admin
```

**Créer `userlist.txt`** :
```
"admin" "md5_hashed_password"
"egoejo_user" "md5_hashed_password"
```

**Note** : Pour générer le hash MD5 :
```bash
echo -n "passwordusername" | md5sum
```

#### Étape 3 : Variables d'environnement Railway

**Service PgBouncer** :
```env
POSTGRES_HOST=postgres.railway.internal  # Host PostgreSQL interne Railway
POSTGRES_DB=railway
POSTGRES_USER=postgres
POSTGRES_PASSWORD=votre-password-postgres
```

**Service Backend** :
```env
# Mettre à jour DATABASE_URL pour pointer vers PgBouncer
DATABASE_URL=postgresql://egoejo_user:password@pgbouncer.railway.app:5432/egoejo
```

### Option B : PgBouncer dans le conteneur (Simple)

Si vous préférez une solution plus simple, vous pouvez installer PgBouncer directement dans votre conteneur Django :

**Ajouter à `requirements.txt`** :
```txt
# Note: PgBouncer n'est pas un package Python, cette option nécessite
# d'installer PgBouncer dans le conteneur via apt-get
```

**Modifier `Dockerfile` backend** :
```dockerfile
FROM python:3.11-slim

# Installer PgBouncer
RUN apt-get update && apt-get install -y pgbouncer postgresql-client

# ... reste de la configuration Django ...
```

**Note** : Cette option est moins recommandée car elle mélange les responsabilités.

---

## ✅ 3. Vérification

### Vérifier R2

```bash
# Tester l'upload d'un fichier via l'admin Django
# Les fichiers doivent apparaître dans le bucket R2
```

### Vérifier PgBouncer

```bash
# Se connecter à PgBouncer
psql -h pgbouncer.railway.app -U egoejo_user -d egoejo

# Vérifier les statistiques
SHOW POOLS;
SHOW STATS;
```

---

## 🔍 4. Dépannage

### R2 : Erreur "Access Denied"

- Vérifier que les credentials sont corrects
- Vérifier les permissions du token R2
- Vérifier que le bucket existe

### PgBouncer : Erreur de connexion

- Vérifier que `DATABASE_URL` pointe vers PgBouncer
- Vérifier que PgBouncer peut se connecter à PostgreSQL
- Vérifier les logs PgBouncer : `docker logs pgbouncer`

### Recherche full-text ne fonctionne pas

```sql
-- Vérifier que l'extension est activée
SELECT * FROM pg_extension WHERE extname = 'pg_trgm';

-- Si absent, activer manuellement
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

---

## 📚 Références

- [Cloudflare R2 Documentation](https://developers.cloudflare.com/r2/)
- [django-storages Documentation](https://django-storages.readthedocs.io/)
- [PgBouncer Documentation](https://www.pgbouncer.org/)
- [PostgreSQL pg_trgm](https://www.postgresql.org/docs/current/pgtrgm.html)

---

**Dernière mise à jour** : 2025-01-27


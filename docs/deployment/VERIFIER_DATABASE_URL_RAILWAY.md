# 🔍 Vérifier DATABASE_URL dans Railway

## ❌ Problème identifié

L'erreur `could not translate host name "db" to address` signifie que :
- Django n'a pas trouvé `DATABASE_URL` dans les variables d'environnement
- Django utilise donc les variables individuelles (`DB_HOST`, `DB_NAME`, etc.)
- Et comme ces variables ne sont pas définies, Django utilise les valeurs par défaut (`DB_HOST='db'`)

---

## ✅ Solution : Vérifier que DATABASE_URL est disponible

Dans Railway :

1. **Allez dans votre service "egoejo"**
2. **Cliquez sur l'onglet "Variables"** en haut
3. **Cherchez la variable `DATABASE_URL`**

### Si DATABASE_URL n'est pas présente :

Cela signifie que Railway n'a pas automatiquement ajouté la variable. Il faut la lier manuellement :

1. **Dans Railway, allez dans votre projet** (pas le service)
2. **Cliquez sur le service PostgreSQL** (dans la sidebar gauche)
3. **Cherchez une section "Variables"** ou **"Connect"**
4. **Notez les variables de connexion** (PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE)
5. **Ou créez manuellement `DATABASE_URL`** dans votre service "egoejo"

---

## 🔧 Solution : Créer DATABASE_URL manuellement

Si Railway n'a pas automatiquement ajouté `DATABASE_URL`, créez-la manuellement :

1. **Dans Railway, allez dans votre service PostgreSQL** (dans la sidebar gauche du projet)
2. **Allez dans l'onglet "Variables"** du service PostgreSQL
3. **Notez les valeurs** :
   - `PGHOST`
   - `PGPORT`
   - `PGUSER`
   - `PGPASSWORD`
   - `PGDATABASE`

4. **Dans votre service "egoejo", ajoutez la variable `DATABASE_URL`** :
   ```
   postgresql://PGUSER:PGPASSWORD@PGHOST:PGPORT/PGDATABASE
   ```
   
   Remplacez :
   - `PGUSER` par la valeur de PGUSER
   - `PGPASSWORD` par la valeur de PGPASSWORD
   - `PGHOST` par la valeur de PGHOST
   - `PGPORT` par la valeur de PGPORT (généralement 5432)
   - `PGDATABASE` par la valeur de PGDATABASE

**Exemple** :
```
postgresql://postgres:password123@monorail.proxy.rlwy.net:5432/railway
```

---

## 🔗 Solution alternative : Lier les services Railway

Railway devrait automatiquement créer `DATABASE_URL` si les services sont liés :

1. **Dans Railway, allez dans votre projet**
2. **Vérifiez que votre service "egoejo" et le service PostgreSQL sont dans le même projet**
3. **Si ce n'est pas le cas**, ajoutez le service PostgreSQL au projet :
   - Cliquez sur "+ New" dans le projet
   - Sélectionnez "Database" → "Add PostgreSQL"

4. **Railway devrait automatiquement créer `DATABASE_URL`** pour votre service "egoejo"

---

## ⚙️ Solution temporaire : Utiliser les variables individuelles

Si vous ne pouvez pas créer `DATABASE_URL`, ajoutez les variables individuelles dans Railway :

Dans votre service "egoejo" → Variables, ajoutez :

```bash
DB_HOST=[valeur de PGHOST du service PostgreSQL]
DB_PORT=[valeur de PGPORT du service PostgreSQL, généralement 5432]
DB_NAME=[valeur de PGDATABASE du service PostgreSQL]
DB_USER=[valeur de PGUSER du service PostgreSQL]
DB_PASSWORD=[valeur de PGPASSWORD du service PostgreSQL]
```

---

## 🆘 Vérification dans Railway

**Dans Railway, vérifiez** :

1. **Service "egoejo"** → **Variables** → Est-ce que `DATABASE_URL` est présente ?
2. **Service PostgreSQL** → **Variables** → Quelles variables sont disponibles ?

**Dites-moi ce que vous voyez et je vous aiderai à configurer correctement !**


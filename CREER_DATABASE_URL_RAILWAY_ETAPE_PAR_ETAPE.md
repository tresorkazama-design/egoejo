# 📝 Guide étape par étape - Créer DATABASE_URL dans Railway

## 🎯 Objectif
Créer la variable d'environnement `DATABASE_URL` dans votre service "egoejo" pour que Django puisse se connecter à PostgreSQL.

---

## 📋 Étape 1 : Trouver les informations PostgreSQL

### Dans Railway :

1. **Ouvrez Railway** dans votre navigateur : https://railway.app

2. **Allez dans votre projet** "fantastic-vibrancy" (ou le nom de votre projet)

3. **Dans la sidebar de gauche**, vous verrez :
   - **Postgres** (ou PostgreSQL)
   - **egoejo**

4. **Cliquez sur "Postgres"** (ou PostgreSQL) dans la sidebar gauche

5. **Cliquez sur l'onglet "Variables"** en haut (à côté de "Deployments", "Metrics", etc.)

6. **Vous verrez plusieurs variables** comme :
   - `PGHOST` = quelque chose comme `monorail.proxy.rlwy.net`
   - `PGPORT` = `5432`
   - `PGUSER` = `postgres`
   - `PGPASSWORD` = un mot de passe généré
   - `PGDATABASE` = `railway`

7. **Notez ces valeurs** (ou gardez cette page ouverte dans un autre onglet)

---

## 📋 Étape 2 : Créer DATABASE_URL dans le service "egoejo"

### Dans Railway :

1. **Revenez à votre projet** (cliquez sur le nom du projet en haut à gauche)

2. **Dans la sidebar de gauche**, cliquez sur **"egoejo"**

3. **Cliquez sur l'onglet "Variables"** en haut

4. **Cherchez la variable `DATABASE_URL`** dans la liste

### Si `DATABASE_URL` n'existe pas :

5. **Cliquez sur le bouton "+ New Variable"** ou **"Add Variable"** (généralement en haut à droite ou au-dessus de la liste des variables)

6. **Dans le formulaire qui apparaît** :
   - **Name** (Nom) : Tapez `DATABASE_URL` (exactement comme ça, en majuscules)
   - **Value** (Valeur) : Tapez cette formule (remplacez les valeurs entre crochets) :
     ```
     postgresql://[PGUSER]:[PGPASSWORD]@[PGHOST]:[PGPORT]/[PGDATABASE]
     ```
   
   **Exemple concret** (remplacez par VOS valeurs du service PostgreSQL) :
   ```
   postgresql://postgres:MonMotDePasse123@monorail.proxy.rlwy.net:5432/railway
   ```

7. **Environment** (Environnement) : Sélectionnez **"Production"** (ou cochez tous les environnements si vous voulez)

8. **Cliquez sur "Add"** ou **"Save"** pour créer la variable

---

## 🔍 Exemple concret

Supposons que dans votre service PostgreSQL, vous voyez :
- `PGHOST` = `monorail.proxy.rlwy.net`
- `PGPORT` = `5432`
- `PGUSER` = `postgres`
- `PGPASSWORD` = `ABC123xyz456`
- `PGDATABASE` = `railway`

Alors dans votre service "egoejo", créez `DATABASE_URL` avec cette valeur :
```
postgresql://postgres:ABC123xyz456@monorail.proxy.rlwy.net:5432/railway
```

⚠️ **Important** : Remplacez `ABC123xyz456` par la vraie valeur de `PGPASSWORD` de votre service PostgreSQL !

---

## ✅ Étape 3 : Vérifier

Après avoir créé `DATABASE_URL` :

1. **Dans la liste des variables** du service "egoejo", vous devriez voir `DATABASE_URL`
2. **Railway va automatiquement redéployer** votre service avec la nouvelle variable
3. **Attendez quelques secondes/minutes** que le redéploiement se termine

---

## 🆘 Si vous ne trouvez pas "+ New Variable"

Dans Railway, le bouton pour ajouter une variable peut être :
- **"+ New Variable"** en haut à droite
- **"Add Variable"** en haut à droite
- **"+"** (icône plus) à côté de "Variables"
- Ou **un champ vide** où vous pouvez taper directement

Si vous ne le trouvez pas, dites-moi ce que vous voyez dans l'onglet "Variables" et je vous guiderai plus précisément.

---

## 📸 Aide visuelle

Quand vous êtes dans votre service "egoejo" → "Variables", vous devriez voir :
- Une liste de variables (comme `DJANGO_SECRET_KEY` que vous avez déjà ajouté)
- Un bouton pour ajouter une nouvelle variable (généralement en haut à droite)
- Quand vous cliquez dessus, un formulaire apparaît avec :
  - **Name** : champ texte pour le nom de la variable
  - **Value** : champ texte pour la valeur de la variable
  - **Environment** : sélecteur pour choisir l'environnement

---

**📝 Dites-moi où vous êtes bloqué et je vous aiderai !**


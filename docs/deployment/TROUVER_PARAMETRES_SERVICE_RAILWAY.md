# 🔍 Comment trouver les paramètres du service (Root Directory, Dockerfile) dans Railway

## ⚠️ Important : Service Settings vs Project Settings

Les paramètres **"Root Directory"** et **"Dockerfile Path"** se trouvent dans les **paramètres du SERVICE**, pas dans les paramètres du projet.

---

## 📍 Étape 1 : Quitter Project Settings

1. Cliquez sur **"< Back"** ou **"Dashboard"** en haut à gauche pour revenir au tableau de bord du projet
2. Ou cliquez sur le nom de votre projet en haut à gauche

---

## 📦 Étape 2 : Aller dans le service Web

Dans votre projet Railway, vous devriez voir :
- Un ou plusieurs **services** listés (comme "web", "worker", etc.)
- Ou si vous venez de créer le projet, il n'y a peut-être pas encore de service

### Si vous n'avez pas encore de service :

1. Cliquez sur **"+ New"** dans votre projet
2. Sélectionnez **"GitHub Repo"**
3. Choisissez votre repository `egoejo`
4. Railway va créer automatiquement un service

### Si vous avez déjà un service :

1. **Cliquez sur le service** (par exemple "web" ou le nom de votre service)
2. Cela vous amène à la page du service

---

## ⚙️ Étape 3 : Accéder aux Service Settings

Une fois dans la page du service :

1. **Cliquez sur l'onglet "Settings"** (dans le menu horizontal en haut)
2. Vous devriez voir plusieurs sections :
   - **"Source"** ← C'est ici !
   - **"Deploy"**
   - **"Variables"**
   - **"Networking"**
   - etc.

---

## 🔧 Étape 4 : Configurer dans "Source"

Dans la section **"Source"**, vous devriez voir :

1. **"Repository"** : Votre repository GitHub
2. **"Branch"** : La branche à déployer (généralement "main")
3. **"Root Directory"** : 📝 Changez cela en `backend`
4. **"Dockerfile Path"** : 📝 Changez cela en `Dockerfile.railway` (ou créez un fichier `Dockerfile` dans `backend/`)

---

## 🎯 Si vous ne voyez toujours pas "Source" :

### Option A : Créer un nouveau service depuis GitHub

1. Allez dans votre projet Railway
2. Cliquez sur **"+ New"**
3. Sélectionnez **"GitHub Repo"**
4. Choisissez votre repository `egoejo`
5. Railway va créer un service et vous amener à sa page
6. Allez dans **"Settings"** → **"Source"**

### Option B : Utiliser railway.toml

Alternativement, Railway peut utiliser le fichier `railway.toml` que nous avons créé à la racine de votre projet. Railway le détectera automatiquement.

---

## 🔄 Étape 5 : Après configuration

Une fois que vous avez configuré :
- **Root Directory** : `backend`
- **Dockerfile Path** : `Dockerfile.railway`

Railway va automatiquement :
1. Détecter les changements
2. Lancer un nouveau déploiement

---

## 🆘 Si ça ne fonctionne toujours pas :

Essayez cette approche alternative :

### Créer un Dockerfile à la racine du projet

Créez un fichier `Dockerfile` à la racine de votre projet (pas dans `backend/`) qui pointe vers le bon répertoire :

```dockerfile
FROM python:3.12-slim

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copier depuis le répertoire backend
COPY backend/requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY backend/ /app/

COPY backend/wait_for_db.sh /wait_for_db.sh
RUN chmod +x /wait_for_db.sh

RUN python manage.py collectstatic --noinput || true

CMD sh -c "/wait_for_db.sh && python manage.py migrate && daphne -b 0.0.0.0 -p ${PORT:-8000} config.asgi:application"
```

Ensuite, dans Railway :
- **Root Directory** : `.` (la racine)
- **Dockerfile Path** : `Dockerfile`

---

**📍 Résumé : Cliquez sur votre SERVICE (pas le projet) → Settings → Source**


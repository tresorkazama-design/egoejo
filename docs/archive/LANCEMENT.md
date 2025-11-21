# Guide de Lancement - EGOEJO

## Prérequis

- Docker Desktop installé et démarré (pour le mode Docker)
- OU Python 3.11+ et Node.js 18+ (pour le mode local)

## Option 1 : Lancement avec Docker (Recommandé)

### 1. Démarrer Docker Desktop

Assurez-vous que Docker Desktop est démarré sur votre machine.

### 2. Créer les migrations

```bash
docker-compose run --rm api python manage.py makemigrations
docker-compose run --rm api python manage.py migrate
```

### 3. Créer un superutilisateur (optionnel)

```bash
docker-compose run --rm api python manage.py createsuperuser
```

### 4. Lancer tous les services

```bash
docker-compose up --build
```

### 5. Accéder aux services

- **API Backend** : http://localhost:8000/api/
- **Django Admin** : http://localhost:8000/admin/
- **Frontend** : http://localhost:3000 (si configuré)

## Option 2 : Lancement Local (Développement)

### Backend (Django)

#### 1. Installer les dépendances

```bash
cd backend
pip install -r requirements.txt
```

#### 2. Configurer les variables d'environnement

Le fichier `backend/.env` doit contenir :

```env
DJANGO_SECRET_KEY=votre-secret-key
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=egoejo_db
DB_USER=egoejo_user
DB_PASSWORD=egoejo_password
DB_HOST=localhost
DB_PORT=5432
ADMIN_TOKEN=votre-admin-token
```

#### 3. Démarrer PostgreSQL

Assurez-vous que PostgreSQL est installé et démarré, puis créez la base de données :

```sql
CREATE DATABASE egoejo_db;
CREATE USER egoejo_user WITH PASSWORD 'egoejo_password';
GRANT ALL PRIVILEGES ON DATABASE egoejo_db TO egoejo_user;
```

#### 4. Créer les migrations

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

#### 5. Créer un superutilisateur (optionnel)

```bash
python manage.py createsuperuser
```

#### 6. Lancer le serveur de développement

```bash
python manage.py runserver
```

Le backend sera accessible sur http://localhost:8000

### Frontend (React)

#### 1. Installer les dépendances

```bash
cd frontend
npm install
```

#### 2. Configurer l'API URL (optionnel)

Créer un fichier `frontend/.env` :

```env
VITE_API_URL=http://localhost:8000
```

#### 3. Lancer le serveur de développement

```bash
npm run dev
```

Le frontend sera accessible sur http://localhost:5173 (ou le port affiché)

## Vérification

### Test de l'API

```bash
# Test de l'endpoint de santé (si disponible)
curl http://localhost:8000/api/

# Test de l'endpoint rejoindre
curl -X POST http://localhost:8000/api/intents/rejoindre/ \
  -H "Content-Type: application/json" \
  -d '{"nom":"Test","email":"test@example.com","profil":"je-decouvre"}'
```

### Test de l'Admin

Accéder à http://localhost:8000/admin/ et se connecter avec le superutilisateur créé.

### Test du Frontend

Accéder à http://localhost:3000 ou http://localhost:5173 selon la configuration.

## Dépannage

### Docker ne démarre pas

- Vérifier que Docker Desktop est installé et démarré
- Vérifier que les ports 5432 (PostgreSQL) et 8000 (API) ne sont pas utilisés
- Vérifier les logs : `docker-compose logs`

### Erreurs de base de données

- Vérifier que PostgreSQL est démarré
- Vérifier les variables d'environnement dans `backend/.env`
- Vérifier les permissions de la base de données

### Erreurs de connexion API

- Vérifier que le backend est démarré
- Vérifier la variable `VITE_API_URL` dans le frontend
- Vérifier les CORS dans `backend/config/settings.py`

### Erreurs de migrations

```bash
# Supprimer les migrations (ATTENTION: perte de données)
cd backend
rm -rf core/migrations/0*.py
python manage.py makemigrations
python manage.py migrate
```

## Commandes Utiles

### Docker

```bash
# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v

# Rebuild les images
docker-compose build --no-cache
```

### Django

```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Shell Django
python manage.py shell

# Tests
python manage.py test
```

### Frontend

```bash
# Installer les dépendances
npm install

# Lancer le serveur de développement
npm run dev

# Build pour la production
npm run build

# Tests
npm run test
```


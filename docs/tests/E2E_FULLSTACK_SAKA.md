# Tests E2E Full-Stack : Cycle SAKA Complet

## 📋 Vue d'ensemble

Ce document décrit les tests E2E full-stack pour valider le cycle complet SAKA avec un backend réel (Django test server).

### Objectif

Valider que le cycle SAKA complet fonctionne correctement :
1. **Création utilisateur** : Inscription et authentification
2. **Récolte SAKA** : Récolte via lecture de contenu ou vote
3. **Plantation SAKA** : Boost d'un projet
4. **Compost** : Vérification du compostage (si activé)
5. **Anti-accumulation** : Vérification qu'aucune accumulation infinie n'est possible

### Contraintes

- ✅ **Backend réel** : Django test server (pas de mocks)
- ✅ **Base de données de test** : Isolée et idempotente
- ✅ **Aucun mock API** : Toutes les requêtes vont vers le backend réel
- ✅ **Test isolé** : Chaque test utilise des identifiants uniques
- ✅ **Test idempotent** : Peut être exécuté plusieurs fois sans effet de bord

---

## 🚀 Exécution Locale

### Prérequis

1. **Backend Django** : Python 3.11+, Django 5.2+
2. **Frontend** : Node.js 18+, npm
3. **Base de données** : SQLite (pour les tests) ou PostgreSQL
4. **Redis** : Optionnel (pour la redistribution du Silo)

### Étape 1 : Démarrer le Backend en Mode Test

#### Option A : Script Shell (Linux/Mac)

```bash
cd backend
chmod +x scripts/start_test_server.sh
./scripts/start_test_server.sh
```

#### Option B : Script PowerShell (Windows)

```powershell
cd backend
.\scripts\start_test_server.ps1
```

#### Option C : Manuel

```bash
cd backend
export DJANGO_SETTINGS_MODULE=config.settings_test
export ENABLE_SAKA=True
export SAKA_COMPOST_ENABLED=True
export SAKA_SILO_REDIS_ENABLED=True
python manage.py migrate --run-syncdb --noinput
python manage.py runserver 127.0.0.1:8000
```

Le serveur démarre sur `http://127.0.0.1:8000`.

### Étape 2 : Démarrer le Frontend

```bash
cd frontend/frontend
npm run dev
```

Le frontend démarre sur `http://localhost:5173`.

### Étape 3 : Exécuter les Tests E2E Full-Stack

```bash
cd frontend/frontend
E2E_MODE=full-stack BACKEND_URL=http://127.0.0.1:8000 npx playwright test e2e/saka-cycle-fullstack.spec.js
```

#### Windows (PowerShell)

```powershell
cd frontend/frontend
$env:E2E_MODE="full-stack"
$env:BACKEND_URL="http://127.0.0.1:8000"
npx playwright test e2e/saka-cycle-fullstack.spec.js
```

---

## 🔧 Configuration CI/CD

### GitHub Actions

Exemple de workflow pour exécuter les tests E2E full-stack :

```yaml
name: E2E Full-Stack SAKA

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  e2e-fullstack:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: egotest_e2e
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4
      
      - name: 🐍 Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
          cache-dependency-path: backend/requirements.txt
      
      - name: 📦 Install backend dependencies
        run: |
          cd backend
          pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: 🗄️ Setup database
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/egotest_e2e
          SECRET_KEY: test-secret-key-for-ci-e2e-fullstack-testing-min-50-chars-required-egoejo
          ENABLE_SAKA: 'True'
          SAKA_COMPOST_ENABLED: 'True'
          SAKA_SILO_REDIS_ENABLED: 'True'
        run: |
          cd backend
          export DJANGO_SETTINGS_MODULE=config.settings_test
          python manage.py migrate --run-syncdb --noinput
      
      - name: 🚀 Start backend server
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/egotest_e2e
          SECRET_KEY: test-secret-key-for-ci-e2e-fullstack-testing-min-50-chars-required-egoejo
          ENABLE_SAKA: 'True'
          SAKA_COMPOST_ENABLED: 'True'
          SAKA_SILO_REDIS_ENABLED: 'True'
          REDIS_URL: redis://localhost:6379/0
        run: |
          cd backend
          export DJANGO_SETTINGS_MODULE=config.settings_test
          python manage.py runserver 127.0.0.1:8000 &
          sleep 5  # Attendre que le serveur démarre
      
      - name: 📦 Install frontend dependencies
        run: |
          cd frontend/frontend
          npm ci
      
      - name: 🧪 Run E2E full-stack tests
        env:
          E2E_MODE: full-stack
          BACKEND_URL: http://127.0.0.1:8000
        run: |
          cd frontend/frontend
          npx playwright test e2e/saka-cycle-fullstack.spec.js
```

---

## 📊 Tests Inclus

### 1. Création utilisateur et authentification

- ✅ Création d'un utilisateur via `/api/auth/register/`
- ✅ Authentification via `/api/auth/login/`
- ✅ Vérification que le wallet SAKA est créé automatiquement

### 2. Récolte SAKA

- ✅ Récolte via lecture de contenu (déclenche automatiquement)
- ✅ Vérification que le solde SAKA augmente

### 3. Plantation SAKA (boost projet)

- ✅ Création d'un projet de test
- ✅ Boost du projet avec du SAKA
- ✅ Vérification que le solde SAKA diminue

### 4. Vérification du cycle complet

- ✅ Vérification que `total_harvested` > 0
- ✅ Vérification que `total_planted` > 0
- ✅ Vérification que `total_harvested` >= `total_planted`

### 5. Vérification anti-accumulation

- ✅ Vérification que le solde n'est pas excessif
- ✅ Vérification que le compostage est configuré

### 6. Test du compostage (si admin disponible)

- ✅ Vérification que le compostage est activé
- ✅ Vérification de l'état du Silo

### 7. Vérification de l'isolation et de l'idempotence

- ✅ Vérification que les données du test sont cohérentes
- ✅ Vérification que le projet existe toujours

---

## 🐛 Dépannage

### Problème : "Backend non accessible"

**Solution** : Vérifier que le backend est démarré :

```bash
curl http://127.0.0.1:8000/api/health/
```

### Problème : "Base de données locked"

**Solution** : Utiliser une base de données en mémoire ou un fichier temporaire :

```python
# Dans settings_test.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Base de données en mémoire
    }
}
```

### Problème : "SAKA non activé"

**Solution** : Vérifier les variables d'environnement :

```bash
export ENABLE_SAKA=True
export SAKA_COMPOST_ENABLED=True
export SAKA_SILO_REDIS_ENABLED=True
```

### Problème : "CORS policy error"

**Solution** : Vérifier la configuration CORS dans `settings_test.py` :

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

---

## ✅ Checklist de Validation

Avant de considérer les tests comme valides :

- [ ] Backend démarré sur `http://127.0.0.1:8000`
- [ ] Frontend démarré sur `http://localhost:5173`
- [ ] SAKA activé (`ENABLE_SAKA=True`)
- [ ] Compostage activé (`SAKA_COMPOST_ENABLED=True`)
- [ ] Base de données de test initialisée
- [ ] Tous les tests passent (7/7)
- [ ] Aucune erreur de connexion
- [ ] Cycle SAKA complet validé

---

## 📝 Notes Importantes

1. **Isolation** : Chaque test utilise des identifiants uniques (timestamp) pour éviter les conflits
2. **Idempotence** : Les tests peuvent être exécutés plusieurs fois sans effet de bord
3. **Backend réel** : Aucun mock API, toutes les requêtes vont vers le backend réel
4. **Base de données de test** : Isolée de la base de données de développement/production

---

**Fin du document**

*Les tests E2E full-stack garantissent que le cycle SAKA complet fonctionne correctement avec un backend réel.*


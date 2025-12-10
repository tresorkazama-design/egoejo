# 🚀 Guide de Démarrage du Backend Django

## Prérequis

1. **Python 3.10+** installé
2. **Dépendances installées** : `pip install -r requirements.txt`
3. **Base de données** : SQLite (par défaut) ou PostgreSQL

---

## 📋 Étapes de Démarrage

### Étape 1 : Ouvrir un Terminal PowerShell

- Appuyez sur `Windows + X` et sélectionnez "Terminal" ou "PowerShell"
- Ou ouvrez PowerShell depuis le menu Démarrer

### Étape 2 : Naviguer vers le dossier backend

```powershell
cd C:\Users\treso\Downloads\egoejo\backend
```

### Étape 3 : Activer l'environnement virtuel (si vous en avez un)

```powershell
.\venv\Scripts\Activate.ps1
```

> **Note** : Si vous n'avez pas d'environnement virtuel, vous pouvez utiliser Python directement.

### Étape 3.5 : Installer les dépendances (IMPORTANT !)

**⚠️ Cette étape est obligatoire avant de démarrer le serveur !**

```powershell
pip install -r requirements.txt
```

Cette commande installe toutes les dépendances nécessaires, y compris :
- Django et Django REST Framework
- Celery (pour les tâches asynchrones)
- Channels (pour WebSockets)
- Et toutes les autres dépendances

> **Note** : Cette étape peut prendre quelques minutes la première fois.

### Étape 4 : Définir la variable d'environnement SECRET_KEY

```powershell
$env:DJANGO_SECRET_KEY='dev-secret-key-for-local-development-only-change-in-production-12345678901234567890'
```

> **Note** : Cette clé est uniquement pour le développement local. En production, utilisez une clé sécurisée.

### Étape 5 : Vérifier les migrations (optionnel mais recommandé)

```powershell
python manage.py migrate
```

Cette commande crée/applique les migrations de la base de données.

### Étape 6 : Démarrer le serveur

```powershell
python manage.py runserver 127.0.0.1:8000
```

---

## ✅ Vérification

Une fois le serveur démarré, vous devriez voir :

```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
December 10, 2025 - XX:XX:XX
Django version 5.2.9, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

## 🌐 URLs Disponibles

Une fois le serveur démarré, vous pouvez accéder à :

- **API Health Check** : http://127.0.0.1:8000/api/health/
- **API Schema** : http://127.0.0.1:8000/api/schema/
- **Admin Django** : http://127.0.0.1:8000/admin/
- **API Docs** : http://127.0.0.1:8000/api/docs/

---

## 🔧 Dépannage

### Erreur : "DJANGO_SECRET_KEY must be set"

**Solution** : Définissez la variable d'environnement (Étape 4)

### Erreur : "Port 8000 already in use"

**Solution** : Utilisez un autre port :
```powershell
python manage.py runserver 127.0.0.1:8001
```

### Erreur : "No module named 'django'"

**Solution** : Installez les dépendances :
```powershell
pip install -r requirements.txt
```

### Erreur : "Table doesn't exist"

**Solution** : Exécutez les migrations :
```powershell
python manage.py migrate
```

---

## 📝 Commandes Utiles

### Arrêter le serveur
Appuyez sur `CTRL + C` dans le terminal

### Voir les logs en temps réel
Le serveur affiche automatiquement les requêtes dans le terminal

### Créer un superutilisateur (pour l'admin)
```powershell
python manage.py createsuperuser
```

---

## 🎯 Script Automatique

Vous pouvez aussi utiliser le script `start-backend.ps1` à la racine du projet :

```powershell
cd C:\Users\treso\Downloads\egoejo
.\start-backend.ps1
```

---

**Bon développement ! 🚀**


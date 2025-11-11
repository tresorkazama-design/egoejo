# Démarrage Rapide - EGOEJO

## 🚀 Méthode la Plus Simple

### 1. Démarrer Docker Desktop

Assurez-vous que Docker Desktop est installé et démarré.

### 2. Lancer le script de démarrage

```powershell
.\start.ps1
```

Ou manuellement :

```bash
# Créer les migrations
docker-compose run --rm api python manage.py makemigrations
docker-compose run --rm api python manage.py migrate

# Lancer les services
docker-compose up --build
```

### 3. Accéder aux services

- **API Backend** : http://localhost:8000/api/
- **Django Admin** : http://localhost:8000/admin/
- **Frontend** : Lancer séparément avec `npm run dev` dans le dossier `frontend`

## 📝 Première Utilisation

### Créer un superutilisateur Django

```bash
docker-compose run --rm api python manage.py createsuperuser
```

Puis accéder à http://localhost:8000/admin/ pour vous connecter.

### Tester l'API

```bash
# Test de l'endpoint rejoindre
curl -X POST http://localhost:8000/api/intents/rejoindre/ \
  -H "Content-Type: application/json" \
  -d '{"nom":"Test","email":"test@example.com","profil":"je-decouvre"}'
```

## 🔧 Dépannage

### Docker ne démarre pas

Vérifier que Docker Desktop est démarré et que les ports 5432 et 8000 sont libres.

### Erreurs de migrations

```bash
docker-compose run --rm api python manage.py makemigrations
docker-compose run --rm api python manage.py migrate
```

### Voir les logs

```bash
docker-compose logs -f
```

## 📚 Documentation Complète

Voir `LANCEMENT.md` pour plus de détails et les options de lancement local.


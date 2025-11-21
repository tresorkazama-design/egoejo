# Instructions pour les Migrations Django

## Créer les migrations

Après avoir modifié les modèles dans `backend/core/models.py`, créez les migrations :

```bash
# Dans Docker
docker-compose run --rm api python manage.py makemigrations

# Ou si Django est installé localement
cd backend
python manage.py makemigrations
```

## Appliquer les migrations

```bash
# Dans Docker
docker-compose run --rm api python manage.py migrate

# Ou localement
cd backend
python manage.py migrate
```

## Nouveau modèle Intent

Le modèle `Intent` a été ajouté. Pour créer et appliquer les migrations :

```bash
docker-compose run --rm api python manage.py makemigrations core
docker-compose run --rm api python manage.py migrate
```

## Vérifier l'état des migrations

```bash
docker-compose run --rm api python manage.py showmigrations
```


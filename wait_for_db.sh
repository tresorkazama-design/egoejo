#!/bin/sh

# Utilise des valeurs par défaut si les variables d'environnement ne sont pas encore chargées
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"

echo "⏳ Attente de la base de données ($DB_HOST:$DB_PORT)..."

# Teste la connexion jusqu'à ce qu'elle réussisse
until nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done

echo "✅ Base de données disponible !"

# Exécute la commande finale (gunicorn, runserver, etc.)
exec "$@"
#!/bin/sh

# Script pour attendre que la base de données PostgreSQL soit prête
echo "⏳ Attente de la base de données ($DATABASE_HOST:$DATABASE_PORT)..."

while ! nc -z "$DATABASE_HOST" "$DATABASE_PORT"; do
  sleep 1
done

echo "✅ Base de données disponible !"

# Exécute la commande passée (ex : lancement du serveur Django)
exec "$@"

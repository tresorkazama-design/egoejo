#!/bin/sh

# Script pour attendre que la base de données PostgreSQL soit prête
# Support DATABASE_URL (Railway/Heroku) ou variables individuelles

if [ -n "$DATABASE_URL" ]; then
  # Extraire host et port depuis DATABASE_URL (format: postgresql://user:pass@host:port/db)
  DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
  DB_PORT=$(echo "$DATABASE_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
  
  if [ -z "$DB_HOST" ] || [ -z "$DB_PORT" ]; then
    # Si on ne peut pas extraire, utiliser les valeurs par défaut PostgreSQL
    DB_HOST=${DATABASE_HOST:-localhost}
    DB_PORT=${DATABASE_PORT:-5432}
  fi
else
  # Utiliser les variables individuelles
  DB_HOST=${DATABASE_HOST:-${DB_HOST:-localhost}}
  DB_PORT=${DATABASE_PORT:-${DB_PORT:-5432}}
fi

echo "⏳ Attente de la base de données ($DB_HOST:$DB_PORT)..."

# Attendre que la base de données soit prête (maximum 60 secondes)
timeout=60
elapsed=0

while ! nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; do
  if [ $elapsed -ge $timeout ]; then
    echo "⚠️  Timeout : la base de données n'est pas accessible après ${timeout}s"
    break
  fi
  sleep 1
  elapsed=$((elapsed + 1))
done

echo "✅ Base de données disponible !"

# Exécute la commande passée (ex : lancement du serveur Django)
exec "$@"

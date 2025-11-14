#!/bin/bash
set -e

echo "=== EGOEJO Backend Starting ==="
echo "Timestamp: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo ""

# Vérifier que Python est disponible
if ! command -v python &> /dev/null; then
    echo "ERROR: Python is not available"
    exit 1
fi

# Vérifier que les variables essentielles sont définies
if [ -z "$DJANGO_SECRET_KEY" ]; then
    echo "ERROR: DJANGO_SECRET_KEY must be set"
    exit 1
fi

# Afficher les informations de configuration (sans les secrets)
echo "Configuration:"
echo "  - DEBUG: ${DEBUG:-0}"
echo "  - ALLOWED_HOSTS: ${ALLOWED_HOSTS:-not set}"
echo "  - DATABASE_URL: ${DATABASE_URL:+set (hidden)}"
echo "  - PORT: ${PORT:-8000}"
echo ""

# Exécuter les migrations
echo "Running migrations..."
python manage.py migrate --no-input || {
    echo "ERROR: Migrations failed"
    exit 1
}

echo "Migrations completed successfully"
echo ""

# Démarrer Daphne
echo "Starting Daphne ASGI server on port ${PORT:-8000}..."
echo "Application: config.asgi:application"
echo ""

exec daphne -b 0.0.0.0 -p ${PORT:-8000} config.asgi:application


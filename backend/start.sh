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
echo "  - RAILWAY_PUBLIC_DOMAIN: ${RAILWAY_PUBLIC_DOMAIN:-not set}"
echo ""

# Vérifier que le port est défini
if [ -z "$PORT" ]; then
    echo "WARNING: PORT environment variable is not set, using default 8000"
    export PORT=8000
fi

# Exécuter les migrations
echo "Running migrations..."
python manage.py migrate --no-input || {
    echo "ERROR: Migrations failed"
    exit 1
}

echo "Migrations completed successfully"
echo ""

# Vérifier que Django peut démarrer (syntax check)
echo "Checking Django configuration..."
python manage.py check --deploy 2>&1 || {
    echo "WARNING: Django check failed, continuing anyway..."
}
echo ""

# Démarrer Daphne avec logging détaillé
echo "Starting Daphne ASGI server..."
echo "  - Host: 0.0.0.0"
echo "  - Port: ${PORT}"
echo "  - Application: config.asgi:application"
echo ""
echo "Daphne will listen on all interfaces (0.0.0.0) on port ${PORT}"
echo "Railway will route traffic to this port automatically"
echo ""
echo "=== Starting server ==="

# Utiliser exec pour que Daphne soit le processus principal
exec daphne -b 0.0.0.0 -p "${PORT}" -v 2 config.asgi:application


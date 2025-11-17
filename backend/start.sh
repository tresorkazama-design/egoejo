#!/bin/sh
set -e

echo "=== EGOEJO Backend Starting ==="
PORT=${PORT:-8080}
echo "PORT=$PORT"
echo ""

echo "Running migrations..."
python manage.py migrate --no-input

echo "Starting Daphne on port $PORT..."
exec daphne -b 0.0.0.0 -p "$PORT" config.asgi:application

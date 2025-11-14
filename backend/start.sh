#!/bin/bash
set -e

echo "Starting migrations..."
python manage.py migrate

echo "Starting Daphne server on port ${PORT:-8000}..."
exec daphne -b 0.0.0.0 -p ${PORT:-8000} config.asgi:application


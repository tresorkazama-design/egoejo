#!/bin/sh
set -e

echo "=== EGOEJO Backend Starting ==="
echo "PORT=\"
echo ""

python manage.py migrate

exec daphne -b 0.0.0.0 -p "\" config.asgi:application

#!/bin/bash
# Script pour démarrer le serveur Django en mode test pour E2E full-stack

set -e

echo "🚀 Démarrage du serveur Django en mode test pour E2E full-stack..."

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "manage.py" ]; then
    echo "❌ Erreur: manage.py non trouvé. Exécutez ce script depuis le répertoire backend/"
    exit 1
fi

# Activer l'environnement virtuel si présent
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

# Variables d'environnement pour les tests
export DJANGO_SETTINGS_MODULE=config.settings_test
export ENABLE_SAKA=True
export SAKA_COMPOST_ENABLED=True
export SAKA_SILO_REDIS_ENABLED=True

# Créer les migrations si nécessaire
echo "📦 Application des migrations..."
python manage.py migrate --run-syncdb --noinput

# Créer un superuser de test si nécessaire (optionnel)
# python manage.py createsuperuser --noinput --username admin_test --email admin_test@test.com || true

echo "✅ Serveur prêt. Démarrage sur http://127.0.0.1:8000"
echo "   Configuration: settings_test.py"
echo "   SAKA activé: Oui"
echo "   Compostage activé: Oui"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter le serveur"

# Démarrer le serveur
python manage.py runserver 127.0.0.1:8000


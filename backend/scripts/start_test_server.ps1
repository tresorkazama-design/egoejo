# Script PowerShell pour démarrer le serveur Django en mode test pour E2E full-stack

Write-Host "🚀 Démarrage du serveur Django en mode test pour E2E full-stack..." -ForegroundColor Green

# Vérifier que nous sommes dans le bon répertoire
if (-not (Test-Path "manage.py")) {
    Write-Host "❌ Erreur: manage.py non trouvé. Exécutez ce script depuis le répertoire backend/" -ForegroundColor Red
    exit 1
}

# Variables d'environnement pour les tests
$env:DJANGO_SETTINGS_MODULE = "config.settings_test"
$env:ENABLE_SAKA = "True"
$env:SAKA_COMPOST_ENABLED = "True"
$env:SAKA_SILO_REDIS_ENABLED = "True"

# Créer les migrations si nécessaire
Write-Host "📦 Application des migrations..." -ForegroundColor Yellow
python manage.py migrate --run-syncdb --noinput

Write-Host "✅ Serveur prêt. Démarrage sur http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "   Configuration: settings_test.py" -ForegroundColor Cyan
Write-Host "   SAKA activé: Oui" -ForegroundColor Cyan
Write-Host "   Compostage activé: Oui" -ForegroundColor Cyan
Write-Host ""
Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur" -ForegroundColor Yellow

# Démarrer le serveur
python manage.py runserver 127.0.0.1:8000


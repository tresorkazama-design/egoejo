# Script de démarrage du backend Django
Set-Location $PSScriptRoot\backend

# Définir la variable d'environnement SECRET_KEY si elle n'existe pas
if (-not $env:DJANGO_SECRET_KEY) {
    $env:DJANGO_SECRET_KEY = "dev-secret-key-for-local-development-only-change-in-production-12345678901234567890"
    Write-Host "✅ DJANGO_SECRET_KEY définie" -ForegroundColor Green
}

Write-Host "`n🚀 Démarrage du serveur Django...`n" -ForegroundColor Cyan
Write-Host "URL: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "API: http://127.0.0.1:8000/api`n" -ForegroundColor Yellow

# Démarrer le serveur
python manage.py runserver 127.0.0.1:8000


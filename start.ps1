# Script de démarrage pour EGOEJO
# Usage: .\start.ps1

Write-Host "=== EGOEJO - Script de Démarrage ===" -ForegroundColor Cyan
Write-Host ""

# Vérifier Docker
$dockerRunning = docker info 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker Desktop n'est pas démarré" -ForegroundColor Red
    Write-Host "Veuillez démarrer Docker Desktop et réessayer." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternative: Lancement en mode local" -ForegroundColor Cyan
    Write-Host "Voir LANCEMENT.md pour les instructions" -ForegroundColor Cyan
    exit 1
}

Write-Host "✅ Docker est disponible" -ForegroundColor Green

# Vérifier le fichier .env
if (-not (Test-Path "backend\.env")) {
    Write-Host "⚠️  Le fichier backend/.env n'existe pas" -ForegroundColor Yellow
    Write-Host "Création du fichier .env..." -ForegroundColor Cyan
    
    $envContent = @"
# Django Settings
DJANGO_SECRET_KEY=django-insecure-dev-key-change-in-production-12345
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Settings
DB_NAME=egoejo_db
DB_USER=egoejo_user
DB_PASSWORD=egoejo_password
DB_HOST=db
DB_PORT=5432

# Admin Settings
ADMIN_TOKEN=dev-admin-token-12345

# Email Settings (Resend)
RESEND_API_KEY=
NOTIFY_EMAIL=tresor.kazama@gmail.com

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173

# Security Settings
SECURE_SSL_REDIRECT=0
SESSION_COOKIE_SECURE=0
CSRF_COOKIE_SECURE=0

# JWT Settings
ACCESS_TOKEN_MINUTES=60
REFRESH_TOKEN_DAYS=7

# Rate Limiting
THROTTLE_ANON=10/minute
THROTTLE_USER=100/minute

# Logging
LOG_LEVEL=INFO
"@
    Set-Content -Path "backend\.env" -Value $envContent -Encoding UTF8
    Write-Host "✅ Fichier .env créé" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Création des migrations ===" -ForegroundColor Cyan
docker-compose run --rm api python manage.py makemigrations

Write-Host ""
Write-Host "=== Application des migrations ===" -ForegroundColor Cyan
docker-compose run --rm api python manage.py migrate

Write-Host ""
Write-Host "=== Démarrage des services ===" -ForegroundColor Cyan
Write-Host "Appuyez sur Ctrl+C pour arrêter les services" -ForegroundColor Yellow
Write-Host ""

docker-compose up --build


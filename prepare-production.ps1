# Script de Préparation Production - EGOEJO
# Usage: .\prepare-production.ps1

Write-Host "=== EGOEJO - Préparation Production ===" -ForegroundColor Cyan
Write-Host ""

# Vérifications
$errors = @()

# 1. Vérifier que DEBUG=0 dans backend/.env
Write-Host "1. Vérification DEBUG=0..." -ForegroundColor Yellow
if (Test-Path "backend\.env") {
    $envContent = Get-Content "backend\.env" -Raw
    if ($envContent -match "DEBUG=1") {
        $errors += "❌ DEBUG=1 trouvé dans backend/.env (doit être DEBUG=0 en production)"
    } else {
        Write-Host "   ✅ DEBUG configuré correctement" -ForegroundColor Green
    }
} else {
    Write-Host "   ⚠️  backend/.env n'existe pas" -ForegroundColor Yellow
}

# 2. Vérifier SECRET_KEY
Write-Host "2. Vérification SECRET_KEY..." -ForegroundColor Yellow
if (Test-Path "backend\.env") {
    $envContent = Get-Content "backend\.env" -Raw
    if ($envContent -match "DJANGO_SECRET_KEY=change-me" -or $envContent -match "DJANGO_SECRET_KEY=$") {
        $errors += "❌ DJANGO_SECRET_KEY doit être changé (minimum 50 caractères)"
    } else {
        Write-Host "   ✅ SECRET_KEY configuré" -ForegroundColor Green
    }
} else {
    $errors += "❌ backend/.env n'existe pas"
}

# 3. Vérifier ALLOWED_HOSTS
Write-Host "3. Vérification ALLOWED_HOSTS..." -ForegroundColor Yellow
if (Test-Path "backend\.env") {
    $envContent = Get-Content "backend\.env" -Raw
    if ($envContent -notmatch "ALLOWED_HOSTS=") {
        $errors += "❌ ALLOWED_HOSTS doit être configuré en production"
    } else {
        Write-Host "   ✅ ALLOWED_HOSTS configuré" -ForegroundColor Green
    }
} else {
    $errors += "❌ backend/.env n'existe pas"
}

# 4. Build frontend
Write-Host "4. Build frontend..." -ForegroundColor Yellow
Set-Location "frontend\frontend"
try {
    npm run build 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Build frontend réussi" -ForegroundColor Green
    } else {
        $errors += "❌ Build frontend échoué"
    }
} catch {
    $errors += "❌ Erreur lors du build frontend: $_"
}
Set-Location "..\.."

# 5. Vérifier les tests
Write-Host "5. Vérification des tests..." -ForegroundColor Yellow
Set-Location "frontend\frontend"
try {
    $testOutput = npm test -- --run 2>&1 | Out-String
    if ($testOutput -match "Test Files.*passed") {
        Write-Host "   ✅ Tests passent" -ForegroundColor Green
    } else {
        $errors += "❌ Des tests échouent"
    }
} catch {
    $errors += "❌ Erreur lors des tests: $_"
}
Set-Location "..\.."

# 6. Vérifier les fichiers de production
Write-Host "6. Vérification des fichiers de production..." -ForegroundColor Yellow
$requiredFiles = @(
    "GUIDE_PRODUCTION.md",
    "CHECKLIST_PRODUCTION.md",
    "PRODUCTION_READY.md",
    ".github/workflows/cd.yml",
    ".github/workflows/ci.yml"
)
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file" -ForegroundColor Green
    } else {
        $errors += "❌ $file manquant"
    }
}

# Résumé
Write-Host ""
Write-Host "=== Résumé ===" -ForegroundColor Cyan
if ($errors.Count -eq 0) {
    Write-Host "✅ Tous les vérifications sont passées !" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Prochaines étapes :" -ForegroundColor Yellow
    Write-Host "1. Configurer les secrets GitHub (VERCEL_TOKEN, RAILWAY_TOKEN, etc.)" -ForegroundColor White
    Write-Host "2. Configurer les variables d'environnement en production" -ForegroundColor White
    Write-Host "3. Déployer via GitHub Actions ou manuellement" -ForegroundColor White
    Write-Host "4. Vérifier les health checks post-déploiement" -ForegroundColor White
    Write-Host ""
    Write-Host "📚 Documentation :" -ForegroundColor Yellow
    Write-Host "- GUIDE_PRODUCTION.md" -ForegroundColor White
    Write-Host "- CHECKLIST_PRODUCTION.md" -ForegroundColor White
    Write-Host "- PRODUCTION_READY.md" -ForegroundColor White
} else {
    Write-Host "❌ Erreurs trouvées :" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "   $error" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Veuillez corriger ces erreurs avant de déployer en production." -ForegroundColor Yellow
}

Write-Host ""


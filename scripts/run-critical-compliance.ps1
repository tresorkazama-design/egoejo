# Script PowerShell pour exécuter tous les tests Critical Compliance (P0/P1) localement
# Usage: .\scripts\run-critical-compliance.ps1

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚨 EXÉCUTION CRITICAL COMPLIANCE (P0/P1)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que nous sommes à la racine du projet
if (-not (Test-Path "backend\requirements.txt") -or -not (Test-Path "frontend\frontend\package.json")) {
    Write-Host "❌ Ce script doit être exécuté depuis la racine du projet" -ForegroundColor Red
    exit 1
}

# 1. Audit Statique
Write-Host "📋 1/5: Audit Statique (mots interdits)..." -ForegroundColor Yellow
Set-Location frontend\frontend
try {
    npm run audit:global
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Audit statique: OK" -ForegroundColor Green
    } else {
        Write-Host "❌ Audit statique: ÉCHEC" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Audit statique: ÉCHEC" -ForegroundColor Red
    exit 1
}
Set-Location ..\..

# 2. Backend Compliance
Write-Host ""
Write-Host "📋 2/5: Backend Compliance Tests..." -ForegroundColor Yellow
Set-Location backend
try {
    pytest tests/compliance/ -v -m egoejo_compliance --tb=short
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Backend Compliance: OK" -ForegroundColor Green
    } else {
        Write-Host "❌ Backend Compliance: ÉCHEC" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Backend Compliance: ÉCHEC" -ForegroundColor Red
    exit 1
}
Set-Location ..

# 3. Backend Permissions
Write-Host ""
Write-Host "📋 3/5: Backend Permission Tests..." -ForegroundColor Yellow
Set-Location backend
try {
    pytest core/tests/api/test_*_permissions.py -v -m critical --tb=short
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Backend Permissions: OK" -ForegroundColor Green
    } else {
        Write-Host "❌ Backend Permissions: ÉCHEC" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Backend Permissions: ÉCHEC" -ForegroundColor Red
    exit 1
}
Set-Location ..

# 4. Frontend Unit
Write-Host ""
Write-Host "📋 4/5: Frontend Unit Tests..." -ForegroundColor Yellow
Set-Location frontend\frontend
try {
    npm test -- --run
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Frontend Unit: OK" -ForegroundColor Green
    } else {
        Write-Host "❌ Frontend Unit: ÉCHEC" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Frontend Unit: ÉCHEC" -ForegroundColor Red
    exit 1
}
Set-Location ..\..

# 5. Frontend E2E Critical
Write-Host ""
Write-Host "📋 5/5: Frontend E2E Critical Tests..." -ForegroundColor Yellow
Write-Host "⚠️  Note: Assurez-vous que le backend et le frontend sont démarrés" -ForegroundColor Yellow
Write-Host "⚠️  Backend: http://localhost:8000" -ForegroundColor Yellow
Write-Host "⚠️  Frontend: http://localhost:5173" -ForegroundColor Yellow
Write-Host ""
$response = Read-Host "Appuyez sur Entrée pour continuer (Ctrl+C pour annuler)"
Set-Location frontend\frontend
$env:BACKEND_URL = "http://localhost:8000"
$env:PLAYWRIGHT_BASE_URL = "http://localhost:5173"
$env:E2E_MODE = "full-stack"
try {
    npm run test:e2e -- e2e/flux-complet-saka-vote.spec.js e2e/flux-complet-projet-financement.spec.js
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Frontend E2E Critical: OK" -ForegroundColor Green
    } else {
        Write-Host "❌ Frontend E2E Critical: ÉCHEC" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Frontend E2E Critical: ÉCHEC" -ForegroundColor Red
    exit 1
}
Set-Location ..\..

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ SUCCÈS : Tous les tests Critical Compliance sont passés !" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""


# Script de Tests Complets - Projet EGOEJO
# Lance tous les tests (backend + frontend)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TESTS COMPLETS - PROJET EGOEJO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$results = @{
    Backend = @{
        Success = $false
        Output = ""
        Errors = @()
    }
    Frontend = @{
        Success = $false
        Output = ""
        Errors = @()
    }
}

# ============================================
# 1. TESTS BACKEND
# ============================================
Write-Host "[1/2] Tests Backend (Django)..." -ForegroundColor Cyan
Write-Host ""

$backendPath = "backend"
if (Test-Path $backendPath) {
    Push-Location $backendPath
    
    # Vérifier si l'environnement virtuel existe
    $venvPath = "venv"
    if (Test-Path $venvPath) {
        Write-Host "  - Activation de l'environnement virtuel..." -ForegroundColor Gray
        & "$venvPath\Scripts\Activate.ps1"
    }
    
    # Vérifier si pytest est installé
    Write-Host "  - Vérification de pytest..." -ForegroundColor Gray
    try {
        $pytestVersion = python -m pytest --version 2>&1
        Write-Host "  - $pytestVersion" -ForegroundColor Green
    } catch {
        Write-Host "  - ⚠️  pytest non trouvé, installation..." -ForegroundColor Yellow
        pip install pytest pytest-django pytest-cov
    }
    
    # Lancer les tests backend
    Write-Host "  - Exécution des tests backend..." -ForegroundColor Gray
    Write-Host ""
    
    try {
        $backendTestOutput = python -m pytest --tb=short -v 2>&1 | Out-String
        $results.Backend.Output = $backendTestOutput
        
        if ($LASTEXITCODE -eq 0) {
            $results.Backend.Success = $true
            Write-Host "  ✅ Tests backend réussis!" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Tests backend échoués (code: $LASTEXITCODE)" -ForegroundColor Red
        }
        
        # Extraire le résumé
        if ($backendTestOutput -match "(\d+)\s+(passed|failed|error)") {
            Write-Host "  Résumé: $backendTestOutput" -ForegroundColor Gray
        }
    } catch {
        $results.Backend.Errors += $_.Exception.Message
        Write-Host "  ❌ Erreur lors de l'exécution des tests: $_" -ForegroundColor Red
    }
    
    Pop-Location
} else {
    Write-Host "  ⚠️  Dossier backend non trouvé" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# 2. TESTS FRONTEND
# ============================================
Write-Host "[2/2] Tests Frontend (React/Vitest)..." -ForegroundColor Cyan
Write-Host ""

$frontendPath = "frontend/frontend"
if (Test-Path $frontendPath) {
    Push-Location $frontendPath
    
    # Vérifier si node_modules existe
    if (-not (Test-Path "node_modules")) {
        Write-Host "  - Installation des dépendances..." -ForegroundColor Gray
        npm install
    }
    
    # Lancer les tests frontend
    Write-Host "  - Exécution des tests frontend..." -ForegroundColor Gray
    Write-Host ""
    
    try {
        $frontendTestOutput = npm test -- --run 2>&1 | Out-String
        $results.Frontend.Output = $frontendTestOutput
        
        if ($LASTEXITCODE -eq 0) {
            $results.Frontend.Success = $true
            Write-Host "  ✅ Tests frontend réussis!" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Tests frontend échoués (code: $LASTEXITCODE)" -ForegroundColor Red
        }
        
        # Extraire le résumé
        if ($frontendTestOutput -match "Test Files\s+(\d+)\s+(failed|passed)") {
            Write-Host "  Résumé: $frontendTestOutput" -ForegroundColor Gray
        }
    } catch {
        $results.Frontend.Errors += $_.Exception.Message
        Write-Host "  ❌ Erreur lors de l'exécution des tests: $_" -ForegroundColor Red
    }
    
    Pop-Location
} else {
    Write-Host "  ⚠️  Dossier frontend/frontend non trouvé" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# RÉSUMÉ
# ============================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RÉSUMÉ DES TESTS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backendStatus = if ($results.Backend.Success) { "✅ RÉUSSI" } else { "❌ ÉCHOUÉ" }
$frontendStatus = if ($results.Frontend.Success) { "✅ RÉUSSI" } else { "❌ ÉCHOUÉ" }

Write-Host "Backend  : $backendStatus" -ForegroundColor $(if ($results.Backend.Success) { "Green" } else { "Red" })
Write-Host "Frontend : $frontendStatus" -ForegroundColor $(if ($results.Frontend.Success) { "Green" } else { "Red" })
Write-Host ""

$allSuccess = $results.Backend.Success -and $results.Frontend.Success

if ($allSuccess) {
    Write-Host "✅ Tous les tests sont réussis!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Certains tests ont échoué" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray


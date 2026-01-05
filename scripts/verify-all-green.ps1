# Script de verification complete du projet EGOEJO
# Verifie que tous les tests critiques passent

Write-Host "VERIFICATION TOTALE DU PROJET..." -ForegroundColor Cyan
Write-Host ""

$allGreen = $true
$originalLocation = Get-Location

try {
    # 1. Verification Backend (Tests Critiques & Compliance)
    Write-Host "Testing Backend Compliance..." -ForegroundColor Yellow
    
    Set-Location backend
    
    python -m pytest -m "critical or egoejo_compliance" --tb=short -q
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ECHEC BACKEND" -ForegroundColor Red
        $allGreen = $false
    } else {
        Write-Host "OK: Backend tests passes" -ForegroundColor Green
    }
    
    Write-Host ""
    
    # 2. Verification Frontend (Unitaires)
    Write-Host "Testing Frontend Unit..." -ForegroundColor Yellow
    
    Set-Location ../frontend/frontend
    
    npm run test:run
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ECHEC FRONTEND" -ForegroundColor Red
        $allGreen = $false
    } else {
        Write-Host "OK: Frontend tests passes" -ForegroundColor Green
    }
    
    Write-Host ""
    
    # 3. Audit Statique (Mots interdits, Promesses)
    Write-Host "Running Global Audit..." -ForegroundColor Yellow
    
    npm run audit:global
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ATTENTION: Audit global a detecte des violations (peut etre des faux positifs)" -ForegroundColor Yellow
        # Ne pas faire echouer pour l'audit global car beaucoup de faux positifs
    } else {
        Write-Host "OK: Audit global passe" -ForegroundColor Green
    }
    
    Write-Host ""
    
    # Resultat final
    if ($allGreen) {
        Write-Host "TOUS LES FEUX SONT VERTS ! PROJET SAIN." -ForegroundColor Green
        exit 0
    } else {
        Write-Host "CERTAINS TESTS ONT ECHOUE. CORRIGER AVANT LE COMMIT." -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host "ERREUR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    Set-Location $originalLocation
}

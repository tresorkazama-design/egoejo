# Commandes PowerShell pour Tests Production - EGOEJO

Write-Host "=== Tests Complets Production EGOEJO ===" -ForegroundColor Cyan
Write-Host ""

# 1. Tests Frontend
Write-Host "1. Tests Frontend..." -ForegroundColor Yellow
cd C:\Users\treso\Downloads\egoejo\frontend\frontend
npm test -- --run
Write-Host ""

# 2. Tests Backend
Write-Host "2. Tests Backend..." -ForegroundColor Yellow
cd C:\Users\treso\Downloads\egoejo\backend
if (Test-Path venv\Scripts\Activate.ps1) {
    .\venv\Scripts\Activate.ps1
    python -m pytest
} else {
    Write-Host "Environnement virtuel non trouve" -ForegroundColor Red
}
Write-Host ""

# 3. Tests Lighthouse
Write-Host "3. Tests Lighthouse..." -ForegroundColor Yellow
cd C:\Users\treso\Downloads\egoejo\frontend\frontend
npm run test:lighthouse
Write-Host ""

# 4. Tests d'Accessibilite
Write-Host "4. Tests d'Accessibilite..." -ForegroundColor Yellow
npm run test:a11y
Write-Host ""

Write-Host "=== Tests Termines ===" -ForegroundColor Green
Write-Host ""
Write-Host "Tests manuels a faire :" -ForegroundColor Yellow
Write-Host "1. Verifier le visuel sur https://frontend-*.vercel.app" -ForegroundColor White
Write-Host "2. Tester toutes les routes" -ForegroundColor White
Write-Host "3. Tester l'upload de fichiers lourds" -ForegroundColor White
Write-Host "4. Tester les connexions (login/register)" -ForegroundColor White
Write-Host "5. Tester les chats (general, projet, communautaire)" -ForegroundColor White
Write-Host ""
Write-Host "Voir : TESTS_COMPLETS_PRODUCTION.md" -ForegroundColor Cyan


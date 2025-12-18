# Script PowerShell pour exécuter les tests E2E en production
# Usage: .\scripts\run-e2e-production.ps1

param(
    [string]$BaseUrl = "https://egoejo.org",
    [string]$TestFile = ""
)

Write-Host "`n🧪 Exécution des tests E2E en production" -ForegroundColor Cyan
Write-Host "URL: $BaseUrl" -ForegroundColor Gray
Write-Host ""

# Vérifier que Playwright est installé
if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
    Write-Host "❌ npx n'est pas disponible. Installez Node.js." -ForegroundColor Red
    exit 1
}

# Aller dans le répertoire frontend
$frontendDir = "frontend\frontend"
if (-not (Test-Path $frontendDir)) {
    Write-Host "❌ Répertoire frontend non trouvé: $frontendDir" -ForegroundColor Red
    exit 1
}

Push-Location $frontendDir

try {
    # Définir la variable d'environnement
    $env:PLAYWRIGHT_BASE_URL = $BaseUrl
    $env:VITE_APP_URL = $BaseUrl
    
    Write-Host "📋 Configuration:" -ForegroundColor Yellow
    Write-Host "  Base URL: $BaseUrl" -ForegroundColor Gray
    Write-Host "  Config: playwright.production.config.js" -ForegroundColor Gray
    Write-Host ""
    
    # Construire la commande
    $command = "npx playwright test --config=playwright.production.config.js"
    
    if ($TestFile) {
        $command += " $TestFile"
        Write-Host "📝 Test spécifique: $TestFile" -ForegroundColor Yellow
    } else {
        Write-Host "📝 Tous les tests E2E" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "🚀 Exécution des tests..." -ForegroundColor Cyan
    Write-Host ""
    
    # Exécuter les tests
    Invoke-Expression $command
    
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host "`n✅ Tous les tests sont passés !" -ForegroundColor Green
    } else {
        Write-Host "`n❌ Certains tests ont échoué (code: $exitCode)" -ForegroundColor Red
    }
    
    exit $exitCode
    
} finally {
    Pop-Location
}


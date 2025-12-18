# Script PowerShell de vérification de l'activation SAKA en production
# Usage: .\scripts\verify-saka-activation.ps1 https://votre-domaine.com

param(
    [string]$BaseUrl = "https://egoejo.org"
)

Write-Host "`n🔍 Vérification de l'activation SAKA sur $BaseUrl" -ForegroundColor Cyan
Write-Host ""

function Check-Api {
    param(
        [string]$Endpoint,
        [string]$ExpectedKey,
        [string]$ExpectedValue
    )
    
    Write-Host -NoNewline "Vérification $Endpoint... "
    
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl$Endpoint" -Method Get -ErrorAction Stop
        
        if ($response.$ExpectedKey -eq $ExpectedValue) {
            Write-Host "✅ OK" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Échec" -ForegroundColor Red
            Write-Host "   Réponse: $($response | ConvertTo-Json)" -ForegroundColor Gray
            return $false
        }
    } catch {
        Write-Host "❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Vérifier les feature flags
Write-Host "📋 Vérification des feature flags..." -ForegroundColor Yellow

$allOk = $true
$allOk = (Check-Api "/api/config/features/" "saka_enabled" $true) -and $allOk
$allOk = (Check-Api "/api/config/features/" "saka_compost_enabled" $true) -and $allOk
$allOk = (Check-Api "/api/config/features/" "saka_silo_redis_enabled" $true) -and $allOk

if (-not $allOk) {
    Write-Host "`n❌ Certains feature flags ne sont pas activés !" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Tous les feature flags sont activés !" -ForegroundColor Green

# Vérifier que l'API SAKA répond
Write-Host "`n📋 Vérification des endpoints SAKA..." -ForegroundColor Yellow
try {
    $siloResponse = Invoke-RestMethod -Uri "$BaseUrl/api/saka/silo/" -Method Get -ErrorAction Stop
    Write-Host "✅ Endpoint Silo accessible" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Endpoint Silo non disponible (peut être normal si aucun SAKA)" -ForegroundColor Yellow
}

Write-Host "`n🎉 Vérification terminée !" -ForegroundColor Green


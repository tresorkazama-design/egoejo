# Script de Configuration des Secrets GitHub - EGOEJO
# Usage: .\config-secrets.ps1

# Se placer à la racine du projet
$projectRoot = "C:\Users\treso\Downloads\egoejo"
Set-Location $projectRoot

Write-Host "=== Configuration des Secrets GitHub ===" -ForegroundColor Cyan
Write-Host ""

# Vérifier que GitHub CLI est installé
try {
    $ghVersion = gh --version 2>&1
    Write-Host "✅ GitHub CLI détecté" -ForegroundColor Green
} catch {
    Write-Host "❌ GitHub CLI n'est pas installé" -ForegroundColor Red
    Write-Host "Installez-le avec : winget install --id GitHub.cli" -ForegroundColor Yellow
    Write-Host "OU : choco install gh" -ForegroundColor Yellow
    exit 1
}

# Vérifier la connexion GitHub
Write-Host "Vérification de la connexion GitHub..." -ForegroundColor Yellow
$ghAuthStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Vous n'êtes pas connecté à GitHub" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Pour vous connecter, exécutez :" -ForegroundColor Cyan
    Write-Host "  gh auth login" -ForegroundColor White
    Write-Host ""
    $login = Read-Host "Voulez-vous vous connecter maintenant ? (O/N)"
    if ($login -eq "O" -or $login -eq "o" -or $login -eq "Y" -or $login -eq "y") {
        gh auth login
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Erreur lors de la connexion" -ForegroundColor Red
            exit 1
        }
        Write-Host "✅ Connecté à GitHub" -ForegroundColor Green
    } else {
        Write-Host "❌ Connexion requise pour continuer" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Connecté à GitHub" -ForegroundColor Green
}

Write-Host ""

# 1. VERCEL_TOKEN
Write-Host "1. Configuration de VERCEL_TOKEN..." -ForegroundColor Yellow
Write-Host "   Obtenez votre token sur : https://vercel.com/account/tokens" -ForegroundColor Gray
$vercelToken = Read-Host "   Entrez votre VERCEL_TOKEN"
if ($vercelToken) {
    gh secret set VERCEL_TOKEN --body $vercelToken
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ VERCEL_TOKEN configuré" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Erreur lors de la configuration" -ForegroundColor Red
    }
} else {
    Write-Host "   ⚠️  VERCEL_TOKEN ignoré" -ForegroundColor Yellow
}
Write-Host ""

# 2. VERCEL_ORG_ID
Write-Host "2. Configuration de VERCEL_ORG_ID..." -ForegroundColor Yellow
Write-Host "   Obtenez votre Org ID sur : https://vercel.com/[votre-org]/settings" -ForegroundColor Gray
$vercelOrgId = Read-Host "   Entrez votre VERCEL_ORG_ID"
if ($vercelOrgId) {
    gh secret set VERCEL_ORG_ID --body $vercelOrgId
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ VERCEL_ORG_ID configuré" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Erreur lors de la configuration" -ForegroundColor Red
    }
} else {
    Write-Host "   ⚠️  VERCEL_ORG_ID ignoré" -ForegroundColor Yellow
}
Write-Host ""

# 3. VERCEL_PROJECT_ID
Write-Host "3. Configuration de VERCEL_PROJECT_ID..." -ForegroundColor Yellow
Write-Host "   Obtenez votre Project ID sur : https://vercel.com/[votre-org]/[votre-projet]/settings" -ForegroundColor Gray
$vercelProjectId = Read-Host "   Entrez votre VERCEL_PROJECT_ID"
if ($vercelProjectId) {
    gh secret set VERCEL_PROJECT_ID --body $vercelProjectId
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ VERCEL_PROJECT_ID configuré" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Erreur lors de la configuration" -ForegroundColor Red
    }
} else {
    Write-Host "   ⚠️  VERCEL_PROJECT_ID ignoré" -ForegroundColor Yellow
}
Write-Host ""

# 4. RAILWAY_TOKEN
Write-Host "4. Configuration de RAILWAY_TOKEN..." -ForegroundColor Yellow
Write-Host "   Obtenez votre token sur : https://railway.app/account/tokens" -ForegroundColor Gray
$railwayToken = Read-Host "   Entrez votre RAILWAY_TOKEN"
if ($railwayToken) {
    gh secret set RAILWAY_TOKEN --body $railwayToken
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ RAILWAY_TOKEN configuré" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Erreur lors de la configuration" -ForegroundColor Red
    }
} else {
    Write-Host "   ⚠️  RAILWAY_TOKEN ignoré" -ForegroundColor Yellow
}
Write-Host ""

# 5. RAILWAY_SERVICE_ID
Write-Host "5. Configuration de RAILWAY_SERVICE_ID..." -ForegroundColor Yellow
Write-Host "   Obtenez votre Service ID sur : https://railway.app/dashboard → Projet → Service → Settings" -ForegroundColor Gray
$railwayServiceId = Read-Host "   Entrez votre RAILWAY_SERVICE_ID"
if ($railwayServiceId) {
    gh secret set RAILWAY_SERVICE_ID --body $railwayServiceId
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ RAILWAY_SERVICE_ID configuré" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Erreur lors de la configuration" -ForegroundColor Red
    }
} else {
    Write-Host "   ⚠️  RAILWAY_SERVICE_ID ignoré" -ForegroundColor Yellow
}
Write-Host ""

# 6. DJANGO_SECRET_KEY
Write-Host "6. Configuration de DJANGO_SECRET_KEY..." -ForegroundColor Yellow
Write-Host "   Génération d'un secret key sécurisé..." -ForegroundColor Gray
try {
    $djangoSecretKey = python -c "import secrets; print(secrets.token_urlsafe(50))"
    Write-Host "   Secret Key généré : $djangoSecretKey" -ForegroundColor Cyan
    $confirm = Read-Host "   Utiliser ce secret key ? (O/N)"
    if ($confirm -eq "O" -or $confirm -eq "o" -or $confirm -eq "Y" -or $confirm -eq "y") {
        gh secret set DJANGO_SECRET_KEY --body $djangoSecretKey
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ DJANGO_SECRET_KEY configuré" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Erreur lors de la configuration" -ForegroundColor Red
        }
    } else {
        $customKey = Read-Host "   Entrez votre propre DJANGO_SECRET_KEY (50+ caractères)"
        if ($customKey -and $customKey.Length -ge 50) {
            gh secret set DJANGO_SECRET_KEY --body $customKey
            if ($LASTEXITCODE -eq 0) {
                Write-Host "   ✅ DJANGO_SECRET_KEY configuré" -ForegroundColor Green
            } else {
                Write-Host "   ❌ Erreur lors de la configuration" -ForegroundColor Red
            }
        } else {
            Write-Host "   ⚠️  Secret key trop court (minimum 50 caractères)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "   ❌ Erreur lors de la génération : $_" -ForegroundColor Red
    $customKey = Read-Host "   Entrez votre DJANGO_SECRET_KEY manuellement"
    if ($customKey) {
        gh secret set DJANGO_SECRET_KEY --body $customKey
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ DJANGO_SECRET_KEY configuré" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Erreur lors de la configuration" -ForegroundColor Red
        }
    }
}
Write-Host ""

# Vérification finale
Write-Host "=== Vérification des Secrets ===" -ForegroundColor Cyan
Write-Host ""
gh secret list

Write-Host ""
Write-Host "✅ Configuration terminée !" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Prochaines étapes :" -ForegroundColor Yellow
Write-Host "1. Vérifier que tous les secrets sont configurés ci-dessus" -ForegroundColor White
Write-Host "2. Configurer les variables d'environnement en production" -ForegroundColor White
Write-Host "   (Railway/Vercel)" -ForegroundColor Gray
Write-Host "3. Deployer via GitHub Actions (push sur main) ou manuellement" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation :" -ForegroundColor Yellow
Write-Host "- CONFIGURER_SECRETS_GITHUB.md" -ForegroundColor White
Write-Host "- GUIDE_PRODUCTION.md" -ForegroundColor White
Write-Host "- VARIABLES_PRODUCTION.md" -ForegroundColor White


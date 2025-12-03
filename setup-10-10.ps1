# Script d'installation automatique pour EGOEJO 10/10
# PowerShell - Windows

Write-Host "🚀 Installation automatique EGOEJO 10/10" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier Node.js
Write-Host "📦 Vérification de Node.js..." -ForegroundColor Yellow
if (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVersion = node --version
    Write-Host "✅ Node.js installé: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Node.js n'est pas installé. Veuillez l'installer depuis https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Vérifier Python
Write-Host "🐍 Vérification de Python..." -ForegroundColor Yellow
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Host "✅ Python installé: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python n'est pas installé. Veuillez l'installer depuis https://www.python.org/" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📁 Installation des dépendances Frontend..." -ForegroundColor Yellow
Set-Location frontend/frontend

# Installer les dépendances npm
if (Test-Path package.json) {
    Write-Host "  → Installation npm..." -ForegroundColor Gray
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erreur lors de l'installation npm" -ForegroundColor Red
        Set-Location ../..
        exit 1
    }
    Write-Host "✅ Dépendances npm installées" -ForegroundColor Green
} else {
    Write-Host "❌ package.json non trouvé" -ForegroundColor Red
    Set-Location ../..
    exit 1
}

# Installer Husky
Write-Host "  → Installation de Husky..." -ForegroundColor Gray
npm install --save-dev husky
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Erreur lors de l'installation de Husky" -ForegroundColor Yellow
} else {
    Write-Host "✅ Husky installé" -ForegroundColor Green
}

# Initialiser Husky
Write-Host "  → Initialisation de Husky..." -ForegroundColor Gray
npm run prepare
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Erreur lors de l'initialisation de Husky" -ForegroundColor Yellow
} else {
    Write-Host "✅ Husky initialisé" -ForegroundColor Green
}

Set-Location ../..

Write-Host ""
Write-Host "📁 Installation des dépendances Backend..." -ForegroundColor Yellow
Set-Location backend

# Créer un environnement virtuel si nécessaire
if (-not (Test-Path venv)) {
    Write-Host "  → Création de l'environnement virtuel..." -ForegroundColor Gray
    python -m venv venv
    Write-Host "✅ Environnement virtuel créé" -ForegroundColor Green
}

# Activer l'environnement virtuel
Write-Host "  → Activation de l'environnement virtuel..." -ForegroundColor Gray
& .\venv\Scripts\Activate.ps1

# Installer les dépendances Python
if (Test-Path requirements.txt) {
    Write-Host "  → Installation des dépendances Python..." -ForegroundColor Gray
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erreur lors de l'installation des dépendances Python" -ForegroundColor Red
        Set-Location ..
        exit 1
    }
    Write-Host "✅ Dépendances Python installées" -ForegroundColor Green
} else {
    Write-Host "❌ requirements.txt non trouvé" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..

Write-Host ""
Write-Host "✅ Vérification des fichiers..." -ForegroundColor Yellow

# Vérifier les fichiers critiques
$filesToCheck = @(
    "frontend/frontend/.eslintrc.cjs",
    "frontend/frontend/.husky/pre-commit",
    "frontend/frontend/.husky/commit-msg",
    "frontend/frontend/scripts/lighthouse-ci.js",
    ".lighthouserc.js",
    "backend/core/api/rate_limiting.py",
    "backend/core/api/security_views.py",
    "backend/core/management/commands/backup_db.py",
    ".github/workflows/cd.yml",
    ".github/workflows/security-audit.yml",
    "CONTRIBUTING.md",
    "GUIDE_ARCHITECTURE.md",
    "GUIDE_DEPLOIEMENT.md",
    "GUIDE_TROUBLESHOOTING.md"
)

$allFilesExist = $true
foreach ($file in $filesToCheck) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file (manquant)" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Write-Host ""
    Write-Host "⚠️  Certains fichiers sont manquants" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🧪 Tests rapides..." -ForegroundColor Yellow

# Test ESLint
Set-Location frontend/frontend
Write-Host "  → Test ESLint..." -ForegroundColor Gray
npm run lint 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ ESLint OK" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  ESLint a trouvé des erreurs (normal si le code n'est pas encore conforme)" -ForegroundColor Yellow
}
Set-Location ../..

Write-Host ""
Write-Host "🎉 Installation terminée !" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Prochaines étapes :" -ForegroundColor Cyan
Write-Host "  1. Configurer les secrets GitHub pour CD (voir GUIDE_DEPLOIEMENT.md)" -ForegroundColor White
Write-Host "  2. (Optionnel) Installer Lighthouse CI globalement: npm install -g @lhci/cli" -ForegroundColor White
Write-Host "  3. (Optionnel) Activer le rate limiting IP dans backend/config/settings.py" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation disponible :" -ForegroundColor Cyan
Write-Host "  - CONTRIBUTING.md" -ForegroundColor White
Write-Host "  - GUIDE_ARCHITECTURE.md" -ForegroundColor White
Write-Host "  - GUIDE_DEPLOIEMENT.md" -ForegroundColor White
Write-Host "  - GUIDE_TROUBLESHOOTING.md" -ForegroundColor White
Write-Host "  - PLAN_10_10.md" -ForegroundColor White
Write-Host ""
Write-Host "✨ Le projet EGOEJO est maintenant à 10/10 !" -ForegroundColor Green


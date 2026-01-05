# Script de Preparation du Commit Final - EGOEJO
# Date: 2026-01-03
# Objectif: Nettoyer et organiser le depot avant le commit final

Write-Host "PREPARATION DU COMMIT FINAL - EGOEJO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verifier qu'on est a la racine du projet
if (-not (Test-Path ".git")) {
    Write-Host "ERREUR: Ce script doit etre execute a la racine du projet" -ForegroundColor Red
    exit 1
}

# ============================================================================
# ETAPE 1 : RESOUDRE LE PROBLEME FRONTEND
# ============================================================================
Write-Host "ETAPE 1 : Resolution du probleme Frontend" -ForegroundColor Yellow
Write-Host ""

if (Test-Path "frontend/.git") {
    Write-Host "ATTENTION: Frontend est un depot git separe" -ForegroundColor Yellow
    Write-Host "   Verification de l'etat..." -ForegroundColor Gray
    
    Push-Location frontend
    $frontendStatus = git status --porcelain
    $frontendUntracked = git ls-files --others --exclude-standard
    
    if ($frontendStatus -or $frontendUntracked) {
        Write-Host "   Fichiers modifies/non trackes detectes dans frontend/" -ForegroundColor Yellow
        Write-Host "   ACTION REQUISE :" -ForegroundColor Yellow
        Write-Host "      1. cd frontend" -ForegroundColor White
        Write-Host "      2. git add ." -ForegroundColor White
        Write-Host "      3. git commit -m 'feat: Infrastructure compliance EGOEJO'" -ForegroundColor White
        Write-Host "      4. cd .." -ForegroundColor White
        Write-Host ""
        Write-Host "   Pause : Executez les commandes ci-dessus, puis appuyez sur Entree pour continuer..." -ForegroundColor Yellow
        Read-Host
    } else {
        Write-Host "   OK: Frontend est propre" -ForegroundColor Green
    }
    Pop-Location
} else {
    Write-Host "   OK: Frontend n'est pas un depot git separe" -ForegroundColor Green
}

Write-Host ""

# ============================================================================
# ETAPE 2 : NETTOYER LES FICHIERS A LA RACINE
# ============================================================================
Write-Host "ETAPE 2 : Nettoyage des fichiers a la racine" -ForegroundColor Yellow
Write-Host ""

# Creer les dossiers de destination si necessaire
$directories = @(
    "docs/reports",
    "docs/audit",
    "docs/philosophie",
    "docs/governance",
    "docs/tests",
    "docs/architecture",
    "docs/infrastructure"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        Write-Host "   OK: Cree $dir" -ForegroundColor Green
    }
}

# Fichiers a deplacer
$filesToMove = @{
    # AUDIT_*.md
    "AUDIT_COMPLIANCE_PHILOSOPHIQUE.md" = "docs/audit/"
    "AUDIT_COMPLIANCE_TESTS.md" = "docs/audit/"
    "AUDIT_FINAL_EGOEJO_2025-01-27.md" = "docs/reports/"
    "AUDIT_QUADRUPLE_EGOEJO_2025.md" = "docs/reports/"
    "AUDIT_STRICT_EGOEJO_2025.md" = "docs/reports/"
    
    # RESUME_*.md
    "RESUME_ACTIONS_GARDIEN.md" = "docs/governance/"
    "RESUME_AUDIT_COMPLIANCE.md" = "docs/reports/"
    "RESUME_TESTS_COMPLETS.md" = "docs/tests/"
    "RESUME_TESTS_COMPLETS_2025-12-10.md" = "docs/tests/"
    
    # SYNTHESE_*.md
    "SYNTHESE_AUDIT_COMPLIANCE.md" = "docs/reports/"
    "SYNTHESE_GARDIEN_PHILOSOPHIQUE.md" = "docs/governance/"
    
    # Autres
    "PUBLICATION_STATUS.md" = "docs/reports/"
    "EGOEJO_ARCHITECTURE_CONSTITUTION.md" = "docs/architecture/"
    "PLAN_ACTION_GARDIEN_PHILOSOPHIQUE.md" = "docs/governance/"
    "README_MIGRATION_INFRA.md" = "docs/infrastructure/"
}

$movedCount = 0
$notFoundCount = 0

foreach ($file in $filesToMove.Keys) {
    if (Test-Path $file) {
        $destination = $filesToMove[$file]
        Move-Item -Path $file -Destination $destination -Force
        Write-Host "   OK: Deplace $file vers $destination" -ForegroundColor Green
        $movedCount++
    } else {
        $notFoundCount++
    }
}

Write-Host ""
Write-Host "   Resume: $movedCount fichier(s) deplace(s)" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# ETAPE 3 : VERIFIER LA COMPLETUDE CI
# ============================================================================
Write-Host "ETAPE 3 : Verification de la completude CI" -ForegroundColor Yellow
Write-Host ""

$criticalFiles = @(
    @{Path = ".github/workflows/audit-global.yml"; Name = "Workflow audit-global"},
    @{Path = ".github/workflows/egoejo-compliance.yml"; Name = "Workflow egoejo-compliance"},
    @{Path = ".github/workflows/pr-bot-home-vision.yml"; Name = "Workflow PR bot"},
    @{Path = "docs/governance/BRANCH_PROTECTION.md"; Name = "Doc Branch Protection"},
    @{Path = "docs/governance/REQUIRED_CHECKS.md"; Name = "Doc Required Checks"},
    @{Path = "backend/core/tests/models/test_saka_wallet_update_prevention.py"; Name = "Test update() prevention"},
    @{Path = "backend/core/tests/models/test_saka_wallet_raw_sql.py"; Name = "Test raw() SQL bypass"}
)

$allPresent = $true
foreach ($file in $criticalFiles) {
    if (Test-Path $file.Path) {
        Write-Host "   OK: $($file.Name)" -ForegroundColor Green
    } else {
        Write-Host "   ERREUR: $($file.Name) - MANQUANT: $($file.Path)" -ForegroundColor Red
        $allPresent = $false
    }
}

Write-Host ""

# Verifier .env.example
if (-not (Test-Path ".env.example")) {
    Write-Host "   ATTENTION: .env.example manquant" -ForegroundColor Yellow
    Write-Host "   Creation d'un .env.example basique..." -ForegroundColor Gray
    
    $envExample = @'
# Variables d'environnement EGOEJO
# Copiez ce fichier en .env et remplissez les valeurs

# Django
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False

# SAKA
ENABLE_SAKA=True
SAKA_COMPOST_ENABLED=True
SAKA_SILO_REDIS_ENABLED=True

# Tests E2E
E2E_TEST_MODE=False

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/egoejo

# Redis
REDIS_URL=redis://localhost:6379/0
'@
    
    Set-Content -Path ".env.example" -Value $envExample -Encoding UTF8
    Write-Host "   OK: .env.example cree" -ForegroundColor Green
} else {
    Write-Host "   OK: .env.example present" -ForegroundColor Green
}

Write-Host ""

# ============================================================================
# ETAPE 4 : RESUME ET PROCHAINES ETAPES
# ============================================================================
Write-Host "ETAPE 4 : Resume et prochaines etapes" -ForegroundColor Yellow
Write-Host ""

if ($allPresent) {
    Write-Host "   OK: Tous les fichiers critiques sont presents" -ForegroundColor Green
} else {
    Write-Host "   ATTENTION: Certains fichiers critiques sont manquants" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "PROCHAINES ETAPES :" -ForegroundColor Cyan
Write-Host ""
Write-Host "   1. Verifier l'etat git:" -ForegroundColor White
Write-Host "      git status" -ForegroundColor Gray
Write-Host ""
Write-Host "   2. Ajouter tous les fichiers:" -ForegroundColor White
Write-Host "      git add ." -ForegroundColor Gray
Write-Host ""
Write-Host "   3. Creer le commit final:" -ForegroundColor White
Write-Host "      git commit -m 'feat: Infrastructure complete de conformite EGOEJO'" -ForegroundColor Gray
Write-Host ""
Write-Host "   4. Pousser les changements:" -ForegroundColor White
Write-Host "      git push origin main" -ForegroundColor Gray
Write-Host ""

Write-Host "PREPARATION TERMINEE" -ForegroundColor Green
Write-Host ""

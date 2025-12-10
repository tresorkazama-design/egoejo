# Script d'Audit Complet - Projet EGOEJO
# Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AUDIT COMPLET DU PROJET EGOEJO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$auditResults = @{
    Backend = @{}
    Frontend = @{}
    Structure = @{}
    Configuration = @{}
    Tests = @{}
    Security = @{}
    Performance = @{}
}

$errors = @()
$warnings = @()
$info = @()

# Fonction pour logger
function Log-Info {
    param($message)
    Write-Host "[INFO] $message" -ForegroundColor Green
    $script:info += $message
}

function Log-Warning {
    param($message)
    Write-Host "[WARNING] $message" -ForegroundColor Yellow
    $script:warnings += $message
}

function Log-Error {
    param($message)
    Write-Host "[ERROR] $message" -ForegroundColor Red
    $script:errors += $message
}

# ============================================
# 1. AUDIT BACKEND
# ============================================
Write-Host "`n[1/7] Audit Backend..." -ForegroundColor Cyan

$backendPath = "backend"
if (Test-Path $backendPath) {
    Push-Location $backendPath
    
    # Vérifier Python
    try {
        $pythonVersion = python --version 2>&1
        Log-Info "Python: $pythonVersion"
    } catch {
        Log-Error "Python non trouvé"
    }
    
    # Vérifier les dépendances
    if (Test-Path "requirements.txt") {
        Log-Info "requirements.txt trouvé"
        $requirements = Get-Content "requirements.txt"
        $auditResults.Backend["dependencies_count"] = ($requirements | Where-Object { $_ -match "^\w" -and $_ -notmatch "^#" }).Count
    }
    
    # Bandit (si installé)
    Write-Host "  - Exécution de Bandit (analyse sécurité Python)..." -ForegroundColor Gray
    try {
        $banditOutput = bandit -r core/ -f json 2>&1 | Out-String
        if ($LASTEXITCODE -eq 0 -or $banditOutput -match "No issues identified") {
            Log-Info "Bandit: Aucun problème de sécurité détecté"
        } else {
            Log-Warning "Bandit: Problèmes de sécurité détectés (voir rapport)"
            $auditResults.Backend["bandit_issues"] = $banditOutput
        }
    } catch {
        Log-Warning "Bandit non installé (pip install bandit)"
    }
    
    # Safety (si installé)
    Write-Host "  - Exécution de Safety (vulnérabilités dépendances)..." -ForegroundColor Gray
    try {
        $safetyOutput = safety check --json 2>&1 | Out-String
        if ($LASTEXITCODE -eq 0 -or $safetyOutput -match "No known security vulnerabilities found") {
            Log-Info "Safety: Aucune vulnérabilité détectée"
        } else {
            Log-Warning "Safety: Vulnérabilités détectées dans les dépendances"
            $auditResults.Backend["safety_issues"] = $safetyOutput
        }
    } catch {
        Log-Warning "Safety non installé (pip install safety)"
    }
    
    # Vérifier les fichiers sensibles
    Write-Host "  - Vérification des secrets commités..." -ForegroundColor Gray
    $secretPatterns = @("password\s*=\s*['\`"]", "secret\s*=\s*['\`"]", "api_key\s*=\s*['\`"]", "token\s*=\s*['\`"]")
    $foundSecrets = @()
    Get-ChildItem -Recurse -Include *.py | ForEach-Object {
        $content = Get-Content $_.FullName -Raw
        foreach ($pattern in $secretPatterns) {
            if ($content -match $pattern) {
                $foundSecrets += "$($_.Name): Ligne contenant potentiel secret"
            }
        }
    }
    if ($foundSecrets.Count -gt 0) {
        Log-Warning "Secrets potentiels détectés: $($foundSecrets.Count) occurrences"
        $auditResults.Backend["potential_secrets"] = $foundSecrets
    } else {
        Log-Info "Aucun secret potentiel détecté"
    }
    
    # Vérifier .env
    if (Test-Path ".env") {
        Log-Warning ".env présent (ne devrait pas être commité)"
    } else {
        Log-Info ".env absent (correct)"
    }
    
    # Django check
    Write-Host "  - Vérification Django..." -ForegroundColor Gray
    try {
        $djangoCheck = python manage.py check --deploy 2>&1 | Out-String
        if ($LASTEXITCODE -eq 0) {
            Log-Info "Django check: OK"
        } else {
            Log-Warning "Django check: Problèmes détectés"
            $auditResults.Backend["django_check"] = $djangoCheck
        }
    } catch {
        Log-Warning "Django check non exécutable (environnement non configuré)"
    }
    
    Pop-Location
} else {
    Log-Error "Dossier backend non trouvé"
}

# ============================================
# 2. AUDIT FRONTEND
# ============================================
Write-Host "`n[2/7] Audit Frontend..." -ForegroundColor Cyan

$frontendPath = "frontend/frontend"
if (Test-Path $frontendPath) {
    Push-Location $frontendPath
    
    # Vérifier Node.js
    try {
        $nodeVersion = node --version
        Log-Info "Node.js: $nodeVersion"
    } catch {
        Log-Error "Node.js non trouvé"
    }
    
    # npm audit
    Write-Host "  - Exécution de npm audit..." -ForegroundColor Gray
    try {
        $npmAudit = npm audit --json 2>&1 | Out-String
        $npmAuditJson = $npmAudit | ConvertFrom-Json
        if ($npmAuditJson.metadata.vulnerabilities.total -eq 0) {
            Log-Info "npm audit: Aucune vulnérabilité détectée"
        } else {
            $vulnCount = $npmAuditJson.metadata.vulnerabilities.total
            Log-Warning "npm audit: $vulnCount vulnérabilité(s) détectée(s)"
            $auditResults.Frontend["npm_vulnerabilities"] = $npmAuditJson.metadata.vulnerabilities
        }
    } catch {
        Log-Warning "npm audit non exécutable (dépendances non installées)"
    }
    
    # Vérifier package.json
    if (Test-Path "package.json") {
        $packageJson = Get-Content "package.json" | ConvertFrom-Json
        $auditResults.Frontend["dependencies_count"] = ($packageJson.dependencies.PSObject.Properties | Measure-Object).Count
        $auditResults.Frontend["devDependencies_count"] = ($packageJson.devDependencies.PSObject.Properties | Measure-Object).Count
        Log-Info "Dépendances: $($auditResults.Frontend.dependencies_count) prod, $($auditResults.Frontend.devDependencies_count) dev"
    }
    
    # ESLint
    Write-Host "  - Exécution de ESLint..." -ForegroundColor Gray
    try {
        $eslintOutput = npm run lint 2>&1 | Out-String
        if ($LASTEXITCODE -eq 0) {
            Log-Info "ESLint: Aucune erreur"
        } else {
            Log-Warning "ESLint: Erreurs détectées"
            $auditResults.Frontend["eslint_errors"] = $eslintOutput
        }
    } catch {
        Log-Warning "ESLint non exécutable"
    }
    
    # Vérifier les secrets dans le code
    Write-Host "  - Vérification des secrets commités..." -ForegroundColor Gray
    $foundSecrets = @()
    Get-ChildItem -Recurse -Include *.js,*.jsx | Where-Object { $_.FullName -notmatch "node_modules" } | ForEach-Object {
        $content = Get-Content $_.FullName -Raw
        if ($content -match "api[_-]?key\s*[:=]\s*['\`"][^'\`"]+['\`"]" -or 
            $content -match "secret\s*[:=]\s*['\`"][^'\`"]+['\`"]" -or
            $content -match "password\s*[:=]\s*['\`"][^'\`"]+['\`"]") {
            $foundSecrets += "$($_.Name): Potentiel secret détecté"
        }
    }
    if ($foundSecrets.Count -gt 0) {
        Log-Warning "Secrets potentiels détectés: $($foundSecrets.Count) occurrences"
        $auditResults.Frontend["potential_secrets"] = $foundSecrets
    } else {
        Log-Info "Aucun secret potentiel détecté"
    }
    
    Pop-Location
} else {
    Log-Error "Dossier frontend/frontend non trouvé"
}

# ============================================
# 3. AUDIT STRUCTURE
# ============================================
Write-Host "`n[3/7] Audit Structure..." -ForegroundColor Cyan

# Vérifier les fichiers dupliqués
$duplicateFiles = @()
$allFiles = Get-ChildItem -Recurse -File | Where-Object { $_.FullName -notmatch "node_modules|venv|__pycache__|\.git" }
$fileGroups = $allFiles | Group-Object Name
foreach ($group in $fileGroups) {
    if ($group.Count -gt 1) {
        $duplicateFiles += "$($group.Name): $($group.Count) occurrences"
    }
}
if ($duplicateFiles.Count -gt 0) {
    Log-Warning "Fichiers dupliqués détectés: $($duplicateFiles.Count)"
    $auditResults.Structure["duplicate_files"] = $duplicateFiles
} else {
    Log-Info "Aucun fichier dupliqué détecté"
}

# Vérifier les dossiers obsolètes
$obsoleteFolders = @("admin-panel-legacy", "frontend/backend")
foreach ($folder in $obsoleteFolders) {
    if (Test-Path $folder) {
        Log-Warning "Dossier potentiellement obsolète: $folder"
        $auditResults.Structure["obsolete_folders"] += $folder
    }
}

# Vérifier la structure
$requiredFolders = @("backend", "frontend", "backend/core", "frontend/frontend/src")
foreach ($folder in $requiredFolders) {
    if (Test-Path $folder) {
        Log-Info "Dossier requis présent: $folder"
    } else {
        Log-Error "Dossier requis absent: $folder"
    }
}

# ============================================
# 4. AUDIT CONFIGURATION
# ============================================
Write-Host "`n[4/7] Audit Configuration..." -ForegroundColor Cyan

# Vérifier .env.template
if (Test-Path "backend/env.template") {
    Log-Info "env.template présent dans backend"
} else {
    Log-Warning "env.template absent dans backend"
}

# Vérifier .gitignore
if (Test-Path ".gitignore") {
    $gitignore = Get-Content ".gitignore"
    $requiredIgnores = @(".env", "node_modules", "__pycache__", "*.pyc", ".venv", "venv")
    $missingIgnores = @()
    foreach ($ignore in $requiredIgnores) {
        if ($gitignore -notcontains $ignore -and $gitignore -notmatch $ignore) {
            $missingIgnores += $ignore
        }
    }
    if ($missingIgnores.Count -gt 0) {
        Log-Warning ".gitignore: Patterns manquants: $($missingIgnores -join ', ')"
    } else {
        Log-Info ".gitignore: Configuration correcte"
    }
} else {
    Log-Warning ".gitignore absent"
}

# Vérifier les fichiers de configuration
$configFiles = @("vercel.json", "railway.json", "railway.toml", "docker-compose.yml")
foreach ($file in $configFiles) {
    if (Test-Path $file) {
        Log-Info "Fichier de configuration présent: $file"
    } else {
        Log-Warning "Fichier de configuration absent: $file"
    }
}

# ============================================
# 5. AUDIT TESTS
# ============================================
Write-Host "`n[5/7] Audit Tests..." -ForegroundColor Cyan

# Backend tests
if (Test-Path "backend/pytest.ini") {
    Log-Info "pytest.ini présent"
} else {
    Log-Warning "pytest.ini absent"
}

# Frontend tests
if (Test-Path "frontend/frontend/vitest.config.js" -or Test-Path "frontend/frontend/vitest.config.ts") {
    Log-Info "Configuration Vitest présente"
} else {
    Log-Warning "Configuration Vitest absente"
}

# Compter les fichiers de tests
$testFiles = Get-ChildItem -Recurse -Include *test*.py,*test*.js,*test*.jsx | Where-Object { $_.FullName -notmatch "node_modules|venv|__pycache__" }
$auditResults.Tests["test_files_count"] = $testFiles.Count
Log-Info "Fichiers de tests: $($testFiles.Count)"

# ============================================
# 6. AUDIT SÉCURITÉ GLOBALE
# ============================================
Write-Host "`n[6/7] Audit Sécurité Globale..." -ForegroundColor Cyan

# Vérifier les permissions de fichiers sensibles
$sensitiveFiles = @(".env", "*.key", "*.pem", "*.p12")
foreach ($pattern in $sensitiveFiles) {
    $files = Get-ChildItem -Recurse -Include $pattern -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notmatch "node_modules|venv" }
    if ($files.Count -gt 0) {
        Log-Warning "Fichiers sensibles trouvés: $($files.Count)"
        foreach ($file in $files) {
            Log-Warning "  - $($file.FullName)"
        }
    }
}

# Vérifier les headers de sécurité
if (Test-Path "frontend/frontend/vercel.json") {
    $vercelJson = Get-Content "frontend/frontend/vercel.json" | ConvertFrom-Json
    if ($vercelJson.headers) {
        Log-Info "Headers de sécurité configurés dans vercel.json"
    } else {
        Log-Warning "Headers de sécurité non configurés dans vercel.json"
    }
}

# ============================================
# 7. AUDIT PERFORMANCE
# ============================================
Write-Host "`n[7/7] Audit Performance..." -ForegroundColor Cyan

# Vérifier le lazy loading
if (Test-Path "frontend/frontend/src/app/router.jsx") {
    $routerContent = Get-Content "frontend/frontend/src/app/router.jsx" -Raw
    if ($routerContent -match "lazy|React\.lazy") {
        Log-Info "Lazy loading configuré dans le router"
    } else {
        Log-Warning "Lazy loading non détecté dans le router"
    }
}

# Vérifier le code splitting
if (Test-Path "frontend/frontend/vite.config.js" -or Test-Path "frontend/frontend/vite.config.ts") {
    Log-Info "Configuration Vite présente"
}

# ============================================
# RÉSUMÉ
# ============================================
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  RÉSUMÉ DE L'AUDIT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ Informations: $($info.Count)" -ForegroundColor Green
Write-Host "⚠️  Avertissements: $($warnings.Count)" -ForegroundColor Yellow
Write-Host "❌ Erreurs: $($errors.Count)" -ForegroundColor Red
Write-Host ""

# Générer le rapport JSON
$report = @{
    date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    summary = @{
        info = $info.Count
        warnings = $warnings.Count
        errors = $errors.Count
    }
    results = $auditResults
    details = @{
        info = $info
        warnings = $warnings
        errors = $errors
    }
}

$reportJson = $report | ConvertTo-Json -Depth 10
$reportJson | Out-File "audit-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').json" -Encoding UTF8

Write-Host "Rapport JSON généré: audit-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').json" -ForegroundColor Green
Write-Host ""

if ($errors.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "✅ Audit terminé: Aucun problème détecté!" -ForegroundColor Green
} elseif ($errors.Count -eq 0) {
    Write-Host "⚠️  Audit terminé: $($warnings.Count) avertissement(s) à examiner" -ForegroundColor Yellow
} else {
    Write-Host "❌ Audit terminé: $($errors.Count) erreur(s) et $($warnings.Count) avertissement(s)" -ForegroundColor Red
}


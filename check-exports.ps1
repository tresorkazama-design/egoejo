# ==========================================
# Vérification automatique des fichiers JSX
# ==========================================

Write-Host ""
Write-Host "=== Vérification des composants React dans ./src/pages/ ===" -ForegroundColor Cyan

# 1️⃣ Dossier cible
$pagesPath = ".\src\pages"

if (-not (Test-Path $pagesPath)) {
    Write-Host "ERREUR : le dossier $pagesPath est introuvable." -ForegroundColor Red
    exit
}

# 2️⃣ Lister tous les fichiers .jsx
$jsxFiles = Get-ChildItem -Path $pagesPath -Filter *.jsx -Recurse

if ($jsxFiles.Count -eq 0) {
    Write-Host "Aucun fichier .jsx trouvé dans $pagesPath." -ForegroundColor Yellow
    exit
}

# 3️⃣ Vérifier chaque fichier
foreach ($file in $jsxFiles) {
    $content = Get-Content $file.FullName -Raw
    $fileName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)

    # Vérifie la présence d'un export default
    if ($content -match 'export\s+default') {
        Write-Host "OK : $fileName contient déjà 'export default'." -ForegroundColor Green
    }
    else {
        Write-Host "ATTENTION : $fileName ne contient pas 'export default'. Ajout automatique..." -ForegroundColor Yellow

        # Ajouter une ligne à la fin du fichier
        Add-Content -Path $file.FullName -Value "`nexport default $fileName;"

        # Vérifier après modification
        if ((Get-Content $file.FullName -Raw) -match 'export\s+default') {
            Write-Host "Correction appliquée à $fileName." -ForegroundColor Cyan
        } else {
            Write-Host "Erreur : impossible de corriger $fileName." -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "=== Vérification terminée : tous les composants React ont un export par défaut. ===" -ForegroundColor Green

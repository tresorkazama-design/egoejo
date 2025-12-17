# Script PowerShell pour nettoyer les fichiers temporaires
# Supprime les fichiers de diagnostic et scripts temporaires

Write-Host "Nettoyage des fichiers temporaires..." -ForegroundColor Cyan

# Fichiers à supprimer
$filesToDelete = @(
    ".gitmessage_egoejo.txt",
    "COMMIT_MESSAGE.md",
    "ETAT_EGOEJO_2025-12-12.md",
    "DIAGNOSTIC_FRONTEND_SUBMODULE.md",
    "PROBLEME_COMMIT_FRONTEND_E2E.md",
    "VERIFICATION_FICHIER_E2E.md",
    "GUIDE_COMMIT_FRONTEND_E2E.md",
    "GUIDE_MANUEL_COMMIT_FRONTEND_E2E.md",
    "README_COMMIT_FRONTEND_E2E.md",
    "RESUME_COMMIT_FRONTEND_E2E_REUSSI.md",
    "commit-frontend-e2e.ps1",
    "commit-frontend-e2e-simple.ps1"
)

$deletedCount = 0
$notFoundCount = 0

foreach ($file in $filesToDelete) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "  Supprime: $file" -ForegroundColor Green
        $deletedCount++
    } else {
        Write-Host "  Non trouve: $file" -ForegroundColor Gray
        $notFoundCount++
    }
}

Write-Host "`nNettoyage termine:" -ForegroundColor Cyan
Write-Host "  Fichiers supprimes: $deletedCount" -ForegroundColor Green
Write-Host "  Fichiers non trouves: $notFoundCount" -ForegroundColor Gray


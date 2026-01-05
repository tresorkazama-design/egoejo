# Script PowerShell de génération des PDFs de la Constitution Éditoriale Institutionnelle

# Vérifier que pandoc est installé
if (-not (Get-Command pandoc -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Erreur : pandoc n'est pas installé." -ForegroundColor Red
    Write-Host "Installation :" -ForegroundColor Yellow
    Write-Host "  - Windows : https://pandoc.org/installing.html" -ForegroundColor White
    Write-Host "  - Ou via Chocolatey : choco install pandoc" -ForegroundColor White
    exit 1
}

# Répertoire de sortie
$OUTPUT_DIR = "pdf"
if (-not (Test-Path $OUTPUT_DIR)) {
    New-Item -ItemType Directory -Path $OUTPUT_DIR | Out-Null
}

# Générer le PDF de la Constitution Éditoriale Institutionnelle
Write-Host "📄 Génération du PDF : Constitution Éditoriale Institutionnelle..." -ForegroundColor Cyan
pandoc CONSTITUTION_EDITORIALE_INSTITUTIONNELLE.md `
    -o "$OUTPUT_DIR/CONSTITUTION_EDITORIALE_INSTITUTIONNELLE.pdf" `
    --pdf-engine=xelatex `
    -V geometry:margin=2.5cm `
    -V fontsize=11pt `
    -V documentclass=article `
    -V lang=fr `
    --toc `
    --toc-depth=2 `
    --number-sections

# Générer le PDF du Résumé Exécutif
Write-Host "📄 Génération du PDF : Résumé Exécutif..." -ForegroundColor Cyan
pandoc RESUME_EXECUTIF_CONSTITUTION_EDITORIALE.md `
    -o "$OUTPUT_DIR/RESUME_EXECUTIF_CONSTITUTION_EDITORIALE.pdf" `
    --pdf-engine=xelatex `
    -V geometry:margin=2.5cm `
    -V fontsize=11pt `
    -V documentclass=article `
    -V lang=fr `
    --number-sections

# Générer le PDF de la FAQ Institutionnelle
Write-Host "📄 Génération du PDF : FAQ Institutionnelle..." -ForegroundColor Cyan
pandoc FAQ_INSTITUTIONNELLE_CONSTITUTION_EDITORIALE.md `
    -o "$OUTPUT_DIR/FAQ_INSTITUTIONNELLE_CONSTITUTION_EDITORIALE.pdf" `
    --pdf-engine=xelatex `
    -V geometry:margin=2.5cm `
    -V fontsize=11pt `
    -V documentclass=article `
    -V lang=fr `
    --toc `
    --toc-depth=2 `
    --number-sections

Write-Host ""
Write-Host "✅ PDFs générés dans le répertoire : $OUTPUT_DIR/" -ForegroundColor Green
Write-Host ""
Write-Host "Fichiers générés :" -ForegroundColor Yellow
Write-Host "  - CONSTITUTION_EDITORIALE_INSTITUTIONNELLE.pdf" -ForegroundColor White
Write-Host "  - RESUME_EXECUTIF_CONSTITUTION_EDITORIALE.pdf" -ForegroundColor White
Write-Host "  - FAQ_INSTITUTIONNELLE_CONSTITUTION_EDITORIALE.pdf" -ForegroundColor White


# Script PowerShell de génération du PDF du Dossier de Reconnaissance Institutionnelle

# Vérifier que pandoc est installé
if (-not (Get-Command pandoc -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Erreur : pandoc n'est pas installé." -ForegroundColor Red
    Write-Host "Voir INSTALLATION_PANDOC.md pour les instructions." -ForegroundColor Yellow
    exit 1
}

# Répertoire de sortie
$OUTPUT_DIR = "pdf"
if (-not (Test-Path $OUTPUT_DIR)) {
    New-Item -ItemType Directory -Path $OUTPUT_DIR | Out-Null
}

# Générer le PDF du Dossier de Reconnaissance Institutionnelle
Write-Host "📄 Génération du PDF : Dossier de Reconnaissance Institutionnelle..." -ForegroundColor Cyan
pandoc DOSSIER_RECONNAISSANCE_INSTITUTIONNELLE.md `
    -o "$OUTPUT_DIR/DOSSIER_RECONNAISSANCE_INSTITUTIONNEL.pdf" `
    --pdf-engine=xelatex `
    -V geometry:margin=2.5cm `
    -V fontsize=11pt `
    -V documentclass=article `
    -V lang=fr `
    --toc `
    --toc-depth=3 `
    --number-sections `
    --metadata title="Dossier de Reconnaissance Institutionnelle - Plateforme EGOEJO" `
    --metadata author="EGOEJO Platform" `
    --metadata date="2025-01-27"

# Générer le PDF du Pitch Institutionnel
Write-Host "📄 Génération du PDF : Pitch Institutionnel..." -ForegroundColor Cyan
pandoc PITCH_INSTITUTIONNEL.md `
    -o "$OUTPUT_DIR/PITCH_INSTITUTIONNEL.pdf" `
    --pdf-engine=xelatex `
    -V geometry:margin=2.5cm `
    -V fontsize=11pt `
    -V documentclass=article `
    -V lang=fr `
    --number-sections `
    --metadata title="Pitch Institutionnel - Plateforme EGOEJO" `
    --metadata author="EGOEJO Platform" `
    --metadata date="2025-01-27"

# Générer le PDF de la FAQ Juridique
Write-Host "📄 Génération du PDF : FAQ Juridique..." -ForegroundColor Cyan
pandoc FAQ_JURIDIQUE.md `
    -o "$OUTPUT_DIR/FAQ_JURIDIQUE.pdf" `
    --pdf-engine=xelatex `
    -V geometry:margin=2.5cm `
    -V fontsize=11pt `
    -V documentclass=article `
    -V lang=fr `
    --toc `
    --toc-depth=2 `
    --number-sections `
    --metadata title="FAQ Juridique - Plateforme EGOEJO" `
    --metadata author="EGOEJO Platform" `
    --metadata date="2025-01-27"

Write-Host ""
Write-Host "✅ PDFs générés dans le répertoire : $OUTPUT_DIR/" -ForegroundColor Green
Write-Host ""
Write-Host "Fichiers générés :" -ForegroundColor Yellow
Write-Host "  - DOSSIER_RECONNAISSANCE_INSTITUTIONNEL.pdf" -ForegroundColor White
Write-Host "  - PITCH_INSTITUTIONNEL.pdf" -ForegroundColor White
Write-Host "  - FAQ_JURIDIQUE.pdf" -ForegroundColor White


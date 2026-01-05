#!/bin/bash
# Script de génération des PDFs de la Constitution Éditoriale Institutionnelle

# Vérifier que pandoc est installé
if ! command -v pandoc &> /dev/null; then
    echo "❌ Erreur : pandoc n'est pas installé."
    echo "Installation :"
    echo "  - macOS : brew install pandoc"
    echo "  - Ubuntu/Debian : sudo apt-get install pandoc"
    echo "  - Windows : https://pandoc.org/installing.html"
    exit 1
fi

# Répertoire de sortie
OUTPUT_DIR="pdf"
mkdir -p "$OUTPUT_DIR"

# Générer le PDF de la Constitution Éditoriale Institutionnelle
echo "📄 Génération du PDF : Constitution Éditoriale Institutionnelle..."
pandoc CONSTITUTION_EDITORIALE_INSTITUTIONNELLE.md \
    -o "$OUTPUT_DIR/CONSTITUTION_EDITORIALE_INSTITUTIONNELLE.pdf" \
    --pdf-engine=xelatex \
    -V geometry:margin=2.5cm \
    -V fontsize=11pt \
    -V documentclass=article \
    -V lang=fr \
    --toc \
    --toc-depth=2 \
    --number-sections

# Générer le PDF du Résumé Exécutif
echo "📄 Génération du PDF : Résumé Exécutif..."
pandoc RESUME_EXECUTIF_CONSTITUTION_EDITORIALE.md \
    -o "$OUTPUT_DIR/RESUME_EXECUTIF_CONSTITUTION_EDITORIALE.pdf" \
    --pdf-engine=xelatex \
    -V geometry:margin=2.5cm \
    -V fontsize=11pt \
    -V documentclass=article \
    -V lang=fr \
    --number-sections

# Générer le PDF de la FAQ Institutionnelle
echo "📄 Génération du PDF : FAQ Institutionnelle..."
pandoc FAQ_INSTITUTIONNELLE_CONSTITUTION_EDITORIALE.md \
    -o "$OUTPUT_DIR/FAQ_INSTITUTIONNELLE_CONSTITUTION_EDITORIALE.pdf" \
    --pdf-engine=xelatex \
    -V geometry:margin=2.5cm \
    -V fontsize=11pt \
    -V documentclass=article \
    -V lang=fr \
    --toc \
    --toc-depth=2 \
    --number-sections

echo ""
echo "✅ PDFs générés dans le répertoire : $OUTPUT_DIR/"
echo ""
echo "Fichiers générés :"
echo "  - CONSTITUTION_EDITORIALE_INSTITUTIONNELLE.pdf"
echo "  - RESUME_EXECUTIF_CONSTITUTION_EDITORIALE.pdf"
echo "  - FAQ_INSTITUTIONNELLE_CONSTITUTION_EDITORIALE.pdf"


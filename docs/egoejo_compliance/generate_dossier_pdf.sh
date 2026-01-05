#!/bin/bash
# Script de génération du PDF du Dossier de Reconnaissance Institutionnelle

# Vérifier que pandoc est installé
if ! command -v pandoc &> /dev/null; then
    echo "❌ Erreur : pandoc n'est pas installé."
    echo "Voir INSTALLATION_PANDOC.md pour les instructions."
    exit 1
fi

# Répertoire de sortie
OUTPUT_DIR="pdf"
mkdir -p "$OUTPUT_DIR"

# Générer le PDF du Dossier de Reconnaissance Institutionnelle
echo "📄 Génération du PDF : Dossier de Reconnaissance Institutionnelle..."
pandoc DOSSIER_RECONNAISSANCE_INSTITUTIONNELLE.md \
    -o "$OUTPUT_DIR/DOSSIER_RECONNAISSANCE_INSTITUTIONNELLE.pdf" \
    --pdf-engine=xelatex \
    -V geometry:margin=2.5cm \
    -V fontsize=11pt \
    -V documentclass=article \
    -V lang=fr \
    --toc \
    --toc-depth=3 \
    --number-sections \
    --metadata title="Dossier de Reconnaissance Institutionnelle - Plateforme EGOEJO" \
    --metadata author="EGOEJO Platform" \
    --metadata date="2025-01-27"

# Générer le PDF du Pitch Institutionnel
echo "📄 Génération du PDF : Pitch Institutionnel..."
pandoc PITCH_INSTITUTIONNEL.md \
    -o "$OUTPUT_DIR/PITCH_INSTITUTIONNEL.pdf" \
    --pdf-engine=xelatex \
    -V geometry:margin=2.5cm \
    -V fontsize=11pt \
    -V documentclass=article \
    -V lang=fr \
    --number-sections \
    --metadata title="Pitch Institutionnel - Plateforme EGOEJO" \
    --metadata author="EGOEJO Platform" \
    --metadata date="2025-01-27"

# Générer le PDF de la FAQ Juridique
echo "📄 Génération du PDF : FAQ Juridique..."
pandoc FAQ_JURIDIQUE.md \
    -o "$OUTPUT_DIR/FAQ_JURIDIQUE.pdf" \
    --pdf-engine=xelatex \
    -V geometry:margin=2.5cm \
    -V fontsize=11pt \
    -V documentclass=article \
    -V lang=fr \
    --toc \
    --toc-depth=2 \
    --number-sections \
    --metadata title="FAQ Juridique - Plateforme EGOEJO" \
    --metadata author="EGOEJO Platform" \
    --metadata date="2025-01-27"

echo ""
echo "✅ PDFs générés dans le répertoire : $OUTPUT_DIR/"
echo ""
echo "Fichiers générés :"
echo "  - DOSSIER_RECONNAISSANCE_INSTITUTIONNELLE.pdf"
echo "  - PITCH_INSTITUTIONNEL.pdf"
echo "  - FAQ_JURIDIQUE.pdf"


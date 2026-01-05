# Génération des PDFs de la Constitution Éditoriale Institutionnelle

## Prérequis

### Installation de Pandoc

**macOS** :
```bash
brew install pandoc
```

**Ubuntu/Debian** :
```bash
sudo apt-get install pandoc
```

**Windows** :
- Télécharger depuis : https://pandoc.org/installing.html
- Ou via Chocolatey : `choco install pandoc`

### Installation de LaTeX (pour la génération PDF)

**macOS** :
```bash
brew install --cask mactex
```

**Ubuntu/Debian** :
```bash
sudo apt-get install texlive-xetex texlive-lang-french
```

**Windows** :
- Installer MiKTeX : https://miktex.org/download

## Génération des PDFs

### Linux/macOS

```bash
cd docs/egoejo_compliance
chmod +x generate_pdf.sh
./generate_pdf.sh
```

### Windows (PowerShell)

```powershell
cd docs/egoejo_compliance
.\generate_pdf.ps1
```

### Génération manuelle

Si vous préférez générer les PDFs manuellement :

```bash
# Constitution Éditoriale Institutionnelle
pandoc CONSTITUTION_EDITORIALE_INSTITUTIONNELLE.md \
    -o pdf/CONSTITUTION_EDITORIALE_INSTITUTIONNELLE.pdf \
    --pdf-engine=xelatex \
    -V geometry:margin=2.5cm \
    -V fontsize=11pt \
    -V documentclass=article \
    -V lang=fr \
    --toc \
    --toc-depth=2 \
    --number-sections

# Résumé Exécutif
pandoc RESUME_EXECUTIF_CONSTITUTION_EDITORIALE.md \
    -o pdf/RESUME_EXECUTIF_CONSTITUTION_EDITORIALE.pdf \
    --pdf-engine=xelatex \
    -V geometry:margin=2.5cm \
    -V fontsize=11pt \
    -V documentclass=article \
    -V lang=fr \
    --number-sections

# FAQ Institutionnelle
pandoc FAQ_INSTITUTIONNELLE_CONSTITUTION_EDITORIALE.md \
    -o pdf/FAQ_INSTITUTIONNELLE_CONSTITUTION_EDITORIALE.pdf \
    --pdf-engine=xelatex \
    -V geometry:margin=2.5cm \
    -V fontsize=11pt \
    -V documentclass=article \
    -V lang=fr \
    --toc \
    --toc-depth=2 \
    --number-sections
```

## Fichiers générés

Les PDFs seront générés dans le répertoire `pdf/` :

- `CONSTITUTION_EDITORIALE_INSTITUTIONNELLE.pdf` : Document complet (9 articles + 4 annexes)
- `RESUME_EXECUTIF_CONSTITUTION_EDITORIALE.pdf` : Résumé exécutif (2 pages)
- `FAQ_INSTITUTIONNELLE_CONSTITUTION_EDITORIALE.pdf` : FAQ institutionnelle (36 questions/réponses)

## Personnalisation

Pour personnaliser la génération des PDFs, vous pouvez modifier les options pandoc dans les scripts :

- `--pdf-engine` : Moteur PDF (xelatex, pdflatex, wkhtmltopdf)
- `-V geometry:margin` : Marges de la page
- `-V fontsize` : Taille de la police
- `-V documentclass` : Classe de document LaTeX
- `--toc` : Table des matières
- `--toc-depth` : Profondeur de la table des matières
- `--number-sections` : Numérotation des sections

## Alternatives

Si pandoc n'est pas disponible, vous pouvez utiliser :

- **Markdown → PDF en ligne** : https://www.markdowntopdf.com/
- **VS Code** : Extension "Markdown PDF"
- **Typora** : Export PDF intégré
- **GitHub** : Visualiser le Markdown et imprimer en PDF


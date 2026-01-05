# Installation de Pandoc pour la génération des PDFs

## Option 1 : Installation via Chocolatey (Recommandé pour Windows)

Si vous avez Chocolatey installé :

```powershell
choco install pandoc
```

Si vous n'avez pas Chocolatey, installez-le d'abord :
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

## Option 2 : Installation manuelle

1. Téléchargez Pandoc depuis : https://pandoc.org/installing.html
2. Exécutez l'installateur
3. Redémarrez PowerShell après l'installation

## Option 3 : Installation de LaTeX (Nécessaire pour la génération PDF)

Pandoc nécessite un moteur LaTeX pour générer les PDFs. Installez MiKTeX :

1. Téléchargez MiKTeX depuis : https://miktex.org/download
2. Exécutez l'installateur
3. MiKTeX installera automatiquement les packages nécessaires lors de la première génération

## Vérification de l'installation

Après installation, vérifiez que pandoc est disponible :

```powershell
pandoc --version
```

## Alternatives si Pandoc n'est pas disponible

### Option A : Utiliser un service en ligne

1. Copiez le contenu du fichier Markdown
2. Utilisez un service en ligne comme :
   - https://www.markdowntopdf.com/
   - https://dillinger.io/ (avec export PDF)
   - https://stackedit.io/ (avec export PDF)

### Option B : Utiliser VS Code

1. Installez l'extension "Markdown PDF" dans VS Code
2. Ouvrez le fichier Markdown
3. Utilisez la commande "Markdown PDF: Export (pdf)"

### Option C : Utiliser Typora

1. Installez Typora : https://typora.io/
2. Ouvrez le fichier Markdown
3. Utilisez File > Export > PDF

### Option D : Utiliser GitHub

1. Visualisez le fichier Markdown sur GitHub
2. Utilisez l'option "Print" du navigateur
3. Sélectionnez "Save as PDF"

## Après installation de Pandoc

Une fois Pandoc installé, exécutez :

```powershell
cd docs/egoejo_compliance
.\generate_pdf.ps1
```

Les PDFs seront générés dans le répertoire `pdf/`.


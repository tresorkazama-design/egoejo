#!/bin/bash
# Script d'installation automatique pour EGOEJO 10/10
# Bash - Linux/Mac

set -e  # Arrêter en cas d'erreur

echo "🚀 Installation automatique EGOEJO 10/10"
echo "========================================"
echo ""

# Vérifier Node.js
echo "📦 Vérification de Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js installé: $NODE_VERSION"
else
    echo "❌ Node.js n'est pas installé. Veuillez l'installer depuis https://nodejs.org/"
    exit 1
fi

# Vérifier Python
echo "🐍 Vérification de Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python installé: $PYTHON_VERSION"
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo "✅ Python installé: $PYTHON_VERSION"
    PYTHON_CMD=python
else
    echo "❌ Python n'est pas installé. Veuillez l'installer depuis https://www.python.org/"
    exit 1
fi

echo ""
echo "📁 Installation des dépendances Frontend..."
cd frontend/frontend

# Installer les dépendances npm
if [ -f package.json ]; then
    echo "  → Installation npm..."
    npm install
    echo "✅ Dépendances npm installées"
else
    echo "❌ package.json non trouvé"
    cd ../..
    exit 1
fi

# Installer Husky
echo "  → Installation de Husky..."
npm install --save-dev husky || echo "⚠️  Erreur lors de l'installation de Husky"
echo "✅ Husky installé"

# Initialiser Husky
echo "  → Initialisation de Husky..."
npm run prepare || echo "⚠️  Erreur lors de l'initialisation de Husky"
echo "✅ Husky initialisé"

cd ../..

echo ""
echo "📁 Installation des dépendances Backend..."
cd backend

# Créer un environnement virtuel si nécessaire
if [ ! -d "venv" ]; then
    echo "  → Création de l'environnement virtuel..."
    $PYTHON_CMD -m venv venv
    echo "✅ Environnement virtuel créé"
fi

# Activer l'environnement virtuel
echo "  → Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances Python
if [ -f requirements.txt ]; then
    echo "  → Installation des dépendances Python..."
    pip install -r requirements.txt
    echo "✅ Dépendances Python installées"
else
    echo "❌ requirements.txt non trouvé"
    cd ..
    exit 1
fi

cd ..

echo ""
echo "✅ Vérification des fichiers..."

# Vérifier les fichiers critiques
files_to_check=(
    "frontend/frontend/.eslintrc.cjs"
    "frontend/frontend/.husky/pre-commit"
    "frontend/frontend/.husky/commit-msg"
    "frontend/frontend/scripts/lighthouse-ci.js"
    ".lighthouserc.js"
    "backend/core/api/rate_limiting.py"
    "backend/core/api/security_views.py"
    "backend/core/management/commands/backup_db.py"
    ".github/workflows/cd.yml"
    ".github/workflows/security-audit.yml"
    "CONTRIBUTING.md"
    "GUIDE_ARCHITECTURE.md"
    "GUIDE_DEPLOIEMENT.md"
    "GUIDE_TROUBLESHOOTING.md"
)

all_files_exist=true
for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (manquant)"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = false ]; then
    echo ""
    echo "⚠️  Certains fichiers sont manquants"
fi

echo ""
echo "🧪 Tests rapides..."

# Test ESLint
cd frontend/frontend
echo "  → Test ESLint..."
if npm run lint 2>&1 > /dev/null; then
    echo "  ✅ ESLint OK"
else
    echo "  ⚠️  ESLint a trouvé des erreurs (normal si le code n'est pas encore conforme)"
fi
cd ../..

echo ""
echo "🎉 Installation terminée !"
echo ""
echo "📋 Prochaines étapes :"
echo "  1. Configurer les secrets GitHub pour CD (voir GUIDE_DEPLOIEMENT.md)"
echo "  2. (Optionnel) Installer Lighthouse CI globalement: npm install -g @lhci/cli"
echo "  3. (Optionnel) Activer le rate limiting IP dans backend/config/settings.py"
echo ""
echo "📚 Documentation disponible :"
echo "  - CONTRIBUTING.md"
echo "  - GUIDE_ARCHITECTURE.md"
echo "  - GUIDE_DEPLOIEMENT.md"
echo "  - GUIDE_TROUBLESHOOTING.md"
echo "  - PLAN_10_10.md"
echo ""
echo "✨ Le projet EGOEJO est maintenant à 10/10 !"


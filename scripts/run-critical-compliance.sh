#!/bin/bash
# Script pour exécuter tous les tests Critical Compliance (P0/P1) localement
# Usage: ./scripts/run-critical-compliance.sh

set -e  # Arrêter en cas d'erreur

echo "=========================================="
echo "🚨 EXÉCUTION CRITICAL COMPLIANCE (P0/P1)"
echo "=========================================="
echo ""

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher un succès
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Fonction pour afficher une erreur
error() {
    echo -e "${RED}❌ $1${NC}"
}

# Fonction pour afficher un avertissement
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Vérifier que nous sommes à la racine du projet
if [ ! -f "backend/requirements.txt" ] || [ ! -f "frontend/frontend/package.json" ]; then
    error "Ce script doit être exécuté depuis la racine du projet"
    exit 1
fi

# 1. Audit Statique
echo "📋 1/5: Audit Statique (mots interdits)..."
cd frontend/frontend
if npm run audit:global; then
    success "Audit statique: OK"
else
    error "Audit statique: ÉCHEC"
    exit 1
fi
cd ../..

# 2. Backend Compliance
echo ""
echo "📋 2/5: Backend Compliance Tests..."
cd backend
if pytest tests/compliance/ -v -m egoejo_compliance --tb=short; then
    success "Backend Compliance: OK"
else
    error "Backend Compliance: ÉCHEC"
    exit 1
fi
cd ..

# 3. Backend Permissions
echo ""
echo "📋 3/5: Backend Permission Tests..."
cd backend
if pytest core/tests/api/test_*_permissions.py -v -m critical --tb=short; then
    success "Backend Permissions: OK"
else
    error "Backend Permissions: ÉCHEC"
    exit 1
fi
cd ..

# 4. Frontend Unit
echo ""
echo "📋 4/5: Frontend Unit Tests..."
cd frontend/frontend
if npm test -- --run; then
    success "Frontend Unit: OK"
else
    error "Frontend Unit: ÉCHEC"
    exit 1
fi
cd ../..

# 5. Frontend E2E Critical
echo ""
echo "📋 5/5: Frontend E2E Critical Tests..."
warning "Note: Assurez-vous que le backend et le frontend sont démarrés"
warning "Backend: http://localhost:8000"
warning "Frontend: http://localhost:5173"
echo ""
read -p "Appuyez sur Entrée pour continuer (Ctrl+C pour annuler)..."
cd frontend/frontend
export BACKEND_URL="http://localhost:8000"
export PLAYWRIGHT_BASE_URL="http://localhost:5173"
export E2E_MODE="full-stack"
if npm run test:e2e -- e2e/flux-complet-saka-vote.spec.js e2e/flux-complet-projet-financement.spec.js; then
    success "Frontend E2E Critical: OK"
else
    error "Frontend E2E Critical: ÉCHEC"
    exit 1
fi
cd ../..

echo ""
echo "=========================================="
echo -e "${GREEN}✅ SUCCÈS : Tous les tests Critical Compliance sont passés !${NC}"
echo "=========================================="
echo ""


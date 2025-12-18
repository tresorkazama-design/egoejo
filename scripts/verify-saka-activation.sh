#!/bin/bash
# Script de vérification de l'activation SAKA en production
# Usage: ./scripts/verify-saka-activation.sh https://votre-domaine.com

set -e

BASE_URL="${1:-https://egoejo.org}"

echo "🔍 Vérification de l'activation SAKA sur $BASE_URL"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour vérifier une réponse API
check_api() {
    local endpoint=$1
    local expected_key=$2
    local expected_value=$3
    
    echo -n "Vérification $endpoint... "
    
    response=$(curl -s "$BASE_URL$endpoint" || echo "ERROR")
    
    if [ "$response" = "ERROR" ]; then
        echo -e "${RED}❌ Erreur de connexion${NC}"
        return 1
    fi
    
    # Vérifier si la clé existe et a la bonne valeur
    if echo "$response" | grep -q "\"$expected_key\":\s*$expected_value"; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ Échec${NC}"
        echo "   Réponse: $response"
        return 1
    fi
}

# Vérifier les feature flags
echo "📋 Vérification des feature flags..."
check_api "/api/config/features/" "saka_enabled" "true" || exit 1
check_api "/api/config/features/" "saka_compost_enabled" "true" || exit 1
check_api "/api/config/features/" "saka_silo_redis_enabled" "true" || exit 1

echo ""
echo "✅ Tous les feature flags sont activés !"
echo ""

# Vérifier que l'API SAKA répond
echo "📋 Vérification des endpoints SAKA..."
check_api "/api/saka/silo/" "enabled" "true" || echo -e "${YELLOW}⚠️  Endpoint Silo non disponible (peut être normal si aucun SAKA)${NC}"

echo ""
echo "🎉 Vérification terminée !"


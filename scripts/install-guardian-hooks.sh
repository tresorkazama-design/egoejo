#!/bin/bash
# 🏛️ Installation des hooks Guardian EGOEJO

echo "🛡️ Installation des hooks Guardian EGOEJO..."

# Créer le répertoire hooks s'il n'existe pas
mkdir -p .git/hooks

# Copier le hook pre-commit
if [ -f ".git/hooks/pre-commit-egoejo-guardian" ]; then
    cp .git/hooks/pre-commit-egoejo-guardian .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    echo "✅ Hook pre-commit Guardian installé"
else
    echo "⚠️ Fichier pre-commit-egoejo-guardian non trouvé"
    echo "Création du hook pre-commit..."
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# 🏛️ EGOEJO Guardian - Pre-commit Hook
# Empêche la trahison du projet techniquement

echo "🛡️ EGOEJO Guardian : Vérification des modifications..."

VIOLATIONS=0

# Vérifier les fichiers modifiés
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E "\.(py|js|jsx|ts|tsx)$")

if [ -z "$FILES" ]; then
    echo "✅ Aucun fichier de code modifié"
    exit 0
fi

# 1. Vérifier absence de conversion SAKA ↔ EUR
echo "🔍 Vérification : Conversion SAKA ↔ EUR"
if git diff --cached | grep -iE "(convert.*saka.*eur|saka.*to.*eur|eur.*to.*saka|saka.*exchange.*rate|saka.*price|saka.*value.*eur|saka.*worth.*eur)"; then
    echo "❌ VIOLATION CRITIQUE : Conversion SAKA ↔ EUR détectée"
    echo "🚫 La structure relationnelle (SAKA) et la structure instrumentale (EUR) sont strictement séparées."
    VIOLATIONS=$((VIOLATIONS + 1))
fi

# 2. Vérifier absence de rendement financier sur SAKA
echo "🔍 Vérification : Rendement financier sur SAKA"
if git diff --cached | grep -iE "(saka.*roi|saka.*yield|saka.*interest|saka.*dividend|saka.*return.*investment|saka.*profit)"; then
    echo "❌ VIOLATION CRITIQUE : Rendement financier sur SAKA détecté"
    echo "🚫 Le SAKA ne peut pas générer de rendement financier. C'est une unité d'engagement non monétaire."
    VIOLATIONS=$((VIOLATIONS + 1))
fi

# 3. Vérifier priorité structure relationnelle
echo "🔍 Vérification : Priorité structure relationnelle (SAKA)"
if git diff --cached | grep -iE "(disable.*saka|saka.*disabled|if.*eur.*then.*disable.*saka|ENABLE_SAKA.*=.*False|SAKA_COMPOST_ENABLED.*=.*False)"; then
    echo "❌ VIOLATION CRITIQUE : Désactivation SAKA détectée"
    echo "🚫 La structure relationnelle (SAKA) est PRIORITAIRE. Elle ne peut pas être désactivée."
    VIOLATIONS=$((VIOLATIONS + 1))
fi

# 4. Vérifier anti-accumulation
echo "🔍 Vérification : Anti-accumulation SAKA"
if git diff --cached | grep -iE "(saka.*accumulate.*infinite|saka.*no.*limit|disable.*compost|skip.*compost|bypass.*compost)"; then
    echo "❌ VIOLATION CRITIQUE : Accumulation infinie ou désactivation compostage détectée"
    echo "🚫 L'accumulation SAKA est interdite. Le cycle compostage est obligatoire."
    VIOLATIONS=$((VIOLATIONS + 1))
fi

# 5. Vérifier cycle SAKA incompressible
echo "🔍 Vérification : Cycle SAKA incompressible"
if git diff --cached | grep -iE "(skip.*saka.*cycle|bypass.*saka.*cycle|compost.*without.*silo)"; then
    echo "❌ VIOLATION CRITIQUE : Contournement cycle SAKA détecté"
    echo "🚫 Le cycle SAKA (Récolte → Usage → Compost → Silo → Redistribution) est NON NÉGOCIABLE."
    VIOLATIONS=$((VIOLATIONS + 1))
fi

# Résultat
if [ $VIOLATIONS -gt 0 ]; then
    echo ""
    echo "🚫 COMMIT BLOQUÉ : $VIOLATIONS violation(s) de la Constitution EGOEJO détectée(s)"
    echo ""
    echo "📋 Constitution EGOEJO :"
    echo "  - Structure Relationnelle (SAKA) : Souveraine, Prioritaire"
    echo "  - Structure Instrumentale (EUR) : Subordonnée, Dormante par défaut"
    echo "  - Règle Absolue : Aucune conversion SAKA ↔ EUR"
    echo "  - Règle Absolue : Aucun rendement financier sur SAKA"
    echo ""
    echo "Consultez docs/architecture/CONSTITUTION_EGOEJO.md pour plus d'informations"
    exit 1
fi

echo "✅ Aucune violation détectée. Commit autorisé."
exit 0
EOF
    chmod +x .git/hooks/pre-commit
    echo "✅ Hook pre-commit Guardian créé et installé"
fi

echo ""
echo "✅ Installation terminée !"
echo ""
echo "🛡️ Le Guardian EGOEJO est maintenant actif :"
echo "  - Pre-commit hook : Vérifie chaque commit"
echo "  - PR Bot : Vérifie chaque Pull Request"
echo ""
echo "📋 Consultez docs/architecture/CONSTITUTION_EGOEJO.md pour les règles"


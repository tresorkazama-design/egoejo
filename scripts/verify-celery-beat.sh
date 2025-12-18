#!/bin/bash
# Script de vérification que Celery Beat est actif
# Vérifie les logs et les tâches planifiées

echo "🔍 Vérification de Celery Beat"
echo ""

# Vérifier si Celery Beat est en cours d'exécution
if pgrep -f "celery.*beat" > /dev/null; then
    echo "✅ Celery Beat est en cours d'exécution"
else
    echo "❌ Celery Beat n'est PAS en cours d'exécution"
    echo "   Action requise: Démarrer Celery Beat"
    exit 1
fi

# Vérifier les logs récents
echo ""
echo "📋 Derniers logs Celery Beat:"
journalctl -u celery-beat -n 20 --no-pager 2>/dev/null || echo "   (Logs non disponibles via journalctl)"

echo ""
echo "✅ Vérification terminée"


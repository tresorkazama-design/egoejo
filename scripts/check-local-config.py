#!/usr/bin/env python
"""
Script de vérification de la configuration locale SAKA
Vérifie que tout est prêt pour l'activation en production
"""
import os
import sys
import django

# Configuration Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from config.celery import app

print("🔍 Vérification de la configuration locale SAKA\n")

# Vérifier les feature flags
print("📋 Feature Flags:")
print(f"  ENABLE_SAKA: {getattr(settings, 'ENABLE_SAKA', False)}")
print(f"  SAKA_COMPOST_ENABLED: {getattr(settings, 'SAKA_COMPOST_ENABLED', False)}")
print(f"  SAKA_SILO_REDIS_ENABLED: {getattr(settings, 'SAKA_SILO_REDIS_ENABLED', False)}")

# Vérifier Celery Beat schedule
print("\n📋 Tâches Celery Beat planifiées:")
beat_schedule = app.conf.beat_schedule
for task_name, task_config in beat_schedule.items():
    print(f"  {task_name}:")
    print(f"    Tâche: {task_config['task']}")
    print(f"    Planification: {task_config['schedule']}")

# Vérifier Redis
print("\n📋 Configuration Redis:")
redis_url = os.environ.get('REDIS_URL', 'Non défini')
print(f"  REDIS_URL: {redis_url}")

# Vérifier les services
print("\n📋 Services disponibles:")
try:
    from core.services.saka_metrics import get_compost_metrics, get_silo_metrics
    print("  ✅ Service métriques SAKA disponible")
except ImportError as e:
    print(f"  ❌ Service métriques SAKA non disponible: {e}")

try:
    from core.tasks_monitoring import check_celery_beat_health
    print("  ✅ Tâches de monitoring disponibles")
except ImportError as e:
    print(f"  ❌ Tâches de monitoring non disponibles: {e}")

# Vérifier les endpoints API
print("\n📋 Endpoints API:")
try:
    from core.api.saka_metrics_views import SakaAllMetricsView
    print("  ✅ Endpoints métriques SAKA disponibles")
except ImportError as e:
    print(f"  ❌ Endpoints métriques SAKA non disponibles: {e}")

print("\n✅ Vérification terminée")


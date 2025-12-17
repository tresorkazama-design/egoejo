"""
Configuration Celery pour tâches asynchrones
"""
import os
from celery import Celery
from celery.schedules import crontab

# Définir le module de configuration Django par défaut
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('egoejo')

# Configuration depuis les variables d'environnement
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Utiliser Redis comme broker et backend
app.conf.broker_url = REDIS_URL.replace('/0', '/2')  # DB 2 pour Celery broker
app.conf.result_backend = REDIS_URL.replace('/0', '/2')  # DB 2 pour Celery results

# Configuration des tâches
app.conf.task_serializer = 'json'
app.conf.accept_content = ['json']
app.conf.result_serializer = 'json'
app.conf.timezone = 'UTC'
app.conf.enable_utc = True

# Configuration des workers
app.conf.worker_prefetch_multiplier = 4
app.conf.worker_max_tasks_per_child = 1000

# Configuration des retries
app.conf.task_acks_late = True
app.conf.task_reject_on_worker_lost = True

# Configuration Celery Beat (tâches périodiques)
app.conf.beat_schedule = {
    # Phase 3 SAKA : Cycle de compostage (tous les lundis à 3h du matin UTC)
    'saka-compost-cycle': {
        'task': 'core.tasks.saka_run_compost_cycle',
        'schedule': crontab(hour=3, minute=0, day_of_week=1),  # Lundi à 3h
        'args': (False,),  # dry_run=False
    },
    # Phase 3 SAKA : Redistribution du Silo Commun (tous les premiers du mois à 4h du matin UTC)
    # Désactivée par défaut (SAKA_SILO_REDIS_ENABLED=False)
    'saka-silo-redistribution': {
        'task': 'core.tasks.run_saka_silo_redistribution',
        'schedule': crontab(hour=4, minute=0, day_of_month=1),  # 1er du mois à 4h
    },
}

# Découverte automatique des tâches
app.autodiscover_tasks()


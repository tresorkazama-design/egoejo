"""
Configuration Celery pour tâches asynchrones
"""
import os
from celery import Celery

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

# Découverte automatique des tâches
app.autodiscover_tasks()


"""
WSGI config for EGOEJO project.

Dead Man's Switch : La vérification SAKA est effectuée dans core.apps.CoreConfig.ready()
qui s'exécute automatiquement lors du chargement de l'application Django.
Si ENABLE_SAKA=False en production, une ImproperlyConfigured exception est levée,
empêchant le serveur (Gunicorn/Daphne) de démarrer.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Le Dead Man's Switch SAKA est dans core.apps.CoreConfig.ready()
# Cette méthode s'exécute automatiquement lors du chargement de l'application
application = get_wsgi_application()
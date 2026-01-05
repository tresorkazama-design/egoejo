"""
URLs pour l'API core.

NOTE IMPORTANTE : Les routes API sont actuellement centralisées dans `backend/core/urls.py`.
Ce fichier existe pour maintenir la structure du module, mais n'est pas inclus dans la configuration principale.

Si vous souhaitez organiser les routes différemment à l'avenir, vous pouvez :
1. Déplacer les routes depuis `core/urls.py` vers ce fichier
2. Inclure ce fichier dans `core/urls.py` avec : `path("api/", include("core.api.urls"))`
3. Ou inclure directement dans `config/urls.py`

Pour l'instant, toutes les routes sont définies dans `core/urls.py` pour simplifier la maintenance.
"""

from django.urls import path

# Les routes sont actuellement définies dans core/urls.py
# Ce fichier est laissé vide pour éviter la duplication

urlpatterns = [
    # Routes centralisées dans core/urls.py
    # Voir backend/core/urls.py pour toutes les définitions de routes
]


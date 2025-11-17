from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET", "HEAD"])
def health_check(request):
    """Endpoint de healthcheck pour Railway - exempté de CSRF"""
    try:
        # Vérifier la connexion à la base de données
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        
        # Vérifier que le résultat est correct
        if result and result[0] == 1:
            logger.info("Health check: Database connection successful")
            return JsonResponse({
                "status": "ok",
                "database": "connected",
                "service": "egoejo-backend"
            })
        else:
            logger.warning("Health check: Database query returned unexpected result")
            return JsonResponse({
                "status": "warning",
                "database": "unexpected_result",
                "service": "egoejo-backend"
            }, status=503)
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return JsonResponse({
            "status": "error",
            "database": "disconnected",
            "error": str(e),
            "service": "egoejo-backend"
        }, status=503)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api/health/', health_check, name='health-check'),
]
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
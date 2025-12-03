from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
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

@csrf_exempt
@require_http_methods(["GET", "HEAD"])
def api_root(request):
    """Endpoint racine pour afficher les informations de l'API"""
    return JsonResponse({
        "service": "egoejo-backend",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health/",
            "api_root": "/api/",
            "admin": "/admin/",
            "intents": {
                "rejoindre": "/api/intents/rejoindre/",
                "admin": "/api/intents/admin/",
                "export": "/api/intents/export/",
            },
            "chat": {
                "threads": "/api/chat/threads/",
                "messages": "/api/chat/messages/",
            },
            "polls": "/api/polls/",
            "projets": "/api/projets/",
            "cagnottes": "/api/cagnottes/",
            "moderation": {
                "reports": "/api/moderation/reports/",
                "audit_logs": "/api/audit/logs/",
            },
        },
        "documentation": "https://github.com/tresorkazama-design/egoejo"
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api/health/', health_check, name='health-check'),
    # OpenAPI/Swagger documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# --- Routes ajoutées pour les contenus éducatifs (Dashboard) ---
from core.api.content_views import EducationalContentViewSet

educational_content_list = EducationalContentViewSet.as_view({
    "get": "list",
    "post": "create",
})

urlpatterns += [
    path("api/contents/", educational_content_list, name="educationalcontent-list"),
]
# --- Fin ajout contenus éducatifs ---

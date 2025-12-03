"""
Health check endpoints pour le monitoring
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """
    Endpoint de health check public
    Vérifie l'état de la base de données et du cache
    """
    permission_classes = []  # Public endpoint
    
    def get(self, request):
        health_status = {
            'status': 'healthy',
            'checks': {}
        }
        
        # Check database
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status['checks']['database'] = 'ok'
        except Exception as e:
            logger.error(f'Health check database error: {e}')
            health_status['checks']['database'] = f'error: {str(e)}'
            health_status['status'] = 'unhealthy'
        
        # Check cache
        try:
            cache.set('health_check', 'ok', 10)
            cache_result = cache.get('health_check')
            if cache_result == 'ok':
                health_status['checks']['cache'] = 'ok'
            else:
                health_status['checks']['cache'] = 'error: cache not working'
                health_status['status'] = 'degraded'
        except Exception as e:
            logger.error(f'Health check cache error: {e}')
            health_status['checks']['cache'] = f'error: {str(e)}'
            health_status['status'] = 'degraded'
        
        status_code = status.HTTP_200_OK if health_status['status'] == 'healthy' else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response(health_status, status=status_code)


class ReadinessCheckView(APIView):
    """
    Endpoint de readiness check (pour Kubernetes)
    Vérifie que l'application est prête à recevoir du trafic
    """
    permission_classes = []
    
    def get(self, request):
        try:
            # Vérifier la base de données
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return Response({'status': 'ready'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Readiness check error: {e}')
            return Response({'status': 'not ready', 'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class LivenessCheckView(APIView):
    """
    Endpoint de liveness check (pour Kubernetes)
    Vérifie que l'application est toujours vivante
    """
    permission_classes = []
    
    def get(self, request):
        return Response({'status': 'alive'}, status=status.HTTP_200_OK)


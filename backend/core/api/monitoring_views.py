"""
Vues API pour le monitoring et les métriques de performance
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging

from core.models.monitoring import PerformanceMetric, MonitoringAlert

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class MetricsView(APIView):
    """
    Endpoint pour recevoir les métriques de performance depuis le frontend
    POST /api/analytics/metrics/
    
    Body:
    {
        "metric": "LCP",
        "value": 1234.5,
        "metadata": {"endpoint": "/api/projets/"},
        "timestamp": "2025-01-27T10:00:00Z",
        "url": "https://egoejo.org/projets"
    }
    """
    permission_classes = [AllowAny]  # Permettre l'envoi depuis le frontend sans auth
    
    def post(self, request):
        """
        Enregistre une métrique de performance
        """
        try:
            metric_name = request.data.get('metric')
            value = request.data.get('value')
            metadata = request.data.get('metadata', {})
            timestamp_str = request.data.get('timestamp')
            url = request.data.get('url', '')
            
            if not metric_name or value is None:
                return Response(
                    {'detail': 'metric et value sont requis'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Convertir le timestamp si fourni
            timestamp = timezone.now()
            if timestamp_str:
                try:
                    timestamp = timezone.datetime.fromisoformat(
                        timestamp_str.replace('Z', '+00:00')
                    )
                except (ValueError, AttributeError):
                    pass
            
            # Déterminer le type de métrique
            metric_type = metric_name
            if metric_name not in dict(PerformanceMetric.METRIC_TYPES):
                metric_type = 'Custom'
            
            # Récupérer l'utilisateur si authentifié
            user = request.user if request.user.is_authenticated else None
            
            # Récupérer l'IP et User-Agent
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Créer la métrique
            metric = PerformanceMetric.objects.create(
                metric_type=metric_type,
                value=float(value),
                url=url[:500] if url else None,
                user=user,
                metadata=metadata,
                timestamp=timestamp,
                user_agent=user_agent[:500] if user_agent else None,
                ip_address=ip_address,
            )
            
            logger.info(f"Métrique enregistrée: {metric_name}={value}")
            
            return Response(
                {'id': metric.id, 'status': 'created'},
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de la métrique: {e}", exc_info=True)
            return Response(
                {'detail': 'Erreur lors de l\'enregistrement'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_client_ip(self, request):
        """Récupère l'IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@method_decorator(csrf_exempt, name='dispatch')
class AlertsView(APIView):
    """
    Endpoint pour recevoir les alertes depuis le frontend
    POST /api/monitoring/alerts/
    
    Body:
    {
        "level": "warning",
        "message": "LCP lent: 3000ms",
        "metadata": {"context": "homepage"},
        "timestamp": "2025-01-27T10:00:00Z",
        "url": "https://egoejo.org/"
    }
    """
    permission_classes = [AllowAny]  # Permettre l'envoi depuis le frontend sans auth
    
    def post(self, request):
        """
        Enregistre une alerte
        """
        try:
            level = request.data.get('level', 'info')
            message = request.data.get('message')
            metadata = request.data.get('metadata', {})
            timestamp_str = request.data.get('timestamp')
            url = request.data.get('url', '')
            
            if not message:
                return Response(
                    {'detail': 'message est requis'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Valider le niveau
            valid_levels = dict(MonitoringAlert.ALERT_LEVELS)
            if level not in valid_levels:
                level = 'info'
            
            # Convertir le timestamp si fourni
            timestamp = timezone.now()
            if timestamp_str:
                try:
                    timestamp = timezone.datetime.fromisoformat(
                        timestamp_str.replace('Z', '+00:00')
                    )
                except (ValueError, AttributeError):
                    pass
            
            # Récupérer l'utilisateur si authentifié
            user = request.user if request.user.is_authenticated else None
            
            # Récupérer l'IP et User-Agent
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Créer l'alerte
            alert = MonitoringAlert.objects.create(
                level=level,
                message=message,
                url=url[:500] if url else None,
                user=user,
                metadata=metadata,
                timestamp=timestamp,
                user_agent=user_agent[:500] if user_agent else None,
                ip_address=ip_address,
            )
            
            # Logger selon le niveau
            if level == 'critical':
                logger.critical(f"Alerte critique: {message}")
            elif level == 'error':
                logger.error(f"Alerte erreur: {message}")
            elif level == 'warning':
                logger.warning(f"Alerte warning: {message}")
            else:
                logger.info(f"Alerte info: {message}")
            
            return Response(
                {'id': alert.id, 'status': 'created'},
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'alerte: {e}", exc_info=True)
            return Response(
                {'detail': 'Erreur lors de l\'enregistrement'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_client_ip(self, request):
        """Récupère l'IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class MetricsStatsView(APIView):
    """
    Endpoint pour consulter les statistiques des métriques (admin uniquement)
    GET /api/monitoring/metrics/stats/
    """
    from rest_framework.permissions import IsAdminUser
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """
        Retourne des statistiques sur les métriques
        """
        from django.db.models import Avg, Min, Max, Count
        from datetime import timedelta
        
        # Période par défaut: 24 dernières heures
        hours = int(request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        
        # Filtrer par type de métrique si fourni
        metric_type = request.query_params.get('metric_type')
        queryset = PerformanceMetric.objects.filter(timestamp__gte=since)
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)
        
        # Statistiques par type de métrique
        stats = {}
        for metric_type_code, metric_type_name in PerformanceMetric.METRIC_TYPES:
            metrics = queryset.filter(metric_type=metric_type_code)
            if metrics.exists():
                stats[metric_type_code] = {
                    'name': metric_type_name,
                    'count': metrics.count(),
                    'avg': metrics.aggregate(Avg('value'))['value__avg'],
                    'min': metrics.aggregate(Min('value'))['value__min'],
                    'max': metrics.aggregate(Max('value'))['value__max'],
                }
        
        return Response({
            'period_hours': hours,
            'since': since.isoformat(),
            'stats': stats,
        })


class AlertsListView(APIView):
    """
    Endpoint pour lister les alertes (admin uniquement)
    GET /api/monitoring/alerts/
    """
    from rest_framework.permissions import IsAdminUser
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """
        Liste les alertes non résolues
        """
        from datetime import timedelta
        
        # Filtrer par niveau si fourni
        level = request.query_params.get('level')
        resolved = request.query_params.get('resolved', 'false').lower() == 'true'
        
        # Période par défaut: 7 derniers jours
        hours = int(request.query_params.get('hours', 168))  # 7 jours
        since = timezone.now() - timedelta(hours=hours)
        
        queryset = MonitoringAlert.objects.filter(
            timestamp__gte=since,
            resolved=resolved
        )
        
        if level:
            queryset = queryset.filter(level=level)
        
        alerts = queryset.order_by('-timestamp')[:100]  # Limiter à 100
        
        return Response({
            'count': queryset.count(),
            'alerts': [
                {
                    'id': alert.id,
                    'level': alert.level,
                    'message': alert.message,
                    'url': alert.url,
                    'timestamp': alert.timestamp.isoformat(),
                    'resolved': alert.resolved,
                    'metadata': alert.metadata,
                }
                for alert in alerts
            ]
        })
    
    def patch(self, request, alert_id=None):
        """
        Marquer une alerte comme résolue
        PATCH /api/monitoring/alerts/{id}/
        """
        from rest_framework.permissions import IsAdminUser
        if not request.user.is_staff:
            return Response(
                {'detail': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            alert = MonitoringAlert.objects.get(id=alert_id)
            alert.resolve()
            return Response({'status': 'resolved'})
        except MonitoringAlert.DoesNotExist:
            return Response(
                {'detail': 'Alerte non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )


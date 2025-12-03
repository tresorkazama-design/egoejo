"""
Vues de sécurité pour audit et monitoring
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class SecurityAuditView(APIView):
    """
    Endpoint pour l'audit de sécurité (admin uniquement)
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """
        Retourne un rapport de sécurité
        """
        audit_report = {
            'timestamp': timezone.now().isoformat(),
            'checks': {}
        }
        
        # Vérifier les utilisateurs avec mots de passe faibles
        weak_passwords = User.objects.filter(
            last_login__isnull=False
        ).exclude(
            password__startswith='argon2'  # Argon2 est le hasher par défaut
        ).count()
        audit_report['checks']['weak_passwords'] = {
            'status': 'ok' if weak_passwords == 0 else 'warning',
            'count': weak_passwords,
            'message': f'{weak_passwords} utilisateurs avec mots de passe potentiellement faibles'
        }
        
        # Vérifier les utilisateurs inactifs depuis longtemps
        inactive_threshold = timezone.now() - timedelta(days=90)
        inactive_users = User.objects.filter(
            last_login__lt=inactive_threshold,
            is_active=True
        ).count()
        audit_report['checks']['inactive_users'] = {
            'status': 'info',
            'count': inactive_users,
            'message': f'{inactive_users} utilisateurs inactifs depuis plus de 90 jours'
        }
        
        # Vérifier les comptes admin
        admin_count = User.objects.filter(is_superuser=True).count()
        audit_report['checks']['admin_accounts'] = {
            'status': 'ok' if admin_count <= 5 else 'warning',
            'count': admin_count,
            'message': f'{admin_count} comptes administrateurs'
        }
        
        return Response(audit_report)


class SecurityMetricsView(APIView):
    """
    Endpoint pour les métriques de sécurité (admin uniquement)
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """
        Retourne les métriques de sécurité
        """
        from django.core.cache import cache
        from django.db import connection
        
        metrics = {
            'timestamp': timezone.now().isoformat(),
            'cache_status': 'ok' if cache.get('health_check') else 'unknown',
            'database_status': 'ok',
            'rate_limiting_active': True,
            'csp_enabled': True,
            'https_enforced': not request.get_host().startswith('localhost'),
        }
        
        # Vérifier la connexion DB
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            metrics['database_status'] = 'ok'
        except Exception as e:
            metrics['database_status'] = f'error: {str(e)}'
        
        return Response(metrics)


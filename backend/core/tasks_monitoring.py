"""
Tâches Celery pour le monitoring et les alertes
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='core.tasks.check_celery_beat_health')
def check_celery_beat_health(self):
    """
    Vérifie que Celery Beat est actif
    Envoie une alerte si aucun cycle de compostage n'a été exécuté récemment
    """
    from core.models.saka import SakaCompostLog
    
    # Vérifier si un compostage a eu lieu dans les 8 derniers jours
    # (normalement tous les lundis, donc max 7 jours)
    cutoff = timezone.now() - timedelta(days=8)
    recent_composts = SakaCompostLog.objects.filter(created_at__gte=cutoff).count()
    
    if recent_composts == 0:
        # Aucun compostage récent, alerter
        logger.error("[ALERTE] Aucun compostage détecté depuis 8 jours. Celery Beat peut être inactif.")
        
        # Envoyer un email d'alerte si configuré
        if hasattr(settings, 'NOTIFY_EMAIL') and settings.NOTIFY_EMAIL:
            send_mail(
                subject='[EGOEJO] Alerte : Celery Beat peut être inactif',
                message='Aucun compostage SAKA détecté depuis 8 jours. Vérifier que Celery Beat est actif.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.NOTIFY_EMAIL],
                fail_silently=True,
            )
        
        return {
            'status': 'error',
            'message': 'Aucun compostage détecté depuis 8 jours',
            'action_required': 'Vérifier Celery Beat',
        }
    
    return {
        'status': 'ok',
        'message': f'{recent_composts} compostage(s) détecté(s) récemment',
    }


@shared_task(bind=True, name='core.tasks.check_compost_failures')
def check_compost_failures(self):
    """
    Vérifie les échecs de compostage
    Envoie une alerte si des erreurs sont détectées dans les logs
    """
    # Cette tâche devrait être exécutée après chaque cycle de compostage
    # Pour l'instant, on vérifie juste que le dernier cycle s'est bien passé
    # (à améliorer avec un système de logs structurés)
    
    from core.models.saka import SakaCompostLog
    from core.services.saka_metrics import get_compost_metrics
    
    metrics = get_compost_metrics(days=7)
    
    # Si aucun compostage dans les 7 derniers jours mais des wallets éligibles
    if metrics['compost_count'] == 0 and metrics['eligible_wallets'] > 0:
        logger.warning(f"[ALERTE] {metrics['eligible_wallets']} wallets éligibles mais aucun compostage dans les 7 derniers jours")
        
        if hasattr(settings, 'NOTIFY_EMAIL') and settings.NOTIFY_EMAIL:
            send_mail(
                subject='[EGOEJO] Alerte : Compostage non exécuté',
                message=f"{metrics['eligible_wallets']} wallets éligibles au compostage mais aucun cycle exécuté récemment.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.NOTIFY_EMAIL],
                fail_silently=True,
            )
        
        return {
            'status': 'warning',
            'message': f"{metrics['eligible_wallets']} wallets éligibles mais aucun compostage",
            'action_required': 'Vérifier les logs de compostage',
        }
    
    return {
        'status': 'ok',
        'message': f"{metrics['compost_count']} compostage(s) dans les 7 derniers jours",
    }


@shared_task(bind=True, name='core.tasks.check_redis_health')
def check_redis_health(self):
    """
    Vérifie que Redis est accessible
    Envoie une alerte si Redis n'est pas accessible
    """
    from django.core.cache import cache
    
    try:
        # Tester la connexion Redis
        cache.set('health_check', 'ok', 10)
        result = cache.get('health_check')
        
        if result != 'ok':
            raise Exception("Redis ne répond pas correctement")
        
        return {
            'status': 'ok',
            'message': 'Redis est accessible',
        }
    except Exception as e:
        logger.error(f"[ALERTE] Redis non accessible: {e}")
        
        if hasattr(settings, 'NOTIFY_EMAIL') and settings.NOTIFY_EMAIL:
            send_mail(
                subject='[EGOEJO] Alerte : Redis non accessible',
                message=f'Redis n\'est pas accessible: {e}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.NOTIFY_EMAIL],
                fail_silently=True,
            )
        
        return {
            'status': 'error',
            'message': f'Redis non accessible: {e}',
            'action_required': 'Vérifier la configuration Redis',
        }


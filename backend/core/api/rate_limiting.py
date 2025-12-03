"""
Rate limiting par IP pour protection contre les attaques DDoS
"""
from django.core.cache import cache
from rest_framework.throttling import BaseThrottle
from rest_framework.exceptions import Throttled
import time


class IPRateThrottle(BaseThrottle):
    """
    Rate limiting par IP pour protéger contre les attaques DDoS
    """
    scope = 'ip'
    cache_format = 'throttle_ip_{scope}_{ident}'
    
    def __init__(self):
        self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)
    
    def get_rate(self):
        """
        Retourne le taux de limitation depuis les settings
        """
        from django.conf import settings
        return getattr(settings, 'REST_FRAMEWORK', {}).get(
            'DEFAULT_THROTTLE_RATES', {}
        ).get(self.scope, '100/hour')
    
    def parse_rate(self, rate):
        """
        Parse le taux (ex: '100/hour' -> (100, 3600))
        """
        if '/' not in rate:
            return (None, None)
        num, period = rate.split('/')
        num_requests = int(num)
        duration = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400,
        }.get(period[0], 1)
        return (num_requests, duration)
    
    def get_cache_key(self, request, view):
        """
        Génère une clé de cache unique pour l'IP
        """
        ident = self.get_ident(request)
        return self.cache_format.format(
            scope=self.scope,
            ident=ident
        )
    
    def get_ident(self, request):
        """
        Identifie l'IP de la requête
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def allow_request(self, request, view):
        """
        Vérifie si la requête est autorisée
        """
        if self.rate is None:
            return True
        
        key = self.get_cache_key(request, view)
        
        # Récupérer l'historique des requêtes
        history = cache.get(key, [])
        now = time.time()
        
        # Nettoyer les requêtes expirées
        while history and history[-1] <= now - self.duration:
            history.pop()
        
        # Vérifier si on a dépassé la limite
        if len(history) >= self.num_requests:
            return False
        
        # Ajouter la requête actuelle
        history.insert(0, now)
        cache.set(key, history, self.duration)
        return True
    
    def wait(self):
        """
        Retourne le temps d'attente en secondes
        """
        return self.duration


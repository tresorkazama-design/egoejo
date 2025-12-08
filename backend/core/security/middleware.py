"""
Middleware de sécurité renforcée
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from django.conf import settings

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Ajoute des headers de sécurité supplémentaires
    """
    
    def process_response(self, request, response):
        """
        Ajoute les headers de sécurité à la réponse
        """
        # X-Content-Type-Options: empêche le MIME-sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options: empêche le clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # X-XSS-Protection: protection XSS (obsolète mais toujours utile)
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer-Policy: contrôle les informations de referrer
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions-Policy: contrôle les fonctionnalités du navigateur
        response['Permissions-Policy'] = (
            'geolocation=(), '
            'microphone=(), '
            'camera=(), '
            'payment=(), '
            'usb=(), '
            'magnetometer=(), '
            'gyroscope=(), '
            'speaker=()'
        )
        
        # Content-Security-Policy (si non déjà défini par CSP middleware)
        if 'Content-Security-Policy' not in response:
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # À restreindre en production
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "upgrade-insecure-requests;"
            )
            response['Content-Security-Policy'] = csp
        
        # Strict-Transport-Security (HSTS) - seulement en HTTPS
        if not settings.DEBUG and request.is_secure():
            response['Strict-Transport-Security'] = (
                f'max-age={settings.SECURE_HSTS_SECONDS}; '
                'includeSubDomains; '
                'preload'
            )
        
        return response


class DataProtectionMiddleware(MiddlewareMixin):
    """
    Middleware pour protéger les données sensibles dans les logs
    """
    
    SENSITIVE_FIELDS = [
        'password', 'token', 'secret', 'api_key', 'apikey',
        'authorization', 'credit_card', 'ssn', 'email',
        'phone', 'address', 'ip_address'
    ]
    
    def process_request(self, request):
        """
        Masque les données sensibles dans les logs
        """
        # Ne pas logger les données sensibles
        if hasattr(request, 'body'):
            try:
                import json
                data = json.loads(request.body.decode('utf-8'))
                masked_data = self._mask_sensitive_data(data)
                request._masked_body = json.dumps(masked_data).encode('utf-8')
            except:
                pass
        
        return None
    
    def _mask_sensitive_data(self, data):
        """
        Masque les données sensibles dans un dictionnaire
        """
        if isinstance(data, dict):
            masked = {}
            for key, value in data.items():
                key_lower = key.lower()
                if any(sensitive in key_lower for sensitive in self.SENSITIVE_FIELDS):
                    masked[key] = '***MASKED***'
                elif isinstance(value, (dict, list)):
                    masked[key] = self._mask_sensitive_data(value)
                else:
                    masked[key] = value
            return masked
        elif isinstance(data, list):
            return [self._mask_sensitive_data(item) for item in data]
        else:
            return data


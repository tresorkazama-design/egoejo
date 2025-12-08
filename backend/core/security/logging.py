"""
Logging sécurisé - masque les données sensibles
"""
import logging
import re
from django.conf import settings


class SecureFormatter(logging.Formatter):
    """
    Formatter qui masque les données sensibles dans les logs
    """
    
    SENSITIVE_PATTERNS = [
        (r'password["\']?\s*[:=]\s*["\']?([^"\'\s]+)', r'password": "***MASKED***"'),
        (r'token["\']?\s*[:=]\s*["\']?([^"\'\s]+)', r'token": "***MASKED***"'),
        (r'secret["\']?\s*[:=]\s*["\']?([^"\'\s]+)', r'secret": "***MASKED***"'),
        (r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\'\s]+)', r'api_key": "***MASKED***"'),
        (r'authorization["\']?\s*[:=]\s*["\']?Bearer\s+([^\s"\']+)', r'authorization": "Bearer ***MASKED***"'),
        (r'email["\']?\s*[:=]\s*["\']?([^"\'\s@]+)@', r'email": "***@***'),
    ]
    
    def format(self, record):
        """
        Formate le message en masquant les données sensibles
        """
        # Formater normalement
        message = super().format(record)
        
        # Masquer les données sensibles
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
        
        return message


def configure_secure_logging():
    """
    Configure le logging avec masquage des données sensibles
    """
    # Récupérer le handler console
    root_logger = logging.getLogger()
    
    for handler in root_logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            # Remplacer le formatter par le formatter sécurisé
            handler.setFormatter(SecureFormatter(
                fmt='{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                style='{',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))


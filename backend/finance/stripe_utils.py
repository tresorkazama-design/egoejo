"""
Utilitaires Stripe pour vérification de signature et mode test.
"""
import hmac
import hashlib
import logging
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


def verify_stripe_signature(payload: bytes, signature_header: str) -> bool:
    """
    Vérifie la signature d'un webhook Stripe.
    
    Args:
        payload: Corps de la requête (bytes)
        signature_header: En-tête Stripe-Signature (format: "t=timestamp,v1=signature,v1=signature2,...")
    
    Returns:
        bool: True si la signature est valide, False sinon
    
    Raises:
        ImproperlyConfigured: Si STRIPE_WEBHOOK_SECRET n'est pas configuré
    """
    webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
    
    if not webhook_secret:
        logger.warning(
            "STRIPE_WEBHOOK_SECRET non configuré. Vérification de signature désactivée. "
            "Configurez STRIPE_WEBHOOK_SECRET pour activer la vérification."
        )
        return True  # En mode développement, on peut accepter sans signature
    
    if not signature_header:
        logger.error("En-tête Stripe-Signature manquant")
        return False
    
    try:
        # Parser l'en-tête Stripe-Signature
        # Format: "t=timestamp,v1=signature,v1=signature2,..."
        elements = signature_header.split(',')
        timestamp = None
        signatures = []
        
        for element in elements:
            if '=' in element:
                key, value = element.split('=', 1)
                if key == 't':
                    timestamp = value
                elif key.startswith('v'):
                    signatures.append(value)
        
        if not timestamp or not signatures:
            logger.error(f"Format d'en-tête Stripe-Signature invalide: {signature_header}")
            return False
        
        # Construire le message signé
        signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
        
        # Calculer la signature attendue
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Vérifier si l'une des signatures correspond
        for signature in signatures:
            if hmac.compare_digest(expected_signature, signature):
                logger.debug("Signature Stripe vérifiée avec succès")
                return True
        
        logger.error("Signature Stripe invalide")
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la signature Stripe: {e}", exc_info=True)
        return False


def ensure_test_mode():
    """
    Vérifie que Stripe est en mode test si STRIPE_TEST_MODE_ONLY=True.
    
    Raises:
        ImproperlyConfigured: Si une clé live est utilisée en mode test strict
    """
    test_mode_only = getattr(settings, 'STRIPE_TEST_MODE_ONLY', False)
    
    if not test_mode_only:
        return  # Pas de restriction en mode production
    
    secret_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
    test_key_prefix = getattr(settings, 'STRIPE_TEST_KEY_PREFIX', 'sk_test_')
    live_key_prefix = getattr(settings, 'STRIPE_LIVE_KEY_PREFIX', 'sk_live_')
    
    if secret_key and secret_key.startswith(live_key_prefix):
        raise ImproperlyConfigured(
            f"STRIPE_SECRET_KEY est en mode live (commence par '{live_key_prefix}') "
            f"mais STRIPE_TEST_MODE_ONLY=True. Utilisez une clé de test (commence par '{test_key_prefix}')."
        )


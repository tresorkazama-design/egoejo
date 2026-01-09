"""
Client HelloAsso (mode simulé pour tests CI).

Interface injectable/mockable pour éviter dépendance réseau externe en CI.
"""
import logging
from typing import Optional, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class HelloAssoClient:
    """
    Client HelloAsso avec interface injectable/mockable.
    
    En mode simulé, toutes les méthodes retournent des réponses mockées
    sans appels réseau réels.
    """
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """
        Initialise le client HelloAsso.
        
        Args:
            client_id: Client ID HelloAsso (optionnel, depuis settings si non fourni)
            client_secret: Client Secret HelloAsso (optionnel, depuis settings si non fourni)
        """
        self.client_id = client_id or getattr(settings, 'HELLOASSO_CLIENT_ID', '')
        self.client_secret = client_secret or getattr(settings, 'HELLOASSO_CLIENT_SECRET', '')
        self._access_token: Optional[str] = None
        self._simulated_mode = getattr(settings, 'HELLOASSO_SIMULATED_MODE', True)
    
    def get_access_token(self) -> str:
        """
        Obtient un token OAuth HelloAsso.
        
        En mode simulé, retourne un token mocké.
        
        Returns:
            str: Token d'accès OAuth
        
        Raises:
            ValueError: Si les credentials sont manquants
        """
        if not self.client_id or not self.client_secret:
            raise ValueError("HELLOASSO_CLIENT_ID et HELLOASSO_CLIENT_SECRET doivent être configurés")
        
        if self._simulated_mode:
            # Mode simulé : retourner un token mocké
            logger.debug("Mode simulé HelloAsso : token mocké retourné")
            self._access_token = "mock_helloasso_token_simulated"
            return self._access_token
        
        # Mode réel : appeler l'API HelloAsso OAuth
        # TODO: Implémenter l'appel réel si nécessaire
        raise NotImplementedError("Mode réel HelloAsso non implémenté (mode simulé uniquement)")
    
    def create_payment_form(
        self,
        amount: float,
        user_id: int,
        project_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Crée un formulaire de paiement HelloAsso.
        
        En mode simulé, retourne une URL mockée.
        
        Args:
            amount: Montant en euros
            user_id: ID utilisateur
            project_id: ID projet (optionnel)
            metadata: Métadonnées supplémentaires (optionnel)
        
        Returns:
            dict: {
                'payment_form_url': str,
                'payment_form_id': str,
                'expires_at': str (ISO-8601)
            }
        
        Raises:
            ValueError: Si les paramètres sont invalides
        """
        if amount <= 0:
            raise ValueError("Le montant doit être strictement positif")
        
        if self._simulated_mode:
            # Mode simulé : retourner une URL mockée
            logger.debug(f"Mode simulé HelloAsso : formulaire de paiement créé (montant: {amount}€)")
            return {
                'payment_form_url': f"https://simulated.helloasso.com/payment/mock_{user_id}_{project_id or 'none'}",
                'payment_form_id': f"mock_form_{user_id}_{project_id or 'none'}",
                'expires_at': "2025-12-31T23:59:59Z"  # Date mockée
            }
        
        # Mode réel : appeler l'API HelloAsso
        # TODO: Implémenter l'appel réel si nécessaire
        raise NotImplementedError("Mode réel HelloAsso non implémenté (mode simulé uniquement)")
    
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature_header: str
    ) -> bool:
        """
        Vérifie la signature d'un webhook HelloAsso.
        
        HelloAsso utilise un header "X-HelloAsso-Signature" avec un secret partagé.
        Format : HMAC-SHA256 du payload avec le secret.
        
        Args:
            payload: Corps de la requête (bytes)
            signature_header: En-tête X-HelloAsso-Signature
        
        Returns:
            bool: True si la signature est valide, False sinon
        """
        webhook_secret = getattr(settings, 'HELLOASSO_WEBHOOK_SECRET', '')
        
        if not webhook_secret:
            logger.warning(
                "HELLOASSO_WEBHOOK_SECRET non configuré. Vérification de signature désactivée. "
                "Configurez HELLOASSO_WEBHOOK_SECRET pour activer la vérification."
            )
            return True  # En mode développement, on peut accepter sans signature
        
        if not signature_header:
            logger.error("En-tête X-HelloAsso-Signature manquant")
            return False
        
        try:
            import hmac
            import hashlib
            
            # Calculer la signature attendue
            expected_signature = hmac.new(
                webhook_secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            # Comparer avec la signature fournie
            if hmac.compare_digest(expected_signature, signature_header):
                logger.debug("Signature HelloAsso vérifiée avec succès")
                return True
            
            logger.error("Signature HelloAsso invalide")
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la signature HelloAsso: {e}", exc_info=True)
            return False


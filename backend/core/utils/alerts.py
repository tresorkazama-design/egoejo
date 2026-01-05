"""
Système d'alerte critique EGOEJO avec dédoublonnage et payload structuré.

Ce module centralise l'envoi d'alertes critiques par email et webhook avec :
- Dédoublonnage via cache (5 minutes)
- Payload structuré JSON
- Gestion robuste des erreurs SMTP et réseau
- Support webhook optionnel (generic, Slack)
- Configuration via variables d'environnement
"""
import json
import logging
from typing import Dict, Optional, Any
from django.core.cache import cache
from django.core.mail import mail_admins
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# Durée de dédoublonnage (5 minutes)
DEDUPE_CACHE_TTL = 300  # 5 minutes en secondes

# Import conditionnel pour requêtes HTTP (webhook)
try:
    import requests
    from requests.exceptions import Timeout, RequestException, ConnectionError as RequestsConnectionError
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    Timeout = None
    RequestException = None
    RequestsConnectionError = None
    logger.warning("Module 'requests' non disponible. Support webhook désactivé.")


def send_critical_alert(
    title: str,
    payload: Dict[str, Any],
    *,
    dedupe_key: Optional[str] = None,
    subject_prefix: Optional[str] = None
) -> bool:
    """
    Envoie une alerte critique par email aux administrateurs.
    
    Args:
        title: Titre de l'alerte (utilisé dans le sujet de l'email)
        payload: Dictionnaire contenant les données structurées de l'alerte
        dedupe_key: Clé de dédoublonnage (optionnel). Si fournie, l'alerte
                    ne sera envoyée qu'une fois toutes les 5 minutes pour cette clé.
        subject_prefix: Préfixe du sujet (optionnel). Par défaut : "[URGENT] EGOEJO"
    
    Returns:
        bool: True si l'email a été envoyé (ou était déjà envoyé récemment),
              False si l'envoi a échoué ou si les alertes sont désactivées.
    
    Exemple:
        send_critical_alert(
            "SAKA WALLET INCONSISTENCY DETECTED",
            {
                "user_id": 123,
                "username": "testuser",
                "old_balance": 1000,
                "new_balance": 2000,
                "delta": 1000,
                "detection_method": "post_save_signal"
            },
            dedupe_key="saka_wallet:123"
        )
    """
    # Vérifier si les alertes sont activées
    alert_enabled = getattr(settings, 'ALERT_EMAIL_ENABLED', True)
    if not alert_enabled:
        logger.debug(f"Alertes email désactivées. Alerte '{title}' ignorée.")
        return False
    
    # Vérifier si des admins sont configurés
    if not getattr(settings, 'ADMINS', []):
        logger.warning(
            f"Aucun admin configuré (ADMINS vide). Alerte '{title}' non envoyée. "
            "Configurez ADMINS dans settings.py ou via variable d'environnement."
        )
        return False
    
    # Dédoublonnage via cache
    if dedupe_key:
        cache_key = f"critical_alert:{dedupe_key}"
        if cache.get(cache_key):
            logger.debug(
                f"Alerte '{title}' (dedupe_key: {dedupe_key}) déjà envoyée récemment. "
                "Ignorée pour éviter le spam."
            )
            return True  # Considéré comme "succès" car l'alerte a déjà été envoyée
    
    # Construire le sujet de l'email
    prefix = subject_prefix or getattr(settings, 'ALERT_EMAIL_SUBJECT_PREFIX', '[URGENT] EGOEJO')
    subject = f"{prefix} {title}"
    
    # Construire le message structuré
    message_lines = [
        f"{title}\n",
        "=" * 80,
        "",
        "PAYLOAD STRUCTURÉ (JSON):",
        json.dumps(payload, indent=2, ensure_ascii=False),
        "",
        "=" * 80,
        "",
        "DÉTAILS LISIBLES:",
    ]
    
    # Ajouter les détails lisibles depuis le payload
    for key, value in payload.items():
        if isinstance(value, (dict, list)):
            message_lines.append(f"{key}: {json.dumps(value, indent=2, ensure_ascii=False)}")
        else:
            message_lines.append(f"{key}: {value}")
    
    message_lines.extend([
        "",
        "=" * 80,
        f"Timestamp: {timezone.now().isoformat()}",
        f"Dedupe Key: {dedupe_key or 'N/A'}",
    ])
    
    message = "\n".join(message_lines)
    
    # Envoyer l'email
    try:
        mail_admins(
            subject=subject,
            message=message,
            fail_silently=False,  # Lever une exception si l'envoi échoue
        )
        
        # Marquer comme envoyé dans le cache (dédoublonnage)
        if dedupe_key:
            cache.set(cache_key, True, DEDUPE_CACHE_TTL)
        
        logger.info(f"Alerte critique envoyée: {title} (dedupe_key: {dedupe_key or 'N/A'})")
        
        # Envoyer également via webhook si activé (non-bloquant, ne bloque pas le flux)
        webhook_sent = send_webhook_alert(title, payload, dedupe_key=dedupe_key)
        
        # Enregistrer l'événement d'alerte critique (uniquement si réellement émis)
        # Déterminer le canal d'envoi
        if webhook_sent:
            channel = 'both'  # Email + Webhook
        else:
            channel = 'email'  # Email uniquement
        
        # Générer un fingerprint si non fourni
        event_fingerprint = dedupe_key or f"{title}:{timezone.now().isoformat()}"
        
        # Enregistrer l'événement (non-bloquant, ne doit pas casser le flux)
        try:
            from core.models.alerts import CriticalAlertEvent
            CriticalAlertEvent.create_from_alert(
                title=title,
                payload=payload,
                channel=channel,
                fingerprint=event_fingerprint,
                severity='critical'
            )
        except Exception as e:
            # Logger l'erreur mais ne pas bloquer le flux
            logger.warning(
                f"Échec enregistrement CriticalAlertEvent pour '{title}': {e}",
                exc_info=True
            )
        
        return True
        
    except Exception as e:
        # Logger l'erreur mais ne pas bloquer l'application
        logger.error(
            f"Échec envoi email alerte critique '{title}': {e}",
            exc_info=True
        )
        
        # Envoyer quand même via webhook si activé (non-bloquant, ne bloque pas le flux)
        send_webhook_alert(title, payload, dedupe_key=dedupe_key)
        
        return False


def send_webhook_alert(
    title: str,
    payload: Dict[str, Any],
    *,
    dedupe_key: Optional[str] = None
) -> bool:
    """
    Envoie une alerte critique via webhook (optionnel).
    
    Supporte les formats :
    - generic : Payload JSON brut
    - slack : Format Slack avec blocks et JSON en pièce jointe
    
    Args:
        title: Titre de l'alerte
        payload: Dictionnaire contenant les données structurées de l'alerte
        dedupe_key: Clé de dédoublonnage (optionnel)
    
    Returns:
        bool: True si le webhook a été envoyé avec succès, False sinon.
    
    Fail-safe : Toute erreur réseau ne bloque pas le flux, mais log un warning structuré.
    """
    # Vérifier si les webhooks sont activés
    webhook_enabled = getattr(settings, 'ALERT_WEBHOOK_ENABLED', False)
    if not webhook_enabled:
        logger.debug(f"Webhooks désactivés. Alerte '{title}' non envoyée via webhook.")
        return False
    
    # Vérifier si requests est disponible
    if not REQUESTS_AVAILABLE:
        logger.warning(
            f"Module 'requests' non disponible. Webhook '{title}' non envoyé. "
            "Installez 'requests' pour activer le support webhook."
        )
        return False
    
    # Vérifier si l'URL est configurée
    webhook_url = getattr(settings, 'ALERT_WEBHOOK_URL', None)
    if not webhook_url:
        logger.warning(
            f"ALERT_WEBHOOK_URL non configurée. Webhook '{title}' non envoyé."
        )
        return False
    
    # Récupérer le type de webhook (generic ou slack)
    webhook_type = getattr(settings, 'ALERT_WEBHOOK_TYPE', 'generic').lower()
    if webhook_type not in ['generic', 'slack']:
        logger.warning(
            f"ALERT_WEBHOOK_TYPE invalide: '{webhook_type}'. Utilisation de 'generic'."
        )
        webhook_type = 'generic'
    
    # Timeout pour la requête HTTP
    timeout = getattr(settings, 'ALERT_WEBHOOK_TIMEOUT_SECONDS', 5)
    
    # Construire le payload selon le type
    if webhook_type == 'slack':
        webhook_payload = _build_slack_payload(title, payload, dedupe_key)
    else:
        # Format generic : payload JSON brut avec métadonnées
        webhook_payload = {
            'title': title,
            'payload': payload,
            'timestamp': timezone.now().isoformat(),
            'dedupe_key': dedupe_key or None,
            'source': 'egoejo_critical_alert'
        }
    
    # Envoyer le webhook (fail-safe : ne bloque pas le flux)
    try:
        response = requests.post(
            webhook_url,
            json=webhook_payload,
            timeout=timeout,
            headers={'Content-Type': 'application/json'}
        )
        
        # Vérifier le code de statut
        if response.status_code >= 200 and response.status_code < 300:
            logger.info(
                f"Webhook alerte envoyé avec succès: {title} "
                f"(status: {response.status_code}, type: {webhook_type})"
            )
            return True
        else:
            logger.warning(
                f"Webhook alerte échoué: {title} "
                f"(status: {response.status_code}, response: {response.text[:200]})",
                extra={
                    'webhook_url': webhook_url,
                    'webhook_type': webhook_type,
                    'status_code': response.status_code,
                    'response_preview': response.text[:200]
                }
            )
            return False
            
    except Timeout:
        logger.warning(
            f"Webhook alerte timeout: {title} (timeout: {timeout}s)",
            extra={
                'webhook_url': webhook_url,
                'webhook_type': webhook_type,
                'timeout': timeout,
                'error_type': 'timeout'
            }
        )
        return False
        
    except RequestException as e:
        logger.warning(
            f"Webhook alerte erreur réseau: {title} (erreur: {str(e)})",
            extra={
                'webhook_url': webhook_url,
                'webhook_type': webhook_type,
                'error_type': type(e).__name__,
                'error_message': str(e)
            },
            exc_info=True
        )
        return False
        
    except Exception as e:
        # Catch-all pour toute autre erreur inattendue
        logger.warning(
            f"Webhook alerte erreur inattendue: {title} (erreur: {str(e)})",
            extra={
                'webhook_url': webhook_url,
                'webhook_type': webhook_type,
                'error_type': type(e).__name__,
                'error_message': str(e)
            },
            exc_info=True
        )
        return False


def _build_slack_payload(
    title: str,
    payload: Dict[str, Any],
    dedupe_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Construit un payload Slack à partir du titre et du payload JSON.
    
    Format Slack :
    - text : Message principal (fallback)
    - blocks : Sections formatées (si supporté)
    - JSON original en pièce jointe dans une section
    
    Args:
        title: Titre de l'alerte
        payload: Dictionnaire contenant les données structurées
        dedupe_key: Clé de dédoublonnage (optionnel)
    
    Returns:
        dict: Payload Slack formaté
    """
    # Message principal (fallback pour clients Slack simples)
    text = f"🚨 *{title}*\n\n"
    
    # Construire les blocks Slack
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🚨 {title}",
                "emoji": True
            }
        },
        {
            "type": "divider"
        }
    ]
    
    # Section avec les détails principaux
    fields = []
    for key, value in payload.items():
        if key in ['user_id', 'username', 'email', 'old_balance', 'new_balance', 'delta', 'violation_type']:
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value, ensure_ascii=False)
            else:
                value_str = str(value)
            fields.append({
                "type": "mrkdwn",
                "text": f"*{key}:* {value_str}"
            })
    
    if fields:
        blocks.append({
            "type": "section",
            "fields": fields[:10]  # Slack limite à 10 fields par section
        })
    
    # Section avec le JSON complet (pièce jointe)
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*Payload JSON complet:*"
        }
    })
    
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"```{json.dumps(payload, indent=2, ensure_ascii=False)}```"
        }
    })
    
    # Footer avec métadonnées
    footer_text = f"Timestamp: {timezone.now().isoformat()}"
    if dedupe_key:
        footer_text += f" | Dedupe Key: {dedupe_key}"
    
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": footer_text
            }
        ]
    })
    
    return {
        "text": text,  # Fallback pour clients Slack simples
        "blocks": blocks
    }


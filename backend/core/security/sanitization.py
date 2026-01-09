"""
Sanitization et validation des données pour prévenir les injections
"""
import re
import html
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError
import logging

try:
    import bleach
    BLEACH_AVAILABLE = True
except ImportError:
    BLEACH_AVAILABLE = False
    logging.warning("bleach non disponible - sanitization HTML limitée")

logger = logging.getLogger(__name__)


def sanitize_string(value: str, max_length: int = None, allow_html: bool = False) -> str:
    """
    Nettoie une chaîne de caractères pour prévenir les injections XSS
    
    Args:
        value: La chaîne à nettoyer
        max_length: Longueur maximale autorisée
        allow_html: Si True, permet le HTML (sanitize avec bleach)
    
    Returns:
        Chaîne nettoyée
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Supprimer les caractères de contrôle
    value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    
    # Échapper le HTML si non autorisé
    if not allow_html:
        value = html.escape(value)
        # Supprimer les balises HTML restantes
        value = strip_tags(value)
    else:
        # Si HTML autorisé, utiliser bleach pour sanitization sécurisée
        if BLEACH_AVAILABLE:
            # Tags HTML autorisés (liste minimale sécurisée)
            allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li', 'blockquote', 'code', 'pre']
            allowed_attributes = {
                'a': ['href', 'title'],
            }
            value = bleach.clean(
                value,
                tags=allowed_tags,
                attributes=allowed_attributes,
                strip=True
            )
        else:
            # Fallback : échapper tout le HTML si bleach non disponible
            logger.warning("bleach non disponible, HTML échappé au lieu d'être sanitizé")
            value = html.escape(value)
            value = strip_tags(value)
    
    # Limiter la longueur
    if max_length and len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"Chaîne tronquée à {max_length} caractères")
    
    return value.strip()


def sanitize_html(value: str, max_length: int = None) -> str:
    """
    Sanitize du HTML avec bleach (tags et attributs autorisés uniquement).
    
    Args:
        value: Le HTML à sanitizer
        max_length: Longueur maximale autorisée
    
    Returns:
        HTML sanitizé
    """
    if not isinstance(value, str):
        value = str(value)
    
    if BLEACH_AVAILABLE:
        # Tags HTML autorisés (liste minimale sécurisée)
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li', 'blockquote', 'code', 'pre']
        allowed_attributes = {
            'a': ['href', 'title'],
        }
        value = bleach.clean(
            value,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
    else:
        # Fallback : échapper tout le HTML si bleach non disponible
        logger.warning("bleach non disponible, HTML échappé au lieu d'être sanitizé")
        value = html.escape(value)
        value = strip_tags(value)
    
    # Limiter la longueur
    if max_length and len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"HTML tronqué à {max_length} caractères")
    
    return value.strip()


def sanitize_email(email: str) -> str:
    """
    Nettoie et valide un email
    """
    if not email:
        raise ValidationError("L'email est requis")
    
    email = email.strip().lower()
    
    # Validation basique du format email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValidationError("Format d'email invalide")
    
    # Limiter la longueur
    if len(email) > 254:  # RFC 5321
        raise ValidationError("L'email est trop long")
    
    return email


def sanitize_url(url: str) -> str:
    """
    Nettoie et valide une URL
    """
    if not url:
        return url
    
    url = url.strip()
    
    # Vérifier que c'est une URL valide
    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if not re.match(url_pattern, url):
        raise ValidationError("Format d'URL invalide")
    
    # Vérifier les schémas autorisés
    if not url.startswith(('http://', 'https://')):
        raise ValidationError("Seules les URLs HTTP/HTTPS sont autorisées")
    
    return url


def sanitize_phone(phone: str) -> str:
    """
    Nettoie et valide un numéro de téléphone
    """
    if not phone:
        return phone
    
    # Supprimer tous les caractères non numériques sauf + au début
    phone = re.sub(r'[^\d+]', '', phone)
    
    # Vérifier la longueur (entre 10 et 15 chiffres)
    digits = re.sub(r'[^\d]', '', phone)
    if len(digits) < 10 or len(digits) > 15:
        raise ValidationError("Numéro de téléphone invalide")
    
    return phone


def prevent_sql_injection(value: str) -> str:
    """
    Vérifie et prévient les injections SQL basiques
    """
    if not isinstance(value, str):
        return value
    
    # Mots-clés SQL dangereux
    dangerous_patterns = [
        r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION|SCRIPT)\b)',
        r'(\b(OR|AND)\s+\d+\s*=\s*\d+)',
        r'(\b(OR|AND)\s+[\'"][^\'"]*[\'"]\s*=\s*[\'"][^\'"]*[\'"])',
        r'(\b(OR|AND)\s+[\'"][^\'"]*[\'"]\s*=\s*[\'"][^\'"]*[\'"])',
        r'(\b(OR|AND)\s+[\'"][^\'"]*[\'"]\s*LIKE\s*[\'"][^\'"]*[\'"])',
        r'(\b(OR|AND)\s+[\'"][^\'"]*[\'"]\s*IN\s*\([^)]*\))',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            logger.warning(f"Tentative d'injection SQL détectée: {value[:50]}")
            raise ValidationError("Caractères non autorisés détectés")
    
    return value


def sanitize_input(data: dict, fields_config: dict) -> dict:
    """
    Nettoie un dictionnaire de données selon une configuration
    
    Args:
        data: Dictionnaire de données à nettoyer
        fields_config: Configuration des champs
            Exemple: {
                'name': {'type': 'string', 'max_length': 100},
                'email': {'type': 'email'},
                'url': {'type': 'url'},
            }
    
    Returns:
        Dictionnaire nettoyé
    """
    cleaned_data = {}
    
    for field, config in fields_config.items():
        if field not in data:
            continue
        
        value = data[field]
        field_type = config.get('type', 'string')
        
        try:
            if field_type == 'string':
                cleaned_data[field] = sanitize_string(
                    value,
                    max_length=config.get('max_length'),
                    allow_html=config.get('allow_html', False)
                )
            elif field_type == 'email':
                cleaned_data[field] = sanitize_email(value)
            elif field_type == 'url':
                cleaned_data[field] = sanitize_url(value)
            elif field_type == 'phone':
                cleaned_data[field] = sanitize_phone(value)
            else:
                # Par défaut, sanitize comme string
                cleaned_data[field] = sanitize_string(str(value))
        except ValidationError as e:
            logger.warning(f"Erreur de validation pour {field}: {e}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors de la sanitization de {field}: {e}")
            raise ValidationError(f"Erreur de validation pour {field}")
    
    return cleaned_data


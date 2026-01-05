"""
Endpoints publics pour la Constitution EGOEJO.

Ces endpoints exposent publiquement le statut de conformité constitutionnelle
basé sur un rapport d'audit signé généré par CI/CD.
"""

import json
import hashlib
import hmac
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

# Chemin par défaut du rapport de compliance (peut être surchargé via settings)
COMPLIANCE_REPORT_PATH = getattr(
    settings,
    'COMPLIANCE_REPORT_PATH',
    Path(__file__).parent.parent.parent.parent / 'compliance_report.json'
)

# Clé secrète pour vérifier la signature (doit correspondre à celle utilisée en CI)
COMPLIANCE_SIGNATURE_SECRET = os.environ.get(
    'COMPLIANCE_SIGNATURE_SECRET',
    getattr(settings, 'COMPLIANCE_SIGNATURE_SECRET', None)
)

# Durée maximale de validité du rapport (24 heures)
MAX_REPORT_AGE_HOURS = 24


def _compute_hmac_sha256(data: str, secret: str) -> str:
    """
    Calcule le HMAC-SHA256 d'une chaîne avec une clé secrète.
    
    Args:
        data: Données à signer
        secret: Clé secrète
        
    Returns:
        str: Signature hexadécimale
    """
    return hmac.new(
        secret.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def _verify_signature(report_data: dict, signature: str) -> bool:
    """
    Vérifie la signature d'un rapport de compliance.
    
    Args:
        report_data: Données du rapport (sans le champ 'signature')
        signature: Signature à vérifier
        
    Returns:
        bool: True si la signature est valide, False sinon
    """
    if not COMPLIANCE_SIGNATURE_SECRET:
        logger.warning("COMPLIANCE_SIGNATURE_SECRET non configurée. Signature non vérifiée.")
        return False
    
    # Créer une copie sans le champ signature pour recalculer
    data_to_sign = {k: v for k, v in report_data.items() if k != 'signature'}
    data_json = json.dumps(data_to_sign, sort_keys=True, ensure_ascii=False)
    
    expected_signature = _compute_hmac_sha256(data_json, COMPLIANCE_SIGNATURE_SECRET)
    
    # Comparaison sécurisée pour éviter les attaques par timing
    return hmac.compare_digest(expected_signature, signature)


def _load_compliance_report() -> dict:
    """
    Charge le rapport de compliance depuis le fichier.
    
    Returns:
        dict: Rapport de compliance ou None si erreur
    """
    try:
        report_path = Path(COMPLIANCE_REPORT_PATH)
        
        if not report_path.exists():
            logger.warning(f"Rapport de compliance non trouvé: {report_path}")
            return None
        
        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        return report
        
    except json.JSONDecodeError as e:
        logger.error(f"Erreur de parsing JSON du rapport de compliance: {e}")
        return None
    except Exception as e:
        logger.error(f"Erreur lors du chargement du rapport de compliance: {e}")
        return None


def _check_report_freshness(report: dict) -> bool:
    """
    Vérifie que le rapport n'est pas trop ancien (> 24h).
    
    Args:
        report: Rapport de compliance
        
    Returns:
        bool: True si le rapport est frais, False sinon
    """
    if 'last_check' not in report:
        logger.warning("Rapport de compliance sans champ 'last_check'")
        return False
    
    try:
        last_check = datetime.fromisoformat(report['last_check'].replace('Z', '+00:00'))
        if last_check.tzinfo is None:
            # Si pas de timezone, assumer UTC
            last_check = last_check.replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        age = now - last_check
        
        if age > timedelta(hours=MAX_REPORT_AGE_HOURS):
            logger.warning(
                f"Rapport de compliance trop ancien: {age.total_seconds() / 3600:.1f} heures "
                f"(max: {MAX_REPORT_AGE_HOURS}h)"
            )
            return False
        
        return True
        
    except (ValueError, KeyError) as e:
        logger.error(f"Erreur lors de la vérification de la fraîcheur du rapport: {e}")
        return False


def _determine_compliance_status(report: dict) -> str:
    """
    Détermine le statut de conformité à partir du rapport.
    
    IMPORTANT: Cette fonction ne renvoie JAMAIS "compliant" si :
    - Le rapport est absent
    - La signature est invalide
    - Le rapport est vieux de > 24h
    
    Args:
        report: Rapport de compliance
        
    Returns:
        str: 'compliant', 'non-compliant', ou 'unknown'
    """
    if not report:
        logger.warning("Rapport de compliance absent")
        return 'unknown'
    
    # Vérifier la signature EN PREMIER (sécurité critique)
    if 'signature' not in report:
        logger.warning("Rapport de compliance sans signature")
        return 'unknown'
    
    if not _verify_signature(report, report['signature']):
        logger.warning("Signature du rapport de compliance invalide")
        return 'unknown'
    
    # Vérifier la fraîcheur (doit être < 24h)
    if not _check_report_freshness(report):
        logger.warning("Rapport de compliance trop ancien (> 24h)")
        return 'unknown'
    
    # Vérifier le statut
    status = report.get('status', 'unknown')
    
    # Ne renvoyer "compliant" que si toutes les vérifications sont passées
    if status == 'compliant':
        return 'compliant'
    elif status == 'non-compliant':
        return 'non-compliant'
    else:
        return 'unknown'


@require_http_methods(["GET"])
def egoejo_constitution_status(request):
    """
    Endpoint public pour exposer le statut de conformité constitutionnelle EGOEJO.
    
    GET /api/public/egoejo-constitution.json
    
    Spécifications :
    {
      "status": "compliant" | "non-compliant" | "unknown",
      "version": "1.0.0",
      "last_check": "ISO-8601",
      "checks": {
        "saka_separation": true,
        "anti_accumulation": true,
        ...
      },
      "proof_hash": "SHA256"
    }
    
    Contraintes :
    - Ne renvoie JAMAIS "compliant" si le rapport est vieux de > 24h
    - Ne renvoie JAMAIS "compliant" si la signature est invalide
    - Lecture seule (GET uniquement)
    - Accessible sans authentification
    
    Returns:
        JsonResponse: Statut de conformité constitutionnelle au format JSON
    """
    # Charger le rapport (toujours vérifier, pas de cache pour la sécurité)
    report = _load_compliance_report()
    
    # Déterminer le statut (vérifications critiques : signature + fraîcheur)
    status = _determine_compliance_status(report)
    
    # Clé de cache pour cet endpoint (mais seulement si statut valide)
    cache_key = "egoejo_constitution_status_json"
    
    # Vérifier le cache UNIQUEMENT si le statut est valide (sécurité)
    # Ne jamais utiliser le cache si le rapport est invalide ou trop ancien
    if status == 'compliant':
        cached_response = cache.get(cache_key)
        if cached_response is not None and cached_response.get('status') == 'compliant':
            # Double vérification : s'assurer que le cache n'est pas obsolète
            # (défense en profondeur)
            response = JsonResponse(
                cached_response,
                json_dumps_params={"indent": 2, "ensure_ascii": False}
            )
            response['Cache-Control'] = 'public, max-age=300'  # Cache 5 minutes
            return response
    
    # Construire la réponse
    # IMPORTANT: Ne jamais renvoyer "compliant" si le rapport est invalide ou trop ancien
    if report and status == 'compliant':
        # Vérifications supplémentaires de sécurité
        if not _verify_signature(report, report.get('signature', '')):
            logger.warning("Signature invalide détectée dans la réponse JSON")
            status = 'unknown'
        if not _check_report_freshness(report):
            logger.warning("Rapport trop ancien détecté dans la réponse JSON")
            status = 'unknown'
        
        if status == 'compliant':
            response_data = {
                "status": "compliant",
                "version": report.get("version", "1.0.0"),
                "last_check": report.get("last_check"),
                "checks": report.get("checks", {}),
                "proof_hash": report.get("signature", "")[:16]  # Premiers 16 caractères pour affichage
            }
        else:
            # Double vérification a échoué
            response_data = {
                "status": "unknown",
                "version": report.get("version", "1.0.0"),
                "last_check": report.get("last_check"),
                "checks": {},
                "proof_hash": None,
                "error": "Rapport de compliance invalide ou trop ancien après vérification"
            }
    else:
        # Rapport absent, invalide, ou trop ancien
        response_data = {
            "status": "unknown",
            "version": "1.0.0",
            "last_check": None,
            "checks": {},
            "proof_hash": None,
            "error": "Rapport de compliance indisponible, invalide, ou trop ancien"
        }
    
    # Mettre en cache UNIQUEMENT si le statut est 'compliant' (sécurité)
    # Ne jamais mettre en cache un statut 'unknown' ou 'non-compliant'
    if status == 'compliant':
        cache.set(cache_key, response_data, timeout=300)
        cache_control = 'public, max-age=300'  # Cache 5 minutes
    else:
        # Ne pas mettre en cache les statuts invalides
        cache_control = 'no-cache, no-store, must-revalidate'  # Pas de cache pour sécurité
    
    response = JsonResponse(
        response_data,
        json_dumps_params={"indent": 2, "ensure_ascii": False}
    )
    response['Cache-Control'] = cache_control
    
    return response


@require_http_methods(["GET"])
def egoejo_constitution_badge(request):
    """
    Endpoint public pour générer le badge SVG de conformité constitutionnelle.
    
    GET /api/public/egoejo-constitution.svg
    
    Contraintes :
    - SVG généré dynamiquement selon le statut de conformité
    - 3 états visuels distincts (compliant=vert, non-compliant=rouge, unknown=orange)
    - Aucun asset externe (tout embarqué dans le SVG)
    - Compatible README GitHub (dimensions standard, lisible)
    
    Accessible sans authentification.
    
    Returns:
        HttpResponse: Badge SVG avec content-type 'image/svg+xml'
    """
    from django.http import HttpResponse
    
    # Clé de cache pour cet endpoint
    cache_key = "egoejo_constitution_badge_svg"
    
    # Charger le rapport et déterminer le statut
    report = _load_compliance_report()
    status = _determine_compliance_status(report)
    
    # Vérifier le cache
    cached_svg = cache.get(f"{cache_key}_{status}")
    if cached_svg is not None:
        response = HttpResponse(cached_svg, content_type='image/svg+xml')
        response['Cache-Control'] = 'public, max-age=300'  # Cache 5 minutes
        response['Content-Type'] = 'image/svg+xml; charset=utf-8'
        return response
    
    # Générer le badge SVG selon le statut
    svg_content = _generate_constitution_badge_svg(status)
    
    # Mettre en cache pour 5 minutes
    cache.set(f"{cache_key}_{status}", svg_content, timeout=300)
    
    response = HttpResponse(svg_content, content_type='image/svg+xml')
    response['Cache-Control'] = 'public, max-age=300'  # Cache 5 minutes
    response['Content-Type'] = 'image/svg+xml; charset=utf-8'
    
    return response


def _generate_constitution_badge_svg(status: str) -> str:
    """
    Génère le badge SVG selon le statut de conformité constitutionnelle.
    
    Args:
        status: Statut de conformité ('compliant', 'non-compliant', 'unknown')
        
    Returns:
        str: Contenu SVG du badge
    """
    # Couleurs selon le statut
    color_map = {
        'compliant': {
            'bg': '#28a745',  # Vert
            'text': '#ffffff',
            'label': 'Constitution'
        },
        'non-compliant': {
            'bg': '#dc3545',  # Rouge
            'text': '#ffffff',
            'label': 'Constitution'
        },
        'unknown': {
            'bg': '#ffc107',  # Orange
            'text': '#000000',
            'label': 'Constitution'
        }
    }
    
    colors = color_map.get(status, color_map['unknown'])
    
    # Texte du badge
    if status == 'compliant':
        message = 'Compliant'
    elif status == 'non-compliant':
        message = 'Non-Compliant'
    else:
        message = 'Unknown'
    
    # Dimensions standard pour README GitHub
    label_width = 90
    message_width = 100
    total_width = label_width + message_width
    height = 20
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{height}" role="img" aria-label="EGOEJO Constitution: {message}">
  <title>EGOEJO Constitution: {message}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{total_width}" height="{height}" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_width}" height="{height}" fill="#555"/>
    <rect x="{label_width}" width="{message_width}" height="{height}" fill="{colors['bg']}"/>
    <rect width="{total_width}" height="{height}" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="{label_width / 2}" y="15" fill="#fff">{colors['label']}</text>
    <text x="{label_width + message_width / 2}" y="15" fill="{colors['text']}">{message}</text>
  </g>
</svg>'''
    
    return svg


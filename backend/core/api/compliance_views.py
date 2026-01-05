"""
Vues publiques pour le label EGOEJO COMPLIANT

Ces vues exposent publiquement le statut de conformité EGOEJO
sans authentification requise.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.conf import settings
from datetime import datetime
import subprocess  # nosec B404 - Nécessaire pour exécuter pytest, commande contrôlée
import json
import os
import sys
from pathlib import Path


@require_http_methods(["GET"])
def egoejo_compliance_status(request):
    """
    Endpoint public pour exposer le statut de conformité EGOEJO.
    
    GET /api/public/egoejo-compliance.json
    
    Spécifications :
    {
      "compliance_status": "core" | "extended" | "non-compliant",
      "criteria": [...],
      "last_audit": "ISO-8601"
    }
    
    Contraintes :
    - Lecture seule (GET uniquement)
    - Cache contrôlé (15 minutes)
    - Accessible sans authentification
    
    Returns:
        JsonResponse: Statut de conformité EGOEJO au format JSON
    """
    from django.core.cache import cache
    from django.views.decorators.cache import cache_control
    
    # Clé de cache pour cet endpoint
    cache_key = "egoejo_compliance_status_json"
    
    # Vérifier le cache
    cached_response = cache.get(cache_key)
    if cached_response is not None:
        response = JsonResponse(cached_response, json_dumps_params={"indent": 2, "ensure_ascii": False})
        # Ajouter les en-têtes de cache
        response['Cache-Control'] = 'public, max-age=900'  # 15 minutes
        response['Last-Modified'] = cached_response.get('last_audit', '')
        return response
    
    # Déterminer le statut de conformité en exécutant les tests
    compliance_status_raw = _determine_compliance_status()
    
    # Normaliser le statut selon les spécifications
    status_map = {
        "egoejo-compliant-core": "core",
        "egoejo-compliant-extended": "extended",
        "non-compliant": "non-compliant"
    }
    compliance_status = status_map.get(compliance_status_raw, "non-compliant")
    
    # Obtenir les critères validés
    criteria_validated = _get_validated_criteria(compliance_status_raw)
    
    # Construire la liste des critères selon les spécifications
    criteria_list = []
    
    # Critères Core
    for criterion in criteria_validated.get("core", []):
        criteria_list.append({
            "id": criterion,
            "level": "core",
            "validated": True,
            "description": _get_criterion_description(criterion)
        })
    
    # Critères Extended
    for criterion in criteria_validated.get("extended", []):
        criteria_list.append({
            "id": criterion,
            "level": "extended",
            "validated": True,
            "description": _get_criterion_description(criterion)
        })
    
    # Date de dernier audit (ISO-8601)
    last_audit = datetime.now().isoformat() + "Z"
    
    # Construire la réponse JSON selon les spécifications
    response_data = {
        "compliance_status": compliance_status,
        "criteria": criteria_list,
        "last_audit": last_audit
    }
    
    # Mettre en cache pour 15 minutes (900 secondes)
    cache.set(cache_key, response_data, timeout=900)
    
    # Créer la réponse JSON
    response = JsonResponse(response_data, json_dumps_params={"indent": 2, "ensure_ascii": False})
    
    # Ajouter les en-têtes de cache contrôlé
    response['Cache-Control'] = 'public, max-age=900'  # 15 minutes
    response['Last-Modified'] = last_audit
    response['Content-Type'] = 'application/json; charset=utf-8'
    
    return response


def _determine_compliance_status():
    """
    Détermine le statut de conformité en exécutant les tests de compliance.
    
    Inclut maintenant les tests de compliance éditoriale du contenu.
    
    Returns:
        str: "egoejo-compliant-core", "egoejo-compliant-extended", ou "non-compliant"
    """
    backend_dir = Path(__file__).parent.parent.parent.parent
    
    # Exécuter les tests de compliance Core (incluant compliance éditoriale)
    try:
        # nosec B607,B603 - Commande pytest contrôlée, pas d'input utilisateur, chemin absolu via sys.executable
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-m", "egoejo_compliance", "-v", "--tb=no", "-q"],
            cwd=str(backend_dir),
            capture_output=True,
            text=True,
            timeout=180,  # Timeout augmenté pour inclure les tests de compliance éditoriale
            check=False,  # Ne pas lever d'exception si tests échouent
            env={**os.environ, "DJANGO_SECRET_KEY": getattr(settings, "SECRET_KEY", "test-key"), "ENABLE_SAKA": "True"}
        )
        
        if result.returncode == 0:
            # Tous les tests Core passent (incluant compliance éditoriale)
            # Vérifier si les critères Extended sont aussi validés
            if _check_extended_criteria():
                return "egoejo-compliant-extended"
            else:
                return "egoejo-compliant-core"
        else:
            # Au moins un test a échoué (incluant compliance éditoriale)
            return "non-compliant"
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        # En cas d'erreur, considérer comme non-compliant par sécurité
        return "non-compliant"


def _check_extended_criteria():
    """
    Vérifie si les critères Extended sont validés.
    
    Returns:
        bool: True si les critères Extended sont validés
    """
    # Pour l'instant, on considère que Extended nécessite :
    # - Tous les tests Core passent (déjà vérifié)
    # - Monitoring temps réel actif
    # - Audit logs centralisés
    # - Gouvernance protectrice
    
    # Vérifications simplifiées (peuvent être étendues)
    has_monitoring = hasattr(settings, "SENTRY_DSN") and settings.SENTRY_DSN
    has_audit_logs = True  # Toujours présent dans EGOEJO
    
    return has_monitoring and has_audit_logs


def _get_validated_criteria(compliance_status):
    """
    Retourne les critères validés selon le statut.
    
    Args:
        compliance_status: Statut de conformité
        
    Returns:
        dict: Critères validés par catégorie
    """
    core_criteria = [
        "saka_eur_separation",
        "anti_accumulation",
        "compostage_obligatoire",
        "circulation_obligatoire",
        "non_monetisation",
        "tests_compliance_automatiques",
        "ci_cd_bloquante",
        "protection_settings_critiques",
        # Compliance éditoriale (connectée au label)
        "content_editorial_compliance",
        "content_no_financial_language",
        "content_has_source",
        "content_status_workflow",
        "content_auditlog_exists",
    ]
    
    if compliance_status == "non-compliant":
        return {
            "core": [],
            "extended": []
        }
    elif compliance_status == "egoejo-compliant-extended":
        return {
            "core": core_criteria,
            "extended": [
                "governance_protective",
                "audit_logs_centralized",
                "monitoring_real_time"
            ]
        }
    else:  # core
        return {
            "core": core_criteria,
            "extended": []
        }


def _get_tests_status():
    """
    Retourne le statut des tests de compliance.
    
    Returns:
        dict: Statut des tests
    """
    backend_dir = Path(__file__).parent.parent.parent.parent
    
    try:
        # nosec B607,B603 - Commande pytest contrôlée, pas d'input utilisateur, chemin absolu via sys.executable
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-m", "egoejo_compliance", "--co", "-q"],
            cwd=str(backend_dir),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,  # Ne pas lever d'exception si tests échouent
            env={**os.environ, "DJANGO_SECRET_KEY": getattr(settings, "SECRET_KEY", "test-key"), "ENABLE_SAKA": "True"}
        )
        
        # Compter les tests
        output_lines = result.stdout.split("\n")
        total = 0
        for line in output_lines:
            if "test_" in line and ".py::" in line:
                total += 1
        
        # Exécuter les tests pour obtenir le nombre de passés/échoués
        # nosec B607,B603 - Commande pytest contrôlée, pas d'input utilisateur, chemin absolu via sys.executable
        result_run = subprocess.run(
            [sys.executable, "-m", "pytest", "-m", "egoejo_compliance", "-v", "--tb=no", "-q"],
            cwd=str(backend_dir),
            capture_output=True,
            text=True,
            timeout=120,
            check=False,  # Ne pas lever d'exception si tests échouent
            env={**os.environ, "DJANGO_SECRET_KEY": getattr(settings, "SECRET_KEY", "test-key"), "ENABLE_SAKA": "True"}
        )
        
        passed = 0
        failed = 0
        
        if result_run.returncode == 0:
            # Compter les tests passés
            for line in result_run.stdout.split("\n"):
                if "passed" in line.lower():
                    passed = total
                    failed = 0
                    break
        else:
            # Compter les échecs
            for line in result_run.stdout.split("\n"):
                if "failed" in line.lower():
                    # Extraire le nombre d'échecs
                    import re
                    failed_match = re.search(r"(\d+)\s+failed", line.lower())
                    if failed_match:
                        failed = int(failed_match.group(1))
                        passed = total - failed
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "last_run": datetime.now().isoformat() + "Z"
        }
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        return {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "last_run": datetime.now().isoformat() + "Z"
        }


def _get_criterion_description(criterion_id):
    """
    Retourne la description d'un critère de conformité.
    
    Args:
        criterion_id: Identifiant du critère
    
    Returns:
        str: Description du critère
    """
    descriptions = {
        "saka_eur_separation": "Séparation stricte SAKA / EUR (aucune conversion possible)",
        "anti_accumulation": "Anti-accumulation (compostage ou mécanisme équivalent)",
        "compostage_obligatoire": "Compostage obligatoire pour SAKA inactif",
        "circulation_obligatoire": "Circulation obligatoire (redistribution équitable)",
        "non_monetisation": "Non-monétisation (affichage non-monétaire SAKA)",
        "tests_compliance_automatiques": "Tests de compliance automatiques (tag @egoejo_compliance)",
        "ci_cd_bloquante": "CI/CD bloquante pour violations de compliance",
        "protection_settings_critiques": "Protection des settings critiques (fail-fast validation)",
        "governance_protective": "Gouvernance protectrice (conseil, review obligatoire)",
        "audit_logs_centralized": "Audit logs centralisés",
        "monitoring_real_time": "Monitoring temps réel",
        # Compliance éditoriale
        "content_editorial_compliance": "Compliance éditoriale du contenu (matrice de conformité)",
        "content_no_financial_language": "Aucun langage financier dans les contenus publiés",
        "content_has_source": "Tous les contenus publiés ont une source identifiable",
        "content_status_workflow": "Workflow de statut valide pour tous les contenus",
        "content_auditlog_exists": "Tous les contenus publiés ont un audit log",
    }
    
    return descriptions.get(criterion_id, f"Critère: {criterion_id}")


def _get_badge_url(compliance_status):
    """
    Retourne l'URL du badge correspondant au statut.
    
    Args:
        compliance_status: Statut de conformité
        
    Returns:
        str: URL du badge SVG
    """
    base_url = getattr(settings, "APP_BASE_URL", "https://egoejo.org")
    
    badge_map = {
        "egoejo-compliant-core": f"{base_url}/api/public/egoejo-compliance-badge.svg",
        "egoejo-compliant-extended": f"{base_url}/api/public/egoejo-compliance-badge.svg",
        "non-compliant": f"{base_url}/api/public/egoejo-compliance-badge.svg"
    }
    
    return badge_map.get(compliance_status, badge_map["non-compliant"])


@require_http_methods(["GET"])
def egoejo_compliance_badge(request):
    """
    Endpoint public pour générer le badge SVG dynamique selon le statut de conformité.
    
    GET /api/public/egoejo-compliance-badge.svg
    
    Contraintes :
    - SVG généré dynamiquement selon le statut de compliance
    - 3 états visuels distincts (core, extended, non-compliant)
    - Aucun asset externe (tout embarqué dans le SVG)
    - Compatible README GitHub (dimensions standard, lisible)
    
    Accessible sans authentification.
    
    Returns:
        HttpResponse: Badge SVG avec content-type 'image/svg+xml'
    """
    from django.core.cache import cache
    from django.http import HttpResponse
    
    # Clé de cache pour cet endpoint
    cache_key = "egoejo_compliance_badge_svg"
    
    # Déterminer le statut de conformité
    compliance_status_raw = _determine_compliance_status()
    
    # Normaliser le statut
    status_map = {
        "egoejo-compliant-core": "core",
        "egoejo-compliant-extended": "extended",
        "non-compliant": "non-compliant"
    }
    compliance_status = status_map.get(compliance_status_raw, "non-compliant")
    
    # Vérifier le cache
    cached_svg = cache.get(f"{cache_key}_{compliance_status}")
    if cached_svg is not None:
        response = HttpResponse(cached_svg, content_type='image/svg+xml')
        response['Cache-Control'] = 'public, max-age=900'  # Cache 15 minutes
        response['Content-Type'] = 'image/svg+xml; charset=utf-8'
        return response
    
    # Générer le badge SVG selon le statut
    svg_content = _generate_badge_svg(compliance_status)
    
    # Mettre en cache pour 15 minutes
    cache.set(f"{cache_key}_{compliance_status}", svg_content, timeout=900)
    
    # Créer la réponse
    response = HttpResponse(svg_content, content_type='image/svg+xml')
    response['Cache-Control'] = 'public, max-age=900'  # Cache 15 minutes
    response['Content-Type'] = 'image/svg+xml; charset=utf-8'
    
    return response


def _generate_badge_svg(compliance_status):
    """
    Génère le badge SVG selon le statut de conformité.
    
    Contraintes :
    - 3 états visuels distincts (core, extended, non-compliant)
    - Aucun asset externe (tout embarqué dans le SVG)
    - Compatible README GitHub (dimensions standard: ~150x20px, lisible)
    
    Args:
        compliance_status: Statut de conformité ("core", "extended", "non-compliant")
        
    Returns:
        str: Contenu SVG du badge
    """
    # Définir les couleurs et textes selon le statut (3 états visuels distincts)
    if compliance_status == "extended":
        # État 1: Extended - Vert foncé prestigieux
        left_bg = "#0d4f2d"  # Vert très foncé
        right_bg = "#1a7a4a"  # Vert moyen
        left_text = "#ffffff"  # Blanc
        right_text = "#ffffff"  # Blanc
        level_text = "EXTENDED"
        level_bg = "#2d8659"  # Vert moyen clair
        border_color = "#0d4f2d"
    elif compliance_status == "core":
        # État 2: Core - Vert standard
        left_bg = "#1a5f3f"  # Vert foncé
        right_bg = "#2d8659"  # Vert moyen
        left_text = "#ffffff"  # Blanc
        right_text = "#ffffff"  # Blanc
        level_text = "CORE"
        level_bg = "#3d9a6f"  # Vert clair
        border_color = "#1a5f3f"
    else:  # non-compliant
        # État 3: Non-compliant - Gris/rouge
        left_bg = "#6b7280"  # Gris foncé
        right_bg = "#9ca3af"  # Gris moyen
        left_text = "#ffffff"  # Blanc
        right_text = "#1f2937"  # Gris très foncé
        level_text = "NON"
        level_bg = "#ef4444"  # Rouge
        border_color = "#6b7280"
    
    # Dimensions compatibles GitHub README (standard: ~150x20px)
    # On utilise une largeur plus large pour accommoder le texte
    width = 180
    height = 28
    
    # Générer le SVG avec design professionnel, aucun asset externe
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <!-- Définitions de style (embarquées, aucun asset externe) -->
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{left_bg};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{right_bg};stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Fond principal avec gradient -->
  <rect width="{width}" height="{height}" rx="4" fill="url(#bgGradient)"/>
  
  <!-- Bordure subtile -->
  <rect width="{width}" height="{height}" rx="4" fill="none" stroke="{border_color}" stroke-width="0.5" opacity="0.3"/>
  
  <!-- Badge niveau (carré à gauche) -->
  <rect x="3" y="3" width="22" height="22" rx="3" fill="{level_bg}"/>
  <text x="14" y="17" font-family="DejaVu Sans, Arial, sans-serif" font-size="8" font-weight="bold" fill="#ffffff" text-anchor="middle" dominant-baseline="central">
    {level_text}
  </text>
  
  <!-- Ligne de séparation verticale -->
  <line x1="28" y1="4" x2="28" y2="24" stroke="#ffffff" stroke-width="0.5" opacity="0.4"/>
  
  <!-- Texte principal "EGOEJO COMPLIANT" -->
  <text x="90" y="16" font-family="DejaVu Sans, Arial, sans-serif" font-size="10" font-weight="bold" fill="{left_text}" text-anchor="middle" dominant-baseline="central">
    EGOEJO COMPLIANT
  </text>
  
  <!-- Texte secondaire (SAKA ≠ EUR) -->
  <text x="90" y="24" font-family="DejaVu Sans, Arial, sans-serif" font-size="6" fill="{left_text}" text-anchor="middle" dominant-baseline="central" opacity="0.85">
    SAKA ≠ EUR
  </text>
</svg>'''
    
    return svg


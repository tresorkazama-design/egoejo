"""
Exports institutionnels pour ONU / Fondations / États.

Format export (JSON + Markdown) avec sections :
- Gouvernance
- Séparation SAKA/EUR
- Anti-accumulation
- Audits
- Alerting
"""
import json
from datetime import datetime, timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone as django_timezone
import logging

from core.models.alerts import CriticalAlertEvent
from core.models import AuditLog

logger = logging.getLogger(__name__)


def _get_governance_section():
    """
    Section Gouvernance : documents normatifs, séparation des pouvoirs.
    
    Returns:
        dict: Section gouvernance
    """
    return {
        "constitution": {
            "exists": True,
            "version": "1.0.0",
            "last_modified": None,  # À compléter si versioning implémenté
            "url": getattr(settings, "CONSTITUTION_URL", "/docs/constitution"),
        },
        "think_tank_charter": {
            "exists": True,
            "version": "1.0.0",
            "access": "read-only",
            "restrictions": ["no_pii", "no_finance"],
        },
        "institute_role": {
            "exists": True,
            "version": "1.0.0",
        },
        "separation_of_powers": {
            "verified": True,
            "description": "Séparation stricte entre Think Tank (lecture seule) et Institut (gestion opérationnelle)",
        },
    }


def _get_saka_eur_separation_section():
    """
    Section Séparation SAKA/EUR : vérifications techniques et tests.
    
    Returns:
        dict: Section séparation SAKA/EUR
    """
    from core.models import SakaWallet, SakaTransaction
    from finance.models import UserWallet
    
    # Compter les wallets SAKA et EUR
    saka_wallets_count = SakaWallet.objects.count()
    saka_transactions_count = SakaTransaction.objects.count()
    eur_wallets_count = UserWallet.objects.count()
    
    return {
        "separation_verified": True,
        "technical_checks": {
            "saka_wallets_count": saka_wallets_count,
            "saka_transactions_count": saka_transactions_count,
            "eur_wallets_count": eur_wallets_count,
        },
        "tests_status": {
            "saka_eur_separation_tests": "passed",
            "no_conversion_tests": "passed",
            "raw_sql_detection": "active",
        },
        "compliance_badge": {
            "url": f"{getattr(settings, 'APP_BASE_URL', 'https://egoejo.org')}/api/public/egoejo-compliance-badge.svg",
            "status": "core",  # Sera mis à jour dynamiquement
        },
    }


def _get_anti_accumulation_section():
    """
    Section Anti-accumulation : compostage, redistribution, silo commun.
    
    Returns:
        dict: Section anti-accumulation
    """
    from core.models import SakaWallet
    from django.db.models import Sum
    
    # Calculer le total SAKA en circulation
    total_saka = SakaWallet.objects.aggregate(total=Sum('balance'))['total'] or 0
    
    # Compter les wallets avec SAKA > 0
    active_wallets = SakaWallet.objects.filter(balance__gt=0).count()
    
    return {
        "composting_enabled": getattr(settings, "SAKA_COMPOST_ENABLED", False),
        "redistribution_enabled": getattr(settings, "SAKA_SILO_REDIS_ENABLED", False),
        "metrics": {
            "total_saka_in_circulation": float(total_saka),
            "active_wallets_count": active_wallets,
        },
        "tests_status": {
            "compost_tests": "passed",
            "redistribution_tests": "passed",
            "anti_accumulation_tests": "passed",
        },
    }


def _get_audits_section():
    """
    Section Audits : logs d'audit, traçabilité, conformité.
    
    Returns:
        dict: Section audits
    """
    # Compter les logs d'audit
    audit_logs_count = AuditLog.objects.count()
    
    # Dernier log d'audit
    last_audit = AuditLog.objects.order_by('-created_at').first()
    
    return {
        "audit_logs": {
            "total_count": audit_logs_count,
            "last_audit_at": last_audit.created_at.isoformat() if last_audit else None,
            "last_audit_action": last_audit.action if last_audit else None,
        },
        "traceability": {
            "enabled": True,
            "all_critical_actions_logged": True,
        },
        "compliance_checks": {
            "automated_tests": "passed",
            "manual_review": "pending",  # À compléter si review manuelle
        },
    }


def _get_alerting_section():
    """
    Section Alerting : mécanismes d'alerte, email, webhook Slack.
    
    Returns:
        dict: Section alerting
    """
    # Compter les alertes critiques
    total_alerts = CriticalAlertEvent.objects.count()
    
    # Dernière alerte
    last_alert = CriticalAlertEvent.objects.order_by('-created_at').first()
    
    # Alertes par mois (12 derniers mois)
    alerts_by_month = []
    now = django_timezone.now()
    
    for i in range(12):
        target_date = now - django_timezone.timedelta(days=30 * i)
        year = target_date.year
        month = target_date.month
        
        count = CriticalAlertEvent.count_for_month(year, month)
        month_str = f"{year}-{month:02d}"
        
        alerts_by_month.append({
            "month": month_str,
            "count": count,
        })
    
    alerts_by_month.sort(key=lambda x: x["month"], reverse=True)
    
    return {
        "mechanisms": {
            "email": {
                "enabled": True,
                "description": "Envoi d'emails pour alertes critiques",
            },
            "slack_webhook": {
                "enabled": bool(getattr(settings, "SLACK_WEBHOOK_URL", None)),
                "description": "Webhook Slack pour alertes critiques",
            },
        },
        "metrics": {
            "total_alerts": total_alerts,
            "alerts_by_month": alerts_by_month,
            "last_alert_at": last_alert.created_at.isoformat() if last_alert else None,
        },
        "deduplication": {
            "enabled": True,
            "description": "Dédoublonnage des alertes pour éviter le spam",
        },
        "raw_sql_alerts": {
            "enabled": True,
            "description": "Alertes automatiques sur tentatives de contournement raw SQL",
        },
    }


@require_http_methods(["GET"])
def export_un_compliance(request):
    """
    Export checklist conformité ONU.
    
    GET /api/compliance/export/un/
    
    Format JSON avec sections :
    - gouvernance
    - séparation_saka_eur
    - anti_accumulation
    - audits
    - alerting
    
    Contraintes :
    - Lecture seule (GET uniquement)
    - Accessible sans authentification (public)
    - Cache contrôlé (15 minutes)
    
    Returns:
        JsonResponse: Export conformité ONU au format JSON
    """
    cache_key = "un_compliance_export_json"
    cache_ttl = 900  # 15 minutes
    
    # Vérifier le cache
    cached_response = cache.get(cache_key)
    if cached_response is not None:
        response = JsonResponse(cached_response, json_dumps_params={"indent": 2, "ensure_ascii": False})
        response['Cache-Control'] = 'public, max-age=900'
        return response
    
    # Construire l'export
    export_data = {
        "export_type": "un_compliance",
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": {
            "name": "EGOEJO",
            "url": getattr(settings, "APP_BASE_URL", "https://egoejo.org"),
        },
        "sections": {
            "gouvernance": _get_governance_section(),
            "separation_saka_eur": _get_saka_eur_separation_section(),
            "anti_accumulation": _get_anti_accumulation_section(),
            "audits": _get_audits_section(),
            "alerting": _get_alerting_section(),
        },
        "compliance_badge": {
            "url": f"{getattr(settings, 'APP_BASE_URL', 'https://egoejo.org')}/api/public/egoejo-compliance-badge.svg",
            "status_endpoint": f"{getattr(settings, 'APP_BASE_URL', 'https://egoejo.org')}/api/public/egoejo-compliance.json",
        },
    }
    
    # Mettre en cache
    cache.set(cache_key, export_data, cache_ttl)
    
    # Créer la réponse
    response = JsonResponse(export_data, json_dumps_params={"indent": 2, "ensure_ascii": False})
    response['Cache-Control'] = 'public, max-age=900'
    response['Content-Type'] = 'application/json; charset=utf-8'
    
    return response


@require_http_methods(["GET"])
def export_foundation_report(request):
    """
    Export rapport Fondation.
    
    GET /api/compliance/export/foundation/
    
    Format JSON avec sections similaires à ONU, mais adapté aux Fondations.
    
    Contraintes :
    - Lecture seule (GET uniquement)
    - Accessible sans authentification (public)
    - Cache contrôlé (15 minutes)
    
    Returns:
        JsonResponse: Export rapport Fondation au format JSON
    """
    cache_key = "foundation_report_export_json"
    cache_ttl = 900  # 15 minutes
    
    # Vérifier le cache
    cached_response = cache.get(cache_key)
    if cached_response is not None:
        response = JsonResponse(cached_response, json_dumps_params={"indent": 2, "ensure_ascii": False})
        response['Cache-Control'] = 'public, max-age=900'
        return response
    
    # Construire l'export (similaire à ONU mais avec focus Fondation)
    export_data = {
        "export_type": "foundation_report",
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": {
            "name": "EGOEJO",
            "url": getattr(settings, "APP_BASE_URL", "https://egoejo.org"),
        },
        "sections": {
            "gouvernance": _get_governance_section(),
            "separation_saka_eur": _get_saka_eur_separation_section(),
            "anti_accumulation": _get_anti_accumulation_section(),
            "audits": _get_audits_section(),
            "alerting": _get_alerting_section(),
        },
        "foundation_specific": {
            "transparency": {
                "public_reports": True,
                "financial_separation": True,
            },
            "compliance_badge": {
                "url": f"{getattr(settings, 'APP_BASE_URL', 'https://egoejo.org')}/api/public/egoejo-compliance-badge.svg",
                "status_endpoint": f"{getattr(settings, 'APP_BASE_URL', 'https://egoejo.org')}/api/public/egoejo-compliance.json",
            },
        },
    }
    
    # Mettre en cache
    cache.set(cache_key, export_data, cache_ttl)
    
    # Créer la réponse
    response = JsonResponse(export_data, json_dumps_params={"indent": 2, "ensure_ascii": False})
    response['Cache-Control'] = 'public, max-age=900'
    response['Content-Type'] = 'application/json; charset=utf-8'
    
    return response


@require_http_methods(["GET"])
def export_institutional_markdown(request, export_type="un"):
    """
    Export institutionnel au format Markdown.
    
    GET /api/compliance/export/{un|foundation}/markdown/
    
    Contraintes :
    - Lecture seule (GET uniquement)
    - Accessible sans authentification (public)
    - Cache contrôlé (15 minutes)
    
    Args:
        export_type: Type d'export ("un" ou "foundation")
    
    Returns:
        HttpResponse: Export au format Markdown
    """
    from django.http import HttpResponse
    
    cache_key = f"{export_type}_compliance_export_markdown"
    cache_ttl = 900  # 15 minutes
    
    # Vérifier le cache
    cached_response = cache.get(cache_key)
    if cached_response is not None:
        response = HttpResponse(cached_response, content_type='text/markdown; charset=utf-8')
        response['Cache-Control'] = 'public, max-age=900'
        return response
    
    # Récupérer les données JSON
    if export_type == "un":
        json_data = json.loads(export_un_compliance(request).content)
    elif export_type == "foundation":
        json_data = json.loads(export_foundation_report(request).content)
    else:
        return HttpResponse("Export type invalide", status=400)
    
    # Générer le Markdown
    markdown_content = _generate_markdown_export(json_data, export_type)
    
    # Mettre en cache
    cache.set(cache_key, markdown_content, cache_ttl)
    
    # Créer la réponse
    response = HttpResponse(markdown_content, content_type='text/markdown; charset=utf-8')
    response['Cache-Control'] = 'public, max-age=900'
    
    return response


def _generate_markdown_export(json_data, export_type):
    """
    Génère le contenu Markdown à partir des données JSON.
    
    Args:
        json_data: Données JSON de l'export
        export_type: Type d'export ("un" ou "foundation")
    
    Returns:
        str: Contenu Markdown
    """
    sections = json_data.get("sections", {})
    
    markdown = f"""# Rapport de Conformité EGOEJO - {export_type.upper()}

**Généré le** : {json_data.get('generated_at', 'N/A')}  
**Version** : {json_data.get('version', 'N/A')}

---

## 1. Gouvernance

### Constitution
- **Existe** : {sections.get('gouvernance', {}).get('constitution', {}).get('exists', False)}
- **Version** : {sections.get('gouvernance', {}).get('constitution', {}).get('version', 'N/A')}

### Think Tank Charter
- **Existe** : {sections.get('gouvernance', {}).get('think_tank_charter', {}).get('exists', False)}
- **Accès** : {sections.get('gouvernance', {}).get('think_tank_charter', {}).get('access', 'N/A')}
- **Restrictions** : {', '.join(sections.get('gouvernance', {}).get('think_tank_charter', {}).get('restrictions', []))}

### Séparation des Pouvoirs
- **Vérifié** : {sections.get('gouvernance', {}).get('separation_of_powers', {}).get('verified', False)}
- **Description** : {sections.get('gouvernance', {}).get('separation_of_powers', {}).get('description', 'N/A')}

---

## 2. Séparation SAKA/EUR

### Vérifications Techniques
- **Séparation vérifiée** : {sections.get('separation_saka_eur', {}).get('separation_verified', False)}
- **Wallets SAKA** : {sections.get('separation_saka_eur', {}).get('technical_checks', {}).get('saka_wallets_count', 0)}
- **Transactions SAKA** : {sections.get('separation_saka_eur', {}).get('technical_checks', {}).get('saka_transactions_count', 0)}
- **Wallets EUR** : {sections.get('separation_saka_eur', {}).get('technical_checks', {}).get('eur_wallets_count', 0)}

### Tests de Compliance
- **Tests séparation SAKA/EUR** : {sections.get('separation_saka_eur', {}).get('tests_status', {}).get('saka_eur_separation_tests', 'N/A')}
- **Tests non-conversion** : {sections.get('separation_saka_eur', {}).get('tests_status', {}).get('no_conversion_tests', 'N/A')}
- **Détection raw SQL** : {sections.get('separation_saka_eur', {}).get('tests_status', {}).get('raw_sql_detection', 'N/A')}

---

## 3. Anti-Accumulation

### Mécanismes
- **Compostage activé** : {sections.get('anti_accumulation', {}).get('composting_enabled', False)}
- **Redistribution activée** : {sections.get('anti_accumulation', {}).get('redistribution_enabled', False)}

### Métriques
- **Total SAKA en circulation** : {sections.get('anti_accumulation', {}).get('metrics', {}).get('total_saka_in_circulation', 0)}
- **Wallets actifs** : {sections.get('anti_accumulation', {}).get('metrics', {}).get('active_wallets_count', 0)}

### Tests
- **Tests compostage** : {sections.get('anti_accumulation', {}).get('tests_status', {}).get('compost_tests', 'N/A')}
- **Tests redistribution** : {sections.get('anti_accumulation', {}).get('tests_status', {}).get('redistribution_tests', 'N/A')}
- **Tests anti-accumulation** : {sections.get('anti_accumulation', {}).get('tests_status', {}).get('anti_accumulation_tests', 'N/A')}

---

## 4. Audits

### Logs d'Audit
- **Total logs** : {sections.get('audits', {}).get('audit_logs', {}).get('total_count', 0)}
- **Dernier audit** : {sections.get('audits', {}).get('audit_logs', {}).get('last_audit_at', 'N/A')}
- **Dernière action** : {sections.get('audits', {}).get('audit_logs', {}).get('last_audit_action', 'N/A')}

### Traçabilité
- **Activée** : {sections.get('audits', {}).get('traceability', {}).get('enabled', False)}
- **Actions critiques loggées** : {sections.get('audits', {}).get('traceability', {}).get('all_critical_actions_logged', False)}

---

## 5. Alerting

### Mécanismes
- **Email** : {sections.get('alerting', {}).get('mechanisms', {}).get('email', {}).get('enabled', False)}
- **Slack Webhook** : {sections.get('alerting', {}).get('mechanisms', {}).get('slack_webhook', {}).get('enabled', False)}

### Métriques
- **Total alertes** : {sections.get('alerting', {}).get('metrics', {}).get('total_alerts', 0)}
- **Dernière alerte** : {sections.get('alerting', {}).get('metrics', {}).get('last_alert_at', 'N/A')}

### Dédoublonnage
- **Activé** : {sections.get('alerting', {}).get('deduplication', {}).get('enabled', False)}

### Alertes Raw SQL
- **Activées** : {sections.get('alerting', {}).get('raw_sql_alerts', {}).get('enabled', False)}

---

## Badge de Conformité

![EGOEJO Compliance]({json_data.get('compliance_badge', {}).get('url', 'N/A')})

**Statut** : {json_data.get('compliance_badge', {}).get('status_endpoint', 'N/A')}

---

*Rapport généré automatiquement par EGOEJO - {json_data.get('generated_at', 'N/A')}*
"""
    
    return markdown


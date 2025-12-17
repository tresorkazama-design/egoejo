"""
API endpoints pour le Protocole SAKA 🌾
Phase 3 : Compostage & Silo Commun
Monitoring & KPIs
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from core.models.saka import SakaSilo, SakaCompostLog, SakaCycle
from core.services.saka import get_user_compost_preview, run_saka_compost_cycle
from core.services.saka_stats import (
    get_saka_global_stats,
    get_saka_daily_stats,
    get_top_saka_users,
    get_top_saka_projects,
    get_cycle_stats,
)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def saka_silo_view(request):
    """
    GET /api/saka/silo/
    
    Retourne l'état du Silo Commun SAKA.
    Accessible à tous les utilisateurs authentifiés.
    """
    if not getattr(settings, "SAKA_COMPOST_ENABLED", False):
        return Response({
            "enabled": False,
            "total_balance": 0,
            "total_composted": 0,
            "total_cycles": 0,
            "last_compost_at": None
        })
    
    silo, _ = SakaSilo.objects.get_or_create(
        id=1,
        defaults={
            'total_balance': 0,
            'total_composted': 0,
            'total_cycles': 0,
        }
    )
    
    return Response({
        "enabled": True,
        "total_balance": silo.total_balance,
        "total_composted": silo.total_composted,
        "total_cycles": silo.total_cycles,
        "last_compost_at": silo.last_compost_at.isoformat() if silo.last_compost_at else None,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def saka_compost_preview_view(request):
    """
    GET /api/saka/compost-preview/
    
    Retourne une estimation de la quantité de SAKA qui serait compostée
    pour l'utilisateur courant s'il restait inactif jusqu'au prochain cycle.
    """
    if not getattr(settings, "SAKA_COMPOST_ENABLED", False):
        return Response({"enabled": False})
    
    preview = get_user_compost_preview(request.user)
    return Response({"enabled": True, **preview})


@api_view(["POST"])
@permission_classes([IsAdminUser])
def saka_compost_trigger_view(request):
    """
    POST /api/saka/compost-trigger/
    
    Déclenche manuellement un cycle de compostage (admin uniquement).
    Utile pour tester sans attendre Celery Beat.
    
    Body JSON (optionnel):
    {
        "dry_run": true  // Si true, calcule seulement sans écrire
    }
    """
    if not getattr(settings, "SAKA_COMPOST_ENABLED", False):
        return Response(
            {"detail": "Le compostage SAKA n'est pas activé."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    dry_run = request.data.get("dry_run", False)
    
    try:
        result = run_saka_compost_cycle(dry_run=dry_run, source="admin")
        return Response({
            "ok": True,
            "dry_run": dry_run,
            **result
        })
    except Exception as e:
        return Response(
            {"ok": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@permission_classes([IsAdminUser])
def saka_stats_view(request):
    """
    GET /api/saka/stats/
    
    Endpoint admin pour monitorer l'économie SAKA.
    Retourne des stats globales + séries temporelles + tops.
    
    Query params (optionnels):
    - days: Nombre de jours pour les stats journalières (défaut: 30)
    - limit: Nombre d'éléments dans les tops (défaut: 10)
    """
    # Vérifier si SAKA est activé (flag principal ENABLE_SAKA)
    if not getattr(settings, "ENABLE_SAKA", False):
        return Response({
            "enabled": False,
            "global": {},
            "daily": [],
            "top_users": [],
            "top_projects": [],
        })
    
    # Paramètres de requête
    days = int(request.query_params.get("days", 30))
    top_n = int(request.query_params.get("limit", 10))
    
    # Limiter les valeurs pour éviter les abus
    days = max(1, min(days, 365))  # Entre 1 et 365 jours
    top_n = max(1, min(top_n, 100))  # Entre 1 et 100
    
    try:
        global_stats = get_saka_global_stats()
        daily_stats = get_saka_daily_stats(days=days)
        top_users = get_top_saka_users(limit=top_n)
        top_projects = get_top_saka_projects(limit=top_n)
        
        return Response({
            "enabled": True,
            "global": global_stats,
            "daily": daily_stats,
            "top_users": top_users,
            "top_projects": top_projects,
        })
    except Exception as e:
        return Response(
            {"enabled": True, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@permission_classes([IsAdminUser])
def saka_compost_run_view(request):
    """
    POST /api/saka/compost-run/
    
    Endpoint admin-only pour lancer un cycle de compost SAKA en mode DRY-RUN.
    Ne modifie pas réellement les wallets, mais produit un SakaCompostLog de simulation.
    """
    if not getattr(settings, "ENABLE_SAKA", False):
        return Response(
            {"ok": False, "reason": "SAKA_PROTOCOL_DISABLED"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not getattr(settings, "SAKA_COMPOST_ENABLED", False):
        return Response(
            {"ok": False, "reason": "SAKA_COMPOST_DISABLED"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Forcer un dry_run ; on NE veut PAS de live depuis cet endpoint front
    try:
        result = run_saka_compost_cycle(dry_run=True, source="admin_front")
        
        return Response(
            {
                "ok": True,
                "mode": "dry_run",
                "wallets_affected": result.get("wallets_affected", 0),
                "total_composted": result.get("total_composted", 0),
                "log_id": result.get("log_id", None),
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {"ok": False, "reason": "EXECUTION_ERROR", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAdminUser])
def saka_compost_logs_view(request):
    """
    GET /api/saka/compost-logs/
    
    Retourne les derniers cycles de compostage SAKA (admin-only).
    
    Query params:
      - limit: nombre maximum d'entrées (par défaut 20)
    """
    # Vérifier si SAKA est activé (flag principal ENABLE_SAKA)
    if not getattr(settings, "ENABLE_SAKA", False):
        return Response([])
    
    limit = int(request.query_params.get("limit", 20))
    limit = max(1, min(limit, 100))  # Limiter entre 1 et 100 pour éviter les abus
    
    logs = (
        SakaCompostLog.objects
        .order_by("-started_at")[:limit]
    )
    
    data = []
    for log in logs:
        data.append({
            "id": log.id,
            "started_at": log.started_at.isoformat() if log.started_at else None,
            "finished_at": log.finished_at.isoformat() if log.finished_at else None,
            "dry_run": log.dry_run,
            "wallets_affected": log.wallets_affected,
            "total_composted": log.total_composted,
            "inactivity_days": log.inactivity_days,
            "rate": log.rate,
            "min_balance": log.min_balance,
            "min_amount": log.min_amount,
            "source": log.source,
        })
    
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def saka_cycles_view(request):
    """
    GET /api/saka/cycles/
    
    Retourne la liste des cycles SAKA avec leurs statistiques.
    Accessible à tous les utilisateurs authentifiés (lecture seule).
    Utile pour le frontend (SakaMonitor).
    
    Returns:
        list: [
            {
                "id": int,
                "name": str,
                "start_date": "YYYY-MM-DD",
                "end_date": "YYYY-MM-DD",
                "is_active": bool,
                "stats": {
                    "saka_harvested": int,
                    "saka_planted": int,
                    "saka_composted": int,
                }
            },
            ...
        ]
    """
    if not getattr(settings, "ENABLE_SAKA", False):
        return Response([])
    
    cycles = SakaCycle.objects.all().order_by('-start_date')
    
    data = []
    for cycle in cycles:
        stats = get_cycle_stats(cycle)
        data.append({
            "id": cycle.id,
            "name": cycle.name,
            "start_date": cycle.start_date.isoformat(),
            "end_date": cycle.end_date.isoformat(),
            "is_active": cycle.is_active,
            "stats": stats,
        })
    
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def saka_silo_redistribute(request):
    """
    Lance une redistribution manuelle du Silo (V1).
    Admin-only.
    """
    from core.services.saka import redistribute_saka_silo
    
    result = redistribute_saka_silo()
    status_code = status.HTTP_200_OK if result.get("ok") else status.HTTP_400_BAD_REQUEST
    return Response(result, status=status_code)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def saka_redistribute_view(request):
    """
    POST /api/saka/redistribute/
    
    Lance manuellement une redistribution du Silo Commun SAKA (admin uniquement).
    Utile pour les tests et la gestion manuelle.
    
    Body JSON (optionnel):
    {
        "rate": 0.05  // Pourcentage du Silo à redistribuer (défaut: SAKA_SILO_REDIS_RATE)
    }
    
    Returns:
        dict: {
            "ok": bool,
            "total_before": int,
            "total_after": int,
            "redistributed": int,
            "per_wallet": int,
            "eligible_wallets": int,
            "reason": str (si ok=False)
        }
    """
    if not getattr(settings, "ENABLE_SAKA", False):
        return Response(
            {"ok": False, "reason": "saka_disabled"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    rate = request.data.get("rate")
    if rate is not None:
        try:
            rate = float(rate)
        except (ValueError, TypeError):
            return Response(
                {"ok": False, "reason": "invalid_rate"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    try:
        from core.services.saka import redistribute_saka_silo
        result = redistribute_saka_silo(rate=rate)
        
        if result["ok"]:
            return Response(result, status=status.HTTP_200_OK)
        else:
            # Retourner 400 pour les erreurs de validation, 500 pour les erreurs serveur
            http_status = status.HTTP_400_BAD_REQUEST if "reason" in result else status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response(result, status=http_status)
    except Exception as e:
        return Response(
            {"ok": False, "reason": f"error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


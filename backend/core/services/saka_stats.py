"""
Services de statistiques et monitoring pour le Protocole SAKA 🌾
KPIs et métriques pour l'administration
"""
from django.db.models import Sum, Count, Q, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from typing import Dict, List
from django.conf import settings

from core.models.saka import SakaWallet, SakaTransaction, SakaSilo, SakaCycle, SakaCompostLog
from core.models.projects import Projet


def get_saka_global_stats() -> Dict:
    """
    Retourne les statistiques globales du protocole SAKA.
    
    Returns:
        dict: {
            "total_users_with_saka": int,
            "total_balance": int,
            "avg_balance": float,
            "total_earned": int,
            "total_spent": int,
            "total_composted": int,
        }
    """
    # Total d'utilisateurs avec SAKA (balance > 0)
    total_users_with_saka = SakaWallet.objects.filter(balance__gt=0).count()
    
    # Total de balance (somme de tous les wallets)
    total_balance_result = SakaWallet.objects.aggregate(
        total=Sum('balance')
    )
    total_balance = total_balance_result['total'] or 0
    
    # Moyenne de balance
    total_users = SakaWallet.objects.count()
    avg_balance = float(total_balance) / max(total_users, 1)
    
    # Total récolté (EARN)
    total_earned_result = SakaTransaction.objects.filter(
        direction='EARN'
    ).aggregate(
        total=Sum('amount')
    )
    total_earned = total_earned_result['total'] or 0
    
    # Total dépensé (SPEND)
    total_spent_result = SakaTransaction.objects.filter(
        direction='SPEND'
    ).aggregate(
        total=Sum('amount')
    )
    total_spent = total_spent_result['total'] or 0
    
    # Total composté (via SakaSilo ou transactions reason="compost")
    try:
        silo = SakaSilo.objects.get(id=1)
        total_composted = silo.total_composted
    except SakaSilo.DoesNotExist:
        # Fallback : somme des transactions compost
        compost_result = SakaTransaction.objects.filter(
            direction='SPEND',
            reason='compost'
        ).aggregate(
            total=Sum('amount')
        )
        total_composted = compost_result['total'] or 0
    
    return {
        "total_users_with_saka": total_users_with_saka,
        "total_balance": total_balance,
        "avg_balance": round(avg_balance, 2),
        "total_earned": total_earned,
        "total_spent": total_spent,
        "total_composted": total_composted,
    }


def get_saka_daily_stats(days: int = 30) -> List[Dict]:
    """
    Retourne les statistiques journalières pour les N derniers jours.
    
    Args:
        days: Nombre de jours à analyser (défaut: 30)
        
    Returns:
        list: [
            {
                "date": "YYYY-MM-DD",
                "earned": int,
                "spent": int,
                "net": int,
            },
            ...
        ]
    """
    cutoff = timezone.now() - timedelta(days=days)
    
    # Agrégation par date pour EARN
    earned_by_date = (
        SakaTransaction.objects
        .filter(direction='EARN', created_at__gte=cutoff)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(earned=Sum('amount'))
        .order_by('date')
    )
    
    # Agrégation par date pour SPEND
    spent_by_date = (
        SakaTransaction.objects
        .filter(direction='SPEND', created_at__gte=cutoff)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(spent=Sum('amount'))
        .order_by('date')
    )
    
    # Créer un dictionnaire pour faciliter la fusion
    earned_dict = {item['date']: item['earned'] for item in earned_by_date}
    spent_dict = {item['date']: item['spent'] for item in spent_by_date}
    
    # Fusionner les dates
    all_dates = set(earned_dict.keys()) | set(spent_dict.keys())
    
    # Construire la liste de résultats
    daily_stats = []
    for date in sorted(all_dates):
        if date:  # Ignorer les dates None
            earned = earned_dict.get(date, 0)
            spent = spent_dict.get(date, 0)
            daily_stats.append({
                "date": date.strftime("%Y-%m-%d"),
                "earned": earned,
                "spent": spent,
                "net": earned - spent,
            })
    
    return daily_stats


def get_top_saka_users(limit: int = 10) -> List[Dict]:
    """
    Retourne le top N des utilisateurs SAKA (par total récolté).
    
    Args:
        limit: Nombre d'utilisateurs à retourner (défaut: 10)
        
    Returns:
        list: [
            {
                "user_id": int,
                "username": str,
                "total_harvested": int,
                "total_planted": int,
                "balance": int,
            },
            ...
        ]
    """
    # Utiliser les champs agrégés de SakaWallet
    top_wallets = (
        SakaWallet.objects
        .select_related('user')
        .filter(total_harvested__gt=0)
        .order_by('-total_harvested')[:limit]
    )
    
    top_users = []
    for wallet in top_wallets:
        top_users.append({
            "user_id": wallet.user.id,
            "username": wallet.user.username,
            "total_harvested": wallet.total_harvested,
            "total_planted": wallet.total_planted,
            "balance": wallet.balance,
        })
    
    return top_users


def get_top_saka_projects(limit: int = 10) -> List[Dict]:
    """
    Retourne le top N des projets nourris avec SAKA.
    
    Args:
        limit: Nombre de projets à retourner (défaut: 10)
        
    Returns:
        list: [
            {
                "project_id": int,
                "name": str,
                "saka_nourished": int,
                "supporters_count": int | None,
            },
            ...
        ]
    """
    # Utiliser le champ saka_score du modèle Projet (plus simple et performant)
    # Le saka_score est mis à jour à chaque boost via l'API
    top_projects = (
        Projet.objects
        .filter(saka_score__gt=0)
        .order_by('-saka_score')[:limit]
    )
    
    top_projects_list = []
    for project in top_projects:
        # Utiliser directement project.saka_score qui est maintenu à jour
        # On pourrait aussi calculer depuis les transactions mais c'est moins performant
        # et le saka_score est déjà la source de vérité
        top_projects_list.append({
            "project_id": project.id,
            "name": project.titre,
            "saka_nourished": project.saka_score,
            "supporters_count": project.saka_supporters_count,
        })
    
    return top_projects_list


def get_cycle_stats(cycle: SakaCycle) -> Dict:
    """
    Retourne les statistiques SAKA pour un cycle donné.
    
    Args:
        cycle: Instance de SakaCycle
        
    Returns:
        dict: {
            "saka_harvested": int,  # Somme des transactions EARN sur la période
            "saka_planted": int,    # Somme des transactions SPEND sur la période
            "saka_composted": int,  # Somme des compost logs liés à ce cycle
        }
    """
    # Convertir les dates en datetime pour la comparaison avec created_at
    from django.utils import timezone
    from datetime import datetime, time
    
    start_datetime = timezone.make_aware(
        datetime.combine(cycle.start_date, time.min)
    )
    end_datetime = timezone.make_aware(
        datetime.combine(cycle.end_date, time.max)
    )
    
    # SAKA récolté (EARN) sur la période
    harvested_result = SakaTransaction.objects.filter(
        direction='EARN',
        created_at__gte=start_datetime,
        created_at__lte=end_datetime
    ).aggregate(total=Sum('amount'))
    saka_harvested = harvested_result['total'] or 0
    
    # SAKA planté (SPEND) sur la période
    planted_result = SakaTransaction.objects.filter(
        direction='SPEND',
        created_at__gte=start_datetime,
        created_at__lte=end_datetime
    ).aggregate(total=Sum('amount'))
    saka_planted = planted_result['total'] or 0
    
    # SAKA composté (via SakaCompostLog liés à ce cycle)
    composted_result = SakaCompostLog.objects.filter(
        cycle=cycle,
        dry_run=False  # Exclure les dry-runs
    ).aggregate(total=Sum('total_composted'))
    saka_composted = composted_result['total'] or 0
    
    return {
        "saka_harvested": saka_harvested,
        "saka_planted": saka_planted,
        "saka_composted": saka_composted,
    }


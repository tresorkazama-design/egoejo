"""
Service de métriques pour le protocole SAKA
Permet de suivre l'exécution du compostage et de la redistribution
"""
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from core.models.saka import (
    SakaWallet, SakaSilo, SakaCompostLog, SakaCycle, SakaTransaction
)


def get_compost_metrics(days=30):
    """
    Récupère les métriques de compostage sur les N derniers jours
    
    Returns:
        dict: Métriques de compostage
    """
    cutoff_date = timezone.now() - timedelta(days=days)
    
    # Compostages récents
    recent_composts = SakaCompostLog.objects.filter(created_at__gte=cutoff_date)
    
    total_composted = recent_composts.aggregate(Sum('amount'))['amount__sum'] or 0
    total_wallets_composted = recent_composts.values('wallet').distinct().count()
    compost_count = recent_composts.count()
    
    # Wallets éligibles au compostage (inactifs depuis 90+ jours)
    eligible_wallets = SakaWallet.objects.filter(
        last_activity_date__lt=timezone.now() - timedelta(days=90),
        balance__gte=10  # Minimum pour être composté
    ).count()
    
    return {
        'period_days': days,
        'total_composted': total_composted,
        'total_wallets_composted': total_wallets_composted,
        'compost_count': compost_count,
        'eligible_wallets': eligible_wallets,
        'average_per_compost': total_composted / compost_count if compost_count > 0 else 0,
    }


def get_redistribution_metrics(days=90):
    """
    Récupère les métriques de redistribution sur les N derniers jours
    
    Returns:
        dict: Métriques de redistribution
    """
    cutoff_date = timezone.now() - timedelta(days=days)
    
    # Redistributions récentes
    recent_redistributions = SakaTransaction.objects.filter(
        transaction_type='REDISTRIBUTION',
        created_at__gte=cutoff_date
    )
    
    total_redistributed = recent_redistributions.aggregate(Sum('amount'))['amount__sum'] or 0
    total_wallets_credited = recent_redistributions.values('wallet').distinct().count()
    redistribution_count = recent_redistributions.count()
    
    return {
        'period_days': days,
        'total_redistributed': total_redistributed,
        'total_wallets_credited': total_wallets_credited,
        'redistribution_count': redistribution_count,
        'average_per_wallet': total_redistributed / total_wallets_credited if total_wallets_credited > 0 else 0,
    }


def get_silo_metrics():
    """
    Récupère les métriques du Silo Commun
    
    Returns:
        dict: Métriques du Silo
    """
    silo = SakaSilo.objects.first()
    
    if not silo:
        return {
            'total_balance': 0,
            'total_composted': 0,
            'last_compost_at': None,
            'last_redistribution_at': None,
        }
    
    # Dernière redistribution
    last_redistribution = SakaTransaction.objects.filter(
        transaction_type='REDISTRIBUTION'
    ).order_by('-created_at').first()
    
    return {
        'total_balance': silo.total_balance,
        'total_composted': silo.total_composted,
        'last_compost_at': silo.last_compost_at,
        'last_redistribution_at': last_redistribution.created_at if last_redistribution else None,
    }


def get_global_saka_metrics():
    """
    Récupère les métriques globales du protocole SAKA
    
    Returns:
        dict: Métriques globales
    """
    wallets = SakaWallet.objects.all()
    
    total_harvested = wallets.aggregate(Sum('total_harvested'))['total_harvested__sum'] or 0
    total_planted = wallets.aggregate(Sum('total_planted'))['total_planted__sum'] or 0
    total_composted = wallets.aggregate(Sum('total_composted'))['total_composted__sum'] or 0
    total_balance = wallets.aggregate(Sum('balance'))['balance__sum'] or 0
    
    active_wallets = wallets.filter(balance__gt=0).count()
    inactive_wallets = wallets.filter(
        last_activity_date__lt=timezone.now() - timedelta(days=90)
    ).count()
    
    return {
        'total_harvested': total_harvested,
        'total_planted': total_planted,
        'total_composted': total_composted,
        'total_balance': total_balance,
        'active_wallets': active_wallets,
        'inactive_wallets': inactive_wallets,
        'total_wallets': wallets.count(),
    }


def get_cycle_metrics():
    """
    Récupère les métriques des cycles SAKA
    
    Returns:
        dict: Métriques des cycles
    """
    cycles = SakaCycle.objects.all().order_by('-start_date')
    
    total_cycles = cycles.count()
    total_harvested = cycles.aggregate(Sum('harvested_total'))['harvested_total__sum'] or 0
    total_planted = cycles.aggregate(Sum('planted_total'))['planted_total__sum'] or 0
    total_composted = cycles.aggregate(Sum('composted_total'))['composted_total__sum'] or 0
    
    last_cycle = cycles.first()
    
    return {
        'total_cycles': total_cycles,
        'total_harvested': total_harvested,
        'total_planted': total_planted,
        'total_composted': total_composted,
        'last_cycle': {
            'start_date': last_cycle.start_date if last_cycle else None,
            'end_date': last_cycle.end_date if last_cycle else None,
            'harvested': last_cycle.harvested_total if last_cycle else 0,
            'planted': last_cycle.planted_total if last_cycle else 0,
            'composted': last_cycle.composted_total if last_cycle else 0,
        } if last_cycle else None,
    }


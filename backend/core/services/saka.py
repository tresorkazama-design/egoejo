"""
Services pour le Protocole SAKA 🌾
Monnaie interne d'engagement (Yin) - Strictement séparée de l'Euro (Yang)

Phase 1 : Fondations - Services simplifiés avec anti-farming minimal
Phase 3 : Compostage & Silo Commun
"""
from django.db import transaction
from django.db import connection
from django.db.models import F, Q
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from enum import Enum
from typing import Optional, Dict
from math import floor
import logging

from core.models.saka import SakaWallet, SakaTransaction, SakaSilo, SakaCompostLog, SakaCycle

logger = logging.getLogger(__name__)


class SakaReason(Enum):
    """Raisons de récolte/dépense SAKA"""
    CONTENT_READ = 'content_read'
    POLL_VOTE = 'poll_vote'
    INVITE_ACCEPTED = 'invite_accepted'
    INVEST_BONUS = 'invest_bonus'
    MANUAL_ADJUST = 'manual_adjust'


# Récompenses de base SAKA (grains)
SAKA_BASE_REWARDS = {
    SakaReason.CONTENT_READ: 10,
    SakaReason.POLL_VOTE: 5,
    SakaReason.INVITE_ACCEPTED: 50,
    SakaReason.INVEST_BONUS: 100,
    SakaReason.MANUAL_ADJUST: 0,  # Montant personnalisé requis
}

# Limites anti-farming (max par jour et par raison)
SAKA_DAILY_LIMITS = {
    SakaReason.CONTENT_READ: 3,  # Max 3 contenus par jour
    SakaReason.POLL_VOTE: 10,   # Max 10 votes par jour
    SakaReason.INVITE_ACCEPTED: 5,  # Max 5 invitations acceptées par jour
    SakaReason.INVEST_BONUS: 1,  # Max 1 bonus investissement par jour
    SakaReason.MANUAL_ADJUST: 0,  # Pas de limite (admin uniquement)
}


def is_saka_enabled():
    """Vérifie si le protocole SAKA est activé"""
    return getattr(settings, 'ENABLE_SAKA', False)


def get_or_create_wallet(user):
    """
    Récupère ou crée le portefeuille SAKA d'un utilisateur.
    
    Args:
        user: Utilisateur Django
        
    Returns:
        SakaWallet
    """
    if not is_saka_enabled():
        return None
    
    wallet, created = SakaWallet.objects.get_or_create(
        user=user,
        defaults={
            'balance': 0,
            'total_harvested': 0,
            'total_planted': 0,
            'total_composted': 0,
        }
    )
    return wallet


@transaction.atomic
def harvest_saka(
    user,
    reason: SakaReason,
    amount: Optional[int] = None,
    metadata: Optional[dict] = None
) -> Optional[SakaTransaction]:
    """
    Récolter des grains SAKA (Proof of Care).
    
    Applique un anti-farming minimal :
    - Limite de récompenses par jour et par raison
    - Ignore si utilisateur anonyme ou SAKA désactivé
    
    Args:
        user: Utilisateur qui récolte (doit être authentifié)
        reason: Raison de la récolte (SakaReason)
        amount: Montant personnalisé (optionnel, sinon utilise SAKA_BASE_REWARDS)
        metadata: Métadonnées supplémentaires (optionnel)
        
    Returns:
        SakaTransaction créée ou None si ignoré
        
    Raises:
        ValidationError: Si limite quotidienne atteinte
    """
    # Ignorer si SAKA désactivé ou utilisateur anonyme
    if not is_saka_enabled() or not user or user.is_anonymous:
        return None
    
    # Déterminer le montant
    if amount is None:
        amount = SAKA_BASE_REWARDS.get(reason, 0)
    
    if amount <= 0:
        return None
    
    # Récupérer ou créer le portefeuille avec select_for_update pour éviter les race conditions
    wallet = get_or_create_wallet(user)
    if not wallet:
        return None
    
    # Verrouiller le wallet pour éviter les race conditions
    wallet = SakaWallet.objects.select_for_update().get(id=wallet.id)
    
    # Anti-farming : vérifier la limite quotidienne
    daily_limit = SAKA_DAILY_LIMITS.get(reason, 0)
    if daily_limit > 0:
        today = date.today()
        # Compter les transactions existantes pour cette raison aujourd'hui
        # Utiliser Sum pour calculer le total déjà gagné aujourd'hui
        from django.db.models import Sum
        today_total = SakaTransaction.objects.filter(
            user=user,
            direction='EARN',
            reason=reason.value,
            created_at__date=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculer la limite restante (en nombre de transactions, pas en montant)
        # On compte le nombre de transactions, pas le montant total
        today_count = SakaTransaction.objects.filter(
            user=user,
            direction='EARN',
            reason=reason.value,
            created_at__date=today
        ).count()
        
        logger.debug(
            f"Vérification limite SAKA pour {user.username}: "
            f"{reason.value} - {today_count}/{daily_limit} transactions aujourd'hui "
            f"(total gagné: {today_total} grains)"
        )
        
        # Si la limite est atteinte, ne rien créditer
        if today_count >= daily_limit:
            logger.warning(
                f"Limite quotidienne SAKA atteinte pour {user.username}: "
                f"{reason.value} ({today_count}/{daily_limit})"
            )
            return None
        
        # Calculer le montant effectif à créditer (limite restante)
        # Pour simplifier, on crédite le montant complet si la limite n'est pas atteinte
        # amount_effective = amount (pas de réduction partielle)
    
    # Mettre à jour le portefeuille
    wallet.balance += amount
    wallet.total_harvested += amount
    wallet.last_activity_date = timezone.now()
    wallet.save()
    
    # Créer la transaction
    saka_transaction = SakaTransaction.objects.create(
        user=user,
        direction='EARN',
        amount=amount,
        reason=reason.value,
        metadata=metadata or {}
    )
    
    logger.info(
        f"SAKA récolté : {user.username} - {amount} grains - {reason.value}"
    )
    
    return saka_transaction


@transaction.atomic
def spend_saka(
    user,
    amount: int,
    reason: str,
    metadata: Optional[dict] = None
) -> bool:
    """
    Dépenser des grains SAKA.
    
    SÉCURISÉ CONTRE LES RACE CONDITIONS :
    - Utilise select_for_update() pour verrouiller le wallet
    - Utilise F() expressions pour les mises à jour atomiques
    - Vérifie le solde après verrouillage
    
    Args:
        user: Utilisateur qui dépense (doit être authentifié)
        amount: Nombre de grains SAKA à dépenser
        reason: Raison de la dépense (ex: 'vote_boost', 'project_boost')
        metadata: Métadonnées supplémentaires (optionnel)
        
    Returns:
        True si la dépense a réussi, False sinon
    """
    # Ignorer si SAKA désactivé, utilisateur anonyme ou montant invalide
    if not is_saka_enabled() or not user or user.is_anonymous or amount <= 0:
        return False
    
    # Récupérer ou créer le portefeuille avec verrouillage
    wallet = get_or_create_wallet(user)
    if not wallet:
        return False
    
    # Verrouiller le wallet pour éviter les race conditions
    wallet = SakaWallet.objects.select_for_update().get(id=wallet.id)
    
    # Vérifier le solde après verrouillage (lecture atomique)
    if wallet.balance < amount:
        logger.warning(
            f"Solde SAKA insuffisant pour {user.username}: "
            f"{wallet.balance} < {amount}"
        )
        return False
    
    # Mettre à jour le portefeuille avec F() expressions pour garantir l'atomicité
    from django.db.models import F
    SakaWallet.objects.filter(id=wallet.id).update(
        balance=F('balance') - amount,
        total_planted=F('total_planted') + amount,
        last_activity_date=timezone.now()
    )
    
    # Créer la transaction
    SakaTransaction.objects.create(
        user=user,
        direction='SPEND',
        amount=amount,
        reason=reason,
        metadata=metadata or {}
    )
    
    logger.info(
        f"SAKA dépensé : {user.username} - {amount} grains - {reason}"
    )
    
    return True


def get_saka_balance(user) -> dict:
    """
    Récupère le solde SAKA d'un utilisateur.
    
    Args:
        user: Utilisateur Django
        
    Returns:
        dict: {
            'balance': int,
            'total_harvested': int,
            'total_planted': int,
            'total_composted': int
        }
    """
    if not is_saka_enabled() or not user or user.is_anonymous:
        return {
            'balance': 0,
            'total_harvested': 0,
            'total_planted': 0,
            'total_composted': 0,
        }
    
    wallet = get_or_create_wallet(user)
    if not wallet:
        return {
            'balance': 0,
            'total_harvested': 0,
            'total_planted': 0,
            'total_composted': 0,
        }
    
    return {
        'balance': wallet.balance,
        'total_harvested': wallet.total_harvested,
        'total_planted': wallet.total_planted,
        'total_composted': wallet.total_composted,
    }


def run_saka_compost_cycle(dry_run: bool = False, source: str = "celery") -> Dict:
    """
    Parcourt les SakaWallet inactifs et composte une partie des balances
    vers le Silo Commun, selon la règle de démurrage.
    
    Phase 3 : Compostage & Silo Commun - Audit Log
    
    Args:
        dry_run: Si True, calcule seulement ce qui serait fait (aucune écriture)
        source: Source du déclenchement (ex: "celery", "admin", "management_command")
        
    Returns:
        dict: {
            "cycles": int,  # Nombre de cycles exécutés (0 si dry_run)
            "wallets_affected": int,  # Nombre de wallets affectés
            "total_composted": int,  # Total de grains compostés
            "skipped": str (optionnel)  # Raison si désactivé
        }
    """
    if not getattr(settings, "SAKA_COMPOST_ENABLED", False):
        return {
            "cycles": 0,
            "wallets_affected": 0,
            "total_composted": 0,
            "skipped": "disabled"
        }
    
    inactivity_days = getattr(settings, "SAKA_COMPOST_INACTIVITY_DAYS", 90)
    rate = float(getattr(settings, "SAKA_COMPOST_RATE", 0.1))
    min_balance = getattr(settings, "SAKA_COMPOST_MIN_BALANCE", 50)
    min_amount = getattr(settings, "SAKA_COMPOST_MIN_AMOUNT", 10)
    
    # Récupérer le cycle actif (si disponible)
    active_cycle = None
    try:
        active_cycle = SakaCycle.objects.filter(is_active=True).first()
    except Exception:
        # Ignorer si SakaCycle n'existe pas encore ou erreur
        pass
    
    # Créer le log d'audit au début
    log_entry = SakaCompostLog.objects.create(
        cycle=active_cycle,
        dry_run=dry_run,
        inactivity_days=inactivity_days,
        rate=rate,
        min_balance=min_balance,
        min_amount=min_amount,
        source=source,
    )
    
    cutoff = timezone.now() - timedelta(days=inactivity_days)
    
    # Sélectionner les wallets inactifs avec balance suffisante
    qs = SakaWallet.objects.select_for_update().filter(
        last_activity_date__lt=cutoff,
        balance__gte=min_balance,
    )
    
    total_composted = 0
    affected = 0
    
    with transaction.atomic():
        # Récupérer ou créer le Silo Commun (singleton)
        silo, _ = SakaSilo.objects.select_for_update().get_or_create(
            id=1,
            defaults={
                'total_balance': 0,
                'total_composted': 0,
                'total_cycles': 0,
            }
        )
        
        for wallet in qs:
            # Calcul du montant à composter
            raw_amount = wallet.balance * rate
            amount = int(floor(raw_amount))
            
            if amount < min_amount:
                continue
            
            if dry_run:
                total_composted += amount
                affected += 1
                continue
            
            # Mise à jour du wallet
            wallet.balance -= amount
            wallet.total_composted += amount
            wallet.last_activity_date = timezone.now()  # Réinitialiser la date d'activité
            wallet.save(update_fields=["balance", "total_composted", "last_activity_date"])
            
            # Créer la transaction SAKA
            SakaTransaction.objects.create(
                user=wallet.user,
                direction='SPEND',
                amount=amount,
                reason='compost',
                metadata={
                    "source": "compost_cycle",
                    "cutoff": cutoff.isoformat(),
                    "rate": rate,
                },
            )
            
            # Mise à jour du silo
            silo.total_balance += amount
            silo.total_composted += amount
            total_composted += amount
            affected += 1
        
        if not dry_run and affected > 0:
            silo.total_cycles += 1
            silo.last_compost_at = timezone.now()
            silo.save(update_fields=[
                "total_balance",
                "total_composted",
                "total_cycles",
                "last_compost_at"
            ])
    
    # Mettre à jour le log d'audit à la fin
    log_entry.wallets_affected = affected
    log_entry.total_composted = total_composted
    log_entry.finished_at = timezone.now()
    log_entry.save(update_fields=["wallets_affected", "total_composted", "finished_at"])
    
    logger.info(
        f"SAKA compost cycle {'(dry-run)' if dry_run else ''} completed: "
        f"{affected} wallets affected, {total_composted} SAKA composted. "
        f"Log ID: {log_entry.id}"
    )
    return {
        "cycles": 1 if not dry_run and affected > 0 else 0,
        "wallets_affected": affected,
        "total_composted": total_composted,
        "dry_run": dry_run,
        "log_id": log_entry.id,  # Retourner l'ID du log pour traçabilité
    }


def get_user_compost_preview(user) -> Dict:
    """
    Retourne une estimation de la quantité de SAKA qui serait compostée pour cet utilisateur
    s'il restait inactif jusqu'au prochain cycle.
    
    Phase 3 : Compostage & Silo Commun
    
    Args:
        user: Utilisateur Django
        
    Returns:
        dict: {
            "eligible": bool,  # Si l'utilisateur est éligible au compostage
            "amount": int,  # Montant estimé qui serait composté
            "days_until_eligible": int (optionnel),  # Jours restants avant éligibilité
        }
    """
    if not getattr(settings, "SAKA_COMPOST_ENABLED", False):
        return {"eligible": False, "amount": 0}
    
    try:
        wallet = user.saka_wallet
    except SakaWallet.DoesNotExist:
        return {"eligible": False, "amount": 0}
    
    inactivity_days = getattr(settings, "SAKA_COMPOST_INACTIVITY_DAYS", 90)
    rate = float(getattr(settings, "SAKA_COMPOST_RATE", 0.1))
    min_balance = getattr(settings, "SAKA_COMPOST_MIN_BALANCE", 50)
    min_amount = getattr(settings, "SAKA_COMPOST_MIN_AMOUNT", 10)
    
    if wallet.balance < min_balance:
        return {"eligible": False, "amount": 0}
    
    # Calculer le montant qui serait composté
    raw_amount = wallet.balance * rate
    amount = int(floor(raw_amount))
    
    if amount < min_amount:
        return {"eligible": False, "amount": 0}
    
    # Calculer les jours restants avant éligibilité
    if wallet.last_activity_date:
        days_since_activity = (timezone.now() - wallet.last_activity_date).days
        days_until_eligible = max(0, inactivity_days - days_since_activity)
    else:
        # Si jamais d'activité, considérer comme éligible immédiatement
        days_until_eligible = 0
    
    return {
        "eligible": days_until_eligible == 0,
        "amount": amount,
        "days_until_eligible": days_until_eligible,
    }


def redistribute_saka_silo(rate: float | None = None) -> Dict:
    """
    Redistribue une partie du Silo SAKA vers les wallets éligibles.
    
    Règle V1 :
    - On prend rate (ou SAKA_SILO_REDIS_RATE).
    - On calcule total_to_redistribute = floor(silo.total_balance * rate).
    - On sélectionne les wallets avec total_harvested >= MIN_ACTIVITY.
    - On répartit de façon égale (division entière).
    
    Retourne un dict avec :
    {
      "ok": bool,
      "total_before": int,
      "total_after": int,
      "redistributed": int,
      "per_wallet": int,
      "eligible_wallets": int,
      "reason": str (si ok=False)
    }
    """
    if not getattr(settings, "SAKA_SILO_REDIS_ENABLED", False):
        return {
            "ok": False,
            "reason": "redistribution_disabled",
        }
    
    from math import floor
    
    if rate is None:
        rate = float(getattr(settings, "SAKA_SILO_REDIS_RATE", 0.05))
    
    min_activity = int(getattr(settings, "SAKA_SILO_REDIS_MIN_WALLET_ACTIVITY", 1))
    
    try:
        with transaction.atomic():
            # Verrouiller le Silo pour éviter les races
            silo = SakaSilo.objects.select_for_update().first()
            
            if not silo:
                return {
                    "ok": False,
                    "reason": "no_silo",
                }
            
            total_before = silo.total_balance or 0
            if total_before <= 0 or rate <= 0:
                return {
                    "ok": False,
                    "reason": "nothing_to_redistribute",
                    "total_before": total_before,
                }
            
            total_to_redistribute = int(floor(total_before * rate))
            if total_to_redistribute <= 0:
                return {
                    "ok": False,
                    "reason": "too_small_to_redistribute",
                    "total_before": total_before,
                }
            
            # Wallets éligibles : ont déjà récolté au moins min_activity grains
            eligible_qs = (
                SakaWallet.objects
                .select_for_update()
                .filter(total_harvested__gte=min_activity)
            )
            eligible_count = eligible_qs.count()
            if eligible_count == 0:
                return {
                    "ok": False,
                    "reason": "no_eligible_wallets",
                    "total_before": total_before,
                    "redistributed": 0,
                }
            
            per_wallet = total_to_redistribute // eligible_count
            if per_wallet <= 0:
                # Si trop peu à distribuer, on n'éparpille pas
                return {
                    "ok": False,
                    "reason": "insufficient_per_wallet",
                    "total_before": total_before,
                    "redistributed": 0,
                    "eligible_wallets": eligible_count,
                }
            
            # Mise à jour des wallets avec F() expressions (atomique via update())
            wallet_ids = list(eligible_qs.values_list('id', flat=True))
            SakaWallet.objects.filter(id__in=wallet_ids).update(
                balance=F('balance') + per_wallet,
                total_harvested=F('total_harvested') + per_wallet,
                last_activity_date=timezone.now()
            )
            
            # Créer les transactions SAKA pour audit
            transactions_to_create = []
            for wallet in eligible_qs:
                transactions_to_create.append(
                    SakaTransaction(
                        user=wallet.user,
                        direction='EARN',  # Utiliser string, pas SakaTransaction.EARN
                        amount=per_wallet,
                        reason='silo_redistribution',
                        metadata={}
                    )
                )
            
            # Créer toutes les transactions en bulk
            SakaTransaction.objects.bulk_create(transactions_to_create)
            
            # Mise à jour du Silo avec F() expressions (atomique via update())
            actual_redistributed = per_wallet * eligible_count
            SakaSilo.objects.filter(id=silo.id).update(
                total_balance=F('total_balance') - actual_redistributed
            )
            
            logger.info(
                f"Redistribution SAKA Silo : {actual_redistributed} grains "
                f"distribués à {eligible_count} wallets "
                f"({per_wallet} grains chacun). "
                f"Silo : {total_before} → {total_before - actual_redistributed}"
            )
        
        # Rechargement en dehors du bloc transaction pour renvoyer les valeurs réelles
        silo.refresh_from_db()
        return {
            "ok": True,
            "total_before": total_before,
            "total_after": silo.total_balance,
            "redistributed": per_wallet * eligible_count,
            "per_wallet": per_wallet,
            "eligible_wallets": eligible_count,
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la redistribution du Silo SAKA : {e}", exc_info=True)
        return {
            "ok": False,
            "reason": f"error: {str(e)}",
        }

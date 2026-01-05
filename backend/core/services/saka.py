"""
Services pour le Protocole SAKA 🌾
Monnaie interne d'engagement (Yin) - Strictement séparée de l'Euro (Yang)

Phase 1 : Fondations - Services simplifiés avec anti-farming minimal
Phase 3 : Compostage & Silo Commun
OPTIMISATION RÉSILIENCE : Utilisation de tenacity pour retries intelligents.
"""
from django.db import transaction
from django.db import connection
from django.db.models import F, Q
from django.db.utils import OperationalError
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from enum import Enum
from typing import Optional, Dict
from math import floor
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_none,
    retry_if_exception_type,
    before_sleep_log,
    after_log,
)

from core.models.saka import SakaWallet, SakaTransaction, SakaSilo, SakaCompostLog, SakaCycle, AllowSakaMutation

logger = logging.getLogger(__name__)

# OPTIMISATION CPU : Helper functions pour lire les settings (compatible avec override_settings dans les tests)
# Ces fonctions lisent les settings à chaque appel, mais sont optimisées pour la production
def _get_saka_compost_enabled():
    """Helper pour lire SAKA_COMPOST_ENABLED (compatible avec override_settings)"""
    return getattr(settings, "SAKA_COMPOST_ENABLED", False)

def _get_saka_compost_inactivity_days():
    """Helper pour lire SAKA_COMPOST_INACTIVITY_DAYS (compatible avec override_settings)"""
    return getattr(settings, "SAKA_COMPOST_INACTIVITY_DAYS", 90)

def _read_compost_rate():
    """Helper pour lire SAKA_COMPOST_RATE (compatible avec override_settings)"""
    return float(getattr(settings, "SAKA_COMPOST_RATE", 0.1))

def _get_saka_compost_min_balance():
    """Helper pour lire SAKA_COMPOST_MIN_BALANCE (compatible avec override_settings)"""
    return getattr(settings, "SAKA_COMPOST_MIN_BALANCE", 50)

def _get_saka_compost_min_amount():
    """Helper pour lire SAKA_COMPOST_MIN_AMOUNT (compatible avec override_settings)"""
    return getattr(settings, "SAKA_COMPOST_MIN_AMOUNT", 10)

def _get_saka_silo_redis_enabled():
    """Helper pour lire SAKA_SILO_REDIS_ENABLED (compatible avec override_settings)"""
    return getattr(settings, "SAKA_SILO_REDIS_ENABLED", False)

def _read_silo_redis_rate():
    """Helper pour lire SAKA_SILO_REDIS_RATE (compatible avec override_settings)"""
    return float(getattr(settings, "SAKA_SILO_REDIS_RATE", 0.05))

def _get_saka_silo_redis_min_wallet_activity():
    """Helper pour lire SAKA_SILO_REDIS_MIN_WALLET_ACTIVITY (compatible avec override_settings)"""
    return int(getattr(settings, "SAKA_SILO_REDIS_MIN_WALLET_ACTIVITY", 1))

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
    SakaReason.MANUAL_ADJUST: 0,  # Limite gérée séparément (voir harvest_saka)
}

# Limites spécifiques pour MANUAL_ADJUST (Constitution EGOEJO: anti-accumulation)
MANUAL_ADJUST_DAILY_LIMIT = 1000  # Max 1000 SAKA/jour/utilisateur (même pour admin)
MANUAL_ADJUST_DUAL_APPROVAL_THRESHOLD = 500  # Montants > 500 nécessitent double validation


def is_saka_enabled():
    """
    Vérifie si le protocole SAKA est activé.
    
    NOTE: Lit settings à chaque appel pour être compatible avec override_settings dans les tests.
    """
    return getattr(settings, 'ENABLE_SAKA', False)


MAX_RETRIES_SAKA = 3


@retry(
    stop=stop_after_attempt(MAX_RETRIES_SAKA),
    wait=wait_none(),  # Pas d'attente : la DB gère les verrous, on ne dort pas avec un verrou
    retry=retry_if_exception_type(OperationalError),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    after=after_log(logger, logging.CRITICAL),
    reraise=True,
)
def _get_or_create_wallet_with_retry(user):
    """
    Wrapper interne avec retry pour get_or_create_wallet.
    
    OPTIMISATION RÉSILIENCE : Utilisation de tenacity avec wait_none() pour éviter de dormir avec un verrou.
    """
    # OPTIMISATION CONCURRENCE : select_for_update() pour éviter race condition
    wallet, created = SakaWallet.objects.select_for_update().get_or_create(
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
def get_or_create_wallet(user):
    """
    Récupère ou crée le portefeuille SAKA d'un user.
    
    OPTIMISATION CONCURRENCE :
    - Utilise select_for_update() pour éviter la création de doublons sous forte charge
    - Gestion deadlocks avec retry intelligent (tenacity)
    
    Args:
        user: Utilisateur Django
        
    Returns:
        SakaWallet ou None si SAKA désactivé
    """
    if not is_saka_enabled():
        return None
    
    return _get_or_create_wallet_with_retry(user)


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
    - Ignore si user anonyme ou SAKA désactivé
    
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
    # Ignorer si SAKA désactivé ou user anonyme
    if not is_saka_enabled() or not user or user.is_anonymous:
        return None
    
    # Déterminer le montant
    if amount is None:
        amount = SAKA_BASE_REWARDS.get(reason, 0)
    
    if amount <= 0:
        return None
    
    # PROTECTION CONSTITUTION EGOEJO : Limites spécifiques pour MANUAL_ADJUST
    # Constitution: no direct SAKA mutation - Anti-accumulation stricte
    # Vérification AVANT le verrouillage pour éviter de verrouiller inutilement
    if reason == SakaReason.MANUAL_ADJUST:
        # BLOCAGE STRICT : Toute transaction unique > 500 SAKA est refusée
        # Constitution EGOEJO: Anti-accumulation - Aucun minting arbitraire autorisé
        if amount > MANUAL_ADJUST_DUAL_APPROVAL_THRESHOLD:
            error_msg = (
                f"VIOLATION CONSTITUTION EGOEJO : MANUAL_ADJUST > {MANUAL_ADJUST_DUAL_APPROVAL_THRESHOLD} SAKA est strictement interdit. "
                f"Montant demandé: {amount} SAKA. "
                f"Seuil maximum par transaction: {MANUAL_ADJUST_DUAL_APPROVAL_THRESHOLD} SAKA. "
                f"Cette opération est refusée pour garantir l'anti-accumulation. "
                f"Aucun mécanisme de double validation n'est disponible. "
                f"Pour des montants supérieurs, utilisez plusieurs transactions de {MANUAL_ADJUST_DUAL_APPROVAL_THRESHOLD} SAKA maximum, "
                f"sous réserve de la limite quotidienne de {MANUAL_ADJUST_DAILY_LIMIT} SAKA/jour."
            )
            logger.critical(error_msg)
            raise ValidationError(error_msg)
    
    # CORRECTION RACE CONDITION : Verrouiller le wallet DIRECTEMENT avec get_or_create
    # Évite la race condition où deux requêtes créent le wallet simultanément
    # et où la vérification de limite se fait avant le verrouillage
    wallet, created = SakaWallet.objects.select_for_update().get_or_create(
        user=user,
        defaults={
            'balance': 0,
            'total_harvested': 0,
            'total_planted': 0,
            'total_composted': 0,
        }
    )
    
    # PROTECTION CONSTITUTION EGOEJO : Hard Cap Quotidien sur 24h (Anti-Accumulation)
    # (pour MANUAL_ADJUST, vérification après verrouillage pour garantir l'atomicité)
    # IMPORTANT: Utiliser select_for_update() sur les transactions pour voir les transactions
    # non commitées dans la même transaction atomique
    if reason == SakaReason.MANUAL_ADJUST:
        from django.db.models import Sum
        
        # HARD CAP : Vérifier la somme des MANUAL_ADJUST sur les dernières 24h
        # Constitution EGOEJO: Anti-accumulation stricte - Impossible de contourner avec plusieurs transactions
        # Utiliser timezone.now() - timedelta(hours=24) pour vérifier les 24 dernières heures
        # (plus robuste que created_at__date=today qui peut être contourné en changeant de jour)
        cutoff_24h = timezone.now() - timedelta(hours=24)
        
        # Vérifier la limite sur 24h (1000 SAKA/24h/utilisateur, même pour admin)
        # Vérification APRÈS verrouillage pour garantir l'atomicité
        # Utiliser select_for_update() pour voir les transactions non commitées dans la même transaction
        last_24h_total_manual = SakaTransaction.objects.select_for_update().filter(
            user=user,
            direction='EARN',
            reason=SakaReason.MANUAL_ADJUST.value,
            created_at__gte=cutoff_24h  # Dernières 24h (plus robuste que created_at__date=today)
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Vérifier si le montant demandé dépasse la limite quotidienne (hard cap)
        # Utiliser >= (strict) pour bloquer si atteint ou dépasse
        if last_24h_total_manual + amount > MANUAL_ADJUST_DAILY_LIMIT:
            error_msg = (
                f"Limite de sécurité atteinte. Impossible de créer plus de {MANUAL_ADJUST_DAILY_LIMIT} SAKA/jour manuellement. "
                f"Limite: {MANUAL_ADJUST_DAILY_LIMIT} SAKA/24h/utilisateur (même pour admin). "
                f"Déjà crédité dans les 24 dernières heures: {last_24h_total_manual} SAKA. "
                f"Montant demandé: {amount} SAKA. "
                f"Total serait: {last_24h_total_manual + amount} SAKA (dépasse de {last_24h_total_manual + amount - MANUAL_ADJUST_DAILY_LIMIT} SAKA). "
                f"Constitution EGOEJO: Anti-accumulation stricte - Aucun minting arbitraire autorisé."
            )
            logger.critical(error_msg)
            raise ValidationError(error_msg)
    
    # Anti-farming : vérifier la limite quotidienne APRÈS verrouillage
    # (dans la même transaction pour éviter double crédit)
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
    
    # Mettre à jour le portefeuille (avec autorisation via contexte)
    with AllowSakaMutation():
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
        transaction_type='HARVEST',
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
    # Ignorer si SAKA désactivé, user anonyme ou montant invalide
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
    # (avec autorisation via contexte)
    from django.db.models import F
    with AllowSakaMutation():
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
        transaction_type='SPEND',
        metadata=metadata or {}
    )
    
    logger.info(
        f"SAKA dépensé : {user.username} - {amount} grains - {reason}"
    )
    
    return True


def get_saka_balance(user) -> dict:
    """
    Récupère le solde SAKA d'un user.
    
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
    # CORRECTION COMPLIANCE : Utiliser helper functions pour compatibilité avec override_settings
    if not _get_saka_compost_enabled():
        return {
            "cycles": 0,
            "wallets_affected": 0,
            "total_composted": 0,
            "skipped": "disabled"
        }
    
    # CORRECTION COMPLIANCE : Utiliser helper functions pour compatibilité avec override_settings
    inactivity_days = _get_saka_compost_inactivity_days()
    rate = _read_compost_rate()
    min_balance = _get_saka_compost_min_balance()
    min_amount = _get_saka_compost_min_amount()
    
    # Récupérer le cycle actif (si disponible)
    active_cycle = None
    try:
        active_cycle = SakaCycle.objects.filter(is_active=True).first()
    except Exception:
        # Ignorer si SakaCycle n'existe pas encore ou exception
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
    
    # OPTIMISATION : Sélectionner les wallets inactifs SANS select_for_update() sur le QuerySet principal
    # (évite le verrouillage massif qui peut causer des deadlocks)
    # On utilisera bulk_update() qui est atomique sans verrouillage lourd
    # CORRECTION COMPLIANCE : Inclure les wallets avec last_activity_date=None (jamais d'activité = éligible)
    from django.db.models import Q
    qs = SakaWallet.objects.filter(
        Q(last_activity_date__isnull=True) | Q(last_activity_date__lt=cutoff),
        balance__gte=min_balance,
    )
    
    total_composted = 0
    affected = 0
    
    # OPTIMISATION : Chunking pour éviter les timeouts (500 wallets par lot)
    BATCH_SIZE = 500
    
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
        
        # OPTIMISATION : Traiter par chunks pour éviter les timeouts
        offset = 0
        while True:
            # Récupérer un chunk de wallets (seulement les champs nécessaires)
            chunk = list(qs[offset:offset + BATCH_SIZE].only('id', 'balance', 'total_composted', 'user_id'))
            
            if not chunk:
                break
            
            # Préparer les mises à jour et transactions en batch
            wallets_to_update = []
            transactions_to_create = []
            chunk_composted = 0
            chunk_affected = 0
            
            for wallet in chunk:
                # Calcul du montant à composter
                raw_amount = wallet.balance * rate
                amount = int(floor(raw_amount))
                
                if amount < min_amount:
                    continue
                
                if dry_run:
                    chunk_composted += amount
                    chunk_affected += 1
                    continue
                
                # OPTIMISATION : Préparer la mise à jour en batch
                wallet.balance -= amount
                wallet.total_composted += amount
                wallet.last_activity_date = timezone.now()
                wallets_to_update.append(wallet)
                
                # OPTIMISATION : Préparer la transaction en batch
                transactions_to_create.append(
                    SakaTransaction(
                        user_id=wallet.user_id,  # Utiliser user_id directement (plus efficace)
                        direction='SPEND',
                        amount=amount,
                        reason='compost',
                        transaction_type='COMPOST',
                        metadata={
                            "source": "compost_cycle",
                            "cutoff": cutoff.isoformat(),
                            "rate": rate,
                        },
                    )
                )
                
                chunk_composted += amount
                chunk_affected += 1
            
            # OPTIMISATION : Bulk update des wallets (1 requête au lieu de N)
            # (avec autorisation via contexte)
            if wallets_to_update:
                with AllowSakaMutation():
                    SakaWallet.objects.bulk_update(
                        wallets_to_update,
                        ['balance', 'total_composted', 'last_activity_date'],
                        batch_size=BATCH_SIZE
                    )
            
            # OPTIMISATION : Bulk create des transactions (1 requête au lieu de N)
            if transactions_to_create:
                SakaTransaction.objects.bulk_create(
                    transactions_to_create,
                    batch_size=BATCH_SIZE
                )
            
            # Accumuler les montants pour mise à jour finale du silo
            total_composted += chunk_composted
            affected += chunk_affected
            
            offset += BATCH_SIZE
        
        # Mise à jour finale du silo (une seule fois, après tous les chunks)
        if not dry_run and total_composted > 0:
            silo.total_balance += total_composted
            silo.total_composted += total_composted
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
    Retourne une estimation de la quantité de SAKA qui serait compostée pour ce user
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
    # CORRECTION COMPLIANCE : Utiliser helper functions pour compatibilité avec override_settings
    if not _get_saka_compost_enabled():
        return {"eligible": False, "amount": 0}
    
    try:
        wallet = user.saka_wallet
    except SakaWallet.DoesNotExist:
        return {"eligible": False, "amount": 0}
    
    # CORRECTION COMPLIANCE : Utiliser helper functions pour compatibilité avec override_settings
    inactivity_days = _get_saka_compost_inactivity_days()
    rate = _read_compost_rate()
    min_balance = _get_saka_compost_min_balance()
    min_amount = _get_saka_compost_min_amount()
    
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
    # CORRECTION COMPLIANCE : Utiliser helper functions pour compatibilité avec override_settings
    if not _get_saka_silo_redis_enabled():
        return {
            "ok": False,
            "reason": "redistribution_disabled",
        }
    
    from math import floor
    
    # CORRECTION COMPLIANCE : Utiliser helper functions pour compatibilité avec override_settings
    if rate is None:
        rate = _read_silo_redis_rate()
    
    min_activity = _get_saka_silo_redis_min_wallet_activity()
    
    try:
        with transaction.atomic():
            # Verrouiller le Silo pour éviter les races (utiliser id=1 pour singleton)
            silo, _ = SakaSilo.objects.select_for_update().get_or_create(
                id=1,
                defaults={
                    'total_balance': 0,
                    'total_composted': 0,
                    'total_cycles': 0,
                }
            )
            
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
            
            # OPTIMISATION : Wallets éligibles SANS select_for_update() sur le QuerySet principal
            # (évite le verrouillage massif qui peut causer des deadlocks)
            # On utilisera F() expressions qui sont atomiques sans verrouillage lourd
            eligible_qs = SakaWallet.objects.filter(total_harvested__gte=min_activity)
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
            
            # OPTIMISATION : Chunking pour éviter OOM (1000 wallets par lot)
            # Charger seulement les IDs et user_id (pas tous les objets en mémoire)
            BATCH_SIZE = 1000
            offset = 0
            total_redistributed = 0
            chunks_processed = 0
            
            while True:
                # OPTIMISATION : Charger seulement les IDs et user_id (évite OOM)
                chunk_data = list(
                    eligible_qs[offset:offset + BATCH_SIZE]
                    .values_list('id', 'user_id')
                )
                
                if not chunk_data:
                    break
                
                chunk_wallet_ids = [row[0] for row in chunk_data]
                chunk_user_ids = {row[0]: row[1] for row in chunk_data}  # Dict pour lookup rapide
                
                # OPTIMISATION : Mise à jour des wallets avec F() expressions (atomique, pas de verrouillage)
                # F() expressions sont atomiques au niveau DB, pas besoin de select_for_update()
                # (avec autorisation via contexte)
                with AllowSakaMutation():
                    SakaWallet.objects.filter(id__in=chunk_wallet_ids).update(
                        balance=F('balance') + per_wallet,
                        total_harvested=F('total_harvested') + per_wallet,
                        last_activity_date=timezone.now()
                    )
                
                # OPTIMISATION : Créer les transactions SAKA en batch
                transactions_to_create = [
                    SakaTransaction(
                        user_id=chunk_user_ids[wallet_id],  # Utiliser user_id directement
                        direction='EARN',
                        amount=per_wallet,
                        reason='silo_redistribution',
                        transaction_type='REDISTRIBUTION',
                        metadata={}
                    )
                    for wallet_id in chunk_wallet_ids
                ]
                
                # OPTIMISATION : Bulk create des transactions (1 requête par chunk)
                SakaTransaction.objects.bulk_create(
                    transactions_to_create,
                    batch_size=BATCH_SIZE
                )
                
                total_redistributed += per_wallet * len(chunk_wallet_ids)
                chunks_processed += 1
                offset += BATCH_SIZE
            
            # Utiliser le montant réel redistribué calculé pendant le chunking
            actual_redistributed = total_redistributed
            
            # OPTIMISATION : Mise à jour du Silo avec F() expressions (atomique via update())
            # Utiliser total_redistributed calculé pendant le chunking (plus précis)
            SakaSilo.objects.filter(id=silo.id).update(
                total_balance=F('total_balance') - total_redistributed
            )
            actual_redistributed = total_redistributed
            
            logger.info(
                f"Redistribution SAKA Silo : {actual_redistributed} grains "
                f"distribués à {eligible_count} wallets "
                f"({per_wallet} grains chacun). "
                f"Silo : {total_before} → {total_before - actual_redistributed} "
                f"(chunks: {chunks_processed})"
            )
        
        # Rechargement en dehors du bloc transaction pour renvoyer les valeurs réelles
        silo.refresh_from_db()
        return {
            "ok": True,
            "total_before": total_before,
            "total_after": silo.total_balance,
            "redistributed": actual_redistributed,
            "per_wallet": per_wallet,
            "eligible_wallets": eligible_count,
        }
        
    except Exception as e:
        logger.error(f"Exception lors de la redistribution du Silo SAKA : {e}", exc_info=True)
        return {
            "ok": False,
            "reason": f"error: {str(e)}",
        }

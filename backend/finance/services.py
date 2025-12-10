"""
Services financiers unifiés pour V1.6 (Dons) et V2.0 (Investissement dormant).
Corrections critiques : Race condition, arrondis, idempotence, asynchronisme.
"""
from django.db import transaction
from django.conf import settings
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP
import uuid
from .models import UserWallet, WalletTransaction, EscrowContract, WalletPocket


@transaction.atomic
def pledge_funds(user, project, amount, pledge_type='DONATION', idempotency_key=None):
    """
    Fonction unique pour Don (V1.6) ET Investissement (V2.0).
    
    CORRECTIONS CRITIQUES APPLIQUÉES :
    - Race condition : select_for_update() pour verrouiller le wallet
    - Idempotence : idempotency_key pour éviter double dépense
    - Arrondis : quantize() pour calculs précis
    
    Args:
        user: Utilisateur qui fait l'engagement
        project: Projet concerné
        amount: Montant (Decimal)
        pledge_type: 'DONATION' ou 'EQUITY'
        idempotency_key: UUID unique pour éviter double dépense (optionnel)
    
    Returns:
        EscrowContract créé
    
    Raises:
        ValidationError: Si conditions non remplies
    """
    # CORRECTION 5 : Vérification idempotence (évite double dépense)
    if idempotency_key:
        if WalletTransaction.objects.filter(idempotency_key=idempotency_key).exists():
            raise ValidationError("Cette transaction a déjà été traitée.")
    
    # 1. Sécurité V2.0 : Bloquer si feature désactivée
    if pledge_type == 'EQUITY' and not settings.ENABLE_INVESTMENT_FEATURES:
        raise ValidationError("L'investissement n'est pas encore ouvert sur la plateforme.")
    
    # Vérifier que le projet accepte ce type de financement
    if pledge_type == 'EQUITY' and project.funding_type not in ['EQUITY', 'HYBRID']:
        raise ValidationError("Ce projet n'accepte pas les investissements.")
    if pledge_type == 'DONATION' and project.funding_type not in ['DONATION', 'HYBRID']:
        raise ValidationError("Ce projet n'accepte pas les dons.")
    
    # CORRECTION 1 : select_for_update() verrouille la ligne jusqu'à la fin du bloc atomic
    # Évite la race condition (double dépense)
    wallet, _ = UserWallet.objects.select_for_update().get_or_create(user=user)
    
    # CORRECTION 2 : Quantize pour arrondi précis (2 décimales)
    cents = Decimal('0.01')
    amount = Decimal(str(amount)).quantize(cents, rounding=ROUND_HALF_UP)
    
    if wallet.balance < amount:
        raise ValidationError("Solde insuffisant.")
    
    # 2. Logique V2.0 : Vérification KYC et Tickets (Si Equity)
    if pledge_type == 'EQUITY':
        # Vérifier KYC (champ à ajouter sur User)
        if not hasattr(user, 'is_kyc_verified') or not user.is_kyc_verified:
            raise ValidationError("Veuillez valider votre identité (KYC) avant d'investir.")
        
        # Vérifier ticket minimum, multiples d'actions, etc.
        if project.share_price:
            share_price = Decimal(str(project.share_price)).quantize(cents, rounding=ROUND_HALF_UP)
            if amount < share_price:
                raise ValidationError(f"Montant minimum: {share_price} € (prix d'une action).")
            
            # Vérifier que le montant est un multiple du prix de l'action
            shares = int(amount / share_price)
            if shares == 0:
                raise ValidationError(f"Montant insuffisant pour acheter au moins une action.")
            # Ajuster le montant au multiple exact (arrondi précis)
            amount = (Decimal(str(shares)) * share_price).quantize(cents, rounding=ROUND_HALF_UP)
    
    # 3. Mouvement Financier (Commun V1.6/V2.0)
    # CORRECTION 2 : Arrondi du solde après soustraction
    wallet.balance = (wallet.balance - amount).quantize(cents, rounding=ROUND_HALF_UP)
    wallet.save()
    
    tx_type = 'PLEDGE_DONATION' if pledge_type == 'DONATION' else 'PLEDGE_EQUITY'
    
    tx = WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        transaction_type=tx_type,
        related_project=project,
        description=f"{pledge_type} pour {project.titre}",
        idempotency_key=idempotency_key  # CORRECTION 5 : Stocker la clé d'idempotence
    )
    
    escrow = EscrowContract.objects.create(
        user=user,
        project=project,
        amount=amount,
        status='LOCKED',
        pledge_transaction=tx
    )
    
    # 4. Si Equity, créer/enregistrer les actions (V2.0)
    if pledge_type == 'EQUITY' and project.share_price:
        from investment.models import ShareholderRegister
        share_price = Decimal(str(project.share_price)).quantize(cents, rounding=ROUND_HALF_UP)
        shares = int(amount / share_price)
        
        # CORRECTION 1 : select_for_update() pour éviter race condition sur ShareholderRegister
        shareholder, created = ShareholderRegister.objects.select_for_update().get_or_create(
            project=project,
            investor=user,
            defaults={
                'number_of_shares': shares,
                'amount_invested': amount.quantize(cents, rounding=ROUND_HALF_UP)
            }
        )
        if not created:
            # CORRECTION 2 : Arrondis précis pour les montants
            shareholder.number_of_shares += shares
            shareholder.amount_invested = (Decimal(str(shareholder.amount_invested)) + amount).quantize(cents, rounding=ROUND_HALF_UP)
            shareholder.save()
    
    return escrow


@transaction.atomic
def release_escrow(escrow_contract):
    """
    Libère les fonds d'un contrat d'escrow vers le projet.
    Calcule et prélève la commission EGOEJO.
    
    CORRECTIONS CRITIQUES APPLIQUÉES :
    - Arrondis : quantize() pour calculs précis
    - Row locking : select_for_update() pour wallet système
    """
    if escrow_contract.status != 'LOCKED':
        raise ValidationError("Ce contrat n'est pas verrouillé.")
    
    from django.utils import timezone
    
    # CORRECTION 2 : Quantize pour arrondi précis (2 décimales)
    cents = Decimal('0.01')
    total_raised = Decimal(str(escrow_contract.amount)).quantize(cents, rounding=ROUND_HALF_UP)
    
    # Calculer commission EGOEJO avec arrondi bancaire
    commission_rate = Decimal(str(settings.EGOEJO_COMMISSION_RATE))
    commission_amount = (total_raised * commission_rate).quantize(cents, rounding=ROUND_HALF_UP)
    
    # Calculer frais Stripe estimés avec arrondi bancaire
    stripe_fee_rate = Decimal(str(settings.STRIPE_FEE_ESTIMATE))
    fees = (total_raised * stripe_fee_rate).quantize(cents, rounding=ROUND_HALF_UP)
    
    # Le net est le reste exact (arrondi)
    net_amount = (total_raised - commission_amount - fees).quantize(cents, rounding=ROUND_HALF_UP)
    
    # CORRECTION 1 : select_for_update() pour wallet système (évite race condition)
    # Note: Wallet système EGOEJO à créer avec user=None ou un user système dédié
    commission_wallet, _ = UserWallet.objects.select_for_update().get_or_create(
        user=None  # Wallet système EGOEJO (à créer)
    )
    
    # CORRECTION 2 : Arrondi du solde après ajout commission
    commission_wallet.balance = (commission_wallet.balance + commission_amount).quantize(cents, rounding=ROUND_HALF_UP)
    commission_wallet.save()
    
    WalletTransaction.objects.create(
        wallet=commission_wallet,
        amount=commission_amount,
        transaction_type='COMMISSION',
        related_project=escrow_contract.project,
        description=f"Commission EGOEJO ({settings.EGOEJO_COMMISSION_RATE * 100}%)"
    )
    
    # Marquer comme libéré
    escrow_contract.status = 'RELEASED'
    escrow_contract.released_at = timezone.now()
    escrow_contract.save()
    
    return {
        'commission': commission_amount,
        'fees': fees,
        'net_amount': net_amount
    }


@transaction.atomic
def close_project_success(project):
    """
    Clôture un projet avec succès (objectif atteint).
    Libère tous les escrows et calcule les commissions.
    
    CORRECTIONS CRITIQUES APPLIQUÉES :
    - Arrondis : quantize() pour calculs précis
    - Asynchronisme : Notifications déléguées à Celery (CORRECTION 4)
    
    Returns:
        dict: Résumé financier (total_raised, total_commission, total_fees, net_project)
    """
    from django.utils import timezone
    from django.db.models import Sum
    
    # CORRECTION 2 : Quantize pour arrondi précis
    cents = Decimal('0.01')
    
    # Récupérer tous les escrows verrouillés pour ce projet
    escrows = EscrowContract.objects.filter(
        project=project,
        status='LOCKED'
    ).select_for_update()  # CORRECTION 1 : Verrouiller les lignes
    
    # Calculer le total levé
    total_raised = escrows.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    total_raised = total_raised.quantize(cents, rounding=ROUND_HALF_UP)
    
    # Libérer chaque escrow (calculs précis)
    commission_rate = Decimal(str(settings.EGOEJO_COMMISSION_RATE))
    stripe_fee_rate = Decimal(str(settings.STRIPE_FEE_ESTIMATE))
    
    total_commission = Decimal('0')
    total_fees = Decimal('0')
    
    for escrow in escrows:
        # Calculer commission et frais pour cet escrow
        escrow_amount = Decimal(str(escrow.amount)).quantize(cents, rounding=ROUND_HALF_UP)
        escrow_commission = (escrow_amount * commission_rate).quantize(cents, rounding=ROUND_HALF_UP)
        escrow_fees = (escrow_amount * stripe_fee_rate).quantize(cents, rounding=ROUND_HALF_UP)
        
        total_commission += escrow_commission
        total_fees += escrow_fees
        
        # Libérer l'escrow (utilise release_escrow qui gère déjà les arrondis)
        release_escrow(escrow)
    
    # Arrondir les totaux
    total_commission = total_commission.quantize(cents, rounding=ROUND_HALF_UP)
    total_fees = total_fees.quantize(cents, rounding=ROUND_HALF_UP)
    net_project = (total_raised - total_commission - total_fees).quantize(cents, rounding=ROUND_HALF_UP)
    
    # CORRECTION 4 : Notifications asynchrones (déléguées à Celery)
    # On ne fait PAS les emails ici (évite timeout)
    try:
        from core.tasks import notify_project_success_task
        notify_project_success_task.delay(project.id)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erreur lors du lancement de la tâche de notification pour le projet {project.id}: {e}")
        # Ne pas bloquer la clôture financière si la notification échoue
    
    return {
        'total_raised': total_raised,
        'total_commission': total_commission,
        'total_fees': total_fees,
        'net_project': net_project
    }


class InsufficientBalanceError(Exception):
    """Exception levée lorsque le solde est insuffisant pour un transfert"""
    pass


@transaction.atomic
def transfer_to_pocket(user, pocket_id, amount: Decimal) -> WalletTransaction:
    """
    Transfère des fonds du UserWallet principal vers une WalletPocket.
    
    Exigences critiques :
    - Verrouillage du wallet avec select_for_update()
    - Création systématique d'une WalletTransaction (type: 'POCKET_TRANSFER')
    - Vérification du solde disponible avant transfert
    - Mise à jour atomique des soldes (wallet principal + pocket)
    
    Args:
        user: Utilisateur propriétaire du wallet
        pocket_id: ID de la WalletPocket cible
        amount: Montant à transférer (Decimal)
    
    Returns:
        WalletTransaction créée
    
    Raises:
        InsufficientBalanceError: Si solde insuffisant
        ValidationError: Si pocket invalide ou autres erreurs
    """
    cents = Decimal('0.01')
    amount = Decimal(str(amount)).quantize(cents, rounding=ROUND_HALF_UP)
    
    if amount <= Decimal('0'):
        raise ValidationError("Le montant doit être strictement positif.")
    
    # 1. Récupérer le wallet avec verrouillage (évite race condition)
    wallet = UserWallet.objects.select_for_update().get(user=user)
    
    # 2. Vérifier le solde disponible
    if wallet.balance < amount:
        raise InsufficientBalanceError(
            f"Solde insuffisant. Solde disponible: {wallet.balance} €, "
            f"montant demandé: {amount} €"
        )
    
    # 3. Récupérer la pocket (avec verrouillage si possible)
    try:
        pocket = WalletPocket.objects.select_for_update().get(
            id=pocket_id,
            wallet=wallet
        )
    except WalletPocket.DoesNotExist:
        raise ValidationError("Pocket introuvable ou n'appartient pas à cet utilisateur.")
    
    # 4. Créer la transaction AVANT de modifier les soldes (audit trail)
    transaction = WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        transaction_type='POCKET_TRANSFER',
        description=f"Transfert vers pocket: {pocket.name}",
        idempotency_key=None  # Pas d'idempotence pour les transfers manuels
    )
    
    # 5. Mettre à jour les soldes (arrondis précis)
    wallet.balance = (wallet.balance - amount).quantize(cents, rounding=ROUND_HALF_UP)
    wallet.save()
    
    pocket.current_amount = (pocket.current_amount + amount).quantize(cents, rounding=ROUND_HALF_UP)
    pocket.save()
    
    return transaction


@transaction.atomic
def allocate_deposit_across_pockets(user, amount: Decimal):
    """
    Alloue automatiquement un dépôt (top-up) selon les pourcentages configurés
    sur les WalletPocket de l'utilisateur.
    
    Logique :
    - Lit toutes les WalletPocket avec allocation_percentage > 0
    - Calcule la part allouée pour chaque pocket (arrondis Decimal)
    - Crée les transferts via transfer_to_pocket (réutilise la logique existante)
    - Le reliquat éventuel reste dans le solde principal
    
    Args:
        user: Utilisateur propriétaire du wallet
        amount: Montant total du dépôt à allouer (Decimal)
    
    Returns:
        dict: {
            'total_allocated': Decimal,
            'remaining': Decimal,
            'transactions': [WalletTransaction, ...]
        }
    """
    cents = Decimal('0.01')
    amount = Decimal(str(amount)).quantize(cents, rounding=ROUND_HALF_UP)
    
    if amount <= Decimal('0'):
        raise ValidationError("Le montant doit être strictement positif.")
    
    # 1. Récupérer le wallet avec verrouillage
    wallet = UserWallet.objects.select_for_update().get(user=user)
    
    # 2. Récupérer toutes les pockets avec allocation_percentage > 0
    pockets = WalletPocket.objects.filter(
        wallet=wallet,
        allocation_percentage__gt=Decimal('0')
    ).order_by('-allocation_percentage')
    
    if not pockets.exists():
        # Aucune allocation configurée, tout reste dans le solde principal
        return {
            'total_allocated': Decimal('0'),
            'remaining': amount,
            'transactions': []
        }
    
    # 3. Calculer les montants alloués (arrondis précis)
    transactions = []
    total_allocated = Decimal('0')
    
    for pocket in pockets:
        # Calculer la part (pourcentage * montant total)
        percentage = pocket.allocation_percentage / Decimal('100')
        allocated = (amount * percentage).quantize(cents, rounding=ROUND_HALF_UP)
        
        if allocated > Decimal('0'):
            # Vérifier que le wallet a assez (normalement oui car c'est un dépôt)
            if wallet.balance >= allocated:
                try:
                    # Utiliser transfer_to_pocket pour la cohérence (crée la transaction)
                    tx = transfer_to_pocket(user, pocket.id, allocated)
                    transactions.append(tx)
                    total_allocated += allocated
                except InsufficientBalanceError:
                    # Ne devrait pas arriver sur un dépôt, mais on continue
                    pass
    
    # 4. Calculer le reliquat
    remaining = (amount - total_allocated).quantize(cents, rounding=ROUND_HALF_UP)
    
    return {
        'total_allocated': total_allocated,
        'remaining': remaining,
        'transactions': transactions
    }


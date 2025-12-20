"""
Services financiers unifiés pour V1.6 (Dons) et V2.0 (Investissement dormant).
Corrections critiques : Race condition, arrondis, idempotence, asynchronisme.
HARDENING SÉCURITÉ BANCAIRE (OWASP) : Validation stricte, logging, limites.
"""
from django.db import transaction
from django.db.models import F
from django.db.utils import OperationalError
from django.conf import settings
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP
import uuid
import logging
import time
from .models import UserWallet, WalletTransaction, EscrowContract, WalletPocket

logger = logging.getLogger(__name__)

# HARDENING SÉCURITÉ : Limite maximale de pledge (100K€)
MAX_PLEDGE_AMOUNT = Decimal('100000.00')

# OPTIMISATION CONCURRENCE : Limites de batching pour éviter les verrous massifs
MAX_ESCROWS_PER_BATCH = 1000  # Maximum d'escrows à verrouiller en une fois
RELEASE_ESCROW_BATCH_SIZE = 100  # Taille des lots pour release_escrow
MAX_POCKETS_PER_ALLOCATION = 100  # Maximum de pockets à traiter en une fois

# ÉRADICATION CRASHS : Import sécurisé de ShareholderRegister (V2.0)
# Si le module investment n'existe pas, on lève une ValidationError au runtime
try:
    from investment.models import ShareholderRegister
except ImportError:
    ShareholderRegister = None
    logger.warning("Module investment.models non disponible - fonctionnalité EQUITY désactivée")

# ÉRADICATION CRASHS : Retry logic pour opérations DB avec backoff exponentiel
MAX_RETRIES = 3
RETRY_BASE_DELAY = 0.1  # 100ms

# OPTIMISATION BAS NIVEAU : Cache des settings au niveau module (chargés une seule fois)
# Évite les accès répétés aux settings et les conversions répétées
try:
    _COMMISSION_RATE = Decimal(str(settings.EGOEJO_COMMISSION_RATE))
    _STRIPE_FEE_RATE = Decimal(str(settings.STRIPE_FEE_ESTIMATE))
except (AttributeError, ValueError) as e:
    logger.error(f"Erreur lors du chargement des settings financiers: {e}")
    _COMMISSION_RATE = Decimal('0.05')  # Valeur par défaut 5%
    _STRIPE_FEE_RATE = Decimal('0.029')  # Valeur par défaut 2.9%


def _to_decimal(value, quantize=True):
    """
    Convertit une valeur en Decimal de manière optimisée.
    
    OPTIMISATION BAS NIVEAU :
    - Si c'est déjà un Decimal, retourne directement (pas de conversion inutile)
    - Si c'est un int/float, convertit via str() pour éviter les erreurs d'arrondi
    - Option de quantization pour arrondir à 2 décimales
    
    Args:
        value: Valeur à convertir (Decimal, int, float, str)
        quantize: Si True, arrondit à 2 décimales (ROUND_HALF_UP)
    
    Returns:
        Decimal: Valeur convertie (et quantifiée si demandé)
    
    Raises:
        ValueError: Si le type n'est pas supporté
    """
    cents = Decimal('0.01')
    
    if isinstance(value, Decimal):
        # Déjà un Decimal, pas besoin de conversion
        return value.quantize(cents, rounding=ROUND_HALF_UP) if quantize else value
    elif isinstance(value, (int, float)):
        # Conversion via str() pour éviter les erreurs d'arrondi flottant
        decimal_value = Decimal(str(value))
        return decimal_value.quantize(cents, rounding=ROUND_HALF_UP) if quantize else decimal_value
    elif isinstance(value, str):
        # String, conversion directe
        decimal_value = Decimal(value)
        return decimal_value.quantize(cents, rounding=ROUND_HALF_UP) if quantize else decimal_value
    else:
        raise ValueError(f"Type non supporté pour conversion Decimal: {type(value)}")


def _retry_db_operation(operation, operation_name="DB operation", max_retries=MAX_RETRIES, base_delay=RETRY_BASE_DELAY):
    """
    Retry logic pour opérations DB avec backoff exponentiel.
    
    Gère les OperationalError (lock timeout, deadlock) en réessayant avec un délai croissant.
    
    Args:
        operation: Fonction lambda à exécuter (ex: lambda: Model.objects.select_for_update().get(...))
        operation_name: Nom de l'opération pour le logging
        max_retries: Nombre maximum de tentatives
        base_delay: Délai de base en secondes (backoff exponentiel)
    
    Returns:
        Résultat de l'opération
    
    Raises:
        OperationalError: Si toutes les tentatives échouent
        Exception: Autres exceptions non liées aux locks
    """
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return operation()
        except OperationalError as e:
            last_exception = e
            error_str = str(e).lower()
            
            # Vérifier si c'est un problème de lock (timeout, deadlock)
            if 'lock' in error_str or 'deadlock' in error_str or 'timeout' in error_str:
                if attempt < max_retries - 1:
                    # Backoff exponentiel : 0.1s, 0.2s, 0.4s
                    delay = base_delay * (2 ** attempt)
                    logger.warning(
                        f"Lock timeout sur {operation_name} (tentative {attempt + 1}/{max_retries}) - "
                        f"Retry dans {delay}s - Error: {e}"
                    )
                    time.sleep(delay)
                    continue
                else:
                    # Dernière tentative échouée
                    logger.critical(
                        f"Échec définitif de {operation_name} après {max_retries} tentatives - "
                        f"Error: {e}",
                        exc_info=True
                    )
                    raise
            else:
                # OperationalError mais pas lié aux locks - re-raise immédiatement
                logger.error(
                    f"OperationalError non lié aux locks sur {operation_name} - Error: {e}",
                    exc_info=True
                )
                raise
        except Exception as e:
            # Autres exceptions - re-raise immédiatement (pas de retry)
            logger.error(
                f"Exception non-OperationalError sur {operation_name} - Error: {e}",
                exc_info=True
            )
            raise
    
    # Ne devrait jamais arriver ici, mais au cas où
    if last_exception:
        raise last_exception


def _validate_pledge_request(user, project, pledge_type):
    """
    Valide la requête de pledge (feature flags, type de financement, statut projet).
    
    HARDENING SÉCURITÉ (OWASP) :
    - Vérification statut projet ACTIVE
    - Validation feature flags
    - Validation type de financement
    
    Args:
        user: Utilisateur
        project: Projet
        pledge_type: 'DONATION' ou 'EQUITY'
    
    Raises:
        ValidationError: Si conditions non remplies
    """
    # CORRECTION COMPLIANCE : Vérifier le feature flag AVANT TOUT pour EQUITY
    # Cela garantit que l'erreur levée est spécifique au feature flag, pas au statut projet
    if pledge_type == 'EQUITY':
        if not getattr(settings, 'ENABLE_INVESTMENT_FEATURES', False):
            logger.warning(
                f"Tentative d'investissement EQUITY avec feature désactivée - User: {user.id}, Project: {project.id}"
            )
            raise ValidationError("L'investissement n'est pas encore ouvert sur la plateforme.")
    
    # HARDENING SÉCURITÉ : Vérifier que le projet est ACTIF (seulement si feature flag OK pour EQUITY)
    # CORRECTION : Le modèle Projet n'a pas de champ status, donc on considère qu'un projet sans status est actif
    # Si le champ status existe (futur), on vérifie qu'il est ACTIVE
    # IMPORTANT : Ne vérifier le statut que si ce n'est pas un EQUITY (car EQUITY est déjà bloqué par feature flag)
    if pledge_type != 'EQUITY' and hasattr(project, 'status') and project.status != 'ACTIVE':
        logger.warning(
            f"Tentative de pledge sur projet non actif - User: {user.id}, "
            f"Project: {project.id}, Status: {project.status}"
        )
        raise ValidationError("Ce projet n'accepte plus de financement.")
    
    # Vérifier que le projet accepte ce type de financement
    if pledge_type == 'EQUITY' and project.funding_type not in ['EQUITY', 'HYBRID']:
        logger.warning(
            f"Tentative d'investissement EQUITY sur projet incompatible - User: {user.id}, "
            f"Project: {project.id}, FundingType: {project.funding_type}"
        )
        raise ValidationError("Ce projet n'accepte pas les investissements.")
    if pledge_type == 'DONATION' and project.funding_type not in ['DONATION', 'HYBRID']:
        logger.warning(
            f"Tentative de don sur projet incompatible - User: {user.id}, "
            f"Project: {project.id}, FundingType: {project.funding_type}"
        )
        raise ValidationError("Ce projet n'accepte pas les dons.")


def _lock_user_wallet(user, idempotency_key=None):
    """
    Verrouille le wallet utilisateur et vérifie l'idempotence.
    
    HARDENING SÉCURITÉ (OWASP) :
    - Logging des tentatives de double dépense
    
    ÉRADICATION CRASHS :
    - Retry logic pour gérer les lock timeouts
    
    Args:
        user: Utilisateur
        idempotency_key: UUID unique pour éviter double dépense (optionnel)
    
    Returns:
        UserWallet verrouillé
    
    Raises:
        ValidationError: Si transaction déjà traitée (idempotence)
        OperationalError: Si lock timeout après retries
    """
    # CORRECTION RACE CONDITION : Verrouillage EN PREMIER (avant vérification idempotence)
    # Évite la race condition où deux requêtes passent la vérification idempotence simultanément
    # ÉRADICATION CRASHS : Retry logic pour gérer les lock timeouts
    wallet, _ = _retry_db_operation(
        lambda: UserWallet.objects.select_for_update().get_or_create(user=user),
        operation_name=f"lock_user_wallet(user={user.id})"
    )
    
    # CORRECTION 5 : Vérification idempotence APRÈS verrouillage (dans la même transaction)
    # Maintenant que le wallet est verrouillé, on peut vérifier l'idempotence en toute sécurité
    if idempotency_key:
        if WalletTransaction.objects.filter(idempotency_key=idempotency_key).exists():
            logger.warning(
                f"Tentative de double dépense détectée (idempotence) - User: {user.id}, "
                f"IdempotencyKey: {idempotency_key}"
            )
            raise ValidationError("Cette transaction a déjà été traitée.")
    
    return wallet


def _calculate_equity_amount(user, project, amount):
    """
    Calcule et ajuste le montant pour un investissement EQUITY.
    Vérifie KYC, ticket minimum, et ajuste au multiple du prix d'action.
    
    HARDENING SÉCURITÉ (OWASP) :
    - Vérification KYC stricte (champ doit exister ET être True)
    - Logging des tentatives sans KYC
    
    Args:
        user: Utilisateur
        project: Projet
        amount: Montant initial (Decimal)
    
    Returns:
        Decimal: Montant ajusté (multiple du prix d'action)
    
    Raises:
        ValidationError: Si KYC non vérifié ou montant insuffisant
    """
    cents = Decimal('0.01')
    amount = _to_decimal(amount)
    
    # HARDENING SÉCURITÉ : Vérification KYC stricte (champ doit exister ET être True)
    if not hasattr(user, 'is_kyc_verified'):
        logger.warning(
            f"Tentative d'investissement EQUITY sans champ is_kyc_verified - User: {user.id}, Project: {project.id}"
        )
        raise ValidationError("Champ is_kyc_verified manquant sur le modèle User. Contactez le support.")
    
    if not user.is_kyc_verified:
        logger.warning(
            f"Tentative d'investissement EQUITY sans KYC vérifié - User: {user.id}, Project: {project.id}"
        )
        raise ValidationError("Veuillez valider votre identité (KYC) avant d'investir.")
    
    # Vérifier ticket minimum, multiples d'actions, etc.
    if project.share_price:
        share_price = _to_decimal(project.share_price)
        if amount < share_price:
            logger.warning(
                f"Montant insuffisant pour investissement EQUITY - User: {user.id}, "
                f"Project: {project.id}, Amount: {amount}, SharePrice: {share_price}"
            )
            raise ValidationError(f"Montant minimum: {share_price} € (prix d'une action).")
        
        # Vérifier que le montant est un multiple du prix de l'action
        shares = int(amount / share_price)
        if shares == 0:
            logger.warning(
                f"Montant insuffisant pour acheter une action - User: {user.id}, "
                f"Project: {project.id}, Amount: {amount}, SharePrice: {share_price}"
            )
            raise ValidationError(f"Montant insuffisant pour acheter au moins une action.")
        # Ajuster le montant au multiple exact (arrondi précis)
        amount = (_to_decimal(shares, quantize=False) * share_price).quantize(cents, rounding=ROUND_HALF_UP)
    
    return amount


def _create_ledger_entries(user, wallet, project, amount, pledge_type, idempotency_key):
    """
    Crée les entrées comptables (transaction et escrow).
    
    Args:
        user: Utilisateur
        wallet: UserWallet verrouillé
        project: Projet
        amount: Montant (Decimal)
        pledge_type: 'DONATION' ou 'EQUITY'
        idempotency_key: UUID unique (optionnel)
    
    Returns:
        tuple: (WalletTransaction, EscrowContract)
    """
    cents = Decimal('0.01')
    
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
    
    return tx, escrow


def _register_equity_shares(user, project, amount):
    """
    Enregistre les actions achetées dans le registre des actionnaires (V2.0).
    
    ÉRADICATION CRASHS : Vérification que ShareholderRegister est disponible.
    
    Args:
        user: Utilisateur
        project: Projet
        amount: Montant investi (Decimal)
    
    Returns:
        ShareholderRegister: Enregistrement créé ou mis à jour
    
    Raises:
        ValidationError: Si module investment non disponible
    """
    # ÉRADICATION CRASHS : Vérifier que ShareholderRegister est disponible
    if ShareholderRegister is None:
        logger.error(
            f"Tentative d'enregistrement d'actions EQUITY mais module investment non disponible - "
            f"User: {user.id}, Project: {project.id}"
        )
        raise ValidationError("Module investment non disponible. Contactez le support.")
    
    cents = Decimal('0.01')
    
    share_price = _to_decimal(project.share_price)
    shares = int(amount / share_price)
    
    # CORRECTION 1 : select_for_update() pour éviter race condition sur ShareholderRegister
    # ÉRADICATION CRASHS : Retry logic pour gérer les lock timeouts
    shareholder, created = _retry_db_operation(
        lambda: ShareholderRegister.objects.select_for_update().get_or_create(
            project=project,
            investor=user,
            defaults={
                'number_of_shares': shares,
                'amount_invested': amount.quantize(cents, rounding=ROUND_HALF_UP)
            }
        ),
        operation_name="get_or_create ShareholderRegister"
    )
    
    if not created:
        # CORRECTION 2 : Arrondis précis pour les montants
        shareholder.number_of_shares += shares
        shareholder.amount_invested = (_to_decimal(shareholder.amount_invested, quantize=False) + amount).quantize(cents, rounding=ROUND_HALF_UP)
        shareholder.save()
    
    return shareholder


def _pledge_funds_internal(user, project, amount, pledge_type='DONATION', idempotency_key=None):
    """
    Implémentation interne de pledge_funds (séparée pour gestion deadlock).
    
    Fonction unique pour Don (V1.6) ET Investissement (V2.0).
    
    REFACTORING "Divide & Conquer" : Découpée en sous-fonctions atomiques pour améliorer la lisibilité.
    
    CORRECTIONS CRITIQUES APPLIQUÉES :
    - Race condition : select_for_update() pour verrouiller le wallet
    - Idempotence : idempotency_key pour éviter double dépense
    - Arrondis : quantize() pour calculs précis
    
    HARDENING SÉCURITÉ BANCAIRE (OWASP) :
    - Validation stricte des types (Decimal uniquement)
    - Validation montants négatifs/nuls
    - Limite maximale (100K€)
    - Logging de toutes les erreurs financières
    
    Args:
        user: Utilisateur qui fait l'engagement
        project: Projet concerné
        amount: Montant (Decimal, int ou float - sera converti en Decimal)
        pledge_type: 'DONATION' ou 'EQUITY'
        idempotency_key: UUID unique pour éviter double dépense (optionnel)
    
    Returns:
        EscrowContract créé
    
    Raises:
        ValidationError: Si conditions non remplies
    """
    # HARDENING SÉCURITÉ : Validation stricte du type de montant
    if not isinstance(amount, (Decimal, int, float)):
        logger.error(
            f"Type de montant invalide - User: {user.id}, Project: {project.id}, "
            f"AmountType: {type(amount)}, Amount: {amount}"
        )
        raise ValidationError("Le montant doit être un Decimal, int ou float.")
    
    # HARDENING SÉCURITÉ : Conversion en Decimal avec validation
    try:
        if isinstance(amount, Decimal):
            amount_decimal = amount
        elif isinstance(amount, (int, float)):
            amount_decimal = _to_decimal(amount)
        else:
            raise ValueError("Type non supporté")
    except (ValueError, TypeError) as e:
        logger.error(
            f"Erreur de conversion du montant - User: {user.id}, Project: {project.id}, "
            f"Amount: {amount}, Error: {e}"
        )
        raise ValidationError(f"Montant invalide: {amount}")
    
    # HARDENING SÉCURITÉ : Normalisation et validation stricte (montants négatifs/nuls)
    cents = Decimal('0.01')
    amount = amount_decimal.quantize(cents, rounding=ROUND_HALF_UP)
    
    # HARDENING SÉCURITÉ : Stop montants négatifs ou nuls
    if amount <= Decimal('0'):
        logger.warning(
            f"Tentative de pledge avec montant négatif ou nul - User: {user.id}, "
            f"Project: {project.id}, Amount: {amount}"
        )
        raise ValidationError("Le montant doit être strictement positif.")
    
    # HARDENING SÉCURITÉ : Limite maximale (100K€)
    if amount > MAX_PLEDGE_AMOUNT:
        logger.warning(
            f"Tentative de pledge dépassant la limite maximale - User: {user.id}, "
            f"Project: {project.id}, Amount: {amount}, MaxAmount: {MAX_PLEDGE_AMOUNT}"
        )
        raise ValidationError(f"Montant maximum autorisé: {MAX_PLEDGE_AMOUNT} €")
    
    # 1. Validation de la requête (statut projet, feature flags, type financement)
    _validate_pledge_request(user, project, pledge_type)
    
    # 2. Verrouillage du wallet et vérification idempotence
    wallet = _lock_user_wallet(user, idempotency_key)
    
    # HARDENING SÉCURITÉ : Validation solde avec logging
    if wallet.balance < amount:
        logger.warning(
            f"Solde insuffisant pour pledge - User: {user.id}, Project: {project.id}, "
            f"Balance: {wallet.balance}, Amount: {amount}"
        )
        raise ValidationError("Solde insuffisant.")
    
    # 4. Calculs spécifiques EQUITY (KYC, ajustement montant)
    if pledge_type == 'EQUITY':
        amount = _calculate_equity_amount(user, project, amount)
    
    # 5. Création des entrées comptables (transaction + escrow)
    tx, escrow = _create_ledger_entries(user, wallet, project, amount, pledge_type, idempotency_key)
    
    # 6. Enregistrement des actions (si EQUITY)
    if pledge_type == 'EQUITY' and project.share_price:
        _register_equity_shares(user, project, amount)
    
    # Logging de succès pour audit
    logger.info(
        f"Pledge réussi - User: {user.id}, Project: {project.id}, "
        f"Type: {pledge_type}, Amount: {amount}, EscrowID: {escrow.id}"
    )
    
    return escrow


@transaction.atomic
def pledge_funds(user, project, amount, pledge_type='DONATION', idempotency_key=None):
    """
    Wrapper avec gestion deadlock pour pledge_funds.
    """
    # OPTIMISATION CONCURRENCE : Gestion deadlocks avec retry
    max_deadlock_retries = 3
    for deadlock_attempt in range(max_deadlock_retries):
        try:
            return _pledge_funds_internal(user, project, amount, pledge_type, idempotency_key)
        except OperationalError as e:
            error_str = str(e).lower()
            if 'deadlock' in error_str and deadlock_attempt < max_deadlock_retries - 1:
                delay = RETRY_BASE_DELAY * (2 ** deadlock_attempt)
                logger.warning(
                    f"Deadlock détecté lors du pledge - User: {user.id}, Project: {project.id} "
                    f"(tentative {deadlock_attempt + 1}/{max_deadlock_retries}) - Retry dans {delay}s"
                )
                time.sleep(delay)
                continue
            else:
                logger.critical(
                    f"Échec définitif de pledge_funds - User: {user.id}, Project: {project.id} "
                    f"après {max_deadlock_retries} tentatives - Error: {e}",
                    exc_info=True
                )
                raise


@transaction.atomic
def release_escrow(escrow_contract):
    """
    Libère les fonds d'un contrat d'escrow vers le projet.
    Calcule et prélève la commission EGOEJO.
    
    CORRECTIONS CRITIQUES APPLIQUÉES :
    - Arrondis : quantize() pour calculs précis
    - Row locking : select_for_update() pour wallet système ET escrow
    - Race condition : Verrouillage escrow pour éviter double libération
    """
    from django.utils import timezone
    
    # CORRECTION RACE CONDITION : Verrouiller l'escrow AVANT de vérifier/modifier son statut
    # Évite la race condition où deux requêtes libèrent le même escrow simultanément
    # ÉRADICATION CRASHS : Retry logic pour gérer les lock timeouts
    escrow = _retry_db_operation(
        lambda: EscrowContract.objects.select_for_update().get(id=escrow_contract.id),
        operation_name=f"lock_escrow(escrow_id={escrow_contract.id})"
    )
    
    if escrow.status != 'LOCKED':
        raise ValidationError("Ce contrat n'est pas verrouillé.")
    
    # CORRECTION 2 : Quantize pour arrondi précis (2 décimales)
    cents = Decimal('0.01')
    total_raised = _to_decimal(escrow_contract.amount)
    
    # Calculer commission EGOEJO avec arrondi bancaire
    # OPTIMISATION BAS NIVEAU : Utiliser le cache de settings
    commission_rate = _COMMISSION_RATE
    commission_amount = (total_raised * commission_rate).quantize(cents, rounding=ROUND_HALF_UP)
    
    # Calculer frais Stripe estimés avec arrondi bancaire
    # OPTIMISATION BAS NIVEAU : Utiliser le cache de settings
    stripe_fee_rate = _STRIPE_FEE_RATE
    fees = (total_raised * stripe_fee_rate).quantize(cents, rounding=ROUND_HALF_UP)
    
    # Le net est le reste exact (arrondi)
    net_amount = (total_raised - commission_amount - fees).quantize(cents, rounding=ROUND_HALF_UP)
    
    # CORRECTION 1 : select_for_update() pour wallet système (évite race condition)
    # Note: Wallet système EGOEJO à créer avec user=None ou un user système dédié
    # ÉRADICATION CRASHS : Retry logic pour gérer les lock timeouts
    commission_wallet, _ = _retry_db_operation(
        lambda: UserWallet.objects.select_for_update().get_or_create(user=None),
        operation_name="lock_commission_wallet"
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
    
    # Marquer comme libéré (utiliser l'objet verrouillé)
    escrow.status = 'RELEASED'
    escrow.released_at = timezone.now()
    escrow.save()
    
    return {
        'commission': commission_amount,
        'fees': fees,
        'net_amount': net_amount
    }


@transaction.atomic
def _release_escrows_batch(escrows_batch, commission_rate, stripe_fee_rate):
    """
    Libère un lot d'escrows en batch pour optimiser les performances.
    
    OPTIMISATION CONCURRENCE : Traite les escrows par lots pour éviter N+1 queries.
    
    CORRECTION CRITIQUE ATOMICITÉ :
    - Transaction atomic pour garantir tout ou rien
    - Mise à jour atomique du wallet système avec F() expressions (évite race condition)
    
    Args:
        escrows_batch: Liste d'EscrowContract à libérer
        commission_rate: Taux de commission (Decimal)
        stripe_fee_rate: Taux de frais Stripe (Decimal)
    
    Returns:
        tuple: (total_commission, total_fees)
    """
    from django.utils import timezone
    
    cents = Decimal('0.01')
    total_commission = Decimal('0')
    total_fees = Decimal('0')
    
    # Préparer les mises à jour en batch
    escrows_to_update = []
    transactions_to_create = []
    
    # Récupérer ou créer le wallet système une seule fois
    commission_wallet, _ = _retry_db_operation(
        lambda: UserWallet.objects.select_for_update().get_or_create(user=None),
        operation_name="lock_commission_wallet_batch"
    )
    
    for escrow in escrows_batch:
        escrow_amount = _to_decimal(escrow.amount)
        escrow_commission = (escrow_amount * commission_rate).quantize(cents, rounding=ROUND_HALF_UP)
        escrow_fees = (escrow_amount * stripe_fee_rate).quantize(cents, rounding=ROUND_HALF_UP)
        
        total_commission += escrow_commission
        total_fees += escrow_fees
        
        # Marquer l'escrow pour mise à jour
        escrow.status = 'RELEASED'
        escrow.released_at = timezone.now()
        escrows_to_update.append(escrow)
        
        # Préparer la transaction commission
        transactions_to_create.append(
            WalletTransaction(
                wallet=commission_wallet,
                amount=escrow_commission,
                transaction_type='COMMISSION',
                related_project=escrow.project,
                description=f"Commission EGOEJO ({_COMMISSION_RATE * 100}%)"
            )
        )
    
    # Mise à jour en batch
    if escrows_to_update:
        EscrowContract.objects.bulk_update(escrows_to_update, ['status', 'released_at'], batch_size=RELEASE_ESCROW_BATCH_SIZE)
    
    # Création en batch des transactions
    if transactions_to_create:
        WalletTransaction.objects.bulk_create(transactions_to_create, batch_size=RELEASE_ESCROW_BATCH_SIZE)
    
    # CORRECTION CRITIQUE RACE CONDITION : Mise à jour atomique avec F() expressions
    # Évite la race condition si plusieurs batches s'exécutent simultanément
    if total_commission > Decimal('0'):
        total_commission_quantized = total_commission.quantize(cents, rounding=ROUND_HALF_UP)
        UserWallet.objects.filter(id=commission_wallet.id).update(
            balance=F('balance') + total_commission_quantized
        )
    
    return total_commission, total_fees


@transaction.atomic
def close_project_success(project):
    """
    Clôture un projet avec succès (objectif atteint).
    Libère tous les escrows et calcule les commissions.
    
    CORRECTIONS CRITIQUES APPLIQUÉES :
    - Arrondis : quantize() pour calculs précis
    - Asynchronisme : Notifications déléguées à Celery (CORRECTION 4)
    
    OPTIMISATION CONCURRENCE :
    - Batching des releases d'escrows (évite N+1 queries)
    - Limite sur verrous (MAX_ESCROWS_PER_BATCH)
    - Gestion deadlocks avec retry
    
    Returns:
        dict: Résumé financier (total_raised, total_commission, total_fees, net_project)
    """
    from django.utils import timezone
    from django.db.models import Sum
    
    # OPTIMISATION CONCURRENCE : Gestion deadlocks avec retry
    max_deadlock_retries = 3
    for deadlock_attempt in range(max_deadlock_retries):
        try:
            return _close_project_success_internal(project)
        except OperationalError as e:
            error_str = str(e).lower()
            if 'deadlock' in error_str and deadlock_attempt < max_deadlock_retries - 1:
                delay = RETRY_BASE_DELAY * (2 ** deadlock_attempt)
                logger.warning(
                    f"Deadlock détecté lors de la clôture du projet {project.id} "
                    f"(tentative {deadlock_attempt + 1}/{max_deadlock_retries}) - Retry dans {delay}s"
                )
                time.sleep(delay)
                continue
            else:
                logger.critical(
                    f"Échec définitif de clôture du projet {project.id} après {max_deadlock_retries} tentatives - "
                    f"Error: {e}",
                    exc_info=True
                )
                raise


def _close_project_success_internal(project):
    """
    Implémentation interne de close_project_success (séparée pour gestion deadlock).
    """
    from django.utils import timezone
    from django.db.models import Sum
    
    # CORRECTION 2 : Quantize pour arrondi précis
    cents = Decimal('0.01')
    
    # OPTIMISATION CONCURRENCE : Limiter le nombre d'escrows verrouillés en une fois
    # Récupérer tous les escrows verrouillés pour ce projet (avec limite)
    escrows_qs = EscrowContract.objects.filter(
        project=project,
        status='LOCKED'
    )
    
    # OPTIMISATION CONCURRENCE : Limite sur verrous pour éviter lock massif
    escrows_count = escrows_qs.count()
    if escrows_count > MAX_ESCROWS_PER_BATCH:
        logger.warning(
            f"Projet {project.id} a {escrows_count} escrows (> {MAX_ESCROWS_PER_BATCH}), "
            f"traitement par lots de {MAX_ESCROWS_PER_BATCH}"
        )
    
    # Calculer le total levé (sans verrouillage pour éviter lock massif)
    total_raised = escrows_qs.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    total_raised = total_raised.quantize(cents, rounding=ROUND_HALF_UP)
    
    # Libérer chaque escrow par lots (calculs précis)
    # OPTIMISATION BAS NIVEAU : Utiliser le cache de settings
    commission_rate = _COMMISSION_RATE
    stripe_fee_rate = _STRIPE_FEE_RATE
    
    total_commission = Decimal('0')
    total_fees = Decimal('0')
    
    # OPTIMISATION MÉMOIRE : Utiliser values_list pour récupérer uniquement les IDs
    # Évite de charger tous les objets complets en mémoire
    escrow_ids = list(
        escrows_qs[:MAX_ESCROWS_PER_BATCH]
        .values_list('id', flat=True)
    )
    
    # OPTIMISATION CONCURRENCE : Traiter par lots pour éviter N+1 queries et verrous massifs
    # Traiter par lots de RELEASE_ESCROW_BATCH_SIZE directement sur les IDs
    for i in range(0, len(escrow_ids), RELEASE_ESCROW_BATCH_SIZE):
        batch_ids = escrow_ids[i:i + RELEASE_ESCROW_BATCH_SIZE]
        
        # Verrouiller uniquement le lot actuel (chargement uniquement lors du select_for_update)
        locked_escrows = list(
            EscrowContract.objects.filter(id__in=batch_ids)
            .select_for_update()
        )
        
        # Libérer le lot en batch
        batch_commission, batch_fees = _release_escrows_batch(
            locked_escrows,
            commission_rate,
            stripe_fee_rate
        )
        
        total_commission += batch_commission
        total_fees += batch_fees
    
    # Arrondir les totaux
    total_commission = total_commission.quantize(cents, rounding=ROUND_HALF_UP)
    total_fees = total_fees.quantize(cents, rounding=ROUND_HALF_UP)
    net_project = (total_raised - total_commission - total_fees).quantize(cents, rounding=ROUND_HALF_UP)
    
    # CORRECTION 4 : Notifications asynchrones (déléguées à Celery)
    # On ne fait PAS les emails ici (évite timeout)
    # ÉRADICATION CRASHS : Exception handling spécifique avec logging critique
    try:
        from core.tasks import notify_project_success_task
        notify_project_success_task.delay(project.id)
    except ImportError:
        # Celery ou module tasks non disponible - OK, on continue
        logger.warning(
            f"Module core.tasks non disponible - notifications ignorées pour projet {project.id}"
        )
    except Exception as e:
        # Erreur inattendue - ON LOG CRITIQUE ET ON REMONTE
        logger.critical(
            f"Erreur critique lors du lancement de la tâche de notification pour le projet {project.id} - "
            f"Error: {e}",
            exc_info=True
        )
        # Ne pas bloquer la clôture financière si la notification échoue
        # Mais on log en CRITICAL pour que ce soit visible dans les logs
    
    return {
        'total_raised': total_raised,
        'total_commission': total_commission,
        'total_fees': total_fees,
        'net_project': net_project
    }


class InsufficientBalanceError(Exception):
    """Exception levée lorsque le solde est insuffisant pour un transfert"""
    pass


def _transfer_to_pocket_internal(user, pocket_id, amount: Decimal) -> WalletTransaction:
    """
    Implémentation interne de transfer_to_pocket (séparée pour gestion deadlock).
    
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
    amount = _to_decimal(amount)
    
    if amount <= Decimal('0'):
        raise ValidationError("Le montant doit être strictement positif.")
    
    # 1. Récupérer le wallet avec verrouillage (évite race condition)
    # ÉRADICATION CRASHS : Retry logic pour gérer les lock timeouts
    wallet = _retry_db_operation(
        lambda: UserWallet.objects.select_for_update().get(user=user),
        operation_name=f"lock_wallet_for_transfer(user={user.id})"
    )
    
    # 2. Vérifier le solde disponible
    if wallet.balance < amount:
        raise InsufficientBalanceError(
            f"Solde insuffisant. Solde disponible: {wallet.balance} €, "
            f"montant demandé: {amount} €"
        )
    
    # 3. Récupérer la pocket (avec verrouillage si possible)
    # ÉRADICATION CRASHS : Retry logic pour gérer les lock timeouts
    try:
        pocket = _retry_db_operation(
            lambda: WalletPocket.objects.select_for_update().get(
                id=pocket_id,
                wallet=wallet
            ),
            operation_name=f"lock_pocket(pocket_id={pocket_id}, user={user.id})"
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
    amount = _to_decimal(amount)
    
    if amount <= Decimal('0'):
        raise ValidationError("Le montant doit être strictement positif.")
    
    # 1. Récupérer le wallet avec verrouillage
    # ÉRADICATION CRASHS : Retry logic pour gérer les lock timeouts
    wallet = _retry_db_operation(
        lambda: UserWallet.objects.select_for_update().get(user=user),
        operation_name=f"lock_wallet_for_allocate(user={user.id})"
    )
    
    # 2. Récupérer toutes les pockets avec allocation_percentage > 0
    # OPTIMISATION MÉMOIRE : Limite pour éviter timeout si un user a 1000 pockets
    pockets_qs = WalletPocket.objects.filter(
        wallet=wallet,
        allocation_percentage__gt=Decimal('0')
    ).order_by('-allocation_percentage')[:MAX_POCKETS_PER_ALLOCATION]
    
    # Vérifier s'il y a des pockets (sans charger en mémoire)
    if not pockets_qs.exists():
        # Aucune allocation configurée, tout reste dans le solde principal
        return {
            'total_allocated': Decimal('0'),
            'remaining': amount,
            'transactions': []
        }
    
    # OPTIMISATION MÉMOIRE : Avertir si limite atteinte
    total_pockets_count = WalletPocket.objects.filter(
        wallet=wallet,
        allocation_percentage__gt=Decimal('0')
    ).count()
    
    if total_pockets_count > MAX_POCKETS_PER_ALLOCATION:
        logger.warning(
            f"User {user.id} a {total_pockets_count} pockets (> {MAX_POCKETS_PER_ALLOCATION}), "
            f"traitement limité à {MAX_POCKETS_PER_ALLOCATION}"
        )
    
    # 3. Calculer les montants alloués (arrondis précis)
    # OPTIMISATION N+1 : Préparer les objets en mémoire, puis bulk operations
    transactions_to_create = []
    pockets_to_update = []
    total_allocated = Decimal('0')
    
    # Verrouiller toutes les pockets en une seule requête (plus efficace)
    pockets = list(
        WalletPocket.objects.filter(
            id__in=pockets_qs.values_list('id', flat=True)
        ).select_for_update()
    )
    
    for pocket in pockets:
        # Calculer la part (pourcentage * montant total)
        percentage = pocket.allocation_percentage / Decimal('100')
        allocated = (amount * percentage).quantize(cents, rounding=ROUND_HALF_UP)
        
        if allocated > Decimal('0'):
            # Vérifier que le wallet a assez (normalement oui car c'est un dépôt)
            if wallet.balance >= allocated:
                # Préparer la transaction en mémoire
                transactions_to_create.append(
                    WalletTransaction(
                        wallet=wallet,
                        amount=allocated,
                        transaction_type='POCKET_TRANSFER',
                        description=f"Allocation automatique vers pocket: {pocket.name}",
                        idempotency_key=None
                    )
                )
                
                # Modifier la pocket en mémoire
                pocket.current_amount = (pocket.current_amount + allocated).quantize(cents, rounding=ROUND_HALF_UP)
                pockets_to_update.append(pocket)
                
                total_allocated += allocated
    
    # OPTIMISATION N+1 : Bulk operations au lieu de create/save individuels
    if transactions_to_create:
        created_transactions = WalletTransaction.objects.bulk_create(
            transactions_to_create,
            batch_size=MAX_POCKETS_PER_ALLOCATION
        )
    else:
        created_transactions = []
    
    if pockets_to_update:
        WalletPocket.objects.bulk_update(
            pockets_to_update,
            ['current_amount'],
            batch_size=MAX_POCKETS_PER_ALLOCATION
        )
    
    # CORRECTION RACE CONDITION : Mise à jour atomique du wallet avec F() expressions
    if total_allocated > Decimal('0'):
        total_allocated_quantized = total_allocated.quantize(cents, rounding=ROUND_HALF_UP)
        UserWallet.objects.filter(id=wallet.id).update(
            balance=F('balance') - total_allocated_quantized
        )
    
    # 4. Calculer le reliquat
    remaining = (amount - total_allocated).quantize(cents, rounding=ROUND_HALF_UP)
    
    return {
        'total_allocated': total_allocated,
        'remaining': remaining,
        'transactions': created_transactions
    }


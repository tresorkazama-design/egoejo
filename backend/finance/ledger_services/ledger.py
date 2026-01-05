"""
Service de Ledger pour répartition proportionnelle des frais Stripe.

Logique :
- Lorsqu'un payment_intent.succeeded arrive (ex: Total 105€ = 100€ Don + 5€ Tip)
- Récupérer les frais réels depuis charge.balance_transaction.fee
- Calculer les ratios Donation/Tip
- Répartir les frais proportionnellement
- Enregistrer dans les Ledgers (PROJECT_ESCROW, OPERATING) avec amount_gross, stripe_fee, amount_net

Garantie : Sum(Net) + Sum(Fees) = Total Payment
"""
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

# Constantes Stripe (chargées depuis settings)
from django.conf import settings

STRIPE_FIXED_FEE = Decimal(str(getattr(settings, 'STRIPE_FIXED_FEE', 0.25)))
STRIPE_PERCENT_FEE = Decimal(str(getattr(settings, 'STRIPE_PERCENT_FEE', 0.015)))  # 1.5%


def _to_decimal(value, quantize=True):
    """
    Convertit une valeur en Decimal de manière optimisée.
    
    Args:
        value: Valeur à convertir (Decimal, int, float, str)
        quantize: Si True, arrondit à 2 décimales (ROUND_HALF_UP)
    
    Returns:
        Decimal: Valeur convertie (et quantifiée si demandé)
    """
    cents = Decimal('0.01')
    
    if isinstance(value, Decimal):
        return value.quantize(cents, rounding=ROUND_HALF_UP) if quantize else value
    elif isinstance(value, (int, float)):
        decimal_value = Decimal(str(value))
        return decimal_value.quantize(cents, rounding=ROUND_HALF_UP) if quantize else decimal_value
    elif isinstance(value, str):
        decimal_value = Decimal(value)
        return decimal_value.quantize(cents, rounding=ROUND_HALF_UP) if quantize else decimal_value
    else:
        raise ValueError(f"Type non supporté pour conversion Decimal: {type(value)}")


def calculate_proportional_fees(
    total_amount: Decimal,
    donation_amount: Decimal,
    tip_amount: Decimal,
    total_stripe_fee: Decimal
) -> tuple[Decimal, Decimal]:
    """
    Calcule la répartition proportionnelle des frais Stripe entre Donation et Tip.
    
    Args:
        total_amount: Montant total du paiement (donation + tip)
        donation_amount: Montant du don
        tip_amount: Montant du tip
        total_stripe_fee: Frais Stripe totaux (depuis charge.balance_transaction.fee)
    
    Returns:
        tuple: (fee_on_donation, fee_on_tip)
    
    Raises:
        ValidationError: Si les montants ne sont pas cohérents
    """
    cents = Decimal('0.01')
    
    # Normaliser les montants
    total_amount = _to_decimal(total_amount)
    donation_amount = _to_decimal(donation_amount)
    tip_amount = _to_decimal(tip_amount)
    total_stripe_fee = _to_decimal(total_stripe_fee)
    
    # Vérifier la cohérence
    expected_total = donation_amount + tip_amount
    if abs(total_amount - expected_total) > cents:
        raise ValidationError(
            f"Montants incohérents: total={total_amount}, donation={donation_amount}, "
            f"tip={tip_amount}, somme={expected_total}"
        )
    
    # Calculer les ratios
    if total_amount == Decimal('0'):
        return Decimal('0'), Decimal('0')
    
    donation_ratio = donation_amount / total_amount
    tip_ratio = tip_amount / total_amount
    
    # Répartir les frais proportionnellement
    fee_on_donation = (total_stripe_fee * donation_ratio).quantize(cents, rounding=ROUND_HALF_UP)
    fee_on_tip = (total_stripe_fee * tip_ratio).quantize(cents, rounding=ROUND_HALF_UP)
    
    # Ajuster pour garantir que la somme des frais = total_stripe_fee (arrondi)
    # Si la somme diffère légèrement à cause des arrondis, ajuster le plus grand
    fee_sum = fee_on_donation + fee_on_tip
    if abs(fee_sum - total_stripe_fee) > cents:
        # Ajuster le plus grand montant pour compenser la différence d'arrondi
        diff = total_stripe_fee - fee_sum
        if fee_on_donation >= fee_on_tip:
            fee_on_donation = (fee_on_donation + diff).quantize(cents, rounding=ROUND_HALF_UP)
        else:
            fee_on_tip = (fee_on_tip + diff).quantize(cents, rounding=ROUND_HALF_UP)
    
    return fee_on_donation, fee_on_tip


@transaction.atomic
def allocate_payment_to_ledgers(
    user,
    donation_amount: Decimal,
    tip_amount: Decimal,
    total_stripe_fee: Decimal,
    project=None,
    idempotency_key=None
):
    """
    Alloue un paiement (Don + Tip) vers les bons Ledgers en déduisant les frais Stripe proportionnellement.
    
    Logique :
    1. Récupérer les frais réels depuis Stripe (charge.balance_transaction.fee)
    2. Calculer les ratios Donation/Tip
    3. Répartir les frais proportionnellement
    4. Enregistrer dans PROJECT_ESCROW (donation net) et OPERATING (tip net)
    
    Args:
        user: Utilisateur qui effectue le paiement
        donation_amount: Montant du don (brut)
        tip_amount: Montant du tip (brut)
        total_stripe_fee: Frais Stripe totaux (depuis charge.balance_transaction.fee)
        project: Projet concerné (optionnel, pour donation)
        idempotency_key: Clé d'idempotence (optionnel)
    
    Returns:
        dict: {
            'donation': {
                'amount_gross': Decimal,
                'stripe_fee': Decimal,
                'amount_net': Decimal,
                'transaction': WalletTransaction
            },
            'tip': {
                'amount_gross': Decimal,
                'stripe_fee': Decimal,
                'amount_net': Decimal,
                'transaction': WalletTransaction
            }
        }
    
    Raises:
        ValidationError: Si les montants sont invalides
    """
    from finance.models import UserWallet, WalletTransaction
    
    cents = Decimal('0.01')
    
    # Normaliser les montants
    donation_amount = _to_decimal(donation_amount)
    tip_amount = _to_decimal(tip_amount)
    total_stripe_fee = _to_decimal(total_stripe_fee)
    total_amount = donation_amount + tip_amount
    
    # Vérifier que les montants sont positifs
    if donation_amount < Decimal('0') or tip_amount < Decimal('0'):
        raise ValidationError("Les montants doivent être positifs ou nuls.")
    
    if total_amount == Decimal('0'):
        raise ValidationError("Le montant total doit être strictement positif.")
    
    # Calculer la répartition proportionnelle des frais
    fee_on_donation, fee_on_tip = calculate_proportional_fees(
        total_amount=total_amount,
        donation_amount=donation_amount,
        tip_amount=tip_amount,
        total_stripe_fee=total_stripe_fee
    )
    
    # Calculer les montants nets
    donation_net = (donation_amount - fee_on_donation).quantize(cents, rounding=ROUND_HALF_UP)
    tip_net = (tip_amount - fee_on_tip).quantize(cents, rounding=ROUND_HALF_UP)
    
    # Vérifier la cohérence : Sum(Net) + Sum(Fees) = Total Payment
    net_sum = donation_net + tip_net
    fee_sum = fee_on_donation + fee_on_tip
    expected_total = net_sum + fee_sum
    
    if abs(expected_total - total_amount) > cents:
        logger.error(
            f"Incohérence dans la répartition des frais: total={total_amount}, "
            f"net_sum={net_sum}, fee_sum={fee_sum}, expected={expected_total}"
        )
        raise ValidationError(
            f"Erreur de calcul: Sum(Net) + Sum(Fees) = {expected_total} ≠ Total Payment = {total_amount}"
        )
    
    # Récupérer ou créer le wallet utilisateur
    wallet, _ = UserWallet.objects.get_or_create(user=user)
    
    # Créer les transactions avec amount_gross, stripe_fee, amount_net
    donation_tx = None
    tip_tx = None
    
    # Transaction pour le don (PROJECT_ESCROW)
    if donation_amount > Decimal('0'):
        donation_tx = WalletTransaction.objects.create(
            wallet=wallet,
            amount=donation_net,  # amount = net (après frais)
            amount_gross=donation_amount,  # Montant brut
            stripe_fee=fee_on_donation,  # Part des frais
            transaction_type='PLEDGE_DONATION',
            related_project=project,
            description=f"Don pour {project.titre if project else 'projet' if project else 'projet'} (net après frais Stripe)",
            idempotency_key=idempotency_key
        )
        
        logger.info(
            f"Transaction donation créée: gross={donation_amount}, fee={fee_on_donation}, "
            f"net={donation_net}, user={user.id}, project={project.id if project else None}"
        )
    
    # Transaction pour le tip (OPERATING)
    # Utiliser un suffixe pour l'idempotency_key du tip pour éviter les conflits
    if tip_amount > Decimal('0'):
        # Vérification d'idempotence pour le tip
        tip_idempotency_key = None
        if idempotency_key:
            import uuid as uuid_module
            if isinstance(idempotency_key, uuid_module.UUID):
                # Générer une clé unique pour le tip basée sur la clé principale
                tip_idempotency_key = uuid_module.uuid5(idempotency_key, 'tip')
            else:
                # Si c'est un string, générer un UUID à partir de celui-ci
                namespace = uuid_module.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
                tip_idempotency_key = uuid_module.uuid5(namespace, f"{idempotency_key}-tip")
        
        if tip_idempotency_key and WalletTransaction.objects.filter(idempotency_key=tip_idempotency_key).exists():
            logger.warning(f"Transaction tip déjà traitée (idempotence): {tip_idempotency_key}")
            raise ValidationError("Cette transaction de tip a déjà été traitée.")
        
        tip_tx = WalletTransaction.objects.create(
            wallet=wallet,
            amount=tip_net,  # amount = net (après frais)
            amount_gross=tip_amount,  # Montant brut
            stripe_fee=fee_on_tip,  # Part des frais
            transaction_type='DEPOSIT',  # Type approprié pour tip (à ajuster selon besoins)
            related_project=None,
            description="Tip pour EGOEJO (net après frais Stripe)",
            idempotency_key=tip_idempotency_key
        )
        
        logger.info(
            f"Transaction tip créée: gross={tip_amount}, fee={fee_on_tip}, "
            f"net={tip_net}, user={user.id}"
        )
    
    return {
        'donation': {
            'amount_gross': donation_amount,
            'stripe_fee': fee_on_donation,
            'amount_net': donation_net,
            'transaction': donation_tx
        } if donation_tx else None,
        'tip': {
            'amount_gross': tip_amount,
            'stripe_fee': fee_on_tip,
            'amount_net': tip_net,
            'transaction': tip_tx
        } if tip_tx else None
    }


def extract_stripe_fee_from_webhook(webhook_event_data: dict) -> Decimal:
    """
    Extrait les frais Stripe réels depuis un événement webhook payment_intent.succeeded.
    
    Logique :
    1. Récupérer charge.balance_transaction.fee depuis l'objet Stripe (vérité source)
    2. Si balance_transaction est expandé, utiliser directement
    3. Sinon, récupérer depuis l'API Stripe
    
    Args:
        webhook_event_data: Données de l'événement Stripe (payment_intent.succeeded)
    
    Returns:
        Decimal: Frais Stripe totaux (depuis charge.balance_transaction.fee)
    
    Raises:
        ValidationError: Si les frais ne peuvent pas être extraits
    """
    try:
        # Import conditionnel de stripe (peut ne pas être installé en dev)
        try:
            import stripe
        except ImportError:
            stripe = None
            logger.warning("Module 'stripe' non installé. Impossible de récupérer balance_transaction depuis l'API.")
        
        # Récupérer le payment_intent
        payment_intent = webhook_event_data.get('data', {}).get('object', {})
        
        # Récupérer la charge associée
        charges = payment_intent.get('charges', {}).get('data', [])
        if not charges:
            raise ValidationError("Aucune charge trouvée dans le payment_intent")
        
        # Prendre la première charge (normalement il n'y en a qu'une)
        charge = charges[0]
        
        # Récupérer balance_transaction
        balance_transaction_id = charge.get('balance_transaction')
        if not balance_transaction_id:
            raise ValidationError("balance_transaction manquant dans la charge")
        
        # Si balance_transaction est un objet (expandé), récupérer directement fee
        if isinstance(balance_transaction_id, dict):
            fee = balance_transaction_id.get('fee')
        else:
            # Sinon, récupérer l'objet balance_transaction depuis l'API Stripe
            # C'est la vérité source : charge.balance_transaction.fee
            if stripe is None:
                raise ValidationError(
                    "balance_transaction non expandé et module 'stripe' non disponible. "
                    "Utilisez expand[]=charges.data.balance_transaction dans la configuration du webhook Stripe, "
                    "ou installez le module 'stripe' (pip install stripe)."
                )
            
            try:
                balance_transaction = stripe.BalanceTransaction.retrieve(balance_transaction_id)
                fee = balance_transaction.fee
            except Exception as stripe_error:
                logger.error(
                    f"Erreur lors de la récupération de balance_transaction depuis Stripe: {stripe_error}",
                    exc_info=True
                )
                raise ValidationError(
                    f"Impossible de récupérer balance_transaction depuis Stripe: {stripe_error}. "
                    "Assurez-vous que STRIPE_SECRET_KEY est configuré, ou utilisez "
                    "expand[]=charges.data.balance_transaction dans la configuration du webhook."
                )
        
        if fee is None:
            raise ValidationError("Frais Stripe non trouvés dans balance_transaction")
        
        return _to_decimal(fee / 100)  # Stripe retourne les montants en centimes
    
    except (KeyError, TypeError, ValueError) as e:
        logger.error(f"Erreur lors de l'extraction des frais Stripe: {e}", exc_info=True)
        raise ValidationError(f"Impossible d'extraire les frais Stripe: {e}")


def process_stripe_payment_webhook(webhook_event_data: dict, user, project=None):
    """
    Traite un webhook Stripe payment_intent.succeeded et alloue les fonds aux Ledgers.
    
    Args:
        webhook_event_data: Données de l'événement Stripe
        user: Utilisateur qui effectue le paiement
        project: Projet concerné (optionnel)
    
    Returns:
        dict: Résultat de allocate_payment_to_ledgers
    """
    # Extraire les montants depuis le payment_intent
    payment_intent = webhook_event_data.get('data', {}).get('object', {})
    total_amount = _to_decimal(payment_intent.get('amount', 0) / 100)  # Stripe en centimes
    
    # Extraire donation_amount et tip_amount depuis metadata ou line_items
    # Pour l'instant, on suppose qu'ils sont dans metadata
    metadata = payment_intent.get('metadata', {})
    donation_amount = _to_decimal(metadata.get('donation_amount', 0))
    tip_amount = _to_decimal(metadata.get('tip_amount', 0))
    
    # Si metadata n'est pas disponible, utiliser des valeurs par défaut
    # (à ajuster selon l'implémentation réelle)
    if donation_amount == Decimal('0') and tip_amount == Decimal('0'):
        # Par défaut, tout est considéré comme donation
        donation_amount = total_amount
        tip_amount = Decimal('0')
    
    # Extraire les frais Stripe réels
    total_stripe_fee = extract_stripe_fee_from_webhook(webhook_event_data)
    
    # Récupérer idempotency_key depuis metadata ou générer un UUID à partir de payment_intent.id
    import uuid as uuid_module
    idempotency_key = metadata.get('idempotency_key')
    if not idempotency_key:
        # Générer un UUID v5 à partir du payment_intent.id pour garantir l'idempotence
        payment_intent_id = payment_intent.get('id', '')
        if payment_intent_id:
            # Utiliser un namespace UUID fixe pour générer un UUID déterministe
            namespace = uuid_module.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # Namespace DNS
            idempotency_key = uuid_module.uuid5(namespace, payment_intent_id)
        else:
            idempotency_key = None
    
    # Allouer aux Ledgers
    return allocate_payment_to_ledgers(
        user=user,
        donation_amount=donation_amount,
        tip_amount=tip_amount,
        total_stripe_fee=total_stripe_fee,
        project=project,
        idempotency_key=idempotency_key
    )


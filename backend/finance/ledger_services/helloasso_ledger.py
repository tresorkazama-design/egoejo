"""
Service de Ledger pour HelloAsso (mode simulé).

Traite les webhooks HelloAsso et alloue les fonds aux Ledgers.
Similaire à process_stripe_payment_webhook mais adapté au format HelloAsso.
"""
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
import logging
import uuid as uuid_module

from .ledger import allocate_payment_to_ledgers, _to_decimal

logger = logging.getLogger(__name__)


def extract_helloasso_fee_from_webhook(webhook_event_data: dict) -> Decimal:
    """
    Extrait les frais HelloAsso depuis un événement webhook.
    
    HelloAsso ne fournit pas toujours les frais dans le webhook.
    En mode simulé, on utilise une estimation basée sur les frais HelloAsso standards.
    
    Args:
        webhook_event_data: Données de l'événement HelloAsso
    
    Returns:
        Decimal: Frais HelloAsso (estimés si non fournis)
    """
    from django.conf import settings
    
    # HelloAsso frais standards : 0.8% + 0.25€ par transaction
    HELLOASSO_PERCENT_FEE = Decimal('0.008')  # 0.8%
    HELLOASSO_FIXED_FEE = Decimal('0.25')  # 0.25€
    
    # Essayer d'extraire les frais depuis le webhook
    payment = webhook_event_data.get('data', {}).get('payment', {})
    fee_amount = payment.get('fee', None)
    
    if fee_amount is not None:
        # Frais fournis dans le webhook (en centimes)
        return _to_decimal(fee_amount / 100)
    
    # Si les frais ne sont pas fournis, estimer depuis le montant
    amount = payment.get('amount', 0)
    if amount > 0:
        amount_decimal = _to_decimal(amount / 100)  # HelloAsso en centimes
        estimated_fee = (amount_decimal * HELLOASSO_PERCENT_FEE) + HELLOASSO_FIXED_FEE
        logger.warning(
            f"Frais HelloAsso non fournis dans webhook, estimation utilisée: {estimated_fee}€ "
            f"(montant: {amount_decimal}€)"
        )
        return _to_decimal(estimated_fee)
    
    raise ValidationError("Impossible d'extraire ou d'estimer les frais HelloAsso")


@transaction.atomic
def process_helloasso_payment_webhook(webhook_event_data: dict, user, project=None):
    """
    Traite un webhook HelloAsso et alloue les fonds aux Ledgers.
    
    Format HelloAsso webhook (exemple) :
    {
        "eventType": "Payment",
        "data": {
            "payment": {
                "id": "payment_123",
                "amount": 10000,  # en centimes
                "fee": 80,  # en centimes (optionnel)
                "metadata": {
                    "user_id": "123",
                    "project_id": "456",
                    "donation_amount": "100.00",
                    "tip_amount": "0.00"
                }
            }
        }
    }
    
    Args:
        webhook_event_data: Données de l'événement HelloAsso
        user: Utilisateur qui effectue le paiement
        project: Projet concerné (optionnel)
    
    Returns:
        dict: Résultat de allocate_payment_to_ledgers
    """
    # Extraire les montants depuis le payment HelloAsso
    payment = webhook_event_data.get('data', {}).get('payment', {})
    total_amount = _to_decimal(payment.get('amount', 0) / 100)  # HelloAsso en centimes
    
    # Extraire donation_amount et tip_amount depuis metadata
    metadata = payment.get('metadata', {})
    donation_amount = _to_decimal(metadata.get('donation_amount', 0))
    tip_amount = _to_decimal(metadata.get('tip_amount', 0))
    
    # Si metadata n'est pas disponible, utiliser des valeurs par défaut
    if donation_amount == Decimal('0') and tip_amount == Decimal('0'):
        # Par défaut, tout est considéré comme donation
        donation_amount = total_amount
        tip_amount = Decimal('0')
    
    # Extraire les frais HelloAsso (estimés si non fournis)
    total_helloasso_fee = extract_helloasso_fee_from_webhook(webhook_event_data)
    
    # Récupérer idempotency_key depuis metadata ou générer un UUID à partir de payment.id
    idempotency_key = metadata.get('idempotency_key')
    if not idempotency_key:
        # Générer un UUID v5 à partir du payment.id pour garantir l'idempotence
        payment_id = payment.get('id', '')
        if payment_id:
            # Utiliser un namespace UUID fixe pour générer un UUID déterministe
            namespace = uuid_module.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # Namespace DNS
            idempotency_key = uuid_module.uuid5(namespace, f"helloasso_{payment_id}")
        else:
            idempotency_key = None
    
    # Allouer aux Ledgers (même logique que Stripe)
    return allocate_payment_to_ledgers(
        user=user,
        donation_amount=donation_amount,
        tip_amount=tip_amount,
        total_stripe_fee=total_helloasso_fee,  # Utilise le même paramètre (frais HelloAsso)
        project=project,
        idempotency_key=idempotency_key
    )


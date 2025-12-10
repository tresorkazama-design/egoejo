"""
Modèles pour le système financier unifié (Wallet, Escrow, Transactions).
Supporte V1.6 (Dons) et V2.0 (Investissement dormant).
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class UserWallet(models.Model):
    """
    Portefeuille utilisateur (Wallet universel).
    Gère les dépôts depuis Stripe et les engagements (Dons ou Investissement).
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Solde disponible (€)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'finance'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Wallet {self.user.username} - {self.balance} €"


class WalletTransaction(models.Model):
    """
    Transaction sur le wallet (universel V1.6/V2.0).
    """
    TYPES = [
        ('DEPOSIT', 'Dépôt (Stripe -> Wallet)'),
        ('PLEDGE_DONATION', 'Don (Cantonné)'),  # V1.6
        ('PLEDGE_EQUITY', 'Investissement (Cantonné)'),  # V2.0 (Dormant)
        ('REFUND', 'Remboursement'),
        ('RELEASE', 'Libération des fonds'),
        ('COMMISSION', 'Commission EGOEJO'),
        ('POCKET_TRANSFER', 'Transfert vers Pocket'),  # Nouveau type pour les transfers vers pockets
    ]

    wallet = models.ForeignKey(
        UserWallet,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TYPES
    )
    related_project = models.ForeignKey(
        'core.Projet',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='wallet_transactions'
    )
    description = models.TextField(blank=True)
    # CORRECTION 5 : Idempotency key pour éviter double dépense
    idempotency_key = models.UUIDField(
        unique=True,
        null=True,
        blank=True,
        help_text="Clé unique pour éviter de rejouer la même transaction (dédoublonnage)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'finance'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['idempotency_key']),  # Index pour recherche rapide
        ]

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} €"


class EscrowContract(models.Model):
    """
    Contrat d'escrow (cantonnement) pour Dons ou Investissement.
    Les fonds sont verrouillés jusqu'à la libération par l'admin.
    """
    STATUS_CHOICES = [
        ('LOCKED', 'Verrouillé (Cantonné)'),
        ('RELEASED', 'Libéré'),
        ('REFUNDED', 'Remboursé'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='escrow_contracts'
    )
    project = models.ForeignKey(
        'core.Projet',
        on_delete=models.PROTECT,
        related_name='escrow_contracts'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='LOCKED'
    )
    pledge_transaction = models.OneToOneField(
        WalletTransaction,
        on_delete=models.PROTECT,
        related_name='escrow_contract',
        help_text="Transaction de cantonnement associée"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'finance'
        ordering = ['-created_at']

    def __str__(self):
        return f"Escrow {self.user.username} - {self.project.titre} - {self.amount} € ({self.status})"


class WalletPocket(models.Model):
    """
    Sous-compte (pocket) lié au UserWallet.
    Permet de segmenter les fonds par objectif (Dons, Réserve d'investissement, etc.).
    """
    POCKET_TYPES = [
        ('DONATION', 'Dons'),
        ('INVESTMENT_RESERVE', 'Réserve d\'investissement'),
    ]

    wallet = models.ForeignKey(
        UserWallet,
        on_delete=models.CASCADE,
        related_name='pockets',
        help_text="Wallet parent"
    )
    name = models.CharField(
        max_length=100,
        help_text="Nom de la pocket (ex: 'Dons Environnement', 'Réserve Investissement')"
    )
    pocket_type = models.CharField(
        max_length=20,
        choices=POCKET_TYPES,
        help_text="Type de pocket"
    )
    allocation_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        validators=[
            MinValueValidator(Decimal('0')),
            # Validation personnalisée pour <= 100 dans clean()
        ],
        help_text="Pourcentage d'allocation automatique (0-100)"
    )
    target_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Montant objectif (optionnel)"
    )
    current_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Montant actuel dans la pocket"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'finance'
        ordering = ['-created_at']
        unique_together = [['wallet', 'name']]  # Un nom unique par wallet

    def clean(self):
        """Validation personnalisée"""
        from django.core.exceptions import ValidationError
        if self.allocation_percentage > Decimal('100'):
            raise ValidationError({
                'allocation_percentage': 'Le pourcentage d\'allocation ne peut pas dépasser 100%.'
            })

    def save(self, *args, **kwargs):
        """Appeler clean() avant la sauvegarde"""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.wallet.user.username}) - {self.current_amount} €"

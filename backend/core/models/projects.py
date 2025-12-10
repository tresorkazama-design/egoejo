"""
Modèles pour les projets et médias associés.
"""
from django.db import models
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q, QuerySet
from django.conf import settings
from decimal import Decimal


class ProjetQuerySet(QuerySet):
    """
    QuerySet personnalisé avec recherche full-text utilisant pg_trgm
    """
    def search(self, query):
        """
        Recherche floue avec pg_trgm (Trigram similarity)
        Nécessite l'extension PostgreSQL: CREATE EXTENSION IF NOT EXISTS pg_trgm;
        """
        if not query or len(query) < 2:
            return self.none()
        
        try:
            # Recherche avec similarité trigram
            # Combine recherche exacte (icontains) et similarité (trigram)
            return self.annotate(
                similarity=TrigramSimilarity('titre', query) +
                           TrigramSimilarity('description', query) * 0.5
            ).filter(
                Q(titre__icontains=query) |
                Q(description__icontains=query) |
                Q(similarity__gt=0.1)  # Seuil de similarité minimum
            ).order_by('-similarity', '-created_at').distinct()
        except Exception:
            # Fallback si pg_trgm n'est pas disponible
            return self.filter(
                Q(titre__icontains=query) |
                Q(description__icontains=query)
            ).order_by('-created_at')


class FundingType(models.TextChoices):
    """
    Types de financement supportés (V1.6 + V2.0 dormant)
    """
    DONATION = 'DONATION', 'Don Philanthropique'
    EQUITY = 'EQUITY', 'Investissement (Actions)'  # Dormant V2.0
    HYBRID = 'HYBRID', 'Mixte (Blended Finance)'  # Dormant V2.0


class Projet(models.Model):
    """
    Modèle pour les projets du collectif.
    Supporte V1.6 (Dons) et V2.0 (Investissement dormant).
    """
    titre = models.CharField(max_length=255)
    description = models.TextField()
    categorie = models.CharField(max_length=100, blank=True, null=True)
    impact_score = models.IntegerField(blank=True, null=True)
    image = models.FileField(upload_to='projets/', blank=True, null=True)
    embedding = models.JSONField(
        blank=True,
        null=True,
        help_text="Vecteur d'embedding pour recherche sémantique (pgvector future)"
    )
    coordinates_3d = models.JSONField(
        blank=True,
        null=True,
        help_text="Coordonnées 3D (x, y, z) pour visualisation Mycélium Numérique"
    )
    
    # ========== V1.6 + V2.0 HYBRID ==========
    # Type de financement
    funding_type = models.CharField(
        max_length=10,
        choices=FundingType.choices,
        default=FundingType.DONATION,
        help_text="Type de financement (DONATION par défaut, EQUITY/HYBRID dormant V2.0)"
    )
    
    # Objectifs financiers distincts
    donation_goal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Objectif de dons (€)"
    )
    investment_goal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Objectif d'investissement (€) - Dormant V2.0"
    )
    
    # Configuration V2.0 (Dormant tant que investment_goal = 0)
    share_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Prix de l'action (€) - Dormant V2.0"
    )
    total_shares = models.IntegerField(
        null=True,
        blank=True,
        help_text="Nombre total d'actions - Dormant V2.0"
    )
    valuation_pre_money = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valorisation pré-money (€) - Dormant V2.0"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    # Utiliser le QuerySet personnalisé
    objects = ProjetQuerySet.as_manager()

    def __str__(self):
        return self.titre
    
    @property
    def is_investment_open(self):
        """
        Vérifie si l'investissement est possible ET activé globalement.
        """
        return (
            settings.ENABLE_INVESTMENT_FEATURES and
            self.funding_type in ['EQUITY', 'HYBRID'] and
            self.investment_goal > 0
        )
    
    @property
    def donation_current(self):
        """
        Montant actuel collecté en dons (via EscrowContract).
        """
        try:
            from finance.models import EscrowContract
            from django.db.models import Sum
            result = EscrowContract.objects.filter(
                project=self,
                status__in=['LOCKED', 'RELEASED'],
                pledge_transaction__transaction_type='PLEDGE_DONATION'
            ).aggregate(
                total=Sum('amount')
            )
            return result['total'] or Decimal('0')
        except Exception:
            return Decimal('0')
    
    @property
    def investment_current(self):
        """
        Montant actuel collecté en investissement (via EscrowContract).
        """
        if not self.is_investment_open:
            return Decimal('0')
        try:
            from finance.models import EscrowContract
            from django.db.models import Sum
            from decimal import Decimal
            result = EscrowContract.objects.filter(
                project=self,
                status__in=['LOCKED', 'RELEASED'],
                pledge_transaction__transaction_type='PLEDGE_EQUITY'
            ).aggregate(
                total=Sum('amount')
            )
            return result['total'] or Decimal('0')
        except Exception:
            return Decimal('0')

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']


class Media(models.Model):
    """
    Modèle pour les médias associés aux projets.
    """
    fichier = models.FileField(upload_to='projets_medias/')
    description = models.CharField(max_length=255, blank=True, null=True)
    projet = models.ForeignKey(
        Projet,
        on_delete=models.CASCADE,
        related_name='medias'
    )

    def __str__(self):
        return f"{self.projet.titre} - {self.description or 'Media'}"

    class Meta:
        app_label = 'core'

"""
Modèles pour l'investissement (V2.0 dormant).
Ce tableau ne se remplira que quand le feature flag ENABLE_INVESTMENT_FEATURES est activé.
"""
from django.db import models
from django.conf import settings
from core.models import Projet


class ShareholderRegister(models.Model):
    """
    Registre des actionnaires (V2.0 dormant).
    Ce tableau ne se remplira que quand le feature flag ENABLE_INVESTMENT_FEATURES est activé.
    """
    project = models.ForeignKey(
        Projet,
        on_delete=models.PROTECT,
        related_name='shareholders'
    )
    investor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='shareholdings'
    )
    
    number_of_shares = models.IntegerField(
        help_text="Nombre d'actions détenues"
    )
    amount_invested = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Montant investi (€)"
    )
    
    # Preuve légale (PDF signé via YouSign/DocuSign)
    subscription_bulletin = models.FileField(
        upload_to='secure/legal/',
        null=True,
        blank=True,
        help_text="Bulletin de souscription signé (PDF)"
    )
    is_signed = models.BooleanField(
        default=False,
        help_text="Bulletin signé et validé"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('project', 'investor')
        app_label = 'investment'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.investor.username} - {self.project.titre} ({self.number_of_shares} actions)"

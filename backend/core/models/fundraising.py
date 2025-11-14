"""
Modèles liés aux cagnottes et contributions.
"""

from django.conf import settings
from django.db import models


class Cagnotte(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    montant_cible = models.FloatField()
    montant_collecte = models.FloatField(default=0)
    projet = models.ForeignKey(
        "core.Projet", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre

    class Meta:
        app_label = "core"


class Contribution(models.Model):
    cagnotte = models.ForeignKey(
        Cagnotte, on_delete=models.CASCADE, related_name="contributions"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    montant = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "core"


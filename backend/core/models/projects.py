"""
Modèles liés aux projets (unités de base du catalogue EGOEJO).
"""

from django.db import models


class Projet(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    categorie = models.CharField(max_length=100, blank=True, null=True)
    impact_score = models.IntegerField(blank=True, null=True)
    image = models.FileField(upload_to="projets/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre

    class Meta:
        app_label = "core"


class Media(models.Model):
    fichier = models.FileField(upload_to="projets_medias/", blank=False, null=False)
    description = models.CharField(max_length=255, blank=True, null=True)
    projet = models.ForeignKey("Projet", on_delete=models.CASCADE, related_name="medias")

    def __str__(self):
        return f"Media pour: {self.projet.titre}"

    class Meta:
        app_label = "core"


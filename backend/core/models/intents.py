"""
Modèles autour des intentions d'engagement.
"""

from django.db import models


class Intent(models.Model):
    nom = models.CharField(max_length=255)
    email = models.EmailField()
    profil = models.CharField(max_length=100)
    message = models.TextField(blank=True, null=True)
    ip = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    document_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        app_label = "core"
        verbose_name = "Intention"
        verbose_name_plural = "Intentions"

    def __str__(self):
        return f"{self.nom} ({self.email}) - {self.profil}"


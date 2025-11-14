"""
Modèles liés à la journalisation des actions sensibles.
"""

from django.conf import settings
from django.db import models

from .common import default_metadata


class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=100)
    target_type = models.CharField(max_length=50)
    target_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=default_metadata, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        app_label = "core"

    def __str__(self):
        return f"{self.action} by {self.actor or 'system'}"


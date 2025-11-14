"""
Modèles pour la modération des contenus et signalements.
"""

from django.conf import settings
from django.db import models


class ModerationReport(models.Model):
    TYPE_MESSAGE = "message"
    TYPE_USER = "user"
    TYPE_POLL = "poll"
    TYPE_PROJECT = "project"
    TYPE_CHOICES = [
        (TYPE_MESSAGE, "Message"),
        (TYPE_USER, "User"),
        (TYPE_POLL, "Poll"),
        (TYPE_PROJECT, "Project"),
    ]

    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
    ]

    report_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    target_id = models.CharField(max_length=64)
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reports_created",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    reason = models.TextField()
    resolution = models.TextField(blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports_resolved",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        app_label = "core"

    def __str__(self):
        return f"Report #{self.pk} ({self.report_type})"


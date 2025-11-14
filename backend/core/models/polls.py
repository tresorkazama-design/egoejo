"""
Modèles pour les scrutins et votes.
"""

from django.conf import settings
from django.db import models

from .common import default_metadata


class Poll(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_OPEN, "Open"),
        (STATUS_CLOSED, "Closed"),
    ]

    project = models.ForeignKey(
        "core.Projet",
        on_delete=models.SET_NULL,
        related_name="polls",
        blank=True,
        null=True,
    )
    title = models.CharField(max_length=255)
    question = models.TextField()
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    is_anonymous = models.BooleanField(default=True)
    allow_multiple = models.BooleanField(default=False)
    quorum = models.PositiveIntegerField(blank=True, null=True)
    opens_at = models.DateTimeField(blank=True, null=True)
    closes_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="polls_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        app_label = "core"

    def __str__(self):
        return self.title


class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
    label = models.CharField(max_length=255)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]
        app_label = "core"

    def __str__(self):
        return f"{self.poll.title} -> {self.label}"


class PollBallot(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="ballots")
    option = models.ForeignKey(
        PollOption, on_delete=models.CASCADE, related_name="ballots"
    )
    voter_hash = models.CharField(max_length=128)
    metadata = models.JSONField(default=default_metadata, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("poll", "option", "voter_hash")
        app_label = "core"

    def __str__(self):
        return f"Ballot {self.pk} for {self.poll.title}"


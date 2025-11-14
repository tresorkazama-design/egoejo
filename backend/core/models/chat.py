"""
Modèles autour du module chat (threads, messages, memberships).
"""

from django.conf import settings
from django.db import models
from django.utils import timezone

from .common import default_metadata


class ChatThread(models.Model):
    title = models.CharField(max_length=255, blank=True)
    project = models.ForeignKey(
        "core.Projet",
        on_delete=models.SET_NULL,
        related_name="threads",
        blank=True,
        null=True,
    )
    is_private = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="threads_created",
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="ChatMembership",
        related_name="chat_threads",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-last_message_at", "-created_at"]
        app_label = "core"

    def __str__(self):
        return self.title or f"Thread #{self.pk}"


class ChatMembership(models.Model):
    ROLE_OWNER = "owner"
    ROLE_MODERATOR = "moderator"
    ROLE_MEMBER = "member"
    ROLE_CHOICES = [
        (ROLE_OWNER, "Owner"),
        (ROLE_MODERATOR, "Moderator"),
        (ROLE_MEMBER, "Member"),
    ]

    thread = models.ForeignKey(
        ChatThread, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_memberships",
    )
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("thread", "user")
        app_label = "core"

    def __str__(self):
        return f"{self.user} -> {self.thread} ({self.role})"


class ChatMessage(models.Model):
    thread = models.ForeignKey(
        ChatThread, on_delete=models.CASCADE, related_name="messages"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="chat_messages",
    )
    content = models.TextField()
    attachment = models.FileField(upload_to="chat_attachments/", blank=True, null=True)
    metadata = models.JSONField(default=default_metadata, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["created_at"]
        app_label = "core"

    def __str__(self):
        return f"Message #{self.pk} in {self.thread}"

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])


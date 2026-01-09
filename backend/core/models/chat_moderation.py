"""
Modèles de modération pour le chat (P1/P2).

Modération minimale : report message -> stored
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class ChatMessageReport(models.Model):
    """
    Signalement d'un message de chat.
    
    Modération minimale : stocker les signalements pour audit.
    """
    STATUS_PENDING = 'pending'
    STATUS_REVIEWED = 'reviewed'
    STATUS_DISMISSED = 'dismissed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'En attente'),
        (STATUS_REVIEWED, 'Examiné'),
        (STATUS_DISMISSED, 'Rejeté'),
    ]
    
    message = models.ForeignKey(
        'core.ChatMessage',
        on_delete=models.CASCADE,
        related_name='reports',
        help_text="Message signalé"
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='chat_reports',
        help_text="Utilisateur qui a signalé le message"
    )
    reason = models.TextField(
        blank=True,
        help_text="Raison du signalement (optionnel)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        help_text="Statut du signalement"
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_reports_reviewed',
        help_text="Modérateur qui a examiné le signalement"
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date d'examen du signalement"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        app_label = 'core'
        # Un utilisateur ne peut signaler un message qu'une fois
        unique_together = [('message', 'reporter')]
    
    def __str__(self):
        return f"Report #{self.pk} - Message #{self.message_id} by {self.reporter}"
    
    def mark_reviewed(self, reviewer):
        """Marque le signalement comme examiné"""
        self.status = self.STATUS_REVIEWED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'updated_at'])
    
    def mark_dismissed(self, reviewer):
        """Marque le signalement comme rejeté"""
        self.status = self.STATUS_DISMISSED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'updated_at'])


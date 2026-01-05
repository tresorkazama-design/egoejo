"""
Modèles pour le système d'alerte critique EGOEJO.

Enregistre les événements d'alerte critique pour traçabilité et métriques.
"""
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
import json


class CriticalAlertEvent(models.Model):
    """
    Événement d'alerte critique enregistré.
    
    Enregistré uniquement quand une alerte est réellement émise
    (après dédoublonnage, si email/webhook envoyé).
    """
    
    SEVERITY_CHOICES = [
        ('critical', 'Critique'),
        ('high', 'Élevée'),
        ('medium', 'Moyenne'),
        ('low', 'Faible'),
    ]
    
    CHANNEL_CHOICES = [
        ('email', 'Email uniquement'),
        ('webhook', 'Webhook uniquement'),
        ('both', 'Email + Webhook'),
    ]
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Date et heure de création de l'événement"
    )
    
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default='critical',
        db_index=True,
        help_text="Sévérité de l'alerte"
    )
    
    event_type = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Type d'événement (ex: 'INTEGRITY BREACH DETECTED', 'SAKA WALLET INCONSISTENCY')"
    )
    
    channel = models.CharField(
        max_length=10,
        choices=CHANNEL_CHOICES,
        db_index=True,
        help_text="Canal d'envoi de l'alerte"
    )
    
    fingerprint = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Empreinte unique pour dédoublonnage (dedupe_key ou généré)"
    )
    
    payload_excerpt = models.JSONField(
        null=True,
        blank=True,
        help_text="Extrait du payload (champs principaux pour recherche rapide)"
    )
    
    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['channel', 'created_at']),
            models.Index(fields=['severity', 'created_at']),
        ]
        verbose_name = "Événement d'alerte critique"
        verbose_name_plural = "Événements d'alerte critique"
    
    def __str__(self):
        return f"{self.event_type} ({self.severity}) - {self.created_at}"
    
    @classmethod
    def create_from_alert(
        cls,
        title: str,
        payload: dict,
        channel: str,
        fingerprint: str,
        severity: str = 'critical'
    ) -> 'CriticalAlertEvent':
        """
        Crée un événement d'alerte critique à partir d'une alerte.
        
        Args:
            title: Titre de l'alerte (utilisé comme event_type)
            payload: Payload complet de l'alerte
            channel: Canal d'envoi ('email', 'webhook', 'both')
            fingerprint: Empreinte unique (dedupe_key ou généré)
            severity: Sévérité de l'alerte (défaut: 'critical')
        
        Returns:
            CriticalAlertEvent: Instance créée
        """
        # Extraire un excerpt du payload (champs principaux)
        excerpt = {}
        important_fields = [
            'user_id', 'username', 'email', 'violation_type',
            'old_balance', 'new_balance', 'delta', 'detection_method'
        ]
        for field in important_fields:
            if field in payload:
                excerpt[field] = payload[field]
        
        return cls.objects.create(
            event_type=title,
            severity=severity,
            channel=channel,
            fingerprint=fingerprint,
            payload_excerpt=excerpt if excerpt else None
        )
    
    @classmethod
    def count_critical_alerts_for_month(cls, year: int, month: int) -> int:
        """
        Compte le nombre d'événements d'alerte critique pour un mois donné.
        
        Alias pour count_for_month() pour compatibilité avec l'API demandée.
        
        Utilise UTC pour les calculs de date (timezone-aware).
        
        Args:
            year: Année (ex: 2025)
            month: Mois (1-12)
        
        Returns:
            int: Nombre d'événements pour le mois
        """
        return cls.count_for_month(year, month)
    
    @classmethod
    def count_for_month(cls, year: int, month: int) -> int:
        """
        Compte le nombre d'événements d'alerte critique pour un mois donné.
        
        Utilise UTC pour les calculs de date (timezone-aware).
        
        Args:
            year: Année (ex: 2025)
            month: Mois (1-12)
        
        Returns:
            int: Nombre d'événements pour le mois
        """
        # Créer les dates de début et fin du mois en UTC
        start_date = timezone.make_aware(
            datetime(year, month, 1, 0, 0, 0)
        )
        
        # Calculer le dernier jour du mois
        if month == 12:
            end_date = timezone.make_aware(
                datetime(year + 1, 1, 1, 0, 0, 0)
            )
        else:
            end_date = timezone.make_aware(
                datetime(year, month + 1, 1, 0, 0, 0)
            )
        
        return cls.objects.filter(
            created_at__gte=start_date,
            created_at__lt=end_date
        ).count()
    
    @classmethod
    def count_by_event_type_for_month(cls, year: int, month: int) -> dict:
        """
        Compte les événements par type pour un mois donné.
        
        Args:
            year: Année (ex: 2025)
            month: Mois (1-12)
        
        Returns:
            dict: Dictionnaire {event_type: count}
        """
        # Créer les dates de début et fin du mois en UTC
        start_date = timezone.make_aware(
            datetime(year, month, 1, 0, 0, 0)
        )
        
        if month == 12:
            end_date = timezone.make_aware(
                datetime(year + 1, 1, 1, 0, 0, 0)
            )
        else:
            end_date = timezone.make_aware(
                datetime(year, month + 1, 1, 0, 0, 0)
            )
        
        from django.db.models import Count
        
        queryset = cls.objects.filter(
            created_at__gte=start_date,
            created_at__lt=end_date
        ).values('event_type').annotate(
            count=Count('id')
        )
        
        return {item['event_type']: item['count'] for item in queryset}
    
    @classmethod
    def count_by_channel_for_month(cls, year: int, month: int) -> dict:
        """
        Compte les événements par canal pour un mois donné.
        
        Args:
            year: Année (ex: 2025)
            month: Mois (1-12)
        
        Returns:
            dict: Dictionnaire {channel: count}
        """
        # Créer les dates de début et fin du mois en UTC
        start_date = timezone.make_aware(
            datetime(year, month, 1, 0, 0, 0)
        )
        
        if month == 12:
            end_date = timezone.make_aware(
                datetime(year + 1, 1, 1, 0, 0, 0)
            )
        else:
            end_date = timezone.make_aware(
                datetime(year, month + 1, 1, 0, 0, 0)
            )
        
        from django.db.models import Count
        
        queryset = cls.objects.filter(
            created_at__gte=start_date,
            created_at__lt=end_date
        ).values('channel').annotate(
            count=Count('id')
        )
        
        return {item['channel']: item['count'] for item in queryset}


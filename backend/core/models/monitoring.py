"""
Modèles pour le monitoring et les métriques de performance
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import json


class PerformanceMetric(models.Model):
    """
    Métrique de performance (LCP, FID, CLS, etc.)
    """
    METRIC_TYPES = [
        ('LCP', 'Largest Contentful Paint'),
        ('FID', 'First Input Delay'),
        ('CLS', 'Cumulative Layout Shift'),
        ('TTFB', 'Time to First Byte'),
        ('FCP', 'First Contentful Paint'),
        ('PageLoad', 'Page Load Time'),
        ('DOMContentLoaded', 'DOM Content Loaded'),
        ('API_Duration', 'API Request Duration'),
        ('Custom', 'Custom Metric'),
    ]

    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    value = models.FloatField(help_text="Valeur de la métrique")
    url = models.URLField(max_length=500, blank=True, null=True, help_text="URL de la page")
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Utilisateur (si authentifié)"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Métadonnées supplémentaires (endpoint, etc.)"
    )
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    user_agent = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'monitoring_performance_metric'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'metric_type']),
            models.Index(fields=['metric_type', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.metric_type}: {self.value} @ {self.timestamp}"


class MonitoringAlert(models.Model):
    """
    Alerte de monitoring (erreurs, performance, etc.)
    """
    ALERT_LEVELS = [
        ('critical', 'Critical'),
        ('error', 'Error'),
        ('warning', 'Warning'),
        ('info', 'Info'),
        ('performance', 'Performance'),
        ('api', 'API'),
    ]

    level = models.CharField(max_length=20, choices=ALERT_LEVELS)
    message = models.TextField(help_text="Message d'alerte")
    url = models.URLField(max_length=500, blank=True, null=True, help_text="URL de la page")
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Utilisateur (si authentifié)"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Métadonnées supplémentaires (contexte, etc.)"
    )
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    resolved = models.BooleanField(default=False, help_text="Alerte résolue")
    resolved_at = models.DateTimeField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'monitoring_alert'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'level']),
            models.Index(fields=['level', 'resolved', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.level}: {self.message[:50]} @ {self.timestamp}"

    def resolve(self):
        """Marquer l'alerte comme résolue"""
        self.resolved = True
        self.resolved_at = timezone.now()
        self.save()


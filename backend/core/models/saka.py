"""
Modèles pour le Protocole SAKA 🌾
Monnaie interne d'engagement (Yin) - Strictement séparée de l'Euro (Yang)

Phase 1 : Fondations - Modèles simplifiés
"""
from django.db import models
from django.conf import settings


class SakaWallet(models.Model):
    """
    Portefeuille SAKA d'un utilisateur.
    Stocke le solde et les statistiques de récolte/plantation/compostage.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saka_wallet',
        help_text="Utilisateur propriétaire du portefeuille SAKA"
    )
    balance = models.PositiveIntegerField(
        default=0,
        help_text="Solde SAKA disponible (grains)"
    )
    total_harvested = models.PositiveIntegerField(
        default=0,
        help_text="Total de grains SAKA jamais récoltés"
    )
    total_planted = models.PositiveIntegerField(
        default=0,
        help_text="Total de grains SAKA jamais plantés (engagés)"
    )
    total_composted = models.PositiveIntegerField(
        default=0,
        help_text="Total de grains SAKA compostés (retournés au Silo)"
    )
    last_activity_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date de la dernière activité SAKA"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date de dernière mise à jour"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date de création du portefeuille"
    )

    class Meta:
        app_label = 'core'
        ordering = ['-balance', '-updated_at']
        verbose_name = "Portefeuille SAKA"
        verbose_name_plural = "Portefeuilles SAKA"

    def __str__(self):
        return f"SAKA {self.user.username} - {self.balance} grains"


class SakaTransaction(models.Model):
    """
    Transaction SAKA (historique complet).
    Enregistre toutes les opérations SAKA (récolte et dépense).
    """
    DIRECTION_CHOICES = [
        ('EARN', 'Récolte - Grains gagnés'),
        ('SPEND', 'Dépense - Grains utilisés'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saka_transactions',
        help_text="Utilisateur concerné"
    )
    direction = models.CharField(
        max_length=5,
        choices=DIRECTION_CHOICES,
        help_text="Direction de la transaction (EARN ou SPEND)"
    )
    amount = models.PositiveIntegerField(
        help_text="Nombre de grains SAKA"
    )
    reason = models.CharField(
        max_length=64,
        help_text="Raison de la transaction (ex: 'content_read', 'poll_vote', 'invite_accepted')"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Métadonnées supplémentaires (JSON)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date de création de la transaction"
    )

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['direction', '-created_at']),
            models.Index(fields=['reason', '-created_at']),
        ]
        verbose_name = "Transaction SAKA"
        verbose_name_plural = "Transactions SAKA"

    def __str__(self):
        return f"{self.get_direction_display()} - {self.amount} grains - {self.reason} - {self.user.username}"


class SakaSilo(models.Model):
    """
    Silo commun où vont les grains compostés.
    Modèle global (un seul en pratique, via get_or_create).
    Phase 3 : Compostage & Silo Commun
    """
    total_balance = models.PositiveIntegerField(
        default=0,
        help_text="Solde total actuel du Silo Commun (grains compostés disponibles)"
    )
    total_composted = models.PositiveIntegerField(
        default=0,
        help_text="Total de grains jamais compostés dans le Silo (cumul historique)"
    )
    total_cycles = models.PositiveIntegerField(
        default=0,
        help_text="Nombre de cycles de compostage exécutés"
    )
    last_compost_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date du dernier cycle de compostage"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date de création du Silo"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date de dernière mise à jour"
    )

    class Meta:
        app_label = 'core'
        verbose_name = "Silo Commun SAKA"
        verbose_name_plural = "Silos Communs SAKA"

    def __str__(self):
        return f"SakaSilo(total_balance={self.total_balance}, cycles={self.total_cycles})"


class SakaCycle(models.Model):
    """
    Représente une saison/cycle SAKA (ex: "Saison 2026 - Printemps").
    Permet d'agréger les chiffres SAKA (récolté, planté, composté) par période.
    """
    name = models.CharField(
        max_length=128,
        help_text="Nom du cycle (ex: 'Saison 2026 / 1')"
    )
    start_date = models.DateField(
        help_text="Date de début du cycle"
    )
    end_date = models.DateField(
        help_text="Date de fin du cycle"
    )
    is_active = models.BooleanField(
        default=False,
        help_text="Si True, ce cycle est actuellement actif"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date de dernière mise à jour"
    )

    class Meta:
        app_label = 'core'
        ordering = ['-start_date']
        verbose_name = "Cycle SAKA"
        verbose_name_plural = "Cycles SAKA"
        indexes = [
            models.Index(fields=['is_active', '-start_date']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        status = "ACTIF" if self.is_active else "INACTIF"
        return f"{self.name} ({status}) - {self.start_date} → {self.end_date}"


class SakaCompostLog(models.Model):
    """
    Audit log des cycles de compost SAKA.
    Permet de tracer chaque exécution (manuelle ou Celery).
    Phase 3 : Compostage & Silo Commun - Audit
    """
    cycle = models.ForeignKey(
        'SakaCycle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='compost_logs',
        help_text="Cycle SAKA associé (optionnel)"
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date de début du cycle de compostage"
    )
    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date de fin du cycle de compostage"
    )
    
    dry_run = models.BooleanField(
        default=False,
        help_text="Si True, cycle de simulation (aucune écriture)"
    )
    wallets_affected = models.PositiveIntegerField(
        default=0,
        help_text="Nombre de wallets affectés par ce cycle"
    )
    total_composted = models.PositiveIntegerField(
        default=0,
        help_text="Total de grains SAKA compostés dans ce cycle"
    )
    
    # Informations contextuelles (paramètres utilisés)
    inactivity_days = models.PositiveIntegerField(
        default=0,
        help_text="Nombre de jours d'inactivité requis pour être éligible"
    )
    rate = models.FloatField(
        default=0.0,
        help_text="Taux de compostage (ex: 0.1 = 10%)"
    )
    min_balance = models.PositiveIntegerField(
        default=0,
        help_text="Balance minimum requise pour être éligible"
    )
    min_amount = models.PositiveIntegerField(
        default=0,
        help_text="Montant minimum à composter par wallet"
    )
    
    # Source du déclenchement
    source = models.CharField(
        max_length=32,
        default="celery",
        help_text="Source du cycle (ex: 'celery', 'admin', 'management_command')"
    )
    
    class Meta:
        app_label = 'core'
        ordering = ['-started_at']
        verbose_name = "Log de Compostage SAKA"
        verbose_name_plural = "Logs de Compostage SAKA"
        indexes = [
            models.Index(fields=['-started_at']),
            models.Index(fields=['dry_run', '-started_at']),
            models.Index(fields=['source', '-started_at']),
        ]
    
    def __str__(self):
        status = "DRY-RUN" if self.dry_run else "LIVE"
        return f"Compost {status} #{self.pk} – {self.total_composted} SAKA ({self.wallets_affected} wallets)"


class SakaProjectSupport(models.Model):
    """
    Modèle pour tracker les supporters uniques d'un projet SAKA.
    Évite les doublons dans le comptage des supporters.
    Phase 2 : Sorgho-boosting
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saka_project_supports',
        help_text="Utilisateur qui a boosté le projet"
    )
    project = models.ForeignKey(
        'core.Projet',
        on_delete=models.CASCADE,
        related_name='saka_supports',
        help_text="Projet boosté"
    )
    total_saka_spent = models.PositiveIntegerField(
        default=0,
        help_text="Total de SAKA dépensé par cet utilisateur pour ce projet"
    )
    first_boost_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date du premier boost"
    )
    last_boost_at = models.DateTimeField(
        auto_now=True,
        help_text="Date du dernier boost"
    )

    class Meta:
        app_label = 'core'
        unique_together = [['user', 'project']]
        indexes = [
            models.Index(fields=['project', '-last_boost_at']),
            models.Index(fields=['user', '-last_boost_at']),
        ]
        verbose_name = "Support SAKA Projet"
        verbose_name_plural = "Supports SAKA Projets"

    def __str__(self):
        return f"{self.user.username} → {self.project.titre} ({self.total_saka_spent} SAKA)"
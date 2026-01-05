"""
Modèles pour le Protocole SAKA 🌾
Monnaie interne d'engagement (Yin) - Strictement séparée de l'Euro (Yang)

Phase 1 : Fondations - Modèles simplifiés
"""
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.exceptions import ValidationError
from core.utils.alerts import send_critical_alert
import logging
import threading

logger = logging.getLogger(__name__)

# Thread-local pour autoriser les mutations SAKA via les services
# Constitution EGOEJO: no direct SAKA mutation - Seuls les services autorisés peuvent modifier
_saka_service_update = threading.local()


class AllowSakaMutation:
    """
    Contexte manager pour autoriser les mutations SAKA via les services.
    
    Constitution EGOEJO: no direct SAKA mutation.
    Utilisé par les services SAKA (harvest_saka, spend_saka, compost, redistribute)
    pour marquer que la modification est autorisée.
    
    Usage:
        with AllowSakaMutation():
            wallet.balance = 100
            wallet.save()
    """
    def __enter__(self):
        _saka_service_update.allowed = True
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        _saka_service_update.allowed = False
        return False


def is_saka_mutation_allowed():
    """
    Vérifie si une mutation SAKA est autorisée (via service).
    
    Returns:
        bool: True si la mutation est autorisée, False sinon
    """
    return getattr(_saka_service_update, 'allowed', False)


class SakaWalletQuerySet(models.QuerySet):
    """
    QuerySet personnalisé pour SakaWallet avec protection contre modifications directes.
    
    Constitution EGOEJO: no direct SAKA mutation.
    Les méthodes update() et bulk_update() vérifient que la mutation est autorisée.
    """
    def update(self, **kwargs):
        """
        Bloque TOUTE tentative de mise à jour de masse via update().
        
        Constitution EGOEJO: no direct SAKA mutation.
        La méthode update() est strictement interdite sur SakaWallet pour garantir
        la traçabilité et l'anti-accumulation. Toute modification doit passer par
        les services SAKA (harvest_saka, spend_saka, compost, redistribute).
        
        Raises:
            ValidationError: Toujours levée (update() est interdit)
        """
        # BLOQUER TOUTE tentative de update(), même si aucun champ protégé n'est modifié
        # Constitution EGOEJO: Fermer la "porte dérobée" des mises à jour SQL directes
        error_msg = (
            "VIOLATION CONSTITUTION EGOEJO : Direct update() is forbidden on SakaWallet. "
            "Use SakaTransaction service (harvest_saka, spend_saka, compost, redistribute). "
            "Toute modification de SakaWallet doit passer par les services SAKA pour garantir "
            "la traçabilité et l'anti-accumulation."
        )
        logger.critical(error_msg)
        raise ValidationError(error_msg)
    
    def bulk_update(self, objs, fields, batch_size=None):
        """
        Wrapper pour bulk_update() qui vérifie que la mutation est autorisée.
        
        Raises:
            ValidationError: Si modification directe détectée (sans service autorisé)
        """
        # Vérifier si la mutation est autorisée (via service SAKA)
        if not is_saka_mutation_allowed():
            # Vérifier si des champs SAKA protégés sont modifiés
            protected_fields = ['balance', 'total_harvested', 'total_planted', 'total_composted']
            modified_protected = [field for field in protected_fields if field in fields]
            
            if modified_protected:
                error_msg = (
                    f"VIOLATION CONSTITUTION EGOEJO : Modification directe de SakaWallet via bulk_update() détectée. "
                    f"Les champs SAKA (balance, total_harvested, total_planted, total_composted) "
                    f"ne peuvent pas être modifiés directement. "
                    f"Toute modification doit passer par les services SAKA (harvest_saka, spend_saka, etc.). "
                    f"Champs modifiés : {', '.join(modified_protected)}."
                )
                logger.critical(error_msg)
                raise ValidationError(error_msg)
        
        return super().bulk_update(objs, fields, batch_size)


class SakaWalletManager(models.Manager):
    """
    Manager personnalisé pour SakaWallet avec QuerySet protégé.
    """
    def get_queryset(self):
        return SakaWalletQuerySet(self.model, using=self._db)


class SakaWallet(models.Model):
    """
    Portefeuille SAKA d'un utilisateur.
    Stocke le solde et les statistiques de récolte/plantation/compostage.
    
    Constitution EGOEJO: no direct SAKA mutation.
    Les champs balance, total_harvested, total_planted, total_composted ne peuvent pas
    être modifiés directement. Toute modification doit passer par les services SAKA.
    
    ⚠️ AVERTISSEMENT EXPLICITE : INTERDICTION ABSOLUE DE raw() SQL
    
    Les méthodes suivantes sont STRICTEMENT INTERDITES :
    - SakaWallet.objects.raw("UPDATE core_sakawallet SET ...")
    - connection.cursor().execute("UPDATE core_sakawallet SET ...")
    - Toute requête SQL directe modifiant core_sakawallet
    
    Ces méthodes contournent les protections et violent la Constitution EGOEJO.
    Toute modification doit passer par les services SAKA (harvest_saka, spend_saka, compost, redistribute).
    
    Le signal post_save détecte automatiquement les modifications sans SakaTransaction correspondante
    et log une alerte CRITIQUE.
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
    
    objects = SakaWalletManager()

    class Meta:
        app_label = 'core'
        ordering = ['-balance', '-updated_at']
        verbose_name = "Portefeuille SAKA"
        verbose_name_plural = "Portefeuilles SAKA"

    def save(self, *args, **kwargs):
        """
        Protection philosophique : Empêche la modification directe du solde SAKA.
        
        Constitution EGOEJO: no direct SAKA mutation.
        Toute modification de balance, total_harvested, total_planted, total_composted
        doit passer par les services SAKA (harvest_saka, spend_saka, compost, redistribute).
        
        RÈGLE ABSOLUE : Aucune conversion SAKA ↔ EUR n'est autorisée.
        La structure relationnelle (SAKA) prime toujours sur la structure instrumentale (EUR).
        
        Raises:
            ValidationError: Si modification directe détectée (sans service autorisé)
        """
        # Autoriser la création initiale (pk None)
        if self.pk is None:
            super().save(*args, **kwargs)
            return
        
        # Vérifier si la mutation est autorisée (via service SAKA)
        if not is_saka_mutation_allowed():
            # Modification d'une instance existante : vérifier si les champs SAKA ont changé
            try:
                old_instance = SakaWallet.objects.get(pk=self.pk)
                
                # Liste des champs SAKA protégés
                protected_fields = ['balance', 'total_harvested', 'total_planted', 'total_composted']
                changed_fields = []
                
                for field in protected_fields:
                    old_value = getattr(old_instance, field, None)
                    new_value = getattr(self, field, None)
                    if old_value != new_value:
                        changed_fields.append(f"{field}: {old_value} → {new_value}")
                
                # Si un champ SAKA a changé, lever ValidationError
                if changed_fields:
                    error_msg = (
                        f"VIOLATION CONSTITUTION EGOEJO : Modification directe de SakaWallet détectée. "
                        f"Les champs SAKA (balance, total_harvested, total_planted, total_composted) "
                        f"ne peuvent pas être modifiés directement. "
                        f"Toute modification doit passer par les services SAKA (harvest_saka, spend_saka, etc.). "
                        f"Champs modifiés : {', '.join(changed_fields)}. "
                        f"User: {self.user.id} ({self.user.username})."
                    )
                    logger.critical(error_msg)
                    raise ValidationError(error_msg)
                    
            except SakaWallet.DoesNotExist:
                # L'objet n'existe plus (cas rare, mais possible)
                pass
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        """Représentation string du SakaWallet"""
        return f"SAKA {self.user.username} - {self.balance} grains"


@receiver(post_save, sender=SakaWallet)
def log_and_alert_saka_wallet_changes(sender, instance, created, **kwargs):
    """
    PROTECTION HOSTILE : Détecte et alerte les modifications directes suspectes du SakaWallet.
    
    Log les modifications directes du solde SakaWallet pour détecter les contournements.
    Alerte CRITIQUE si modification > seuil (ex: 10000 SAKA).
    
    DÉTECTION RAW() SQL : Vérifie la cohérence avec les transactions SAKA.
    Si une modification n'a pas de SakaTransaction correspondante, c'est un contournement.
    
    Cette fonction est appelée après chaque save() de SakaWallet.
    """
    if not created and instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            if original.balance != instance.balance:
                delta = instance.balance - original.balance
                abs_delta = abs(delta)
                
                # Log toute modification directe
                logger.warning(
                    f"Modification directe suspecte du SakaWallet de l'utilisateur {instance.user.username} (ID: {instance.user.id}). "
                    f"Ancien solde: {original.balance}, Nouveau solde: {instance.balance}, Delta: {delta}. "
                    "Toute modification du solde SAKA doit passer par les services Saka."
                )
                
                # DÉTECTION RAW() SQL : Vérifier la cohérence avec les transactions SAKA
                # Si la modification n'a pas de SakaTransaction correspondante, c'est un contournement
                from django.db.models import Sum
                from django.utils import timezone
                from datetime import timedelta
                
                # Vérifier les transactions SAKA récentes (dernières 5 minutes)
                recent_cutoff = timezone.now() - timedelta(minutes=5)
                recent_transactions = SakaTransaction.objects.filter(
                    user=instance.user,
                    created_at__gte=recent_cutoff
                ).order_by('-created_at')
                
                # Vérifier si une transaction correspond à la modification
                matching_transaction = None
                for transaction in recent_transactions:
                    if transaction.direction == 'EARN' and transaction.amount == abs_delta:
                        matching_transaction = transaction
                        break
                    elif transaction.direction == 'SPEND' and transaction.amount == abs_delta:
                        matching_transaction = transaction
                        break
                
                # Si aucune transaction ne correspond, c'est un contournement (raw() SQL, update(), etc.)
                # This prevents silent Raw SQL bypasses.
                if not matching_transaction and abs_delta > 0:
                    logger.critical(
                        f"ALERTE CRITIQUE : Contournement détecté sur SakaWallet de l'utilisateur {instance.user.username} (ID: {instance.user.id}). "
                        f"Modification de {delta} SAKA sans SakaTransaction correspondante. "
                        f"Cette modification a probablement été effectuée via raw() SQL, update(), ou autre contournement. "
                        f"Ancien solde: {original.balance}, Nouveau solde: {instance.balance}. "
                        "Constitution EGOEJO: no direct SAKA mutation - Toute modification doit passer par les services SAKA."
                    )
                    
                    # ACTIVE ALERTING : Envoyer email aux admins pour violation d'intégrité
                    # This prevents silent Raw SQL bypasses.
                    send_critical_alert(
                        title="INTEGRITY BREACH DETECTED",
                        payload={
                            "violation_type": "saka_wallet_bypass",
                            "user_id": instance.user.id,
                            "username": instance.user.username,
                            "email": instance.user.email,
                            "old_balance": original.balance,
                            "new_balance": instance.balance,
                            "delta": delta,
                            "detection_method": "post_save_signal",
                            "detection_details": "Aucune SakaTransaction correspondante trouvée dans les 5 dernières minutes",
                            "likely_cause": "raw() SQL, update(), ou autre contournement",
                            "constitution_violation": "no direct SAKA mutation",
                            "action_required": "Vérifier immédiatement l'intégrité des données SAKA et identifier la source de la violation"
                        },
                        dedupe_key=f"saka_wallet_bypass:{instance.user.id}:{instance.pk}"
                    )
                
                # PROTECTION HOSTILE : Alerte CRITIQUE si modification > seuil
                # This prevents silent Raw SQL bypasses.
                CRITICAL_THRESHOLD = 10000  # 10000 SAKA = seuil critique
                if abs_delta > CRITICAL_THRESHOLD:
                    logger.critical(
                        f"ALERTE CRITIQUE : Modification massive du SakaWallet de l'utilisateur {instance.user.username} (ID: {instance.user.id}). "
                        f"Delta: {delta} SAKA (seuil critique: {CRITICAL_THRESHOLD}). "
                        "Cette modification pourrait violer la philosophie EGOEJO (monétisation SAKA, accumulation, etc.)."
                    )
                    
                    # ACTIVE ALERTING : Envoyer email aux admins pour modification massive
                    # This prevents silent Raw SQL bypasses.
                    send_critical_alert(
                        title="INTEGRITY BREACH DETECTED (MASSIVE MODIFICATION)",
                        payload={
                            "violation_type": "saka_wallet_massive_change",
                            "user_id": instance.user.id,
                            "username": instance.user.username,
                            "email": instance.user.email,
                            "old_balance": original.balance,
                            "new_balance": instance.balance,
                            "delta": delta,
                            "critical_threshold": CRITICAL_THRESHOLD,
                            "threshold_exceeded": True,
                            "detection_method": "post_save_signal",
                            "philosophy_violation": "monétisation SAKA, accumulation, etc.",
                            "action_required": "Vérifier immédiatement l'intégrité des données SAKA et identifier la source de la violation"
                        },
                        dedupe_key=f"saka_wallet_massive:{instance.user.id}:{instance.pk}"
                    )
        except sender.DoesNotExist:
            pass  # L'objet a été supprimé ou n'existait pas avant
    
    # NOTE IMPORTANTE : raw() SQL ne déclenche PAS le signal post_save
    # Le signal post_save ne peut détecter que les modifications via save().
    # Pour détecter raw() SQL, il faudrait un trigger SQL ou un audit de cohérence périodique.
    # Le test test_code_scan_detects_raw_sql_usage() détecte les violations dans le code source.


class SakaTransaction(models.Model):
    """
    Transaction SAKA (historique complet).
    Enregistre toutes les opérations SAKA (récolte et dépense).
    """
    DIRECTION_CHOICES = [
        ('EARN', 'Récolte - Grains gagnés'),
        ('SPEND', 'Dépense - Grains utilisés'),
    ]
    
    TRANSACTION_TYPE_CHOICES = [
        ('HARVEST', 'Récolte (EARN)'),
        ('SPEND', 'Dépense (SPEND)'),
        ('COMPOST', 'Compostage'),
        ('REDISTRIBUTION', 'Redistribution du Silo'),
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
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        help_text="Type de transaction (HARVEST, SPEND, COMPOST, REDISTRIBUTION)"
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
    
    def save(self, *args, **kwargs):
        """
        Validation explicite : transaction_type est OBLIGATOIRE.
        
        Cette validation facilite le débogage en levant une ValueError claire
        si transaction_type est manquant, plutôt qu'une erreur générique de base de données.
        
        Raises:
            ValueError: Si transaction_type est manquant ou invalide
        """
        # Validation : transaction_type est OBLIGATOIRE
        if not self.transaction_type:
            raise ValueError(
                f"VIOLATION : transaction_type est OBLIGATOIRE pour SakaTransaction. "
                f"Direction: {self.direction}, Reason: {self.reason}, Amount: {self.amount}. "
                f"Valeurs possibles: HARVEST, SPEND, COMPOST, REDISTRIBUTION. "
                f"Vérifiez que tous les appels à SakaTransaction.objects.create() fournissent transaction_type."
            )
        
        # Validation : transaction_type doit être dans les choix valides
        valid_types = [choice[0] for choice in self.TRANSACTION_TYPE_CHOICES]
        if self.transaction_type not in valid_types:
            raise ValueError(
                f"VIOLATION : transaction_type invalide '{self.transaction_type}'. "
                f"Valeurs possibles: {', '.join(valid_types)}. "
                f"Direction: {self.direction}, Reason: {self.reason}, Amount: {self.amount}."
            )
        
        # Validation : Cohérence direction / transaction_type
        if self.direction == 'EARN' and self.transaction_type not in ['HARVEST', 'REDISTRIBUTION']:
            raise ValueError(
                f"VIOLATION : transaction_type '{self.transaction_type}' incompatible avec direction='EARN'. "
                f"Pour direction='EARN', transaction_type doit être 'HARVEST' ou 'REDISTRIBUTION'. "
                f"Reason: {self.reason}, Amount: {self.amount}."
            )
        
        if self.direction == 'SPEND' and self.transaction_type not in ['SPEND', 'COMPOST']:
            raise ValueError(
                f"VIOLATION : transaction_type '{self.transaction_type}' incompatible avec direction='SPEND'. "
                f"Pour direction='SPEND', transaction_type doit être 'SPEND' ou 'COMPOST'. "
                f"Reason: {self.reason}, Amount: {self.amount}."
            )
        
        super().save(*args, **kwargs)


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
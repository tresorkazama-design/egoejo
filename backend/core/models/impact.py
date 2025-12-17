"""
Modèle pour le tableau de bord d'impact utilisateur
"""
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class ImpactDashboard(models.Model):
    """
    Tableau de bord d'impact personnel pour chaque utilisateur.
    Stocke les métriques agrégées pour éviter de recalculer à chaque requête.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='impact_dashboard'
    )
    total_contributions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total des contributions en euros"
    )
    projects_supported = models.IntegerField(
        default=0,
        help_text="Nombre de projets soutenus"
    )
    cagnottes_contributed = models.IntegerField(
        default=0,
        help_text="Nombre de cagnottes auxquelles l'utilisateur a contribué"
    )
    intentions_submitted = models.IntegerField(
        default=0,
        help_text="Nombre d'intentions soumises"
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text="Date de dernière mise à jour des métriques"
    )

    class Meta:
        db_table = 'impact_dashboard'
        verbose_name = "Tableau de bord d'impact"
        verbose_name_plural = "Tableaux de bord d'impact"

    def __str__(self):
        return f"Impact de {self.user.username or self.user.email}"

    def update_metrics(self):
        """
        Met à jour les métriques depuis les modèles réels.
        À appeler après chaque contribution ou intention.
        """
        from core.models.fundraising import Contribution
        from core.models.intents import Intent

        # Calculer les contributions
        contributions = Contribution.objects.filter(user=self.user)
        self.total_contributions = sum(c.montant for c in contributions)
        self.projects_supported = contributions.values('cagnotte__projet').distinct().count()
        self.cagnottes_contributed = contributions.values('cagnotte').distinct().count()

        # Calculer les intentions
        self.intentions_submitted = Intent.objects.filter(email=self.user.email).count()

        self.save()


class ProjectImpact4P(models.Model):
    """
    Modèle pour stocker les scores 4P (Performance Partagée) par projet.
    
    Les 4 dimensions :
    - P1 : Performance financière (euros mobilisés)
      → Dérivé d'agrégats financiers réels (contributions, escrows)
    
    - P2 : Performance vivante (SAKA mobilisé)
      → Dérivé de SAKA réellement mobilisé (supporters, boosts)
    
    - P3 : Performance sociale/écologique (score d'impact agrégé)
      → PROXY V1 INTERNE : Utilise impact_score du projet (ou 0)
      → À ne pas interpréter comme mesure académique d'impact
      → Sera affiné avec des données d'impact plus riches dans les versions futures
    
    - P4 : Purpose / Sens (indicateur qualitatif)
      → PROXY V1 INTERNE : Formule simplifiée basée sur supporters SAKA + cagnottes
      → À ne pas interpréter comme mesure académique d'impact
      → Sera affiné avec des indicateurs qualitatifs plus robustes dans les versions futures
    """
    project = models.OneToOneField(
        'core.Projet',
        on_delete=models.CASCADE,
        related_name='impact_4p',
        help_text="Projet associé"
    )
    
    # Scores 4P
    financial_score = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="P1 : Performance financière (euros mobilisés)"
    )
    saka_score = models.PositiveIntegerField(
        default=0,
        help_text="P2 : Performance vivante (SAKA mobilisé pour ce projet)"
    )
    social_score = models.PositiveIntegerField(
        default=0,
        help_text="P3 : Performance sociale/écologique (PROXY V1 - score d'impact interne simplifié, non académique)"
    )
    purpose_score = models.PositiveIntegerField(
        default=0,
        help_text="P4 : Purpose / Sens (PROXY V1 - indicateur interne simplifié, non académique)"
    )
    
    # Métadonnées
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date de dernière mise à jour des scores 4P"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date de création"
    )

    class Meta:
        db_table = 'project_impact_4p'
        verbose_name = "Score 4P Projet"
        verbose_name_plural = "Scores 4P Projets"
        ordering = ['-updated_at']

    def __str__(self):
        return f"4P - {self.project.titre} (F:{self.financial_score}, S:{self.saka_score}, So:{self.social_score}, P:{self.purpose_score})"
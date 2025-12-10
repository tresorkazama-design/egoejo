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


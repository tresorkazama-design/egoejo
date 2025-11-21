from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Engagement(models.Model):
    """
    Offre d'aide déposée par un membre ou une personne non connectée.

    Correspond au formulaire "Je veux aider" côté frontend.
    """

    HELP_TYPE_CHOICES = [
        ("financier", "Financier"),
        ("temps", "Temps / accompagnement"),
        ("competences", "Compétences spécifiques"),
        ("materiel", "Matériel / ressources"),
    ]

    SCOPE_CHOICES = [
        ("local", "Principalement local / proche"),
        ("international", "Ouvert à l’international"),
        ("both", "Les deux"),
    ]

    ANONYMITY_CHOICES = [
        ("pseudo", "Afficher le pseudo"),
        ("team_only", "Visible seulement pour l'équipe EGOEJO"),
    ]

    STATUS_CHOICES = [
        ("new", "Nouvel engagement"),
        ("in_review", "En cours d'étude"),
        ("active", "Actif"),
        ("archived", "Archivé"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="engagements",
        help_text="Utilisateur connecté à l'origine de l'engagement (peut être nul).",
    )

    help_request = models.ForeignKey(
        "core.HelpRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="engagements",
        help_text="Demande d'aide / projet lié à cet engagement (optionnel).",
    )

    # Listes de types d'aide et de domaines : on utilise JSONField pour rester simple
    help_types = models.JSONField(
        default=list,
        blank=True,
        help_text="Liste des types d'aide proposés (financier, temps, compétences, matériel).",
    )

    domains = models.JSONField(
        default=list,
        blank=True,
        help_text="Liste des domaines (éducation, santé, agriculture, etc.).",
    )

    availability = models.TextField(
        blank=True,
        help_text="Disponibilités décrites par la personne (jours, horaires, fréquence).",
    )

    scope = models.CharField(
        max_length=20,
        choices=SCOPE_CHOICES,
        default="both",
    )

    anonymity = models.CharField(
        max_length=20,
        choices=ANONYMITY_CHOICES,
        default="pseudo",
    )

    notes = models.TextField(
        blank=True,
        help_text="Message complémentaire sur la manière d’aider.",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Engagement(id={self.id}, scope={self.scope})"

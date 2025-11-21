from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class HelpRequest(models.Model):
    """
    Demande d'aide déposée par un membre (ou une personne non connectée).

    Ce modèle correspond au formulaire "J'ai besoin d'aide" côté frontend.
    """

    HELP_TYPE_CHOICES = [
        ("financier", "Financier"),
        ("humain", "Humain / accompagnement"),
        ("materiel", "Matériel"),
        ("autre", "Autre"),
    ]

    URGENCY_CHOICES = [
        ("low", "Faible"),
        ("medium", "Moyenne"),
        ("high", "Élevée"),
    ]

    ANONYMITY_CHOICES = [
        ("pseudo", "Afficher le pseudo"),
        ("team_only", "Visible seulement pour l'équipe EGOEJO"),
    ]

    STATUS_CHOICES = [
        ("new", "Nouvelle demande"),
        ("in_review", "En cours d'étude"),
        ("accepted", "Acceptée"),
        ("rejected", "Refusée"),
        ("archived", "Archivée"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="help_requests",
        help_text="Utilisateur connecté à l'origine de la demande (peut être nul).",
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    help_type = models.CharField(
        max_length=20,
        choices=HELP_TYPE_CHOICES,
        default="financier",
    )

    urgency = models.CharField(
        max_length=10,
        choices=URGENCY_CHOICES,
        default="medium",
    )

    is_linked_to_project = models.BooleanField(
        default=False,
        help_text="La demande est-elle liée à un projet EGOEJO ?",
    )

    project = models.ForeignKey(
        "core.Projet",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="help_requests",
        help_text="Projet lié (optionnel).",
    )


    anonymity = models.CharField(
        max_length=20,
        choices=ANONYMITY_CHOICES,
        default="pseudo",
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
        return f"HelpRequest(id={self.id}, title={self.title})"

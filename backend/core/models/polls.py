"""
Modèles pour les scrutins et votes.
"""

from django.conf import settings
from django.db import models

from .common import default_metadata


class Poll(models.Model):
    """
    Modèle pour les sondages avec support de méthodes de vote avancées.
    """
    VOTING_METHOD_CHOICES = [
        ('binary', 'Binaire (Oui/Non)'),
        ('quadratic', 'Vote Quadratique'),
        ('majority', 'Jugement Majoritaire'),
    ]
    STATUS_DRAFT = "draft"
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_OPEN, "Open"),
        (STATUS_CLOSED, "Closed"),
    ]

    project = models.ForeignKey(
        "core.Projet",
        on_delete=models.SET_NULL,
        related_name="polls",
        blank=True,
        null=True,
    )
    title = models.CharField(max_length=255)
    question = models.TextField()
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    is_anonymous = models.BooleanField(default=True)
    allow_multiple = models.BooleanField(default=False)
    quorum = models.PositiveIntegerField(blank=True, null=True)
    opens_at = models.DateTimeField(blank=True, null=True)
    closes_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="polls_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    voting_method = models.CharField(
        max_length=20,
        choices=VOTING_METHOD_CHOICES,
        default='binary',
        help_text="Méthode de vote utilisée pour ce sondage"
    )
    max_points = models.IntegerField(
        default=100,
        null=True,
        blank=True,
        help_text="Nombre maximum de points à distribuer (Vote Quadratique uniquement)"
    )

    class Meta:
        ordering = ["-created_at"]
        app_label = "core"

    is_shareholder_vote = models.BooleanField(
        default=False,
        help_text="Vote réservé aux actionnaires (V2.0) - Pondération par nombre d'actions"
    )

    def __str__(self):
        return self.title
    
    def get_vote_weight(self, user):
        """
        V1.6 : 1 personne = 1 voix
        V2.0 : 1 action = 1 voix (x100 pour Fondateurs)
        """
        # Si c'est un Sondage "Actionnaires" (V2.0)
        if self.is_shareholder_vote:
            try:
                # Import dynamique pour éviter boucle
                from investment.models import ShareholderRegister
                shares = ShareholderRegister.objects.get(
                    project=self.project, investor=user
                ).number_of_shares
                
                # PROTECTION FONDATEUR (Golden Share)
                if user.groups.filter(name=settings.FOUNDER_GROUP_NAME).exists():
                    return shares * 100
                return shares
            except ShareholderRegister.DoesNotExist:
                return 0
            except Exception:
                return 0
        
        # Mode V1.6 Standard
        return 1


class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
    label = models.CharField(max_length=255)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]
        app_label = "core"

    def __str__(self):
        return f"{self.poll.title} -> {self.label}"


class PollBallot(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="ballots")
    option = models.ForeignKey(
        PollOption, on_delete=models.CASCADE, related_name="ballots"
    )
    voter_hash = models.CharField(max_length=128)
    metadata = models.JSONField(default=default_metadata, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField(
        default=1,
        null=True,
        blank=True,
        help_text="Points attribués à cette option (Vote Quadratique)"
    )
    ranking = models.IntegerField(
        null=True,
        blank=True,
        help_text="Classement de cette option (Jugement Majoritaire: 1=meilleur, N=pire)"
    )

    class Meta:
        unique_together = ("poll", "option", "voter_hash")
        app_label = "core"

    def __str__(self):
        return f"Ballot {self.pk} for {self.poll.title}"


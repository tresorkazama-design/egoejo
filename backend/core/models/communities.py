"""
Modèle pour les Communautés EGOEJO.
Prépare la subsidiarité : décisions au niveau le plus bas capable.
"""
from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Community(models.Model):
    """
    Représente une communauté locale ou thématique.
    
    V1 : Structure minimale pour préparer la subsidiarité.
    Permet de regrouper des projets et des membres autour d'un objectif commun.
    """
    name = models.CharField(
        max_length=255,
        help_text="Nom de la communauté"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text="Identifiant unique URL-friendly (auto-généré si vide)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description de la communauté"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Si False, la communauté est désactivée"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date de dernière mise à jour"
    )
    
    # Membres de la communauté (ManyToMany optionnel pour V1)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="communities",
        help_text="Membres de la communauté"
    )
    
    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        verbose_name = "Communauté"
        verbose_name_plural = "Communautés"
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', '-created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-génère le slug si vide"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


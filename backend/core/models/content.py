"""
Modèles liés aux contenus éducatifs (podcasts, PDF, vidéos).
"""

from django.conf import settings
from django.db import models


class ContenuEducatif(models.Model):
    """Modèle pour les contenus éducatifs (podcasts, PDF, vidéos)."""
    
    TYPE_PODCAST = 'podcast'
    TYPE_PDF = 'pdf'
    TYPE_VIDEO = 'video'
    
    TYPE_CHOICES = [
        (TYPE_PODCAST, 'Podcast'),
        (TYPE_PDF, 'PDF'),
        (TYPE_VIDEO, 'Vidéo'),
    ]
    
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    type_contenu = models.CharField(max_length=20, choices=TYPE_CHOICES)
    fichier = models.FileField(upload_to='contenus_educatifs/')
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contenus_educatifs'
    )
    is_validated = models.BooleanField(default=False, verbose_name='Validé par admin')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = "core"
        verbose_name = "Contenu éducatif"
        verbose_name_plural = "Contenus éducatifs"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.titre} ({self.get_type_contenu_display()})"


class Like(models.Model):
    """Modèle pour les likes sur les contenus éducatifs."""
    
    contenu = models.ForeignKey(
        ContenuEducatif,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes_contenus'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "core"
        verbose_name = "Like"
        verbose_name_plural = "Likes"
        unique_together = ['contenu', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Like de {self.user.username} sur {self.contenu.titre}"


class Commentaire(models.Model):
    """Modèle pour les commentaires sur les contenus éducatifs."""
    
    contenu = models.ForeignKey(
        ContenuEducatif,
        on_delete=models.CASCADE,
        related_name='commentaires'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commentaires_contenus'
    )
    texte = models.TextField(max_length=2000)
    is_validated = models.BooleanField(default=False, verbose_name='Validé par admin')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = "core"
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Commentaire de {self.user.username if self.user else 'Anonyme'} sur {self.contenu.titre}"


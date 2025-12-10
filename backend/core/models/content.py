from django.conf import settings
from django.db import models
import hashlib

User = settings.AUTH_USER_MODEL


class EducationalContent(models.Model):
  """
  Contenu éducatif : podcast, vidéo, PDF, poème, article, etc.
  Validé par l'admin avant publication.
  """

  CONTENT_TYPES = [
      ("podcast", "Podcast"),
      ("video", "Vidéo"),
      ("pdf", "PDF / Rapport"),
      ("article", "Article"),
      ("poeme", "Poème"),
      ("chanson", "Chanson"),
      ("autre", "Autre"),
  ]

  STATUS_CHOICES = [
      ("draft", "Brouillon"),
      ("pending", "En attente de validation"),
      ("published", "Publié"),
      ("rejected", "Rejeté"),
  ]

  CATEGORY_CHOICES = [
      ("ressources", "Ressources"),
      ("guides", "Guides"),
      ("videos", "Vidéos"),
      ("racines-philosophie", "Racines & Philosophie"),
      ("autres", "Autres"),
  ]

  title = models.CharField(max_length=255)
  slug = models.SlugField(max_length=255, unique=True)
  type = models.CharField(max_length=20, choices=CONTENT_TYPES, default="article")
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
  category = models.CharField(
      max_length=50,
      choices=CATEGORY_CHOICES,
      default="autres",
      help_text="Catégorie du contenu (ex: Racines & Philosophie pour Steiner, Biodynamie)"
  )
  tags = models.JSONField(
      default=list,
      blank=True,
      help_text="Tags comme 'Steiner', 'Biodynamie', etc."
  )
  embedding = models.JSONField(
      blank=True,
      null=True,
      help_text="Vecteur d'embedding pour recherche sémantique (pgvector future)"
  )

  author = models.ForeignKey(
      User,
      on_delete=models.SET_NULL,
      null=True,
      blank=True,
      related_name="educational_contents",
      help_text="Auteur du contenu (peut être nul si anonyme).",
  )

  anonymous_display_name = models.CharField(
      max_length=255,
      blank=True,
      help_text="Nom/pseudo à afficher si l'auteur veut rester discret.",
  )

  description = models.TextField(blank=True)

  # Fichier uploadé (optionnel)
  file = models.FileField(
      upload_to="educational_contents/",
      blank=True,
      null=True,
      help_text="Fichier PDF, audio, etc. (optionnel si lien externe).",
  )

  # Lien externe (YouTube, Spotify, site…)
  external_url = models.URLField(
      blank=True,
      help_text="Lien externe (YouTube, Spotify, site…) si pas de fichier uploadé.",
  )

  # Fichier audio généré (TTS) ⭐ NOUVEAU v1.5.0
  audio_file = models.FileField(
      upload_to="educational_contents/audio/",
      blank=True,
      null=True,
      help_text="Fichier audio généré automatiquement (TTS) pour accessibilité terrain.",
  )
  # Hash du texte ayant servi à générer l'audio (évite régénérations payantes)
  audio_source_hash = models.CharField(
      max_length=64,
      blank=True,
      help_text="SHA-256 du texte source utilisé pour le TTS (pour éviter les doublons)."
  )

  # Hash du texte ayant servi à générer l'embedding (évite régénérations payantes)
  embedding_source_hash = models.CharField(
      max_length=64,
      blank=True,
      help_text="SHA-256 du texte source utilisé pour l'embedding (pour éviter les doublons)."
  )

  # Lien éventuel vers un projet EGOEJO
  project = models.ForeignKey(
      "core.Projet",
      on_delete=models.SET_NULL,
      blank=True,
      null=True,
      related_name="educational_contents",
      help_text="Projet EGOEJO lié (optionnel).",
  )

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
      ordering = ["-created_at"]

  def __str__(self):
      return self.title

  @property
  def likes_count(self):
      return self.likes.count()

  @property
  def comments_count(self):
      return self.comments.count()

  # Helpers de hash (pour TTS / embeddings)
  def compute_text_hash(self):
      """
      Calcule le hash du texte (titre + description) pour éviter les recalculs coûteux.
      """
      text = (self.title or "") + "\n" + (self.description or "")
      return hashlib.sha256(text.encode("utf-8")).hexdigest()


class ContentLike(models.Model):
  """
  Like sur un contenu éducatif.
  Un user ne peut liker qu'une seule fois un contenu.
  """

  user = models.ForeignKey(
      User,
      on_delete=models.CASCADE,
      related_name="content_likes",
  )
  content = models.ForeignKey(
      EducationalContent,
      on_delete=models.CASCADE,
      related_name="likes",
  )
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
      unique_together = ("user", "content")

  def __str__(self):
      return f"{self.user} ♥ {self.content}"


class ContentComment(models.Model):
  """
  Commentaire sur un contenu éducatif.
  """

  user = models.ForeignKey(
      User,
      on_delete=models.SET_NULL,
      null=True,
      blank=True,
      related_name="content_comments",
  )
  content = models.ForeignKey(
      EducationalContent,
      on_delete=models.CASCADE,
      related_name="comments",
  )
  text = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

  display_name = models.CharField(
      max_length=255,
      blank=True,
      help_text="Nom/pseudo affiché pour ce commentaire si différent du profil.",
  )

  class Meta:
      ordering = ["created_at"]

  def __str__(self):
      who = self.display_name or (self.user and getattr(self.user, "username", None)) or "Anonyme"
      return f"Commentaire sur {self.content} par {who}"



from django.conf import settings
from django.db import models

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

  title = models.CharField(max_length=255)
  slug = models.SlugField(max_length=255, unique=True)
  type = models.CharField(max_length=20, choices=CONTENT_TYPES, default="article")
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

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



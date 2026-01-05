from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
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
      ("archived", "Archivé"),
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
  
  # Champs de tracking pour le workflow CMS V1
  published_by = models.ForeignKey(
      User,
      on_delete=models.SET_NULL,
      null=True,
      blank=True,
      related_name="published_contents",
      help_text="Utilisateur qui a publié ce contenu.",
  )
  published_at = models.DateTimeField(
      null=True,
      blank=True,
      help_text="Date de publication du contenu.",
  )
  modified_by = models.ForeignKey(
      User,
      on_delete=models.SET_NULL,
      null=True,
      blank=True,
      related_name="modified_contents",
      help_text="Dernier utilisateur ayant modifié ce contenu.",
  )

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
  
  # Workflow CMS V1 - Transitions autorisées
  ALLOWED_TRANSITIONS = {
      "draft": ["pending"],  # draft -> pending (Contributor, Editor)
      "pending": ["published", "rejected"],  # pending -> published (Admin) ou rejected (Editor, Admin)
      "published": ["archived"],  # published -> archived (Admin)
      "rejected": ["draft", "pending"],  # rejected -> draft/pending (pour révision)
      "archived": [],  # archived est terminal (pas de transition depuis archived)
  }
  
  def can_transition_to(self, new_status, user=None):
      """
      Vérifie si une transition de status est autorisée.
      
      Args:
          new_status: Le nouveau statut souhaité
          user: L'utilisateur qui effectue la transition (optionnel)
      
      Returns:
          tuple: (bool, str) - (autorisé, message d'erreur si non autorisé)
      """
      current_status = self.status
      
      # Vérifier si la transition est dans la liste autorisée
      if new_status not in self.ALLOWED_TRANSITIONS.get(current_status, []):
          return False, f"Transition non autorisée : {current_status} -> {new_status}"
      
      # Vérifications spécifiques selon le rôle (si user fourni)
      if user:
          from core.permissions import is_content_editor, is_content_admin, is_content_contributor
        
          # draft -> pending : Contributor ou Editor
          if current_status == "draft" and new_status == "pending":
              if not user.is_authenticated:
                  return False, "Authentification requise pour soumettre un brouillon"
              if not (is_content_contributor(user) or is_content_editor(user)):
                  return False, "Seuls les Contributors et Editors peuvent soumettre un brouillon"
          
          # pending -> published : Admin uniquement
          elif current_status == "pending" and new_status == "published":
              if not user.is_authenticated:
                  return False, "Authentification requise pour publier un contenu"
              if not is_content_admin(user):
                  return False, "Seuls les Admins peuvent publier un contenu"
          
          # pending -> rejected : Editor ou Admin
          elif current_status == "pending" and new_status == "rejected":
              if not user.is_authenticated:
                  return False, "Authentification requise pour rejeter un contenu"
              if not is_content_editor(user):
                  return False, "Seuls les Editors et Admins peuvent rejeter un contenu"
          
          # published -> archived : Admin uniquement
          elif current_status == "published" and new_status == "archived":
              if not user.is_authenticated:
                  return False, "Authentification requise pour archiver un contenu"
              if not is_content_admin(user):
                  return False, "Seuls les Admins peuvent archiver un contenu"
      
      return True, ""
  
  def transition_to(self, new_status, user=None):
      """
      Effectue une transition de status avec validation.
      
      Args:
          new_status: Le nouveau statut
          user: L'utilisateur qui effectue la transition
      
      Raises:
          ValidationError: Si la transition n'est pas autorisée
      """
      can_transition, error_message = self.can_transition_to(new_status, user)
      
      if not can_transition:
          raise ValidationError(error_message)
      
      old_status = self.status
      self.status = new_status
      
      # Mettre à jour les champs de tracking
      if user and user.is_authenticated:
          self.modified_by = user
          
          # Si publication, enregistrer published_by et published_at
          if new_status == "published" and old_status != "published":
              self.published_by = user
              self.published_at = timezone.now()
      
      self.save(update_fields=["status", "published_by", "published_at", "modified_by", "updated_at"])


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



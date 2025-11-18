# backend/core/admin.py

from django.contrib import admin
from .models import (
    AuditLog,
    Cagnotte,
    ChatMembership,
    ChatMessage,
    ChatThread,
    Commentaire,
    ContenuEducatif,
    Contribution,
    Intent,
    Like,
    Media,
    ModerationReport,
    Poll,
    PollBallot,
    PollOption,
    Profile,
    Projet,
)

# 1. Définir l'interface en ligne (pour ajouter plusieurs fichiers dans la même page)
class MediaInline(admin.TabularInline):
    model = Media
    extra = 1 # Affiche un champ d'upload vide par défaut

# 2. Définir le modèle Projet
class ProjetAdmin(admin.ModelAdmin):
    inlines = [MediaInline]
    # Ici, nous pouvons retirer l'ancien champ 'image' de la vue principale (si on veut)
    # fields = ('titre', 'description', 'categorie', 'impact_score', 'created_at') # Exemple si on veut masquer le champ image unique

# 3. Enregistrement des modèles
admin.site.register(Projet, ProjetAdmin) # <-- Enregistrez en utilisant la classe ProjetAdmin

admin.site.register(Cagnotte)
admin.site.register(Contribution)
# Media est géré via ProjetAdmin, donc pas besoin de l'enregistrer ici.

# Admin pour Intent
class IntentAdmin(admin.ModelAdmin):
    list_display = ['nom', 'email', 'profil', 'created_at']
    list_filter = ['profil', 'created_at']
    search_fields = ['nom', 'email']
    readonly_fields = ['ip', 'user_agent', 'created_at']

admin.site.register(Intent, IntentAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'created_at', 'updated_at')
    search_fields = ('user__username', 'display_name')


class ChatMembershipInline(admin.TabularInline):
    model = ChatMembership
    extra = 0


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('author', 'content', 'is_deleted', 'created_at')


@admin.register(ChatThread)
class ChatThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_private', 'created_by', 'last_message_at', 'created_at')
    list_filter = ('is_private',)
    search_fields = ('title',)
    inlines = [ChatMembershipInline, ChatMessageInline]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread', 'author', 'is_deleted', 'created_at')
    list_filter = ('is_deleted', 'thread')
    search_fields = ('content',)


class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 1


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'is_anonymous', 'allow_multiple', 'opens_at', 'closes_at')
    list_filter = ('status', 'is_anonymous')
    search_fields = ('title', 'question')
    inlines = [PollOptionInline]


@admin.register(PollBallot)
class PollBallotAdmin(admin.ModelAdmin):
    list_display = ('poll', 'option', 'voter_hash', 'submitted_at')
    search_fields = ('voter_hash',)


@admin.register(ModerationReport)
class ModerationReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'status', 'reporter', 'created_at')
    list_filter = ('report_type', 'status')
    search_fields = ('target_id', 'reason')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'actor', 'target_type', 'target_id', 'created_at')
    list_filter = ('action', 'target_type')
    search_fields = ('target_id', 'action')


class CommentaireInline(admin.TabularInline):
    """Inline pour afficher les commentaires dans l'admin des contenus."""
    model = Commentaire
    extra = 0
    readonly_fields = ('user', 'texte', 'created_at', 'updated_at')
    fields = ('user', 'texte', 'is_validated', 'created_at', 'updated_at')


@admin.register(ContenuEducatif)
class ContenuEducatifAdmin(admin.ModelAdmin):
    """Admin pour les contenus éducatifs avec validation."""
    list_display = ('titre', 'type_contenu', 'auteur', 'is_validated', 'created_at')
    list_filter = ('type_contenu', 'is_validated', 'created_at')
    search_fields = ('titre', 'description', 'auteur__username')
    readonly_fields = ('auteur', 'created_at', 'updated_at')
    inlines = [CommentaireInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'description', 'type_contenu', 'fichier', 'auteur')
        }),
        ('Validation', {
            'fields': ('is_validated',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['valider_contenus', 'invalider_contenus']
    
    def valider_contenus(self, request, queryset):
        """Action pour valider plusieurs contenus."""
        count = queryset.update(is_validated=True)
        self.message_user(request, f'{count} contenu(s) validé(s).')
    valider_contenus.short_description = "Valider les contenus sélectionnés"
    
    def invalider_contenus(self, request, queryset):
        """Action pour invalider plusieurs contenus."""
        count = queryset.update(is_validated=False)
        self.message_user(request, f'{count} contenu(s) invalidé(s).')
    invalider_contenus.short_description = "Invalider les contenus sélectionnés"


@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    """Admin pour les commentaires avec validation."""
    list_display = ('contenu', 'user', 'texte_preview', 'is_validated', 'created_at')
    list_filter = ('is_validated', 'created_at')
    search_fields = ('texte', 'user__username', 'contenu__titre')
    readonly_fields = ('user', 'contenu', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Commentaire', {
            'fields': ('contenu', 'user', 'texte')
        }),
        ('Validation', {
            'fields': ('is_validated',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def texte_preview(self, obj):
        """Affiche un aperçu du texte du commentaire."""
        return obj.texte[:50] + '...' if len(obj.texte) > 50 else obj.texte
    texte_preview.short_description = 'Aperçu'
    
    actions = ['valider_commentaires', 'invalider_commentaires']
    
    def valider_commentaires(self, request, queryset):
        """Action pour valider plusieurs commentaires."""
        count = queryset.update(is_validated=True)
        self.message_user(request, f'{count} commentaire(s) validé(s).')
    valider_commentaires.short_description = "Valider les commentaires sélectionnés"
    
    def invalider_commentaires(self, request, queryset):
        """Action pour invalider plusieurs commentaires."""
        count = queryset.update(is_validated=False)
        self.message_user(request, f'{count} commentaire(s) invalidé(s).')
    invalider_commentaires.short_description = "Invalider les commentaires sélectionnés"


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """Admin pour les likes."""
    list_display = ('contenu', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('contenu__titre', 'user__username')
    readonly_fields = ('contenu', 'user', 'created_at')
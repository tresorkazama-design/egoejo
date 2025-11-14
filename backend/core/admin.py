# backend/core/admin.py

from django.contrib import admin
from .models import (
    AuditLog,
    Cagnotte,
    ChatMembership,
    ChatMessage,
    ChatThread,
    Contribution,
    Intent,
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
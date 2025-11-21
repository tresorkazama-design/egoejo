from django.contrib import admin

from .models import (
    # Projets & financement
    Projet,
    Media,
    Cagnotte,
    Contribution,
    # Intents / intentions
    Intent,
    # Comptes & profils
    Profile,
    # Chat
    ChatThread,
    ChatMembership,
    ChatMessage,
    # Sondages
    Poll,
    PollOption,
    PollBallot,
    # Modération & audit
    ModerationReport,
    AuditLog,
    # Contenus éducatifs (nouveau système)
    EducationalContent,
    ContentLike,
    ContentComment,
    # Aide & engagement
    HelpRequest,
    Engagement,
)


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ("id", "titre", "created_at")
    search_fields = ("titre",)
    ordering = ("-created_at",)


@admin.register(Cagnotte)
class CagnotteAdmin(admin.ModelAdmin):
    list_display = ("id", "projet", "montant_cible", "montant_collecte")
    search_fields = ("projet__titre",)


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ("id", "cagnotte", "montant", "created_at")
    search_fields = ("cagnotte__projet__titre",)


@admin.register(EducationalContent)
class EducationalContentAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "status", "created_at")
    list_filter = ("type", "status", "created_at")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(HelpRequest)
class HelpRequestAdmin(admin.ModelAdmin):
    list_display = ("title", "help_type", "urgency", "status", "created_at")
    list_filter = ("help_type", "urgency", "status", "created_at")
    search_fields = ("title", "description")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Engagement)
class EngagementAdmin(admin.ModelAdmin):
    list_display = ("id", "scope", "status", "created_at")
    list_filter = ("scope", "status", "created_at")
    search_fields = ("availability", "notes")
    readonly_fields = ("created_at", "updated_at")


# Enregistrement simple des autres modèles pour les avoir dans l’admin
admin.site.register(Media)
admin.site.register(Intent)
admin.site.register(Profile)
admin.site.register(ChatThread)
admin.site.register(ChatMembership)
admin.site.register(ChatMessage)
admin.site.register(Poll)
admin.site.register(PollOption)
admin.site.register(PollBallot)
admin.site.register(ModerationReport)
admin.site.register(AuditLog)
admin.site.register(ContentLike)
admin.site.register(ContentComment)


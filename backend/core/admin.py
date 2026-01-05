from django.contrib import admin, messages
from django.conf import settings

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
    # Protocole SAKA 🌾
    SakaWallet,
    SakaTransaction,
    SakaSilo,  # Phase 3 : Compostage & Silo Commun
    SakaCompostLog,  # Phase 3 : Audit logs de compostage
    # Communautés
    Community,
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
    list_display = ("title", "type", "status", "author", "published_at", "created_at")
    list_filter = ("type", "status", "created_at")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at", "published_at", "published_by", "modified_by")
    
    fieldsets = (
        ("Informations générales", {
            "fields": ("title", "slug", "type", "category", "status", "description", "tags")
        }),
        ("Auteur", {
            "fields": ("author", "anonymous_display_name")
        }),
        ("Fichiers et liens", {
            "fields": ("file", "external_url", "audio_file")
        }),
        ("Projet lié", {
            "fields": ("project",)
        }),
        ("Tracking workflow", {
            "fields": ("published_by", "published_at", "modified_by", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """
        Définit les champs en lecture seule selon le statut.
        """
        readonly = list(self.readonly_fields)
        
        if obj:
            # Si le contenu est publié ou archivé, certains champs sont en lecture seule
            if obj.status in ["published", "archived"]:
                readonly.extend(["title", "slug", "type", "category", "description", "tags", "author"])
        
        return readonly
    
    actions = ["publish_contents", "archive_contents", "reject_contents"]
    
    def publish_contents(self, request, queryset):
        """Action admin : Publier les contenus sélectionnés"""
        from django.core.exceptions import ValidationError
        count = 0
        errors = []
        for content in queryset:
            try:
                content.transition_to("published", user=request.user)
                count += 1
            except ValidationError as e:
                errors.append(f"{content.title}: {str(e)}")
        
        if count > 0:
            self.message_user(request, f"{count} contenu(s) publié(s).")
        if errors:
            self.message_user(request, f"Erreurs: {', '.join(errors)}", level="error")
    publish_contents.short_description = "Publier les contenus sélectionnés"
    
    def archive_contents(self, request, queryset):
        """Action admin : Archiver les contenus sélectionnés"""
        from django.core.exceptions import ValidationError
        count = 0
        errors = []
        for content in queryset:
            try:
                content.transition_to("archived", user=request.user)
                count += 1
            except ValidationError as e:
                errors.append(f"{content.title}: {str(e)}")
        
        if count > 0:
            self.message_user(request, f"{count} contenu(s) archivé(s).")
        if errors:
            self.message_user(request, f"Erreurs: {', '.join(errors)}", level="error")
    archive_contents.short_description = "Archiver les contenus sélectionnés"
    
    def reject_contents(self, request, queryset):
        """Action admin : Rejeter les contenus sélectionnés"""
        from django.core.exceptions import ValidationError
        count = 0
        errors = []
        for content in queryset:
            try:
                content.transition_to("rejected", user=request.user)
                count += 1
            except ValidationError as e:
                errors.append(f"{content.title}: {str(e)}")
        
        if count > 0:
            self.message_user(request, f"{count} contenu(s) rejeté(s).")
        if errors:
            self.message_user(request, f"Erreurs: {', '.join(errors)}", level="error")
    reject_contents.short_description = "Rejeter les contenus sélectionnés"


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


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("members",)


# Enregistrement simple des autres modèles pour les avoir dans l'admin
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


# ==============================================
# PROTOCOLE SAKA 🌾 (V2.1 - Le Cerveau Yin)
# ==============================================
from core.services.saka import run_saka_compost_cycle


# Actions admin pour lancer des cycles de compostage SAKA
@admin.action(description="Lancer un cycle de compost (dry-run, simulation)")
def action_run_saka_compost_dry_run(modeladmin, request, queryset):
    """
    Action admin pour lancer un cycle de compost SAKA en mode DRY-RUN.
    Ne touche pas réellement aux wallets, mais enregistre un log de simulation.
    """
    if not getattr(settings, "SAKA_COMPOST_ENABLED", False):
        messages.warning(
            request,
            "Le compostage SAKA n'est pas activé. Activez SAKA_COMPOST_ENABLED dans les settings."
        )
        return
    
    try:
        result = run_saka_compost_cycle(dry_run=True, source="admin")
        wallets = result.get("wallets_affected", 0)
        total = result.get("total_composted", 0)
        log_id = result.get("log_id", "N/A")
        messages.info(
            request,
            f"Cycle de compost (DRY-RUN) exécuté : {wallets} wallets concernés, "
            f"{total} SAKA seraient compostés. (Log ID: {log_id})"
        )
    except Exception as e:
        messages.error(
            request,
            f"Erreur lors du cycle de compost (DRY-RUN) : {str(e)}"
        )


@admin.action(description="Lancer un cycle de compost (LIVE, effectif)")
def action_run_saka_compost_live(modeladmin, request, queryset):
    """
    Action admin pour lancer un cycle de compost SAKA en mode LIVE.
    Applique réellement le démurrage et alimente le Silo.
    
    ⚠️ ATTENTION : Cette action modifie réellement les wallets et alimente le Silo Commun.
    Django admin demandera confirmation avant d'exécuter l'action.
    """
    if not getattr(settings, "SAKA_COMPOST_ENABLED", False):
        messages.warning(
            request,
            "Le compostage SAKA n'est pas activé. Activez SAKA_COMPOST_ENABLED dans les settings."
        )
        return
    
    try:
        result = run_saka_compost_cycle(dry_run=False, source="admin")
        wallets = result.get("wallets_affected", 0)
        total = result.get("total_composted", 0)
        log_id = result.get("log_id", "N/A")
        messages.success(
            request,
            f"Cycle de compost (LIVE) exécuté : {wallets} wallets affectés, "
            f"{total} SAKA compostés. (Log ID: {log_id})"
        )
    except Exception as e:
        messages.error(
            request,
            f"Erreur lors du cycle de compost (LIVE) : {str(e)}"
        )
@admin.register(SakaWallet)
class SakaWalletAdmin(admin.ModelAdmin):
    """
    Admin pour les portefeuilles SAKA.
    
    Constitution EGOEJO: no direct SAKA mutation.
    Les champs balance, total_harvested, total_planted, total_composted sont en lecture seule.
    Toute modification SAKA doit passer par les services (harvest_saka, spend_saka, etc.).
    """
    list_display = ("user", "balance", "total_harvested", "total_planted", "total_composted", "last_activity_date", "updated_at")
    list_filter = ("last_activity_date", "updated_at")
    search_fields = ("user__username", "user__email")
    # Constitution: no direct SAKA mutation - Tous les champs de solde/cumul sont en lecture seule
    readonly_fields = ("created_at", "updated_at", "last_activity_date", "balance", "total_harvested", "total_planted", "total_composted")
    ordering = ("-balance", "-updated_at")
    # Pas de list_editable : empêche l'édition en masse
    # Pas de fieldsets personnalisés : utilise les champs par défaut avec readonly_fields


@admin.register(SakaTransaction)
class SakaTransactionAdmin(admin.ModelAdmin):
    """
    Admin pour les transactions SAKA.
    Permet de filtrer et rechercher dans l'historique complet.
    """
    list_display = ("id", "user", "direction", "amount", "reason", "created_at")
    list_filter = ("direction", "reason", "created_at")
    search_fields = ("user__username", "user__email", "reason", "metadata")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 50
    
    def get_queryset(self, request):
        """Optimiser les requêtes avec select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(SakaSilo)
class SakaSiloAdmin(admin.ModelAdmin):
    """
    Admin pour le Silo Commun SAKA (Phase 3 : Compostage).
    Permet de visualiser l'état du Silo et de déclencher manuellement un cycle de compostage.
    """
    list_display = ('id', 'total_balance', 'total_composted', 'total_cycles', 'last_compost_at')
    readonly_fields = ('created_at', 'updated_at', 'total_balance', 'total_composted', 'total_cycles', 'last_compost_at')
    
    def has_add_permission(self, request):
        # Empêcher la création manuelle (le Silo est un singleton)
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Empêcher la suppression (le Silo est critique)
        return False
    
    actions = ['trigger_compost_cycle']
    
    def trigger_compost_cycle(self, request, queryset):
        """
        Action admin pour déclencher manuellement un cycle de compostage.
        """
        from core.services.saka import run_saka_compost_cycle
        
        try:
            result = run_saka_compost_cycle(dry_run=False, source="admin")
            log_id = result.get("log_id", "N/A")
            self.message_user(
                request,
                f"Cycle de compostage exécuté : {result['wallets_affected']} wallets affectés, "
                f"{result['total_composted']} SAKA compostés. (Log ID: {log_id})"
            )
        except Exception as e:
            self.message_user(request, f"Erreur lors du compostage : {str(e)}", level='ERROR')
    
    trigger_compost_cycle.short_description = "Déclencher un cycle de compostage (LIVE)"


@admin.register(SakaCompostLog)
class SakaCompostLogAdmin(admin.ModelAdmin):
    """
    Admin pour les logs de compostage SAKA.
    Permet de consulter l'historique des cycles de compostage et de lancer de nouveaux cycles.
    """
    list_display = ("id", "started_at", "finished_at", "dry_run", "wallets_affected", "total_composted", "source")
    list_filter = ("dry_run", "source", "started_at")
    search_fields = ("id", "source")
    readonly_fields = ("started_at", "finished_at", "inactivity_days", "rate", "min_balance", "min_amount", "source")
    ordering = ("-started_at",)
    date_hierarchy = "started_at"
    list_per_page = 50
    
    # Actions admin pour lancer des cycles de compostage
    actions = [action_run_saka_compost_dry_run, action_run_saka_compost_live]
    
    fieldsets = (
        ("Cycle", {
            "fields": ("started_at", "finished_at", "dry_run", "source")
        }),
        ("Résultats", {
            "fields": ("wallets_affected", "total_composted")
        }),
        ("Paramètres", {
            "fields": ("inactivity_days", "rate", "min_balance", "min_amount"),
            "classes": ("collapse",)
        }),
    )


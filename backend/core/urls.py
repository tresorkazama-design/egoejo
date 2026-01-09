from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.api.engagement_views import EngagementViewSet
from core.api.help_views import HelpRequestViewSet
from core.api.content_views import EducationalContentViewSet
from core.api.auth_views import RegisterView, CurrentUserView
from core.api.token_views import RefreshTokenView
from core.api.security_views import SecurityAuditView, SecurityMetricsView
from core.api.gdpr_views import DataExportView, DataDeleteView
from core.api.monitoring_views import MetricsView, AlertsView, MetricsStatsView, AlertsListView
from core.api.impact_views import ImpactDashboardView, GlobalAssetsView
from core.api.chat_support import ConciergeThreadView, ConciergeEligibilityView, SupportContactView
from core.api.chat_moderation import ChatMessageReportViewSet
from finance.views import (
    PocketTransferView, WalletPassAppleView, WalletPassGoogleView,
    StripeWebhookView, HelloAssoCheckoutView, HelloAssoWebhookView
)

from .views import (
    CagnotteListCreate,
    ChatMessageViewSet,
    ChatMessageReportViewSet,
    ChatThreadViewSet,
    ProjetListCreate,
    rejoindre,
    admin_data,
    contribute,
    delete_intent,
    export_intents,
    PollViewSet,
    ModerationReportViewSet,
    AuditLogViewSet,
)
from core.api.projects import boost_project, ProjetRetrieveUpdateDestroy
from core.api.search_views import ProjetSearchView
from core.api.semantic_search_views import SemanticSearchView, SemanticSuggestionsView
from core.api.mycelium_views import MyceliumDataView, MyceliumReduceView
from core.api.config_views import FeaturesConfigView  # Feature flags V1.6/V2.0
from core.api.oracle_views import ProjectOraclesView, AvailableOraclesView  # Oracles d'impact
from investment.views import ShareholderRegisterViewSet  # V2.0 dormant (protégé par permission)
from core.api import saka_views  # Phase 3 SAKA : Compostage & Silo Commun
from core.api import communities_views  # Communautés (subsidiarité)
from core.api.saka_metrics_views import (  # Métriques SAKA pour monitoring
    SakaCompostMetricsView,
    SakaRedistributionMetricsView,
    SakaSiloMetricsView,
    SakaGlobalMetricsView,
    SakaCycleMetricsView,
    SakaAllMetricsView,
)
from core.api.compliance_views import egoejo_compliance_status, egoejo_compliance_badge, critical_alert_metrics  # Label public EGOEJO COMPLIANT
from core.api.public_compliance import egoejo_constitution_status, egoejo_constitution_badge  # Constitution EGOEJO
from core.api.content_compliance_views import (
    content_compliance_report,
)  # Compliance éditoriale du contenu
from core.api.institutional_exports import export_un_compliance, export_foundation_report, export_institutional_markdown  # Exports institutionnels ONU/Fondation

router = DefaultRouter()

# Chat
router.register(r"chat/threads", ChatThreadViewSet, basename="chat-thread")
router.register(r"chat/messages", ChatMessageViewSet, basename="chat-message")
router.register(r"chat/reports", ChatMessageReportViewSet, basename="chat-report")

# Sondages / modération / audit
router.register(r"polls", PollViewSet, basename="poll")
router.register(r"moderation/reports", ModerationReportViewSet, basename="moderation-report")
router.register(r"audit/logs", AuditLogViewSet, basename="audit-log")

# Contenus éducatifs
router.register(r"contents", EducationalContentViewSet, basename="content")

# Investment (V2.0 dormant) - Protégé par IsInvestmentFeatureEnabled
router.register(r"investment/shareholders", ShareholderRegisterViewSet, basename="shareholder-register")

# Aide & engagement
router.register(r"help-requests", HelpRequestViewSet, basename="help-request")
router.register(r"engagements", EngagementViewSet, basename="engagement")

urlpatterns = [
    # Toutes les routes issues du router DRF (chat, polls, contents, help, engagements, etc.)
    path("", include(router.urls)),

    # --- AUTHENTIFICATION (JWT) ---
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", RefreshTokenView.as_view(), name="token_refresh"),  # Rotation des tokens
    path("auth/register/", RegisterView.as_view(), name="auth_register"),
    path("auth/me/", CurrentUserView.as_view(), name="auth_me"),

    # --- SÉCURITÉ (Admin uniquement) ---
    path("security/audit/", SecurityAuditView.as_view(), name="security-audit"),
    path("security/metrics/", SecurityMetricsView.as_view(), name="security-metrics"),
    
    # --- GDPR/RGPD (Utilisateur authentifié) ---
    path("user/data-export/", DataExportView.as_view(), name="user-data-export"),
    path("user/data-delete/", DataDeleteView.as_view(), name="user-data-delete"),
    
    # --- MONITORING & ANALYTICS ---
    path("analytics/metrics/", MetricsView.as_view(), name="analytics-metrics"),
    path("monitoring/alerts/", AlertsView.as_view(), name="monitoring-alerts"),
    path("monitoring/metrics/stats/", MetricsStatsView.as_view(), name="monitoring-metrics-stats"),
    path("monitoring/alerts/list/", AlertsListView.as_view(), name="monitoring-alerts-list"),
    
    # --- IMPACT & GAMIFICATION ---
    path("impact/dashboard/", ImpactDashboardView.as_view(), name="impact-dashboard"),
    path("impact/global-assets/", GlobalAssetsView.as_view(), name="global-assets"),  # Expose SAKA dans la réponse
    
    # --- WALLET & POCKETS ---
    path("wallet/pockets/transfer/", PocketTransferView.as_view(), name="pocket-transfer"),
    path("wallet-pass/apple/", WalletPassAppleView.as_view(), name="wallet-pass-apple"),
    path("wallet-pass/google/", WalletPassGoogleView.as_view(), name="wallet-pass-google"),
    
    # --- STRIPE WEBHOOKS ---
    path("finance/stripe/webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
    
    # --- HELLOASSO PAYMENTS (Mode Simulé) ---
    path("payments/helloasso/start/", HelloAssoCheckoutView.as_view(), name="helloasso-checkout"),
    path("payments/helloasso/webhook/", HelloAssoWebhookView.as_view(), name="helloasso-webhook"),
    
    # --- SUPPORT CONCIERGE ---
    path("support/concierge/", ConciergeThreadView.as_view(), name="concierge-thread"),
    path("support/concierge/eligibility/", ConciergeEligibilityView.as_view(), name="concierge-eligibility"),
    path("support/contact/", SupportContactView.as_view(), name="support-contact"),
    
    # --- AUTRES VUES ---
    path("projets/", ProjetListCreate.as_view(), name="projet-list-create"),
    path("projets/<int:pk>/", ProjetRetrieveUpdateDestroy.as_view(), name="projet-detail"),  # Détail, mise à jour, suppression
    path("projets/<int:pk>/boost/", boost_project, name="projet-boost"),  # Phase 2 : Sorgho-boosting SAKA
    path("projets/<int:pk>/oracles/", ProjectOraclesView.as_view(), name="projet-oracles"),  # Oracles d'impact
    path("projets/search/", ProjetSearchView.as_view(), name="projet-search"),
    path("projets/semantic-search/", SemanticSearchView.as_view(), name="semantic-search"),
    path("projets/semantic-suggestions/", SemanticSuggestionsView.as_view(), name="semantic-suggestions"),
    
    # --- ORACLES D'IMPACT ---
    path("oracles/available/", AvailableOraclesView.as_view(), name="oracles-available"),  # Liste des oracles disponibles
    
    # --- MYCÉLIUM NUMÉRIQUE (3D) --- ⭐ NOUVEAU v1.5.0
    path("mycelium/data/", MyceliumDataView.as_view(), name="mycelium-data"),
    path("mycelium/reduce/", MyceliumReduceView.as_view(), name="mycelium-reduce"),
    
           # --- CONFIGURATION FEATURES (V1.6/V2.0) ⭐ NOUVEAU ---
           path("config/features/", FeaturesConfigView.as_view(), name="config-features"),
           
           # --- SAKA PROTOCOL - PHASE 3 : COMPOSTAGE & SILO COMMUN 🌾 ---
           path("saka/silo/", saka_views.saka_silo_view, name="saka-silo"),
           path("saka/silo/redistribute/", saka_views.saka_silo_redistribute, name="saka-silo-redistribute"),  # Admin uniquement - Redistribution Silo (V1 simple)
           path("saka/compost-preview/", saka_views.saka_compost_preview_view, name="saka-compost-preview"),
          path("saka/transactions/", saka_views.saka_transactions_view, name="saka-transactions"),  # Historique des transactions SAKA
          path("saka/grant/", saka_views.saka_grant_test_view, name="saka-grant-test"),  # Test-only: Créditer SAKA (E2E)
           path("saka/compost-trigger/", saka_views.saka_compost_trigger_view, name="saka-compost-trigger"),  # Admin uniquement
           path("saka/compost-run/", saka_views.saka_compost_run_view, name="saka-compost-run"),  # Admin uniquement - Dry-run depuis frontend
           path("saka/stats/", saka_views.saka_stats_view, name="saka-stats"),  # Admin uniquement - Monitoring & KPIs
          path("saka/compost-logs/", saka_views.saka_compost_logs_view, name="saka-compost-logs"),  # Admin uniquement - Audit logs
          path("saka/cycles/", saka_views.saka_cycles_view, name="saka-cycles"),  # Liste des cycles SAKA avec stats
          path("saka/redistribute/", saka_views.saka_redistribute_view, name="saka-redistribute"),  # Admin uniquement - Redistribution Silo (avec rate optionnel)
          
          # --- SAKA METRICS (Admin uniquement - Monitoring) ---
          path("saka/metrics/compost/", SakaCompostMetricsView.as_view(), name="saka-metrics-compost"),
          path("saka/metrics/redistribution/", SakaRedistributionMetricsView.as_view(), name="saka-metrics-redistribution"),
          path("saka/metrics/silo/", SakaSiloMetricsView.as_view(), name="saka-metrics-silo"),
          path("saka/metrics/global/", SakaGlobalMetricsView.as_view(), name="saka-metrics-global"),
          path("saka/metrics/cycles/", SakaCycleMetricsView.as_view(), name="saka-metrics-cycles"),
          path("saka/metrics/all/", SakaAllMetricsView.as_view(), name="saka-metrics-all"),  # Toutes les métriques en une requête
          
          # --- COMMUNAUTÉS (V1 - Lecture seule) ---
          path("communities/", communities_views.community_list_view, name="community-list"),
          path("communities/<str:slug>/", communities_views.community_detail_view, name="community-detail"),
          
          path("cagnottes/", CagnotteListCreate.as_view(), name="cagnotte-list-create"),
    path("cagnottes/<int:pk>/contribute/", contribute, name="cagnotte-contribute"),
    path("intents/rejoindre/", rejoindre, name="intent-rejoindre"),
    path("intents/admin/", admin_data, name="intent-admin-data"),
    path("intents/export/", export_intents, name="intent-export"),
    path("intents/<int:intent_id>/delete/", delete_intent, name="intent-delete"),
    
    # --- LABEL PUBLIC EGOEJO COMPLIANT ---
    path("public/egoejo-compliance.json", egoejo_compliance_status, name="egoejo-compliance-status"),
    path("public/egoejo-compliance-badge.svg", egoejo_compliance_badge, name="egoejo-compliance-badge"),
    
    # --- CONSTITUTION EGOEJO (Rapport signé CI/CD) ---
    path("public/egoejo-constitution.json", egoejo_constitution_status, name="egoejo-constitution-status"),
    path("public/egoejo-constitution.svg", egoejo_constitution_badge, name="egoejo-constitution-badge"),
    
    # --- COMPLIANCE ÉDITORIALE CONTENU ---
    path("public/content-compliance.json", content_compliance_report, name="content-compliance-report"),
    
    # --- MÉTRIQUES ALERTES CRITIQUES (Observabilité & Transparence) ---
    path("compliance/alerts/metrics/", critical_alert_metrics, name="critical-alert-metrics"),
    
    # --- EXPORTS INSTITUTIONNELS (ONU / FONDATION) ---
    path("compliance/export/un/", export_un_compliance, name="export-un-compliance"),
    path("compliance/export/foundation/", export_foundation_report, name="export-foundation-report"),
    path("compliance/export/un/markdown/", lambda r: export_institutional_markdown(r, "un"), name="export-un-markdown"),
    path("compliance/export/foundation/markdown/", lambda r: export_institutional_markdown(r, "foundation"), name="export-foundation-markdown"),
]

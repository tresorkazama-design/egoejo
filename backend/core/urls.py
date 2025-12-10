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
from finance.views import PocketTransferView, WalletPassAppleView, WalletPassGoogleView

from .views import (
    CagnotteListCreate,
    ChatMessageViewSet,
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
from core.api.search_views import ProjetSearchView
from core.api.semantic_search_views import SemanticSearchView, SemanticSuggestionsView
from core.api.mycelium_views import MyceliumDataView, MyceliumReduceView
from core.api.config_views import FeaturesConfigView  # Feature flags V1.6/V2.0
from investment.views import ShareholderRegisterViewSet  # V2.0 dormant (protégé par permission)

router = DefaultRouter()

# Chat
router.register(r"chat/threads", ChatThreadViewSet, basename="chat-thread")
router.register(r"chat/messages", ChatMessageViewSet, basename="chat-message")

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
    path("impact/global-assets/", GlobalAssetsView.as_view(), name="global-assets"),
    
    # --- WALLET & POCKETS ---
    path("wallet/pockets/transfer/", PocketTransferView.as_view(), name="pocket-transfer"),
    path("wallet-pass/apple/", WalletPassAppleView.as_view(), name="wallet-pass-apple"),
    path("wallet-pass/google/", WalletPassGoogleView.as_view(), name="wallet-pass-google"),
    
    # --- SUPPORT CONCIERGE ---
    path("support/concierge/", ConciergeThreadView.as_view(), name="concierge-thread"),
    path("support/concierge/eligibility/", ConciergeEligibilityView.as_view(), name="concierge-eligibility"),
    path("support/contact/", SupportContactView.as_view(), name="support-contact"),
    
    # --- AUTRES VUES ---
    path("projets/", ProjetListCreate.as_view(), name="projet-list-create"),
    path("projets/search/", ProjetSearchView.as_view(), name="projet-search"),
    path("projets/semantic-search/", SemanticSearchView.as_view(), name="semantic-search"),
    path("projets/semantic-suggestions/", SemanticSuggestionsView.as_view(), name="semantic-suggestions"),
    
    # --- MYCÉLIUM NUMÉRIQUE (3D) --- ⭐ NOUVEAU v1.5.0
    path("mycelium/data/", MyceliumDataView.as_view(), name="mycelium-data"),
    path("mycelium/reduce/", MyceliumReduceView.as_view(), name="mycelium-reduce"),
    
    # --- CONFIGURATION FEATURES (V1.6/V2.0) ⭐ NOUVEAU ---
    path("config/features/", FeaturesConfigView.as_view(), name="config-features"),
    
    path("cagnottes/", CagnotteListCreate.as_view(), name="cagnotte-list-create"),
    path("cagnottes/<int:pk>/contribute/", contribute, name="cagnotte-contribute"),
    path("intents/rejoindre/", rejoindre, name="intent-rejoindre"),
    path("intents/admin/", admin_data, name="intent-admin-data"),
    path("intents/export/", export_intents, name="intent-export"),
    path("intents/<int:intent_id>/delete/", delete_intent, name="intent-delete"),
]

from django.urls import include, path
from rest_framework.routers import DefaultRouter

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

router = DefaultRouter()
router.register('chat/threads', ChatThreadViewSet, basename='chat-thread')
router.register('chat/messages', ChatMessageViewSet, basename='chat-message')
router.register('polls', PollViewSet, basename='poll')
router.register('moderation/reports', ModerationReportViewSet, basename='moderation-report')
router.register('audit/logs', AuditLogViewSet, basename='audit-log')

urlpatterns = [
    path('', include(router.urls)),
    path('projets/', ProjetListCreate.as_view(), name='projet-list-create'),
    path('cagnottes/', CagnotteListCreate.as_view(), name='cagnotte-list-create'),
    path('cagnottes/<int:pk>/contribute/', contribute, name='cagnotte-contribute'),
    path('intents/rejoindre/', rejoindre, name='intent-rejoindre'),
    path('intents/admin/', admin_data, name='intent-admin-data'),
    path('intents/export/', export_intents, name='intent-export'),
    path('intents/<int:intent_id>/delete/', delete_intent, name='intent-delete'),
]
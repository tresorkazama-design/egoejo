"""
Point d'entrée unique pour les vues de l'API ``core``.

Chaque domaine expose ses vues dans un module dédié mais
elles sont ré-exportées ici pour conserver la compatibilité
avec le code existant (`from core.views import ...`).
"""

from .projects import ProjetListCreate  # noqa: F401
from .fundraising import CagnotteListCreate, contribute  # noqa: F401
from .chat import ChatThreadViewSet, ChatMessageViewSet  # noqa: F401
from .chat_moderation import ChatMessageReportViewSet  # noqa: F401
from .polls import PollViewSet  # noqa: F401
from .moderation import ModerationReportViewSet  # noqa: F401
from .audit import AuditLogViewSet  # noqa: F401
from .intents import rejoindre, admin_data, export_intents, delete_intent  # noqa: F401
from .help_views import HelpRequestViewSet


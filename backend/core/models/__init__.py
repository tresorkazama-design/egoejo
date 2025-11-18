"""
Module d'agrégation pour les modèles de l'application ``core``.

Ce package expose les modèles métiers répartis par domaine
(`chat`, `polls`, `moderation`, etc.) tout en conservant un
point d'import unique compatible avec l'existant
(`from core.models import ...`).
"""

from .common import default_metadata  # noqa: F401
from .projects import Projet, Media  # noqa: F401
from .fundraising import Cagnotte, Contribution  # noqa: F401
from .intents import Intent  # noqa: F401
from .accounts import Profile  # noqa: F401
from .chat import ChatThread, ChatMembership, ChatMessage  # noqa: F401
from .polls import Poll, PollOption, PollBallot  # noqa: F401
from .moderation import ModerationReport  # noqa: F401
from .audit import AuditLog  # noqa: F401
from .content import ContenuEducatif, Like, Commentaire  # noqa: F401


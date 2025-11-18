"""
Module d'agrégation pour les sérialiseurs ``core``.
"""

from .projects import ProjetSerializer, MediaSerializer  # noqa: F401
from .fundraising import CagnotteSerializer, ContributionSerializer  # noqa: F401
from .intents import IntentSerializer  # noqa: F401
from .accounts import ProfileSerializer, UserSummarySerializer  # noqa: F401
from .chat import ChatThreadSerializer, ChatMessageSerializer  # noqa: F401
from .polls import PollSerializer, PollOptionSerializer, PollVoteSerializer, PollBallotSerializer  # noqa: F401
from .moderation import ModerationReportSerializer  # noqa: F401
from .audit import AuditLogSerializer  # noqa: F401
from .content import ContenuEducatifSerializer, LikeSerializer, CommentaireSerializer  # noqa: F401


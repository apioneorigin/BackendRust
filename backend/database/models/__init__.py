"""
SQLAlchemy models mirroring Prisma schema from reality-transformer.
"""

from .enums import (
    InvitationStatus,
    SubscriptionStatus,
    SubscriptionTier,
    UsageType,
    UserRole,
)
from .auth import (
    User,
    UserSession,
    Organization,
    Invitation,
    UserPattern,
    UserInteraction,
)
from .session import (
    Session,
    Interaction,
    Insight,
    InsightGeneration,
    AuditLog,
)
from .chat import (
    ChatConversation,
    ChatMessage,
    ChatSummary,
)
from .goal import (
    Goal,
    MatrixValue,
    GapTopology,
    CoherenceSnapshot,
    ValueTrajectory,
    DiscoveredGoal,
    UserGoalInventory,
)
from .document import (
    Document,
    MilestoneConcept,
    DocumentMilestoneMapping,
    SuperTask,
    SuperTaskDocument,
    SubTask,
    DocumentAssumption,
    DocumentGoalConnection,
    DocumentProgress,
)
from .analytics import (
    CalculationSnapshot,
    MatrixPopulation,
    UsageRecord,
    AIServiceLog,
    AIAssistMessage,
    OOFCOSAnalytics,
    InteractionPsychology,
    ElementAction,
    SessionPsychology,
    UserPsychologyProfile,
    PsychologyPopulationMetrics,
)
from .intelligence import (
    UserIntelligence,
    MetricTimeSeries,
    BehaviorPattern,
    GlobalPattern,
    ArchetypeInsight,
)
from .oof import (
    AwarenessSnapshot,
    TransformExecution,
    ChainedExecution,
    SurveySession,
)
from .settings import (
    GlobalSettings,
    PromoCode,
    PromoCodeRedemption,
)

__all__ = [
    # Enums
    "InvitationStatus",
    "SubscriptionStatus",
    "SubscriptionTier",
    "UsageType",
    "UserRole",
    # Auth
    "User",
    "UserSession",
    "Organization",
    "Invitation",
    "UserPattern",
    "UserInteraction",
    # Session
    "Session",
    "Interaction",
    "Insight",
    "InsightGeneration",
    "AuditLog",
    # Chat
    "ChatConversation",
    "ChatMessage",
    "ChatSummary",
    # Goal
    "Goal",
    "MatrixValue",
    "GapTopology",
    "CoherenceSnapshot",
    "ValueTrajectory",
    "DiscoveredGoal",
    "UserGoalInventory",
    # Document
    "Document",
    "MilestoneConcept",
    "DocumentMilestoneMapping",
    "SuperTask",
    "SuperTaskDocument",
    "SubTask",
    "DocumentAssumption",
    "DocumentGoalConnection",
    "DocumentProgress",
    # Analytics
    "CalculationSnapshot",
    "MatrixPopulation",
    "UsageRecord",
    "AIServiceLog",
    "AIAssistMessage",
    "OOFCOSAnalytics",
    "InteractionPsychology",
    "ElementAction",
    "SessionPsychology",
    "UserPsychologyProfile",
    "PsychologyPopulationMetrics",
    # Intelligence
    "UserIntelligence",
    "MetricTimeSeries",
    "BehaviorPattern",
    "GlobalPattern",
    "ArchetypeInsight",
    # OOF
    "AwarenessSnapshot",
    "TransformExecution",
    "ChainedExecution",
    "SurveySession",
    # Settings
    "GlobalSettings",
    "PromoCode",
    "PromoCodeRedemption",
]

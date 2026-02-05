"""
Database package for SQLAlchemy models and configuration.
"""

from .config import (
    Base,
    engine,
    AsyncSessionLocal,
    get_db,
    init_db,
    close_db,
)

from .models import (
    # Enums
    InvitationStatus,
    SubscriptionStatus,
    SubscriptionTier,
    UsageType,
    UserRole,
    # Auth
    User,
    UserSession,
    Organization,
    Invitation,
    UserPattern,
    UserInteraction,
    # Session
    Session,
    Interaction,
    Insight,
    InsightGeneration,
    AuditLog,
    # Chat
    ChatConversation,
    ChatMessage,
    ChatSummary,
    # Goal
    Goal,
    MatrixValue,
    GapTopology,
    CoherenceSnapshot,
    ValueTrajectory,
    DiscoveredGoal,
    UserGoalInventory,
    FileGoalDiscovery,
    # Document
    Document,
    MilestoneConcept,
    DocumentMilestoneMapping,
    SuperTask,
    SuperTaskDocument,
    SubTask,
    DocumentAssumption,
    DocumentGoalConnection,
    DocumentProgress,
    # Analytics
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
    # Intelligence
    UserIntelligence,
    MetricTimeSeries,
    BehaviorPattern,
    GlobalPattern,
    ArchetypeInsight,
    # OOF
    AwarenessSnapshot,
    TransformExecution,
    ChainedExecution,
    SurveySession,
    # Settings
    GlobalSettings,
    PromoCode,
    PromoCodeRedemption,
)

__all__ = [
    # Config
    "Base",
    "engine",
    "AsyncSessionLocal",
    "get_db",
    "init_db",
    "close_db",
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
    "FileGoalDiscovery",
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

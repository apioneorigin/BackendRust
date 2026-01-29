"""
Enum definitions matching Prisma schema.
"""

import enum


class InvitationStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EXPIRED = "EXPIRED"
    CANCELED = "CANCELED"


class SubscriptionStatus(str, enum.Enum):
    TRIALING = "TRIALING"
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    CANCELED = "CANCELED"
    EXPIRED = "EXPIRED"
    PAUSED = "PAUSED"


class SubscriptionTier(str, enum.Enum):
    STARTER = "STARTER"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"
    CUSTOM = "CUSTOM"


class UsageType(str, enum.Enum):
    SESSION_CREATED = "SESSION_CREATED"
    CREDITS_SPENT = "CREDITS_SPENT"
    API_CALL = "API_CALL"
    FILE_UPLOAD = "FILE_UPLOAD"
    INSIGHT_GENERATED = "INSIGHT_GENERATED"
    PROMPT_SENT = "PROMPT_SENT"


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    ORG_OWNER = "ORG_OWNER"
    ORG_ADMIN = "ORG_ADMIN"
    USER = "USER"
    VIEWER = "VIEWER"

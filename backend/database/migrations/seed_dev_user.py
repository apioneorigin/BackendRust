"""
Seed development database with super admin user.
Run: python -m database.migrations.seed_dev_user
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

# Force SQLite for this script
os.environ["USE_SQLITE"] = "true"


async def seed_dev_user():
    from database import get_db, init_db, engine
    from database.models.auth import Organization, User, UserSession
    from database.models.enums import UserRole, SubscriptionStatus, SubscriptionTier, is_super_admin
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    import secrets
    import hashlib

    # Initialize database tables
    await init_db()
    print("[SEED] Database tables initialized")

    async with AsyncSession(engine) as db:
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.email == "raghavan.vinod@gmail.com")
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"[SEED] User already exists: {existing_user.email}")
            print(f"[SEED] User ID: {existing_user.id}")
            print(f"[SEED] Organization ID: {existing_user.organization_id}")

            # Create a new session for the user
            token = secrets.token_urlsafe(32)
            session = UserSession(
                id=secrets.token_urlsafe(16),
                user_id=existing_user.id,
                token=token,
                expires_at=datetime.utcnow() + timedelta(days=30),
                ip_address="127.0.0.1",
                user_agent="seed-script",
            )
            db.add(session)
            await db.commit()

            print(f"\n[SEED] New session created!")
            print(f"[SEED] Token (use this for login): {token}")
            return

        # Create organization
        org_id = secrets.token_urlsafe(16)
        org = Organization(
            id=org_id,
            name="Super Admin Org",
            slug="super-admin-org",
            subscription_status=SubscriptionStatus.ACTIVE,
            subscription_tier=SubscriptionTier.ENTERPRISE,
            max_credits_per_month=999999,
            used_credits=0,
        )
        db.add(org)
        print(f"[SEED] Organization created: {org_id}")

        # Create super admin user
        user_id = secrets.token_urlsafe(16)
        # Simple password hash for dev (password: "admin123")
        password_hash = hashlib.sha256("admin123".encode()).hexdigest()

        user = User(
            id=user_id,
            organization_id=org_id,
            email="raghavan.vinod@gmail.com",
            name="Raghavan Vinod",
            password_hash=password_hash,
            role=UserRole.SUPER_ADMIN,
            is_active=True,
            email_verified=True,
        )
        db.add(user)
        print(f"[SEED] Super admin user created: raghavan.vinod@gmail.com")

        # Create session with long-lived token
        token = secrets.token_urlsafe(32)
        session = UserSession(
            id=secrets.token_urlsafe(16),
            user_id=user_id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(days=30),
            ip_address="127.0.0.1",
            user_agent="seed-script",
        )
        db.add(session)

        await db.commit()

        print(f"\n{'='*60}")
        print(f"[SEED] Development user seeded successfully!")
        print(f"{'='*60}")
        print(f"Email: raghavan.vinod@gmail.com")
        print(f"Password: admin123")
        print(f"User ID: {user_id}")
        print(f"Org ID: {org_id}")
        print(f"Role: SUPER_ADMIN (no credits check)")
        print(f"Token: {token}")
        print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(seed_dev_user())

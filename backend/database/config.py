"""
Database configuration with SQLite for development and PostgreSQL for production.
- Set DATABASE_URL for PostgreSQL (production)
- Leave DATABASE_URL unset or set USE_SQLITE=true for SQLite (development)
"""

import os
import ssl
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "")
USE_SQLITE = os.getenv("USE_SQLITE", "").lower() in ("true", "1", "yes") or not DATABASE_URL

# Determine which database to use
if USE_SQLITE:
    # SQLite for local development
    # Store database file in backend/data directory
    DATA_DIR = Path(__file__).parent.parent / "data"
    DATA_DIR.mkdir(exist_ok=True)
    SQLITE_PATH = DATA_DIR / "dev.db"

    ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///{SQLITE_PATH}"
    connect_args = {"check_same_thread": False}

    # SQLite-specific engine settings
    engine = create_async_engine(
        ASYNC_DATABASE_URL,
        echo=False,
        connect_args=connect_args,
    )

    print(f"[Database] Using SQLite for development: {SQLITE_PATH}")

else:
    # PostgreSQL for production
    def prepare_async_url(url: str) -> tuple[str, dict]:
        """
        Prepare database URL for asyncpg.
        Strips sslmode/channel_binding from URL and returns connect_args for SSL.
        """
        parsed = urlparse(url)

        # Parse query parameters
        query_params = parse_qs(parsed.query)

        # Check if SSL is required
        ssl_required = query_params.pop('sslmode', [None])[0] in ('require', 'verify-ca', 'verify-full')
        query_params.pop('channel_binding', None)  # asyncpg doesn't support this

        # Rebuild query string without unsupported params
        new_query = urlencode({k: v[0] for k, v in query_params.items()}, doseq=False)

        # Rebuild URL with postgresql+asyncpg scheme
        scheme = 'postgresql+asyncpg'
        new_parsed = parsed._replace(scheme=scheme, query=new_query)
        clean_url = urlunparse(new_parsed)

        # Prepare connect_args for SSL
        conn_args = {}
        if ssl_required:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            conn_args['ssl'] = ssl_context

        return clean_url, conn_args

    # Convert to async URL and get SSL config
    ASYNC_DATABASE_URL, connect_args = prepare_async_url(DATABASE_URL)

    # Create async engine for PostgreSQL
    engine = create_async_engine(
        ASYNC_DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        connect_args=connect_args,
    )

    print(f"[Database] Using PostgreSQL: {urlparse(DATABASE_URL).hostname}")

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def get_db() -> AsyncSession:
    """Dependency for FastAPI to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def _run_sqlite_migrations(conn):
    """Run SQLite migrations to add missing columns to existing tables."""
    from sqlalchemy import text

    # Define columns that may need to be added (table, column, type, default)
    migrations = [
        ("chat_messages", "feedback", "TEXT", None),
    ]

    for table, column, col_type, default in migrations:
        # Check if column exists
        result = await conn.execute(text(f"PRAGMA table_info({table})"))
        columns = [row[1] for row in result.fetchall()]

        if column not in columns:
            # Add missing column
            default_clause = f" DEFAULT {default}" if default is not None else ""
            stmt = f'ALTER TABLE {table} ADD COLUMN {column} {col_type}{default_clause}'
            try:
                await conn.execute(text(stmt))
                print(f"[Database] Added missing column: {table}.{column}")
            except Exception as e:
                print(f"[Database] Migration warning: {e}")


async def _migrate_articulated_insights():
    """Migrate articulated_insights to ensure all required fields exist."""
    from sqlalchemy import text
    import json

    async with AsyncSessionLocal() as session:
        # Get all conversations with generated_documents
        result = await session.execute(
            text("SELECT id, generated_documents FROM chat_conversations WHERE generated_documents IS NOT NULL")
        )
        rows = result.fetchall()

        migrated_count = 0
        for row in rows:
            conv_id, docs_json = row
            if not docs_json:
                continue

            # Parse JSON (may be string or already parsed depending on driver)
            docs = json.loads(docs_json) if isinstance(docs_json, str) else docs_json
            if not isinstance(docs, list):
                continue

            modified = False
            for doc in docs:
                matrix_data = doc.get("matrix_data", {})

                # Fix row_options
                for opt in matrix_data.get("row_options", []):
                    insight = opt.get("articulated_insight")
                    if insight and isinstance(insight, dict):
                        # Add missing required fields
                        if "title" not in insight:
                            insight["title"] = insight.get("the_mark_name", "Insight")
                            modified = True
                        if "the_truth_law" not in insight:
                            insight["the_truth_law"] = insight.get("your_truth", "")[:100]
                            modified = True
                        if "your_truth_revelation" not in insight:
                            insight["your_truth_revelation"] = insight.get("the_mark_identity", "")
                            modified = True

                # Fix column_options
                for opt in matrix_data.get("column_options", []):
                    insight = opt.get("articulated_insight")
                    if insight and isinstance(insight, dict):
                        if "title" not in insight:
                            insight["title"] = insight.get("the_mark_name", "Insight")
                            modified = True
                        if "the_truth_law" not in insight:
                            insight["the_truth_law"] = insight.get("your_truth", "")[:100]
                            modified = True
                        if "your_truth_revelation" not in insight:
                            insight["your_truth_revelation"] = insight.get("the_mark_identity", "")
                            modified = True

            if modified:
                # Update the conversation
                await session.execute(
                    text("UPDATE chat_conversations SET generated_documents = :docs WHERE id = :id"),
                    {"docs": json.dumps(docs), "id": conv_id}
                )
                migrated_count += 1

        if migrated_count > 0:
            await session.commit()
            print(f"[Database] Migrated articulated_insights in {migrated_count} conversations")


async def init_db():
    """Initialize database tables and run migrations for SQLite."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # For SQLite, run migrations to add missing columns
        if USE_SQLITE:
            await _run_sqlite_migrations(conn)

    # Run data migrations
    await _migrate_articulated_insights()


async def close_db():
    """Close database connections."""
    await engine.dispose()

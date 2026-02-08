"""
Database configuration with SQLite for development and PostgreSQL for production.
- Set DATABASE_URL for PostgreSQL (production)
- Leave DATABASE_URL unset or set USE_SQLITE=true for SQLite (development)
"""

import os
import ssl
from pathlib import Path
from urllib.parse import urlparse
from sqlalchemy import make_url
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
        Uses SQLAlchemy's make_url to safely handle password encoding.
        Handles DigitalOcean/Heroku URL formats, strips unsupported params.
        """
        # Normalize scheme: postgres:// → postgresql://
        if url.startswith('postgres://'):
            url = 'postgresql://' + url[len('postgres://'):]

        sa_url = make_url(url)

        # Validate
        if not sa_url.host:
            raise ValueError(
                f"Could not parse DATABASE_URL: missing hostname. "
                f"Expected format: postgresql://user:pass@host:port/dbname"
            )

        # Strip unsupported query params, check SSL
        query = dict(sa_url.query)
        ssl_required = query.pop('sslmode', None) in ('require', 'verify-ca', 'verify-full')
        query.pop('channel_binding', None)  # asyncpg doesn't support this

        # Rebuild URL with asyncpg driver and cleaned query params
        sa_url = sa_url.set(
            drivername='postgresql+asyncpg',
            query=query,
        )

        # Prepare connect_args for SSL
        conn_args = {}
        if ssl_required:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            conn_args['ssl'] = ssl_context

        return str(sa_url), conn_args

    # Log what we received (mask password)
    _parsed_for_log = urlparse(DATABASE_URL)
    _masked = DATABASE_URL.replace(f":{_parsed_for_log.password}@", ":***@") if _parsed_for_log.password else DATABASE_URL
    print(f"[Database] Received DATABASE_URL: {_masked}")

    # Convert to async URL and get SSL config
    try:
        ASYNC_DATABASE_URL, connect_args = prepare_async_url(DATABASE_URL)
    except Exception as e:
        print(f"[Database] ERROR parsing DATABASE_URL: {e}")
        print(f"[Database] Falling back to SQLite")
        USE_SQLITE = True
        DATA_DIR = Path(__file__).parent.parent / "data"
        DATA_DIR.mkdir(exist_ok=True)
        SQLITE_PATH = DATA_DIR / "dev.db"
        ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///{SQLITE_PATH}"
        connect_args = {"check_same_thread": False}
        engine = create_async_engine(ASYNC_DATABASE_URL, echo=False, connect_args=connect_args)

    if not USE_SQLITE:
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
        ("chat_conversations", "generated_presets", "TEXT", None),
        ("chat_conversations", "generated_documents", "TEXT", None),
        ("file_goal_discoveries", "file_summary", "TEXT", None),
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
                        if "micro_moment" not in insight:
                            insight["micro_moment"] = ""
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
                        if "micro_moment" not in insight:
                            insight["micro_moment"] = ""
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

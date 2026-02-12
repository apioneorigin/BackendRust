"""
Database configuration with SQLite for development and PostgreSQL for production.
- Set DATABASE_URL for PostgreSQL (production)
- Leave DATABASE_URL unset or set USE_SQLITE=true for SQLite (development)

On DigitalOcean App Platform, DATABASE_URL is auto-discovered from attached
database components — no manual env var entry needed.  See utils/resolve_do_env.py.
"""

import os
import ssl
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

# Auto-discover DATABASE_URL from DigitalOcean-injected env vars (or explicit)
from utils.resolve_do_env import resolve_database_url
DATABASE_URL = resolve_database_url()
IS_PRODUCTION = os.getenv("ENVIRONMENT") == "production"
USE_SQLITE = os.getenv("USE_SQLITE", "").lower() in ("true", "1", "yes") or not DATABASE_URL

# Log env var status at startup (always, regardless of environment)
print(f"[Database] ENVIRONMENT={os.getenv('ENVIRONMENT', '<unset>')}")
print(f"[Database] DATABASE_URL={'set (' + str(len(DATABASE_URL)) + ' chars)' if DATABASE_URL else 'EMPTY or unset'}")
print(f"[Database] USE_SQLITE={USE_SQLITE}")

# In production, DATABASE_URL is required — never fall back to ephemeral SQLite
if IS_PRODUCTION and USE_SQLITE:
    raise RuntimeError(
        "\n" + "="*80 + "\n"
        "[Database] FATAL: DATABASE_URL is not set (or is empty) in production!\n"
        "="*80 + "\n"
        "Without DATABASE_URL, the app uses SQLite inside the container.\n"
        "Container storage is EPHEMERAL — all data is lost on each deploy.\n\n"
        "DigitalOcean 'type: SECRET' env vars are injected as EMPTY strings\n"
        "until you enter the actual value in the Console UI.\n\n"
        "To fix:\n"
        "  1. Go to DigitalOcean Console → Apps → reality-transformer\n"
        "  2. Click Settings → backend component → Environment Variables\n"
        "  3. Click 'Edit' next to DATABASE_URL\n"
        "  4. PASTE the actual PostgreSQL connection string from:\n"
        "     Databases → your cluster → Connection Details → Connection String\n"
        "  5. Also set JWT_SECRET to any random 32+ character string\n"
        "  6. Save → Redeploy\n"
        + "="*80
    )

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
    from urllib.parse import urlparse, unquote
    from sqlalchemy import URL

    # Parse the raw URL to extract components
    _raw = DATABASE_URL
    if _raw.startswith('postgres://'):
        _raw = 'postgresql://' + _raw[len('postgres://'):]

    _parsed = urlparse(_raw)
    if not _parsed.hostname:
        raise ValueError(f"DATABASE_URL missing hostname. Expected: postgresql://user:pass@host:port/db")

    _password = unquote(_parsed.password) if _parsed.password else None
    _host = _parsed.hostname
    _port = _parsed.port or 25060
    _user = unquote(_parsed.username) if _parsed.username else "doadmin"
    _database = _parsed.path.lstrip('/') or "defaultdb"

    # Check sslmode from query string
    _qs = dict(p.split('=', 1) for p in _parsed.query.split('&') if '=' in p) if _parsed.query else {}
    _ssl_required = _qs.get('sslmode') in ('require', 'verify-ca', 'verify-full')

    # Log parsed components (mask password)
    print(f"[Database] Received DATABASE_URL: postgresql://{_user}:***@{_host}:{_port}/{_database}?sslmode={_qs.get('sslmode', 'unset')}")
    print(f"[Database] Password length: {len(_password) if _password else 0} chars")

    # Build SQLAlchemy URL with explicit components (avoids URL re-encoding issues)
    ASYNC_DATABASE_URL = URL.create(
        drivername='postgresql+asyncpg',
        username=_user,
        password=_password,
        host=_host,
        port=_port,
        database=_database,
    )

    # Prepare connect_args for SSL
    connect_args = {}
    if _ssl_required:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connect_args['ssl'] = ssl_context

    if not USE_SQLITE:
        # Create async engine for PostgreSQL
        engine = create_async_engine(
            ASYNC_DATABASE_URL,
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=300,  # Recycle connections every 5 min to prevent stale connection errors
            connect_args=connect_args,
        )

    print(f"[Database] Using PostgreSQL: {_host}")

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
    """Initialize database tables and run migrations.

    Retries connection up to 4 times with exponential backoff (2s, 4s, 8s, 16s)
    to handle race conditions when the database container is still starting.
    """
    import asyncio

    max_retries = 4 if not USE_SQLITE else 0  # Only retry for PostgreSQL
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

                # For SQLite, run migrations to add missing columns
                if USE_SQLITE:
                    await _run_sqlite_migrations(conn)

            # Run data migrations
            await _migrate_articulated_insights()
            return  # Success

        except Exception as e:
            last_error = e
            error_type = type(e).__name__
            error_str = str(e).lower()

            # Only retry on connection errors, not auth or schema errors
            is_connection_error = (
                "could not connect" in error_str
                or "connection refused" in error_str
                or "connection reset" in error_str
                or "timeout" in error_str
                or "ConnectionRefusedError" in error_type
                or "OSError" in error_type
            )

            if is_connection_error and attempt < max_retries:
                delay = 2 ** (attempt + 1)  # 2s, 4s, 8s, 16s
                print(f"[Database] Connection failed (attempt {attempt + 1}/{max_retries + 1}), retrying in {delay}s...")
                await asyncio.sleep(delay)
                continue

            # Non-retryable error or final attempt — provide helpful messages
            if "InvalidPasswordError" in error_type or "authentication failed" in error_str:
                print(f"\n{'='*80}")
                print(f"[Database] AUTHENTICATION ERROR: Password authentication failed")
                print(f"{'='*80}")
                print(f"[Database] Your DATABASE_URL has incorrect or expired credentials.")
                print(f"[Database]")
                print(f"[Database] To fix this:")
                print(f"[Database] 1. Go to DigitalOcean Console → Databases")
                print(f"[Database] 2. Select your PostgreSQL cluster")
                print(f"[Database] 3. Copy the connection string from 'Connection Details'")
                print(f"[Database] 4. Update DATABASE_URL in App Platform environment variables")
                print(f"[Database]")
                print(f"[Database] See DATABASE_FIX.md for detailed instructions.")
                print(f"{'='*80}\n")
            elif is_connection_error:
                print(f"\n{'='*80}")
                print(f"[Database] CONNECTION ERROR: Cannot reach database server after {max_retries + 1} attempts")
                print(f"{'='*80}")
                print(f"[Database] The database server is unreachable.")
                print(f"[Database] Check if:")
                print(f"[Database] - The database is running in DigitalOcean")
                print(f"[Database] - Network connectivity is working")
                print(f"[Database] - Firewall rules allow connections")
                print(f"{'='*80}\n")
            else:
                print(f"\n{'='*80}")
                print(f"[Database] ERROR: {error_type}")
                print(f"{'='*80}")
                print(f"[Database] {e}")
                print(f"{'='*80}\n")

            # Re-raise to stop the application
            raise


async def close_db():
    """Close database connections."""
    await engine.dispose()

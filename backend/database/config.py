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


async def init_db():
    """Initialize database tables and run migrations for SQLite."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # For SQLite, run migrations to add missing columns
        if USE_SQLITE:
            await _run_sqlite_migrations(conn)


async def close_db():
    """Close database connections."""
    await engine.dispose()

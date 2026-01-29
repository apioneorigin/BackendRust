"""
Database configuration for PostgreSQL with SQLAlchemy async support.
Mirrors the Prisma/PostgreSQL setup from reality-transformer.
"""

import os
import ssl
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

# Get DATABASE_URL from environment (same as Prisma uses)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/reality_transformer")


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
    connect_args = {}
    if ssl_required:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connect_args['ssl'] = ssl_context

    return clean_url, connect_args


# Convert to async URL and get SSL config
ASYNC_DATABASE_URL, connect_args = prepare_async_url(DATABASE_URL)

# Create async engine
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,  # Set to True for SQL logging
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    connect_args=connect_args,
)

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


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections."""
    await engine.dispose()

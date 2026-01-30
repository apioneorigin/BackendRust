"""
Diagnostic script to check authentication tables and sessions.
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import ssl
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    exit(1)


def prepare_async_url(url: str) -> tuple[str, dict]:
    """Prepare database URL for asyncpg."""
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    ssl_required = query_params.pop('sslmode', [None])[0] in ('require', 'verify-ca', 'verify-full')
    query_params.pop('channel_binding', None)
    new_query = urlencode({k: v[0] for k, v in query_params.items()}, doseq=False)
    scheme = 'postgresql+asyncpg'
    new_parsed = parsed._replace(scheme=scheme, query=new_query)
    clean_url = urlunparse(new_parsed)

    conn_args = {}
    if ssl_required:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        conn_args['ssl'] = ssl_context

    return clean_url, conn_args


async def check_auth():
    async_url, connect_args = prepare_async_url(DATABASE_URL)
    engine = create_async_engine(async_url, connect_args=connect_args)

    print(f"Connecting to: {urlparse(DATABASE_URL).hostname}")
    print("=" * 60)

    async with engine.begin() as conn:
        # Check user_sessions table columns
        print("\n1. USER_SESSIONS TABLE COLUMNS:")
        result = await conn.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'user_sessions'
            ORDER BY ordinal_position
        """))
        columns = result.fetchall()
        for col_name, col_type in columns:
            print(f"   {col_name}: {col_type}")

        # Check if there are any sessions
        print("\n2. SESSION COUNT:")
        result = await conn.execute(text("SELECT COUNT(*) FROM user_sessions"))
        count = result.scalar()
        print(f"   Total sessions: {count}")

        # Check recent sessions
        print("\n3. RECENT SESSIONS (last 5):")
        result = await conn.execute(text("""
            SELECT id, user_id, expires_at, created_at
            FROM user_sessions
            ORDER BY created_at DESC
            LIMIT 5
        """))
        sessions = result.fetchall()
        now = datetime.utcnow()
        for sess_id, user_id, expires_at, created_at in sessions:
            expired = "EXPIRED" if expires_at < now else "VALID"
            print(f"   {sess_id[:16]}... | user: {user_id[:16]}... | {expired} | expires: {expires_at}")

        # Check users table
        print("\n4. USERS TABLE COLUMNS:")
        result = await conn.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """))
        columns = result.fetchall()
        for col_name, col_type in columns:
            print(f"   {col_name}: {col_type}")

        # Check user count
        print("\n5. USER COUNT:")
        result = await conn.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        print(f"   Total users: {count}")

    await engine.dispose()
    print("\n" + "=" * 60)
    print("Diagnostic complete.")


if __name__ == "__main__":
    asyncio.run(check_auth())

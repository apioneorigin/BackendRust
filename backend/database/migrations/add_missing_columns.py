"""
Add missing columns to database tables.
Compares model schema with actual database and adds missing columns.
"""

import asyncio
import os
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


# Define missing columns for chat_conversations
# NOTE: matrix_data removed - now using generated_documents instead
MISSING_COLUMNS = [
    ("chat_conversations", "generated_paths", "JSONB"),
    ("chat_conversations", "generated_documents", "JSONB"),
    ("chat_messages", "feedback", "TEXT"),
    ("chat_messages", "attachments", "JSONB"),
]


async def add_missing_columns():
    async_url, connect_args = prepare_async_url(DATABASE_URL)
    engine = create_async_engine(async_url, connect_args=connect_args)

    print(f"Connecting to: {urlparse(DATABASE_URL).hostname}")

    async with engine.begin() as conn:
        # Get existing columns
        result = await conn.execute(text("""
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
        """))
        existing = {(row[0], row[1]) for row in result.fetchall()}

        added = 0
        for table, column, col_type in MISSING_COLUMNS:
            if (table, column) not in existing:
                try:
                    stmt = f'ALTER TABLE "{table}" ADD COLUMN "{column}" {col_type}'
                    await conn.execute(text(stmt))
                    print(f"  Added: {table}.{column} ({col_type})")
                    added += 1
                except Exception as e:
                    print(f"  Failed: {table}.{column} - {e}")
            else:
                print(f"  Exists: {table}.{column}")

        print(f"\nDone: {added} columns added")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(add_missing_columns())

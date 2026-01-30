"""
Migrate database columns from camelCase to snake_case.
Queries actual schema and renames columns dynamically.
"""

import asyncio
import os
import re
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


def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


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


async def run_migration():
    async_url, connect_args = prepare_async_url(DATABASE_URL)
    engine = create_async_engine(async_url, connect_args=connect_args)

    print(f"Connecting to: {urlparse(DATABASE_URL).hostname}")

    async with engine.begin() as conn:
        # Get all tables and columns from the database
        result = await conn.execute(text("""
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """))
        columns = result.fetchall()

        # Find columns that need renaming (camelCase -> snake_case)
        renames = []
        for table_name, column_name in columns:
            snake_name = camel_to_snake(column_name)
            if snake_name != column_name and column_name != column_name.lower():
                renames.append((table_name, column_name, snake_name))

        print(f"Found {len(renames)} columns to rename")

        if not renames:
            print("No columns need renaming - database already uses snake_case")
            await engine.dispose()
            return

        # Execute renames
        success = 0
        failed = 0
        for table_name, old_name, new_name in renames:
            try:
                # Use quoted identifiers for the old name (camelCase)
                stmt = f'ALTER TABLE "{table_name}" RENAME COLUMN "{old_name}" TO "{new_name}"'
                await conn.execute(text(stmt))
                success += 1
                print(f"  Renamed: {table_name}.{old_name} -> {new_name}")
            except Exception as e:
                error_msg = str(e)
                if "does not exist" in error_msg:
                    pass  # Column already renamed
                else:
                    print(f"  Failed: {table_name}.{old_name} - {error_msg[:60]}")
                    failed += 1

        print(f"\nMigration complete: {success} renamed, {failed} failed")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_migration())

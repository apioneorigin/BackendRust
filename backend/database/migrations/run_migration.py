"""
Run SQL migration against the database.
Usage: python run_migration.py
"""

import asyncio
import os
from pathlib import Path
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


async def run_migration():
    migration_file = Path(__file__).parent / "001_camelcase_to_snake_case.sql"

    if not migration_file.exists():
        print(f"ERROR: Migration file not found: {migration_file}")
        exit(1)

    sql_content = migration_file.read_text()

    # Remove BEGIN/COMMIT as we'll handle transaction ourselves
    sql_content = sql_content.replace("BEGIN;", "").replace("COMMIT;", "")

    # Split into individual statements
    statements = [s.strip() for s in sql_content.split(";") if s.strip() and not s.strip().startswith("--")]

    async_url, connect_args = prepare_async_url(DATABASE_URL)
    engine = create_async_engine(async_url, connect_args=connect_args)

    print(f"Connecting to: {urlparse(DATABASE_URL).hostname}")
    print(f"Running {len(statements)} ALTER statements...")

    async with engine.begin() as conn:
        success = 0
        skipped = 0
        for i, stmt in enumerate(statements):
            if not stmt:
                continue
            try:
                await conn.execute(text(stmt))
                success += 1
                if (i + 1) % 50 == 0:
                    print(f"  Progress: {i + 1}/{len(statements)}")
            except Exception as e:
                error_msg = str(e)
                if "does not exist" in error_msg or "already exists" in error_msg:
                    skipped += 1  # Column already renamed or doesn't exist
                else:
                    print(f"  Warning: {stmt[:60]}... - {error_msg[:80]}")
                    skipped += 1

    await engine.dispose()
    print(f"\nMigration complete: {success} renamed, {skipped} skipped")


if __name__ == "__main__":
    asyncio.run(run_migration())

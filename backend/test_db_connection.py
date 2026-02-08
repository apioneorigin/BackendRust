#!/usr/bin/env python3
"""
Database connection diagnostic tool.
Run this to test your DATABASE_URL before deploying.
"""

import asyncio
import os
import sys
from urllib.parse import urlparse, quote_plus
from dotenv import load_dotenv

load_dotenv()


async def test_connection():
    """Test database connection with detailed diagnostics."""
    database_url = os.getenv("DATABASE_URL", "")

    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable is not set")
        print("\nSet it by running:")
        print('export DATABASE_URL="postgresql://user:password@host:port/dbname"')
        return False

    # Parse the URL
    try:
        parsed = urlparse(database_url)
        print("=" * 80)
        print("DATABASE CONNECTION DIAGNOSTICS")
        print("=" * 80)
        print(f"\n✓ DATABASE_URL is set")
        print(f"  Host:     {parsed.hostname}")
        print(f"  Port:     {parsed.port}")
        print(f"  Database: {parsed.path.lstrip('/')}")
        print(f"  User:     {parsed.username}")
        print(f"  Password: {'*' * len(parsed.password) if parsed.password else '(empty)'}")
        print(f"  SSL Mode: {'require' if 'sslmode=require' in database_url else 'not specified'}")

        # Check for special characters in password
        if parsed.password:
            special_chars = set('!@#$%^&*(){}[]|\\:";\'<>?,./`~')
            password_special = special_chars.intersection(set(parsed.password))
            if password_special:
                print(f"\n⚠️  WARNING: Password contains special characters: {password_special}")
                print("   These may need URL encoding if copied from DigitalOcean")
                print(f"   URL-encoded password: {quote_plus(parsed.password)}")
                print(f"\n   Try this URL:")
                encoded_url = f"{parsed.scheme}://{parsed.username}:{quote_plus(parsed.password)}@{parsed.hostname}:{parsed.port}{parsed.path}"
                if 'sslmode' in database_url:
                    encoded_url += "?sslmode=require"
                print(f"   {encoded_url}")

    except Exception as e:
        print(f"❌ ERROR parsing DATABASE_URL: {e}")
        return False

    # Test connection
    print(f"\n{'=' * 80}")
    print("TESTING CONNECTION...")
    print("=" * 80)

    try:
        import asyncpg

        # Build connection params
        conn_params = {
            'host': parsed.hostname,
            'port': parsed.port or 25060,
            'database': parsed.path.lstrip('/') or 'defaultdb',
            'user': parsed.username,
            'password': parsed.password,
        }

        # Add SSL if required
        if 'sslmode=require' in database_url.lower():
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            conn_params['ssl'] = ssl_context
            print("✓ SSL context created")

        print(f"✓ Attempting to connect to {parsed.hostname}:{parsed.port}...")

        conn = await asyncpg.connect(**conn_params, timeout=10)
        print("✅ CONNECTION SUCCESSFUL!")

        # Test a simple query
        version = await conn.fetchval('SELECT version()')
        print(f"\n✓ PostgreSQL version: {version.split(',')[0]}")

        # Check if tables exist
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
            LIMIT 10
        """)

        if tables:
            print(f"\n✓ Found {len(tables)} table(s) in database:")
            for table in tables[:5]:
                print(f"  - {table['table_name']}")
            if len(tables) > 5:
                print(f"  ... and {len(tables) - 5} more")
        else:
            print("\n⚠️  No tables found (database is empty)")

        await conn.close()
        print("\n" + "=" * 80)
        print("✅ ALL CHECKS PASSED - Your DATABASE_URL is correct!")
        print("=" * 80)
        return True

    except asyncpg.exceptions.InvalidPasswordError:
        print("\n" + "=" * 80)
        print("❌ AUTHENTICATION FAILED")
        print("=" * 80)
        print("\nThe password is incorrect. Please verify:")
        print("1. You copied the COMPLETE connection string from DigitalOcean")
        print("2. The password hasn't been changed/rotated")
        print("3. You're using the 'doadmin' user credentials")
        print("\nTo get the correct credentials:")
        print("  → DigitalOcean Console → Databases → Your Cluster")
        print("  → Connection Details tab → Connection String")
        print("  → Copy the ENTIRE string including the password")
        return False

    except asyncpg.exceptions.ConnectionDoesNotExistError as e:
        print("\n" + "=" * 80)
        print("❌ CONNECTION REFUSED")
        print("=" * 80)
        print(f"\nCannot connect to database server: {e}")
        print("\nPossible causes:")
        print("1. Database is not running")
        print("2. Firewall/network blocking the connection")
        print("3. Wrong hostname or port")
        return False

    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ ERROR: {type(e).__name__}")
        print("=" * 80)
        print(f"\n{e}")
        return False


async def test_with_sqlalchemy():
    """Test using SQLAlchemy (same as the app uses)."""
    print("\n" + "=" * 80)
    print("TESTING WITH SQLALCHEMY (same as app)")
    print("=" * 80)

    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        import ssl
        from sqlalchemy import make_url

        database_url = os.getenv("DATABASE_URL", "")
        parsed = urlparse(database_url)

        # Convert to asyncpg format
        if database_url.startswith('postgres://'):
            database_url = 'postgresql://' + database_url[len('postgres://'):]

        sa_url = make_url(database_url)
        sa_url = sa_url.set(drivername='postgresql+asyncpg')

        connect_args = {}
        if 'sslmode=require' in database_url.lower():
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connect_args['ssl'] = ssl_context

        engine = create_async_engine(
            str(sa_url),
            echo=False,
            connect_args=connect_args,
        )

        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar()
            print(f"✅ SQLAlchemy connection successful! Test query returned: {value}")

        await engine.dispose()
        return True

    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("DATABASE CONNECTION DIAGNOSTIC TOOL")
    print("=" * 80)
    print("\nThis script will test your DATABASE_URL connection.")
    print("Make sure DATABASE_URL is set in your environment or .env file.\n")

    result = asyncio.run(test_connection())

    if result:
        asyncio.run(test_with_sqlalchemy())
        print("\n✅ Your database connection is working correctly!")
        print("The authentication error in DigitalOcean App Platform might be due to:")
        print("  1. Environment variable not updated in App Platform")
        print("  2. Old deployment cache - try redeploying")
        sys.exit(0)
    else:
        print("\n❌ Connection test failed. Fix the issues above and try again.")
        sys.exit(1)

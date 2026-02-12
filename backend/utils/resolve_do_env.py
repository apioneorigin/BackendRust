"""
Auto-discover DigitalOcean App Platform database connection URLs at runtime.

When databases are attached to a DigitalOcean app (via app spec `databases:`
section or the Console UI), connection details are injected as environment
variables.  This module discovers them automatically so DATABASE_URL and
REDIS_URL don't need to be manually entered as secrets in the backend
component.

Discovery order for PostgreSQL:
  1. DATABASE_URL (explicit, current behaviour preserved)
  2. Any env var whose *value* starts with postgresql:// or postgres://
  3. Constructed from individual component vars ({PREFIX}_HOSTNAME, _PORT, …)

Discovery order for Redis / Valkey:
  1. REDIS_URL (explicit)
  2. VALKEY_URL / CACHE_URL (common alternatives)
  3. Any env var whose *value* starts with redis:// or rediss://
  4. Constructed from individual component vars ({PREFIX}_HOSTNAME, _PORT, …)
"""

import os
from typing import Optional


# ---------------------------------------------------------------------------
# PostgreSQL
# ---------------------------------------------------------------------------

def resolve_database_url() -> str:
    """Return a PostgreSQL connection URL from the environment, or ``""``."""

    # 1. Explicit DATABASE_URL
    url = os.getenv("DATABASE_URL", "").strip()
    if url:
        return url

    # 2. Scan every env var for a value that looks like a PG connection string
    for key, value in sorted(os.environ.items()):
        if key == "DATABASE_URL":
            continue
        v = value.strip()
        if v.startswith(("postgresql://", "postgres://", "postgresql+asyncpg://")):
            print(f"[DO Auto-Discovery] Found PostgreSQL URL in ${key}")
            return v

    # 3. Build from individual component vars
    constructed = _construct_pg_url()
    if constructed:
        return constructed

    return ""


# ---------------------------------------------------------------------------
# Redis / Valkey
# ---------------------------------------------------------------------------

def resolve_redis_url() -> str:
    """Return a Redis / Valkey connection URL from the environment, or ``""``."""

    # 1. Explicit well-known names
    for name in ("REDIS_URL", "VALKEY_URL", "CACHE_URL"):
        url = os.getenv(name, "").strip()
        if url:
            if name != "REDIS_URL":
                print(f"[DO Auto-Discovery] Using Redis URL from ${name}")
            return url

    # 2. Scan every env var for a value that looks like a Redis URI
    for key, value in sorted(os.environ.items()):
        if key in ("REDIS_URL", "VALKEY_URL", "CACHE_URL"):
            continue
        v = value.strip()
        if v.startswith(("redis://", "rediss://")):
            print(f"[DO Auto-Discovery] Found Redis URL in ${key}")
            return v

    # 3. Build from individual component vars
    constructed = _construct_redis_url()
    if constructed:
        return constructed

    return ""


# ---------------------------------------------------------------------------
# Helpers – construct URLs from individual DO component variables
# ---------------------------------------------------------------------------
# DigitalOcean injects {COMPONENT}_HOSTNAME, {COMPONENT}_PORT, etc.
# when a database component is attached to the app.  The component name
# is upper-cased and hyphens become underscores.

_PG_PREFIXES = ("DB", "DATABASE", "PG", "POSTGRESQL", "POSTGRES")
_REDIS_PREFIXES = ("REDIS", "VALKEY", "CACHE", "KV")


def _find_component_prefixes(priority: tuple[str, ...]) -> list[str]:
    """Return env var prefixes that have a corresponding _HOSTNAME variable."""
    found: set[str] = set()
    for key in os.environ:
        if key.endswith("_HOSTNAME"):
            prefix = key.removesuffix("_HOSTNAME")
            if prefix:
                found.add(prefix)

    # Return priority prefixes first, then the rest alphabetically
    ordered: list[str] = []
    for p in priority:
        if p in found:
            ordered.append(p)
            found.discard(p)
    ordered.extend(sorted(found))
    return ordered


def _construct_pg_url() -> Optional[str]:
    for prefix in _find_component_prefixes(_PG_PREFIXES):
        hostname = os.getenv(f"{prefix}_HOSTNAME", "").strip()
        if not hostname:
            continue
        username = os.getenv(f"{prefix}_USERNAME", "").strip()
        if not username:
            continue
        password = os.getenv(f"{prefix}_PASSWORD", "").strip()
        port = os.getenv(f"{prefix}_PORT", "25060").strip()
        database = os.getenv(f"{prefix}_DATABASE", "defaultdb").strip()
        ca_cert = os.getenv(f"{prefix}_CA_CERT", "").strip()

        auth = f"{username}:{password}@" if password else f"{username}@"
        sslmode = "sslmode=require" if not ca_cert else "sslmode=verify-ca"
        url = f"postgresql://{auth}{hostname}:{port}/{database}?{sslmode}"

        print(f"[DO Auto-Discovery] Constructed PostgreSQL URL from ${prefix}_* variables")
        return url
    return None


def _construct_redis_url() -> Optional[str]:
    for prefix in _find_component_prefixes(_REDIS_PREFIXES):
        hostname = os.getenv(f"{prefix}_HOSTNAME", "").strip()
        if not hostname:
            continue
        port = os.getenv(f"{prefix}_PORT", "25061").strip()
        password = os.getenv(f"{prefix}_PASSWORD", "").strip()

        # DigitalOcean managed Redis/Valkey always uses TLS → rediss://
        auth = f"default:{password}@" if password else ""
        url = f"rediss://{auth}{hostname}:{port}"

        print(f"[DO Auto-Discovery] Constructed Redis URL from ${prefix}_* variables")
        return url
    return None

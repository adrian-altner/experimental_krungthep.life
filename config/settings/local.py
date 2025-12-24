# Local overrides for development. Keep secrets or machine-specific settings here.
import os
from urllib.parse import unquote, urlparse

from .base import BASE_DIR, DATABASES


env_path = BASE_DIR / ".env.local"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key, value)


def _database_from_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in {"postgres", "postgresql"}:
        return None
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": parsed.path.lstrip("/"),
        "USER": unquote(parsed.username or ""),
        "PASSWORD": unquote(parsed.password or ""),
        "HOST": parsed.hostname or "localhost",
        "PORT": str(parsed.port or 5432),
    }


if env_path.exists():
    database_url = os.environ.get("DATABASE_URL")
    DATABASES["default"] = _database_from_url(database_url) or {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "postgres"),
        "USER": os.environ.get("POSTGRES_USER", ""),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }

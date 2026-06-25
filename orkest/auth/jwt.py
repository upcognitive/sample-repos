"""JWT token creation and validation."""

import os
from datetime import UTC, datetime, timedelta

import jwt

ALGORITHM = "HS256"
DEFAULT_EXPIRE_MINUTES = 60


def _secret_key() -> str:
    return os.environ.get("ORKEST_JWT_SECRET", "change-me-in-production")


def create_access_token(client_id: str, expires_minutes: int = DEFAULT_EXPIRE_MINUTES) -> str:
    """Create a signed JWT access token for the given client."""
    expire = datetime.now(UTC) + timedelta(minutes=expires_minutes)
    payload = {"sub": client_id, "exp": expire}
    return jwt.encode(payload, _secret_key(), algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""
    return jwt.decode(token, _secret_key(), algorithms=[ALGORITHM])

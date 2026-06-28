"""Password hashing and validation utilities."""

import hashlib
import re
import secrets

PASSWORD_MIN_LENGTH = 6
PASSWORD_PATTERN = re.compile(r"^(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).+$")


def validate_password(password: str) -> str | None:
    """Return an error message when the password is invalid."""
    if len(password) < PASSWORD_MIN_LENGTH:
        return (
            "Password must be at least 6 characters and include numbers and special characters"
        )
    if not PASSWORD_PATTERN.match(password):
        return (
            "Password must be at least 6 characters and include numbers and special characters"
        )
    return None


def hash_password(password: str) -> str:
    """Hash a password with a random salt."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored hash."""
    salt, hashed = stored_hash.split(":", 1)
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest() == hashed

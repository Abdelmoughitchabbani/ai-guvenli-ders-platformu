"""Environment-configured administrator authentication for the API."""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from getpass import getpass
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


PASSWORD_HASH_SCHEME = "pbkdf2_sha256"
PASSWORD_HASH_ITERATIONS = 600_000
MIN_PASSWORD_HASH_ITERATIONS = 100_000
MAX_PASSWORD_HASH_ITERATIONS = 2_000_000
TOKEN_TTL_SECONDS = 8 * 60 * 60
bearer_scheme = HTTPBearer(auto_error=False)


class AuthConfigurationError(ValueError):
    """Raised when required administrator settings are missing or invalid."""


def hash_password(password: str) -> str:
    """Create a salted PBKDF2 password hash for APP_ADMIN_PASSWORD_HASH."""
    if len(password) < 14:
        raise ValueError("Choose an administrator password with at least 14 characters.")
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_HASH_ITERATIONS
    )
    return "$".join(
        (
            PASSWORD_HASH_SCHEME,
            str(PASSWORD_HASH_ITERATIONS),
            salt.hex(),
            digest.hex(),
        )
    )


def _read_admin_settings() -> tuple[str, str, int, bytes, bytes]:
    username = os.getenv("APP_ADMIN_USERNAME", "").strip()
    encoded_hash = os.getenv("APP_ADMIN_PASSWORD_HASH", "")
    session_secret = os.getenv("APP_SESSION_SECRET", "")
    if not username or not encoded_hash or len(session_secret) < 32:
        raise AuthConfigurationError("Administrator authentication is not configured.")

    try:
        scheme, iteration_text, salt_text, digest_text = encoded_hash.split("$", 3)
        iterations = int(iteration_text)
        salt = bytes.fromhex(salt_text)
        expected_digest = bytes.fromhex(digest_text)
        if (
            scheme != PASSWORD_HASH_SCHEME
            or not MIN_PASSWORD_HASH_ITERATIONS <= iterations <= MAX_PASSWORD_HASH_ITERATIONS
            or len(salt) < 16
            or len(expected_digest) != hashlib.sha256().digest_size
        ):
            raise ValueError
    except (ValueError, TypeError):
        raise AuthConfigurationError("Administrator authentication is not configured.") from None

    return username, session_secret, iterations, salt, expected_digest


def _b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_access_token(username: str, session_secret: str) -> str:
    now = int(time.time())
    payload = _b64url_encode(
        json.dumps(
            {"sub": username, "role": "admin", "iat": now, "exp": now + TOKEN_TTL_SECONDS},
            separators=(",", ":"),
        ).encode("utf-8")
    )
    signature = hmac.new(
        session_secret.encode("utf-8"), payload.encode("ascii"), hashlib.sha256
    ).digest()
    return f"{payload}.{_b64url_encode(signature)}"


def authenticate_admin(username: str, password: str) -> str:
    """Check configured administrator credentials and return a signed session."""
    configured_username, session_secret, iterations, salt, expected_digest = (
        _read_admin_settings()
    )
    supplied_digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations
    )
    username_matches = hmac.compare_digest(
        username.encode("utf-8"), configured_username.encode("utf-8")
    )
    password_matches = hmac.compare_digest(supplied_digest, expected_digest)
    if not (username_matches and password_matches):
        raise PermissionError("Invalid administrator credentials.")
    return create_access_token(configured_username, session_secret)


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="جلسة الدخول غير صالحة أو انتهت. سجّل الدخول مجددًا.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, str]:
    """Validate a signed session and require the administrator role."""
    try:
        username, session_secret, _, _, _ = _read_admin_settings()
    except AuthConfigurationError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="لم يتم إعداد دخول الإدارة على الخادم.",
        ) from None

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized()

    try:
        payload_part, signature_part = credentials.credentials.split(".", 1)
        supplied_signature = _b64url_decode(signature_part)
        expected_signature = hmac.new(
            session_secret.encode("utf-8"), payload_part.encode("ascii"), hashlib.sha256
        ).digest()
        if not hmac.compare_digest(supplied_signature, expected_signature):
            raise ValueError
        payload: dict[str, Any] = json.loads(_b64url_decode(payload_part))
        issued_at = int(payload["iat"])
        expires_at = int(payload["exp"])
        now = int(time.time())
        if (
            payload.get("role") != "admin"
            or not hmac.compare_digest(
                str(payload.get("sub", "")).encode("utf-8"), username.encode("utf-8")
            )
            or issued_at > now + 60
            or expires_at <= now
            or expires_at - issued_at > TOKEN_TTL_SECONDS
        ):
            raise ValueError
    except (ValueError, TypeError, KeyError, UnicodeDecodeError, json.JSONDecodeError):
        raise _unauthorized() from None

    return {"username": username, "role": "admin"}


if __name__ == "__main__":
    print("Paste this value into APP_ADMIN_PASSWORD_HASH in your local environment:")
    print(hash_password(getpass("New administrator password (14+ characters): ")))

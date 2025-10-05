from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlmodel import Session

from config import settings
from db import get_session
from models import User

http_bearer = HTTPBearer(auto_error=False)


class _AuthError(HTTPException):
    """Customised HTTP exception for authentication failures."""

    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True when the provided password matches the stored bcrypt hash."""

    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    """Hash the provided password using bcrypt with a randomly generated salt."""

    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(*, subject: int, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT using the configured algorithm and expiry."""

    expire_delta = expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    expire = datetime.now(timezone.utc) + expire_delta
    payload = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


@lru_cache(maxsize=128)
def _decode_access_token(token: str) -> dict:
    """Decode and cache JWT payloads to avoid repeated signature checks in a request."""

    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    session: Session = Depends(get_session),
) -> User:
    """Retrieve the authenticated user based on the Authorization header."""

    if not credentials:
        raise _AuthError("Not authenticated")

    token = credentials.credentials
    try:
        payload = _decode_access_token(token)
        subject = payload.get("sub")
        if subject is None:
            raise _AuthError("Invalid token payload")
        user_id = int(subject)
    except (JWTError, ValueError):
        raise _AuthError("Invalid token") from None

    user = session.get(User, user_id)
    if not user:
        raise _AuthError("User not found")

    return user

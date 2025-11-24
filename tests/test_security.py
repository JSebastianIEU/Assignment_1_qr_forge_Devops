import asyncio
from datetime import timedelta

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import SQLModel, Session

from core.security import create_access_token, get_current_user, get_password_hash, verify_password
from db import get_engine
from models import User


@pytest.fixture()
def memory_session():
    engine = get_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


def test_password_hash_roundtrip() -> None:
    raw = "supersafepass"
    hashed = get_password_hash(raw)
    assert hashed != raw
    assert verify_password(raw, hashed)
    assert not verify_password("wrong", hashed)


def test_create_access_token_contains_subject(memory_session: Session) -> None:
    user = User(email="jwt@example.com", full_name="", hashed_password=get_password_hash("password123"))
    memory_session.add(user)
    memory_session.commit()
    memory_session.refresh(user)

    token = create_access_token(subject=user.id, expires_delta=timedelta(minutes=5))
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    resolved_user = asyncio.run(get_current_user(credentials, memory_session))
    assert resolved_user.id == user.id


def test_get_current_user_invalid_token(memory_session: Session) -> None:
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="not-a-jwt")
    with pytest.raises(HTTPException):
        asyncio.run(get_current_user(credentials, memory_session))

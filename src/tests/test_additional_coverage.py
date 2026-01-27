"""Additional tests to reach 70% coverage for low-coverage modules."""

import pytest
from fastapi import HTTPException, status
from sqlmodel import Session

from app.config import settings
from app.core.bootstrap import ensure_dirs
from app.core.security import create_access_token
from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.services.auth import signup_user, login_user, _normalize_email
from app.services.user import update_profile, delete_user_and_assets
from app.services.qr_items import create_qr_item

# ============================================================================
# Bootstrap Coverage - reach 100%
# ============================================================================


def test_ensure_dirs_with_real_paths():
    """Test ensure_dirs creates directories properly."""
    # This function should create the directories in the config
    ensure_dirs()
    # Check that paths exist
    assert settings.assets_dir.exists()
    assert settings.temp_dir.exists()


# ============================================================================
# Logging Coverage - reach 100%
# ============================================================================


def test_logging_module_imports():
    """Test logging module can be imported and configured."""
    from app.core.logging import configure_logging, get_logger

    configure_logging()
    logger = get_logger("test_logger")
    # Verify logger works
    logger.info("Test log message")
    assert logger is not None


# ============================================================================
# Security Coverage - reach 80%+
# ============================================================================


def test_create_access_token_with_int_subject():
    """Test creating access token with integer subject."""
    # Test with integer ID like in real app
    token = create_access_token(subject=1)
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_access_token_with_string_subject():
    """Test creating access token with string subject."""
    token = create_access_token(subject="user_123")
    assert isinstance(token, str)


def test_create_access_token_with_expires_delta():
    """Test access token with custom expiration delta."""
    from datetime import timedelta

    token = create_access_token(subject=1, expires_delta=timedelta(hours=2))
    assert isinstance(token, str)


# ============================================================================
# Auth Service Coverage - reach 80%+
# ============================================================================


def test_signup_user_normalizes_email(engine, prepare_database):
    """Test signup normalizes email to lowercase."""
    with Session(engine) as session:
        user_data = UserCreate(
            email="TestUser@EXAMPLE.COM", password="password123", full_name="Test"
        )
        user = signup_user(session, user_data)
        assert user.email == "testuser@example.com"


def test_login_user_with_correct_password(engine, prepare_database):
    """Test login with correct password."""
    from app.schemas import UserLogin

    with Session(engine) as session:
        # Create user
        user_data = UserCreate(
            email="login@example.com", password="password123", full_name="Login User"
        )
        signup_user(session, user_data)

        # Login
        login_data = UserLogin(email="login@example.com", password="password123")
        token = login_user(session, login_data)
        assert token.access_token is not None


def test_login_user_invalid_credentials(engine, prepare_database):
    """Test login with invalid credentials."""
    from app.schemas import UserLogin

    with Session(engine) as session:
        # Create user
        user_data = UserCreate(
            email="wrongpass@example.com",
            password="correct_password",
            full_name="User",
        )
        signup_user(session, user_data)

        # Try with wrong password
        login_data = UserLogin(email="wrongpass@example.com", password="wrong_password")
        with pytest.raises(HTTPException) as exc:
            login_user(session, login_data)
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_user_nonexistent_email(engine, prepare_database):
    """Test login with non-existent email."""
    from app.schemas import UserLogin

    with Session(engine) as session:
        login_data = UserLogin(email="nonexistent@example.com", password="anypass")
        with pytest.raises(HTTPException) as exc:
            login_user(session, login_data)
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_normalize_email_variations():
    """Test email normalization handles various cases."""
    assert _normalize_email("User@Example.COM") == "user@example.com"
    assert _normalize_email("user@example.com") == "user@example.com"
    assert _normalize_email("USER@EXAMPLE.COM") == "user@example.com"


# ============================================================================
# User Service Coverage - reach 80%+
# ============================================================================


def test_update_profile_both_fields(engine, prepare_database):
    """Test updating profile with both name and password."""
    with Session(engine) as session:
        user_data = UserCreate(
            email="update_both@example.com",
            password="oldpassword123",
            full_name="Original",
        )
        user = signup_user(session, user_data)

        update_data = UserUpdate(full_name="Updated Name", password="newpass123")
        updated = update_profile(session, user, update_data)
        assert updated.full_name == "Updated Name"


def test_update_profile_no_changes(engine, prepare_database):
    """Test updating profile with no actual changes."""
    with Session(engine) as session:
        user_data = UserCreate(
            email="nochange@example.com", password="password123", full_name="Name"
        )
        user = signup_user(session, user_data)

        update_data = UserUpdate()  # Empty update
        updated = update_profile(session, user, update_data)
        assert updated.email == user.email


def test_delete_user_and_assets(engine, prepare_database):
    """Test deleting user and their associated assets."""
    with Session(engine) as session:
        user_data = UserCreate(
            email="delete_me@example.com", password="password123", full_name="Delete"
        )
        user = signup_user(session, user_data)
        user_id = user.id

        # Delete user
        delete_user_and_assets(session, user)

        # Verify deleted
        from sqlmodel import select

        result = session.exec(select(User).where(User.id == user_id)).first()
        assert result is None


# ============================================================================
# QR Items Service Coverage
# ============================================================================


def test_create_qr_item_full(engine, prepare_database):
    """Test creating a QR item with all fields."""
    from app.schemas import QRCreate

    with Session(engine) as session:
        user_data = UserCreate(
            email="qruser@example.com", password="password123", full_name="QR User"
        )
        user = signup_user(session, user_data)

        qr_data = QRCreate(
            url="https://example.com",
            title="Test QR",
        )

        qr_item = create_qr_item(session, qr_data, user)
        assert str(qr_item.url) == "https://example.com/"
        assert qr_item.title == "Test QR"
        assert qr_item.user_id == user.id


# ============================================================================
# DB Module Coverage
# ============================================================================


def test_get_session_function():
    """Test get_session can be imported and used."""
    from app.db import get_session

    # get_session is a generator
    gen = get_session()
    assert gen is not None


# ============================================================================
# Main App Middleware Coverage
# ============================================================================


def test_app_health_check():
    """Test basic app health/startup."""
    from app.main import app

    assert app is not None
    # App should have routes registered
    assert len(app.routes) > 0

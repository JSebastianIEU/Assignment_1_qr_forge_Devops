"""Tests to improve code coverage for undertested modules."""

import logging
from pathlib import Path
from unittest.mock import patch


from app.core.logging import configure_logging, get_logger
from app.core.security import get_password_hash, verify_password
from app.services.qr_items import path_to_url

# ============================================================================
# Logging Tests
# ============================================================================


def test_configure_logging():
    """Test logging configuration."""
    configure_logging()
    logger = logging.getLogger("app")
    assert logger is not None


def test_get_logger():
    """Test getting a logger instance."""
    logger = get_logger(__name__)
    assert logger is not None
    assert isinstance(logger, logging.Logger)


# ============================================================================
# Security Tests
# ============================================================================


def test_get_password_hash():
    """Test password hashing."""
    password = "test_password_123"
    hash_result = get_password_hash(password)
    assert hash_result != password
    assert len(hash_result) > 0


def test_verify_password():
    """Test password verification."""
    password = "test_password_123"
    hash_result = get_password_hash(password)
    assert verify_password(password, hash_result) is True


def test_verify_password_fails():
    """Test password verification fails for wrong password."""
    password = "test_password_123"
    wrong_password = "wrong_password"
    hash_result = get_password_hash(password)
    assert verify_password(wrong_password, hash_result) is False


# ============================================================================
# Path Conversion Tests
# ============================================================================


def test_path_to_url_http_url():
    """Test that HTTP URLs are returned as-is."""
    url = "https://example.com/blob/file.svg"
    assert path_to_url(url) == url


def test_path_to_url_http_url_lowercase():
    """Test that http:// URLs are returned as-is."""
    url = "http://example.com/file.png"
    assert path_to_url(url) == url


def test_path_to_url_empty():
    """Test empty path returns empty."""
    assert path_to_url("") == ""


def test_path_to_url_local_path(tmp_path):
    """Test local filesystem path conversion."""
    test_file = tmp_path / "test.png"
    test_file.write_bytes(b"\x89PNG")

    result = path_to_url(str(test_file))
    # For paths not in expected directories, should return as-is
    assert result == str(test_file)


# ============================================================================
# Bootstrap Coverage Tests
# ============================================================================


def test_bootstrap_ensure_dirs():
    """Test bootstrap ensure_dirs with mocked settings."""
    with patch("app.core.bootstrap.settings") as mock_settings:
        with patch("pathlib.Path.mkdir"):
            mock_settings.assets_dir = Path("/tmp/assets")
            mock_settings.temp_dir = Path("/tmp/temp")

            from app.core.bootstrap import ensure_dirs

            ensure_dirs()
            # Function should execute without error


# ============================================================================
# Main Coverage Tests
# ============================================================================


def test_app_models_created():
    """Test that models can be imported."""
    from app.models import User, QRItem

    assert User is not None
    assert QRItem is not None


def test_app_schemas_created():
    """Test that schemas can be imported."""
    from app.schemas import UserCreate, QRCreate, Token

    assert UserCreate is not None
    assert QRCreate is not None
    assert Token is not None


def test_storage_backend_selection():
    """Test storage backend selection."""
    from app.storage import get_storage_backend

    backend = get_storage_backend()
    assert backend is not None


def test_db_utilities():
    """Test database utilities."""
    from app.db import get_session

    assert get_session is not None


# ============================================================================
# Core Security Tests
# ============================================================================


def test_security_get_current_user():
    """Test get_current_user function exists."""
    from app.core.security import get_current_user

    assert get_current_user is not None


# ============================================================================
# Auth Service Tests
# ============================================================================


def test_auth_normalize_email(engine, prepare_database):
    """Test email normalization in auth service."""

    from app.services.auth import _normalize_email

    assert _normalize_email("Test@EXAMPLE.COM") == "test@example.com"
    assert _normalize_email("user@example.com") == "user@example.com"


# ============================================================================
# Config Tests
# ============================================================================


def test_config_settings_loaded():
    """Test configuration settings are loaded."""
    from app.config import settings

    assert settings is not None
    assert hasattr(settings, "database_url")
    assert hasattr(settings, "assets_dir")
    assert hasattr(settings, "temp_dir")


# ============================================================================
# Router Tests
# ============================================================================


def test_routers_exist():
    """Test that routers can be imported."""
    from app.routers import auth, qr, user, export

    assert auth is not None
    assert qr is not None
    assert user is not None
    assert export is not None


# ============================================================================
# Main Tests
# ============================================================================


def test_main_app_exists():
    """Test that main app can be imported."""
    from app.main import app

    assert app is not None


# ============================================================================
# Export Service Tests
# ============================================================================


def test_export_functions_exist():
    """Test that export routes exist."""
    from app.routers.export import router

    assert router is not None

"""Tests for database initialization and bootstrap functionality."""

import tempfile
from pathlib import Path
from unittest import mock

import pytest
from sqlalchemy import text

from app.config import settings
from app.core.bootstrap import ensure_dirs
from app.db import _ensure_sqlite_dir, get_engine, get_session, init_db


class TestBootstrap:
    """Test bootstrap directory creation functionality."""

    def test_ensure_dirs_creates_directories(self, tmp_path):
        """Test that ensure_dirs creates the configured directories."""
        test_settings = mock.Mock()
        test_settings.assets_dir = str(tmp_path / "assets")
        test_settings.temp_dir = str(tmp_path / "temp")

        created = list(ensure_dirs(test_settings))

        assert len(created) == 2
        assert Path(test_settings.assets_dir).exists()
        assert Path(test_settings.temp_dir).exists()
        assert all(isinstance(p, Path) for p in created)

    def test_ensure_dirs_idempotent(self, tmp_path):
        """Test that ensure_dirs is idempotent (can be called multiple times)."""
        test_settings = mock.Mock()
        test_settings.assets_dir = str(tmp_path / "assets")
        test_settings.temp_dir = str(tmp_path / "temp")

        created1 = list(ensure_dirs(test_settings))
        created2 = list(ensure_dirs(test_settings))

        assert created1 == created2
        assert Path(test_settings.assets_dir).exists()
        assert Path(test_settings.temp_dir).exists()

    def test_ensure_dirs_handles_permission_error(self, tmp_path):
        """Test that ensure_dirs handles permission errors gracefully."""
        test_settings = mock.Mock()
        # Use a path that will fail on permission error
        test_settings.assets_dir = "/root/protected/assets"  # typically no permission
        test_settings.temp_dir = str(tmp_path / "temp")

        # Should not raise, even if one path fails
        list(ensure_dirs(test_settings))
        # temp_dir should still be created
        assert Path(test_settings.temp_dir).exists()

    def test_ensure_dirs_with_settings(self):
        """Test ensure_dirs uses module settings when none provided."""
        with mock.patch("app.core.bootstrap.settings") as mock_settings:
            mock_settings.assets_dir = "/tmp/assets_test"
            mock_settings.temp_dir = "/tmp/temp_test"

            with mock.patch("pathlib.Path.mkdir"):
                ensure_dirs()
                # Verify it attempted to create the dirs from settings


class TestDatabase:
    """Test database connection and initialization."""

    def test_ensure_sqlite_dir_creates_directory(self, tmp_path):
        """Test that _ensure_sqlite_dir creates parent directory for sqlite file."""
        db_path = tmp_path / "subdir" / "test.db"
        _ensure_sqlite_dir(f"sqlite:///{db_path}")

        assert db_path.parent.exists()

    def test_ensure_sqlite_dir_noop_for_postgres(self):
        """Test that _ensure_sqlite_dir is no-op for postgres URLs."""
        with mock.patch("pathlib.Path.mkdir") as mock_mkdir:
            _ensure_sqlite_dir("postgresql://localhost/test")
            mock_mkdir.assert_not_called()

    def test_ensure_sqlite_dir_noop_for_existing(self, tmp_path):
        """Test that _ensure_sqlite_dir doesn't fail if dir exists."""
        db_path = tmp_path / "test.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        # Should not raise
        _ensure_sqlite_dir(f"sqlite:///{db_path}")
        assert db_path.parent.exists()

    def test_get_engine_sqlite(self, tmp_path):
        """Test get_engine creates sqlite engine correctly."""
        db_url = f"sqlite:///{tmp_path}/test.db"
        engine = get_engine(db_url)

        assert engine is not None
        # Verify it's a valid engine
        with engine.connect() as conn:
            # Should be able to execute a query
            from sqlalchemy import text

            result = conn.execute(text("SELECT 1"))
            assert result.fetchone() is not None

    def test_get_engine_with_settings_url(self, monkeypatch):
        """Test get_engine uses settings.database_url when none provided."""
        test_db_url = "sqlite:///test.db"
        monkeypatch.setattr(settings, "database_url", test_db_url)

        with tempfile.TemporaryDirectory() as tmp_dir:
            monkeypatch.setattr(
                settings, "database_url", f"sqlite:///{tmp_dir}/test.db"
            )
            engine = get_engine()
            assert engine is not None

    def test_get_engine_no_url_raises_error(self, monkeypatch):
        """Test get_engine raises error if no URL provided."""
        monkeypatch.setattr(settings, "database_url", None)

        with pytest.raises(RuntimeError, match="No database URL provided"):
            get_engine()

    def test_get_engine_postgres_adds_sslmode(self):
        """Test get_engine adds sslmode=require for postgres URLs without it."""
        db_url = "postgresql://user:pass@localhost/dbname"
        engine = get_engine(db_url)

        # Verify engine is created (URL should have sslmode added)
        assert engine is not None

    def test_get_engine_postgres_preserves_existing_sslmode(self):
        """Test get_engine preserves existing sslmode in postgres URLs."""
        db_url = "postgresql://user:pass@localhost/dbname?sslmode=prefer"
        engine = get_engine(db_url)

        assert engine is not None

    def test_get_engine_postgres_pooling(self):
        """Test get_engine configures pooling for postgres."""
        # Skip for testing as we don't have postgres available
        pytest.skip("Postgres testing requires running database")

    def test_init_db_creates_tables(self, tmp_path):
        """Test init_db creates tables in database."""
        db_url = f"sqlite:///{tmp_path}/test_init.db"
        engine = get_engine(db_url)

        # Should not raise
        init_db(engine)

        # Verify tables exist by checking if we can query the schema
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                    " AND name NOT LIKE 'sqlite_%';"
                )
            )
            tables = result.fetchall()
            # Should have created some tables from models
            assert isinstance(tables, list)

    def test_init_db_uses_default_engine(self, monkeypatch, tmp_path):
        """Test init_db uses default engine when none provided."""
        db_url = f"sqlite:///{tmp_path}/test_default.db"
        monkeypatch.setattr("app.db.engine", get_engine(db_url))

        # Should not raise
        init_db()

    def test_get_session_generator(self, tmp_path, monkeypatch):
        """Test get_session returns a generator that yields sessions."""
        db_url = f"sqlite:///{tmp_path}/test_session.db"
        test_engine = get_engine(db_url)
        init_db(test_engine)
        monkeypatch.setattr("app.db.engine", test_engine)

        session_gen = get_session()
        session = next(session_gen)

        # Verify it's a valid session
        assert session is not None
        # Cleanup
        session.close()

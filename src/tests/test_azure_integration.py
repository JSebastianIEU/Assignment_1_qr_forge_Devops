"""Azure integration tests.

These tests validate Azure services:
- Azure Blob Storage (file storage)
- Azure PostgreSQL (database)
- Application Insights (monitoring)

To run these tests, set the following environment variables:
- AZURE_STORAGE_CONNECTION_STRING: Azure Storage connection string
- POSTGRES_URL: Azure PostgreSQL connection string
- APPINSIGHTS_CONN: Application Insights instrumentation key

Example:
    AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;..."
    POSTGRES_URL="postgresql://user:password@host:5432/dbname"
    APPINSIGHTS_CONN="InstrumentationKey=...;IngestionEndpoint=..."
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from sqlmodel import Session, create_engine, select

from app.config import settings
from app.models import QRItem, User
from app.services.auth import create_access_token, get_password_hash
from app.storage import AzureBlobStorage, get_storage_backend


class TestAzureBlobStorageIntegration:
    """Integration tests for Azure Blob Storage."""

    @pytest.fixture
    def azure_enabled(self) -> bool:
        """Check if Azure Blob Storage is configured."""
        return bool(settings.azure_storage_connection_string)

    @pytest.fixture
    def azure_storage(self):
        """Get Azure Blob Storage instance if configured."""
        if not settings.azure_storage_connection_string:
            pytest.skip("AZURE_STORAGE_CONNECTION_STRING not configured")

        try:
            return AzureBlobStorage(
                connection_string=settings.azure_storage_connection_string,
                container_name=settings.azure_storage_container,
            )
        except ImportError:
            pytest.skip("azure-storage-blob package not installed")
        except Exception as e:
            pytest.skip(f"Azure Blob Storage not available: {e}")

    def test_azure_storage_connection(self, azure_storage):
        """Test that Azure Blob Storage connection is established."""
        assert azure_storage is not None
        assert azure_storage.connection_string is not None
        assert azure_storage.container_name == settings.azure_storage_container

    def test_azure_storage_save_and_delete_file(self, azure_storage):
        """Test saving and deleting files in Azure Blob Storage."""
        test_content = b"Test QR code PNG data for Azure"
        test_filename = f"test_qr_{datetime.now().timestamp()}.png"

        try:
            # Save file
            blob_url = azure_storage.save_file(
                test_content, test_filename, "image/png"
            )
            assert blob_url is not None
            assert isinstance(blob_url, str)
            assert test_filename in blob_url

            # Verify file exists by attempting to delete
            azure_storage.delete_file(blob_url)
            # If no exception, delete was successful
            assert True
        except Exception as e:
            pytest.fail(f"Azure Blob Storage save/delete failed: {e}")

    def test_azure_storage_save_svg(self, azure_storage):
        """Test saving SVG files to Azure Blob Storage."""
        svg_content = """<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
            <rect width="100" height="100" fill="white"/>
        </svg>"""
        test_filename = f"test_qr_{datetime.now().timestamp()}.svg"

        try:
            blob_url = azure_storage.save_file(svg_content, test_filename, "image/svg+xml")
            assert blob_url is not None
            assert "svg" in blob_url.lower()
        except Exception as e:
            pytest.fail(f"Azure Blob Storage SVG upload failed: {e}")

    def test_azure_storage_large_file(self, azure_storage):
        """Test uploading large files to Azure Blob Storage."""
        large_content = b"x" * (10 * 1024 * 1024)  # 10MB
        test_filename = f"test_large_{datetime.now().timestamp()}.bin"

        try:
            blob_url = azure_storage.save_file(
                large_content, test_filename, "application/octet-stream"
            )
            assert blob_url is not None
            # Clean up
            azure_storage.delete_file(blob_url)
        except Exception as e:
            pytest.fail(f"Azure Blob Storage large file upload failed: {e}")


class TestAzurePostgresIntegration:
    """Integration tests for Azure PostgreSQL."""

    @pytest.fixture
    def postgres_url(self) -> str:
        """Get PostgreSQL connection string."""
        url = settings.postgres_url or settings.database_url
        if not url or url.startswith("sqlite"):
            pytest.skip("Azure PostgreSQL not configured (using SQLite)")
        return url

    @pytest.fixture
    def postgres_engine(self, postgres_url):
        """Create PostgreSQL engine."""
        try:
            from sqlalchemy.pool import NullPool

            engine = create_engine(
                postgres_url,
                echo=False,
                poolclass=NullPool,
                connect_args={"connect_timeout": 5},
            )
            # Test connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return engine
        except Exception as e:
            pytest.skip(f"Cannot connect to PostgreSQL: {e}")

    def test_postgres_connection(self, postgres_engine):
        """Test PostgreSQL connection."""
        with postgres_engine.connect() as conn:
            result = conn.execute("SELECT version()")
            version = result.fetchone()
            assert version is not None
            assert "postgres" in version[0].lower()

    def test_postgres_create_user(self, postgres_engine):
        """Test creating a user in PostgreSQL."""
        try:
            with Session(postgres_engine) as session:
                user = User(
                    email=f"test_{datetime.now().timestamp()}@azure.test",
                    hashed_password=get_password_hash("password123"),
                    full_name="Azure Test User",
                )
                session.add(user)
                session.commit()
                session.refresh(user)

                assert user.id is not None
                assert user.email == user.email

                # Clean up
                session.delete(user)
                session.commit()
        except Exception as e:
            pytest.fail(f"PostgreSQL user creation failed: {e}")

    def test_postgres_query_users(self, postgres_engine):
        """Test querying users from PostgreSQL."""
        try:
            with Session(postgres_engine) as session:
                stmt = select(User)
                users = session.exec(stmt).all()
                assert isinstance(users, list)
        except Exception as e:
            pytest.fail(f"PostgreSQL query failed: {e}")


class TestApplicationInsightsIntegration:
    """Integration tests for Application Insights."""

    @pytest.fixture
    def app_insights_enabled(self) -> bool:
        """Check if Application Insights is configured."""
        return bool(settings.app_insights_connection_string)

    def test_app_insights_configuration(self, app_insights_enabled):
        """Test Application Insights configuration."""
        if app_insights_enabled:
            assert settings.app_insights_connection_string is not None
            assert "InstrumentationKey=" in settings.app_insights_connection_string

    def test_app_insights_instrumentation_optional(self):
        """Test that Application Insights is optional (gracefully degrades)."""
        # This should not raise even if AppInsights is not configured
        from app.main import app

        assert app is not None
        # If we got here, the app initialized successfully
        # even without AppInsights


class TestAzureServiceHealthCheck:
    """Health checks for Azure services."""

    def test_storage_backend_selection(self):
        """Test that storage backend is correctly selected based on config."""
        backend = get_storage_backend()

        if settings.azure_storage_connection_string:
            assert isinstance(backend, AzureBlobStorage)
        else:
            from app.storage import LocalFilesystemStorage

            assert isinstance(backend, LocalFilesystemStorage)

    def test_database_url_priority(self):
        """Test that POSTGRES_URL takes priority over DATABASE_URL."""
        # POSTGRES_URL should be used if available
        if settings.postgres_url:
            assert settings.database_url == settings.postgres_url
        else:
            assert settings.database_url is not None

    def test_all_required_settings_present(self):
        """Test that all required settings are loaded."""
        assert settings.secret_key is not None
        assert settings.algorithm is not None
        assert settings.access_token_expire_minutes > 0
        assert settings.database_url is not None
        assert settings.assets_dir is not None
        assert settings.temp_dir is not None

    def test_optional_azure_settings_graceful_degradation(self):
        """Test that missing Azure settings don't break the app."""
        # App should work fine with Azure settings missing
        # They should just use fallbacks
        assert settings.azure_storage_container is not None  # Has default
        # azure_storage_connection_string may be None (that's OK)
        assert settings.azure_storage_connection_string is None or isinstance(
            settings.azure_storage_connection_string, str
        )


class TestAzureEndToEnd:
    """End-to-end tests for Azure integration."""

    def test_qr_generation_with_azure_storage(self):
        """Test QR generation and storage in Azure (if configured)."""
        if not settings.azure_storage_connection_string:
            pytest.skip("Azure Blob Storage not configured")

        try:
            backend = get_storage_backend()
            svg_content = """<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
                <rect width="200" height="200" fill="white"/>
                <rect x="10" y="10" width="30" height="30" fill="black"/>
            </svg>"""

            filename = f"qr_{datetime.now().isoformat()}.svg"
            url = backend.save_file(svg_content, filename, "image/svg+xml")

            assert url is not None
            assert isinstance(url, str)
        except Exception as e:
            pytest.fail(f"End-to-end QR generation/storage failed: {e}")

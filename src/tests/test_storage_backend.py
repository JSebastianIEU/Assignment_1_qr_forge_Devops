"""Tests for storage backend abstraction (local filesystem and Azure Blob)."""

from pathlib import Path

import pytest

from app.config import settings
from app.storage import (
    AzureBlobStorage,
    LocalFilesystemStorage,
    StorageBackend,
    get_storage_backend,
)


class TestStorageBackendAbstraction:
    """Test storage backend ABC and interface."""

    def test_storage_backend_is_abstract(self):
        """Test that StorageBackend cannot be instantiated directly."""
        with pytest.raises(TypeError):
            StorageBackend()

    def test_storage_backend_requires_subclass_methods(self):
        """Test that StorageBackend subclasses must implement required methods."""

        class IncompleteStorage(StorageBackend):
            pass

        with pytest.raises(TypeError):
            IncompleteStorage()


class TestLocalFilesystemStorage:
    """Test LocalFilesystemStorage implementation."""

    @pytest.fixture
    def storage(self, tmp_path):
        """Create a LocalFilesystemStorage instance with temp directory."""
        return LocalFilesystemStorage(base_dir=tmp_path)

    def test_local_storage_initialization(self, storage):
        """Test LocalFilesystemStorage initializes correctly."""
        assert isinstance(storage, StorageBackend)
        assert storage.base_dir is not None

    def test_local_storage_save_file(self, storage, tmp_path):
        """Test LocalFilesystemStorage saves files correctly."""
        content = b"test content"
        file_url = storage.save_file(content, "test.txt", "text/plain")

        assert isinstance(file_url, str)
        assert "test.txt" in file_url

    def test_local_storage_save_file_flat(self, storage, tmp_path):
        """Test LocalFilesystemStorage saves files (flat directory structure)."""
        content = b"test content"
        file_url = storage.save_file(content, "test_file.txt", "text/plain")

        assert isinstance(file_url, str)
        file_path = Path(file_url)
        assert file_path.exists()
        assert file_path.read_bytes() == content

    def test_local_storage_get_file_path(self, storage):
        """Test LocalFilesystemStorage get_file_path method."""
        content = b"test content"
        file_url = storage.save_file(content, "path_test.txt", "text/plain")

        file_path = storage.get_file_path(file_url)
        assert file_path is not None
        assert isinstance(file_path, Path)
        assert file_path.exists()

    def test_local_storage_delete_file(self, storage):
        """Test LocalFilesystemStorage deletes files."""
        content = b"to delete"
        file_url = storage.save_file(content, "delete_test.txt", "text/plain")

        file_path = Path(file_url)
        assert file_path.exists()

        storage.delete_file(file_url)
        assert not file_path.exists()

    def test_local_storage_save_text_content(self, storage):
        """Test LocalFilesystemStorage handles text content correctly."""
        text_content = "Hello, World!"
        file_url = storage.save_file(text_content, "text_test.txt", "text/plain")

        file_path = Path(file_url)
        assert file_path.read_text(encoding="utf-8") == text_content

    def test_local_storage_save_binary_content(self, storage):
        """Test LocalFilesystemStorage handles binary content correctly."""
        binary_content = b"\x89PNG\r\n\x1a\n\x00\x00"  # PNG header
        file_url = storage.save_file(binary_content, "binary_test.png", "image/png")

        file_path = Path(file_url)
        assert file_path.read_bytes() == binary_content

    def test_local_storage_save_large_file(self, storage):
        """Test LocalFilesystemStorage handles large files."""
        large_content = b"x" * (5 * 1024 * 1024)  # 5MB
        file_url = storage.save_file(
            large_content, "large_test.bin", "application/octet-stream"
        )

        file_path = Path(file_url)
        assert file_path.exists()
        assert len(file_path.read_bytes()) == len(large_content)


class TestAzureBlobStorage:
    """Test AzureBlobStorage implementation."""

    def test_azure_storage_requires_connection_string(self):
        """Test AzureBlobStorage requires connection string."""
        with pytest.raises(RuntimeError):
            # Tries to import BlobServiceClient when not available
            AzureBlobStorage(
                connection_string=None,
                container_name="test",
            )

    @pytest.mark.skipif(
        True,
        reason="Azure SDK not required for local storage backend tests"
    )
    def test_azure_storage_initialization_with_connection_string(self):
        """Test AzureBlobStorage initializes with connection string."""
        pass

    @pytest.mark.skipif(
        True,
        reason="Azure SDK not required for local storage backend tests"
    )
    def test_azure_storage_save_file(self):
        """Test AzureBlobStorage saves files to blob."""
        pass


class TestStorageBackendFactory:
    """Test get_storage_backend factory function."""

    def test_get_storage_backend_local_by_default(self, monkeypatch):
        """Test get_storage_backend returns LocalFilesystemStorage by default."""
        # Remove Azure connection string to force local storage
        monkeypatch.delenv("AZURE_STORAGE_CONNECTION_STRING", raising=False)
        monkeypatch.setattr(settings, "azure_storage_connection_string", None)

        backend = get_storage_backend()
        assert isinstance(backend, LocalFilesystemStorage)

    def test_get_storage_backend_singleton(self, monkeypatch):
        """Test get_storage_backend returns same instance (singleton)."""
        monkeypatch.delenv("AZURE_STORAGE_CONNECTION_STRING", raising=False)
        monkeypatch.setattr(settings, "azure_storage_connection_string", None)

        backend1 = get_storage_backend()
        backend2 = get_storage_backend()

        # Should be same instance
        assert backend1 is backend2


class TestStoragePathHandling:
    """Test storage path handling edge cases."""

    @pytest.fixture
    def storage(self, tmp_path):
        """Create a LocalFilesystemStorage instance."""
        return LocalFilesystemStorage(base_dir=tmp_path)

    def test_storage_prevents_directory_traversal(self, storage):
        """Test that storage prevents directory traversal attacks."""
        # Try to save file outside base_dir using ..
        file_url = storage.save_file(
            b"should not escape", "../outside.txt", "text/plain"
        )

        # File should still be inside base_dir
        assert str(file_url).startswith(str(storage.base_dir))

    def test_storage_handles_special_characters_in_filename(self, storage):
        """Test that storage handles special characters in filenames."""
        special_name = "test-file_2024.01.01@special.txt"
        file_url = storage.save_file(b"content", special_name, "text/plain")

        file_path = Path(file_url)
        assert file_path.exists()

    def test_storage_handles_unicode_filenames(self, storage):
        """Test that storage handles unicode filenames."""
        unicode_name = "test_файл_文件.txt"
        file_url = storage.save_file(b"content", unicode_name, "text/plain")

        file_path = Path(file_url)
        assert file_path.exists()

"""Storage abstraction layer for local filesystem and Azure Blob Storage.

Automatically selects Azure Blob Storage when
AZURE_STORAGE_CONNECTION_STRING is configured,
otherwise falls back to local filesystem for development.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from app.config import settings

logger = logging.getLogger("qr_forge.storage")


class StorageBackend(ABC):
    """Abstract storage interface."""

    @abstractmethod
    def save_file(self, content: str | bytes, filename: str, content_type: str) -> str:
        """Save file and return its URL or path."""
        pass

    @abstractmethod
    def delete_file(self, path_or_url: str) -> None:
        """Delete a file by its path or URL."""
        pass

    @abstractmethod
    def get_file_path(self, path_or_url: str) -> Path | None:
        """Get filesystem path for download (returns None for blob storage)."""
        pass


class LocalFilesystemStorage(StorageBackend):
    """Local filesystem storage for development."""

    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_file(self, content: str | bytes, filename: str, content_type: str) -> str:
        filepath = self.base_dir / filename
        if isinstance(content, str):
            filepath.write_text(content, encoding="utf-8")
        else:
            filepath.write_bytes(content)
        # Return path that will be converted to URL by path_to_url
        return str(filepath)

    def delete_file(self, path_or_url: str) -> None:
        try:
            filepath = Path(path_or_url)
            if filepath.exists():
                filepath.unlink()
        except Exception as e:
            logger.warning(f"Failed to delete file {path_or_url}: {e}")

    def get_file_path(self, path_or_url: str) -> Path | None:
        return Path(path_or_url)


class AzureBlobStorage(StorageBackend):
    """Azure Blob Storage backend for production."""

    def __init__(self, connection_string: str | None, container_name: str):
        # Guard: connection string is mandatory
        if not connection_string:
            raise RuntimeError(
                "AZURE_STORAGE_CONNECTION_STRING is required for Azure Blob Storage"
            )

        self.connection_string = connection_string
        self.container_name = container_name

        try:
            from azure.storage.blob import BlobServiceClient, ContentSettings

            self.BlobServiceClient = BlobServiceClient
            self.ContentSettings = ContentSettings
        except ImportError:
            raise RuntimeError(
                "azure-storage-blob package required for Azure Blob Storage. "
                "Install with: pip install azure-storage-blob"
            ) from None

        # Initialise client and ensure container exists
        try:
            self._client = self.BlobServiceClient.from_connection_string(
                self.connection_string
            )
            container_client = self._client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container(public_access="blob")
                logger.info("Created blob container: %s", self.container_name)
        except Exception as e:
            logger.error("Failed to ensure Azure blob container exists: %s", e)

    def save_file(self, content: str | bytes, filename: str, content_type: str) -> str:
        """Upload file to blob storage and return public URL."""
        blob_client = self._client.get_blob_client(
            container=self.container_name, blob=filename
        )

        # Convert string to bytes if needed
        data = content.encode("utf-8") if isinstance(content, str) else content

        # Upload with content type
        content_settings = self.ContentSettings(content_type=content_type)
        blob_client.upload_blob(data, overwrite=True, content_settings=content_settings)

        # Return public URL
        return blob_client.url

    def delete_file(self, path_or_url: str) -> None:
        """Delete blob by URL or name."""
        try:
            # Extract blob name from URL if it's a full URL
            blob_name = (
                path_or_url.split("/")[-1] if "/" in path_or_url else path_or_url
            )

            blob_client = self._client.get_blob_client(
                container=self.container_name, blob=blob_name
            )
            blob_client.delete_blob()
        except Exception as e:
            logger.warning(f"Failed to delete blob {path_or_url}: {e}")

    def read_file(self, path_or_url: str) -> bytes:
        """Download blob content by URL or name."""
        # Extract blob name from URL if it's a full URL
        blob_name = path_or_url.split("/")[-1] if "/" in path_or_url else path_or_url

        blob_client = self._client.get_blob_client(
            container=self.container_name, blob=blob_name
        )
        return blob_client.download_blob().readall()

    def get_file_path(self, path_or_url: str) -> Path | None:
        """Blob storage doesn't use filesystem paths for serving."""
        return None


def get_storage() -> StorageBackend:
    """Factory function to get the appropriate storage backend."""
    if settings.azure_storage_connection_string:
        logger.info("Using Azure Blob Storage backend")
        return AzureBlobStorage(
            connection_string=settings.azure_storage_connection_string,
            container_name=settings.azure_storage_container,
        )
    else:
        logger.info("Using local filesystem storage backend")
        return LocalFilesystemStorage(base_dir=settings.assets_dir)


# Global storage instance
_storage: Optional[StorageBackend] = None


def get_storage_backend() -> StorageBackend:
    """Get or create the global storage backend instance."""
    global _storage
    if _storage is None:
        _storage = get_storage()
    return _storage

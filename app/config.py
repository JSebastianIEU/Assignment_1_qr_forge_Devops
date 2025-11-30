"""Application configuration.

Centralises environment-driven settings. Supports Key Vault-style references
in environment variables (the App Service Key Vault reference syntax is
parsed at runtime by `app.py` which will attempt to resolve secrets from
Azure Key Vault when available).
"""

import logging
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("qr_forge.config")
BASE_DIR = Path(__file__).resolve().parent
# Writable defaults under the user's home (works locally and in Azure)
HOME_DIR = Path.home()


@dataclass
class Settings:
    """Runtime configuration pulled from environment variables.

    This dataclass centralises environment-driven configuration. It prefers
    `POSTGRES_URL` (for production) and falls back to `DATABASE_URL` which
    may point to a local sqlite file for development and tests.
    """

    secret_key: str = field(
        default_factory=lambda: os.getenv("SECRET_KEY", "change-me-in-env")
    )
    access_token_expire_minutes: int = field(
        default_factory=lambda: int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "720"))
    )
    algorithm: str = field(default_factory=lambda: os.getenv("ALGORITHM", "HS256"))
    postgres_url: Optional[str] = field(
        default_factory=lambda: os.getenv("POSTGRES_URL")
    )
    database_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL", f"sqlite:///{(HOME_DIR / 'data' / 'qrcodes.db').as_posix()}"
        )
    )
    assets_dir: Path = field(
        default_factory=lambda: Path(
            os.getenv("QR_ASSETS_DIR", str(HOME_DIR / "data" / "qr_assets"))
        )
    )
    temp_dir: Path = field(
        default_factory=lambda: Path(
            os.getenv("QR_TEMP_DIR", str(HOME_DIR / "data" / "qr_temp"))
        )
    )
    # Optional telemetry and observability configuration
    app_insights_connection_string: Optional[str] = field(
        default_factory=lambda: os.getenv("APPINSIGHTS_CONN")
    )

    def __post_init__(self) -> None:
        # Use POSTGRES_URL when available, otherwise DATABASE_URL
        self.database_url = self.postgres_url or self.database_url
        if not self.database_url:
            logger.warning(
                "No database URL configured; application may not function correctly"
            )
        # Normalise paths for downstream usage; directory creation should be
        # performed at application startup by calling `ensure_dirs(settings)`
        self.assets_dir = Path(self.assets_dir)
        self.temp_dir = Path(self.temp_dir)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached Settings instance."""
    return Settings()


settings = get_settings()

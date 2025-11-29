from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    """Runtime configuration pulled from environment variables."""

    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY", "change-me-in-env"))
    access_token_expire_minutes: int = field(
        default_factory=lambda: int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "720"))
    )
    algorithm: str = field(default_factory=lambda: os.getenv("ALGORITHM", "HS256"))
    postgres_url: str | None = field(default_factory=lambda: os.getenv("POSTGRES_URL"))
    database_url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:////home/data/qrcodes.db")
    )
    assets_dir: Path = field(default_factory=lambda: Path(os.getenv("QR_ASSETS_DIR", "/home/site/wwwroot/qr_assets")))
    temp_dir: Path = field(default_factory=lambda: Path(os.getenv("QR_TEMP_DIR", "/home/site/wwwroot/qr_temp")))

    def __post_init__(self) -> None:
        self.database_url = self.postgres_url or self.database_url
        # Normalise paths for downstream usage and ensure directories exist for file writes.
        self.assets_dir = Path(self.assets_dir)
        self.temp_dir = Path(self.temp_dir)
        os.makedirs(self.assets_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

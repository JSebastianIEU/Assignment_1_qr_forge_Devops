from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    """Runtime configuration pulled from environment variables."""

    secret_key: str = field(default_factory=lambda: os.getenv("QR_FORGE_SECRET_KEY", "change-me-in-env"))
    access_token_expire_minutes: int = field(
        default_factory=lambda: int(os.getenv("QR_FORGE_TOKEN_EXPIRE_MINUTES", "720"))
    )
    algorithm: str = field(default_factory=lambda: os.getenv("QR_FORGE_TOKEN_ALG", "HS256"))
    database_url: str = field(default_factory=lambda: os.getenv("QR_FORGE_DATABASE_URL", "sqlite:///qr.db"))
    svg_dir: Path = field(default_factory=lambda: Path(os.getenv("QR_FORGE_SVG_DIR", "generated_svgs")))
    png_dir: Path = field(default_factory=lambda: Path(os.getenv("QR_FORGE_PNG_DIR", "generated_pngs")))

    def __post_init__(self) -> None:
        # Normalise paths for downstream usage.
        self.svg_dir = Path(self.svg_dir)
        self.png_dir = Path(self.png_dir)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

from dataclasses import dataclass
import os


@dataclass
class Settings:
    secret_key: str = os.getenv("QR_FORGE_SECRET_KEY", "change-me-in-env")
    access_token_expire_minutes: int = int(os.getenv("QR_FORGE_TOKEN_EXPIRE_MINUTES", "720"))
    algorithm: str = os.getenv("QR_FORGE_TOKEN_ALG", "HS256")


settings = Settings()

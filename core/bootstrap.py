from pathlib import Path
from typing import Iterable

from config import settings


def ensure_dirs(s=None) -> Iterable[Path]:
    """Ensure asset and temp directories exist. Returns created Path objects.

    If `s` is not provided, use module `settings`.
    """
    s = s or settings
    created = []
    for p in (s.assets_dir, s.temp_dir):
        try:
            Path(p).mkdir(parents=True, exist_ok=True)
            created.append(Path(p))
        except Exception:
            # In some CI/runners writing to the configured path may fail; let
            # the app continue and surface the error elsewhere if needed.
            pass
    return created

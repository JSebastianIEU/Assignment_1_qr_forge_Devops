import pytest

from db import get_engine
from config import settings


def test_get_engine_raises_when_no_url(monkeypatch) -> None:
    # If settings.database_url is empty or None and no database_url is
    # provided, get_engine should raise a RuntimeError.
    monkeypatch.setattr(settings, "database_url", "")
    with pytest.raises(RuntimeError):
        get_engine(None)

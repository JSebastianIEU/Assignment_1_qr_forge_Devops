from pathlib import Path

import pytest
from sqlmodel import SQLModel

from app.db import get_engine
from app.models import User
from app.schemas import QRCreate
import app.services.qr_items as qr_items


def _make_engine_and_create_tables():
    engine = get_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


def test_get_owned_item_not_found_raises_http_exception():
    engine = _make_engine_and_create_tables()
    # Create a persisted user and assert get_owned_item raises HTTPException
    from sqlmodel import Session
    from fastapi import HTTPException

    with Session(engine) as session:
        user = User(email="noone@example.com", full_name="No One", hashed_password="x")
        session.add(user)
        session.commit()
        session.refresh(user)

        with pytest.raises(HTTPException) as exc:
            qr_items.get_owned_item(session, user, 99999)

        assert exc.value.status_code == 404


def test_create_qr_item_propagates_asset_errors(monkeypatch, tmp_path: Path):
    engine = _make_engine_and_create_tables()
    from sqlmodel import Session

    # create a user
    with Session(engine) as session:
        user = User(email="test@example.com", full_name="T", hashed_password="x")
        session.add(user)
        session.commit()
        session.refresh(user)

    payload = QRCreate(
        title="T",
        url="https://example.com",
        foreground_color="#000000",
        background_color="#ffffff",
        size=128,
        padding=4,
        border_radius=0,
    )

    # Monkeypatch generate_qr_assets to raise an OSError (simulate disk full / IO)
    def _boom(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(qr_items, "generate_qr_assets", _boom)

    with Session(engine) as session:
        with pytest.raises(OSError):
            qr_items.create_qr_item(
                session,
                payload,
                user,
                svg_dir=tmp_path / "svgs",
                png_dir=tmp_path / "pngs",
            )

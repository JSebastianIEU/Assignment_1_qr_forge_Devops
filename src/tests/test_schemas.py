import pytest
from pydantic import ValidationError

from app.schemas import QRCreate


def _base_payload() -> dict:
    return {
        "title": "Valid QR",
        "url": "https://example.com",
        "foreground_color": "#123456",
        "background_color": "#ffffff",
        "size": 256,
        "padding": 8,
        "border_radius": 8,
    }


def test_invalid_hex_colors_raise_validation_error() -> None:
    payload = _base_payload()
    payload["foreground_color"] = "gggggg"
    with pytest.raises(ValidationError):
        QRCreate(**payload)

    payload = _base_payload()
    payload["background_color"] = "#12345"
    with pytest.raises(ValidationError):
        QRCreate(**payload)


def test_invalid_url_rejected() -> None:
    payload = _base_payload()
    payload["url"] = "notaurl"
    with pytest.raises(ValidationError):
        QRCreate(**payload)


def test_overlay_text_length_enforced() -> None:
    payload = _base_payload()
    payload["overlay_text"] = "TOO-LONG"
    with pytest.raises(ValidationError):
        QRCreate(**payload)


def test_size_constraints_enforced() -> None:
    payload = _base_payload()
    payload["size"] = 32
    with pytest.raises(ValidationError):
        QRCreate(**payload)

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(index=True, sa_column_kwargs={"unique": True})
    full_name: str = Field(default="")
    hashed_password: str
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class QRItem(SQLModel, table=True):
    __tablename__ = "qr_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    url: str
    foreground_color: str = Field(default="#000000", max_length=7)
    background_color: str = Field(default="#FFFFFF", max_length=7)
    size: int = Field(default=256, ge=64, le=1024)
    padding: int = Field(default=10, ge=0, le=80)
    border_radius: int = Field(default=0, ge=0, le=60)
    overlay_text: Optional[str] = Field(default=None, max_length=4)
    svg_path: str
    png_path: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=utcnow, index=True)
    updated_at: datetime = Field(default_factory=utcnow)

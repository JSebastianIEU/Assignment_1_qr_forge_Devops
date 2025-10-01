from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


HexColor = Annotated[str, Field(pattern=r"^#[0-9a-fA-F]{6}$")]
HexOrTransparent = Annotated[str, Field(pattern=r"^(#[0-9a-fA-F]{6}|transparent)$")]


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "email": "user@example.com",
            "full_name": "Sample User",
            "password": "strongpass123",
        }
    })


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": 1,
            "email": "user@example.com",
            "full_name": "Sample User",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-02T12:00:00Z",
        }
    })


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "email": "user@example.com",
            "password": "strongpass123",
        }
    })


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
        }
    })


class TokenPayload(BaseModel):
    sub: int
    exp: datetime


class QRBase(BaseModel):
    title: str
    url: HttpUrl
    foreground_color: HexColor = "#000000"
    background_color: HexOrTransparent = "#FFFFFF"
    size: int = Field(default=512, ge=128, le=1024)
    padding: int = Field(default=16, ge=0, le=128)
    border_radius: int = Field(default=0, ge=0, le=120)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "title": "Campaign QR",
            "url": "https://example.com",
            "foreground_color": "#1f3a93",
            "background_color": "#ffffff",
            "size": 320,
            "padding": 12,
            "border_radius": 20,
        }
    })


class QRCreate(QRBase):
    pass


class QRPreviewResponse(BaseModel):
    svg_data: str
    png_data: str

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "svg_data": "<svg xmlns=...>",
            "png_data": "iVBORw0KGgoAAAANSUhEUg...",
        }
    })

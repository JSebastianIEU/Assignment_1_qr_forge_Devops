from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl


HexColor = Annotated[str, Field(pattern=r"^#[0-9a-fA-F]{6}$")]
HexOrTransparent = Annotated[str, Field(pattern=r"^(#[0-9a-fA-F]{6}|transparent)$")]


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


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


class QRCreate(QRBase):
    pass


class QRPreviewResponse(BaseModel):
    svg_data: str
    png_data: str

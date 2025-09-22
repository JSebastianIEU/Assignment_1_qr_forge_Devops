from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class QRItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    url: str
    svg_path: str
    created_at: datetime

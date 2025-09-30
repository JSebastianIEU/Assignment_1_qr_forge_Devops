from collections.abc import Generator
from typing import Any, Dict

from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///qr.db"

# sqlite needs this connect arg for threaded servers
connect_args: Dict[str, Any] = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

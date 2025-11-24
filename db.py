from collections.abc import Generator
from typing import Any, Dict, Optional

from sqlmodel import Session, SQLModel, create_engine

from config import settings


def _connect_args(database_url: str) -> Dict[str, Any]:
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


def get_engine(database_url: Optional[str] = None):
    url = database_url or settings.database_url
    return create_engine(url, echo=False, connect_args=_connect_args(url))


engine = get_engine()


def init_db(db_engine=None) -> None:
    active_engine = db_engine or engine
    SQLModel.metadata.create_all(active_engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

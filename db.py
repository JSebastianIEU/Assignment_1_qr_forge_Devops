from sqlmodel import SQLModel, create_engine
from typing import Dict, Any

DATABASE_URL = "sqlite:///qr.db"

# sqlite needs this connect arg for threaded servers
connect_args: Dict[str, Any] = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

def init_db():
    SQLModel.metadata.create_all(engine)

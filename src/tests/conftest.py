import sys
from pathlib import Path
from typing import Generator

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine  # noqa: E402

from app.main import app  # noqa: E402
from app.db import get_session  # noqa: E402

TEST_DATABASE_URL = "sqlite://"


def _create_engine():
    return create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture(scope="session")
def engine() -> Generator:
    engine = _create_engine()
    yield engine


@pytest.fixture(autouse=True)
def prepare_database(engine) -> Generator:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture()
def client(tmp_path: Path, monkeypatch, engine) -> TestClient:
    def override_get_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    from app.storage import LocalFilesystemStorage
    
    # Create local storage with tmp_path for testing
    tmp_storage_dir = tmp_path / "storage"
    tmp_storage_dir.mkdir(parents=True, exist_ok=True)
    
    # Monkeypatch to use local storage for tests
    def override_get_storage():
        return LocalFilesystemStorage(base_dir=tmp_storage_dir)
    
    from app import storage as storage_module
    storage_module._storage_backend = None  # Reset singleton
    monkeypatch.setattr(storage_module, "get_storage_backend", override_get_storage, raising=False)

    return TestClient(app)

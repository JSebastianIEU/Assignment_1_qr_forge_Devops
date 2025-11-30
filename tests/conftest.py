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

from app import app  # noqa: E402
from db import get_session  # noqa: E402

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

    from routers import qr

    svg_dir = tmp_path / "svg"
    png_dir = tmp_path / "png"
    svg_dir.mkdir(parents=True, exist_ok=True)
    png_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(qr, "SVG_DIR", svg_dir, raising=False)
    monkeypatch.setattr(qr, "PNG_DIR", png_dir, raising=False)

    return TestClient(app)

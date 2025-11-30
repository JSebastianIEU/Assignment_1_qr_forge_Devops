import os
from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlmodel import SQLModel

# Import project models only to populate metadata; avoid importing application
# config or db modules which may have side effects (like creating directories).
import app.models  # noqa: F401
from alembic import context

# This is the Alembic Config object. It provides access to the
# values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# pick up the metadata from your models (models import ensures classes are registered)
target_metadata = SQLModel.metadata


def get_url() -> str:
    """Return the DB URL to use for migrations.

    Preference order:
    1. `POSTGRES_URL` environment variable (used by CI/CD)
    2. `sqlalchemy.url` value from `alembic.ini`
    3. `DATABASE_URL` environment variable

    If none are set, raise an explicit error to avoid silent defaults that may
    attempt to create directories under restricted paths.
    """
    url = os.getenv("POSTGRES_URL")
    if url:
        return url
    url = config.get_main_option("sqlalchemy.url")
    if url:
        return url
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    raise RuntimeError(
        "No database URL configured for Alembic. Set POSTGRES_URL or"
        " sqlalchemy.url in alembic.ini"
    )


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = get_url()
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    connectable = create_engine(url, echo=False, connect_args=connect_args)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

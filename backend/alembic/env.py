"""Alembic environment configuration."""
from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.db.base import Base

# Import all models so Alembic sees them
from app.models import user, profile, aqi_reading, daily_plan, knowledge_chunk, community, alert  # noqa

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata


def get_url():
    return os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://cleanair:cleanair@localhost:5432/cleanair",
    )


async def run_migrations_online():
    engine = create_async_engine(get_url(), echo=False)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


asyncio.run(run_migrations_online())


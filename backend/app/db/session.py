"""Database session factory — async PostgreSQL + resilient cache."""
from __future__ import annotations

import time
from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DEBUG,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class InMemoryCache:
    """In-memory cache fallback when Redis is not deployed."""

    def __init__(self):
        self._data: dict[str, tuple[str, float]] = {}

    async def get(self, key: str) -> str | None:
        if key in self._data:
            val, expires = self._data[key]
            if time.time() < expires:
                return val
            del self._data[key]
        return None

    async def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        self._data[key] = (value, time.time() + ttl_seconds)

    async def aclose(self) -> None:
        self._data.clear()


# Initialize Redis if configured, otherwise fallback to in-memory cache
def _init_cache():
    if settings.REDIS_URL and not settings.REDIS_URL.startswith("none"):
        try:
            from redis.asyncio import from_url
            return from_url(settings.REDIS_URL, decode_responses=True)
        except Exception:
            return InMemoryCache()
    return InMemoryCache()


redis_client = _init_cache()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_redis():
    return redis_client

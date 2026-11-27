"""FastAPI application factory."""
from __future__ import annotations

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.db.session import engine, redis_client

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio
    logger.info("CleanAir Companion starting up", version=settings.APP_VERSION)
    yield
    try:
        await asyncio.wait_for(engine.dispose(), timeout=1.0)
    except Exception as exc:
        logger.debug("Database engine cleanup notice", error=str(exc))
    try:
        await asyncio.wait_for(redis_client.aclose(), timeout=1.0)
    except Exception as exc:
        logger.debug("Cache connection cleanup notice", error=str(exc))
    logger.info("CleanAir Companion shut down cleanly")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
        openapi_url="/api/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ── Middleware ─────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # ── Exception handlers ────────────────────────────────────────────────────
    register_exception_handlers(app)

    # ── Routes ────────────────────────────────────────────────────────────────
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_app()


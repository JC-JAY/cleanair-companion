"""Health check endpoint."""
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/")
async def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@router.get("/ready")
async def readiness():
    """K8s / Docker healthcheck readiness probe."""
    return {"status": "ready"}


"""FastAPI v1 router — wires all endpoint modules."""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    aqi, auth, chat, community, health, impact, plan, profile, alerts
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(aqi.router, prefix="/aqi", tags=["aqi"])
api_router.include_router(plan.router, prefix="/plan", tags=["plan"])
api_router.include_router(impact.router, prefix="/impact", tags=["impact"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(community.router, prefix="/community", tags=["community"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])


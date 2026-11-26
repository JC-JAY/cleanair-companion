"""AQI endpoint — location-aware air quality lookup."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db, get_redis
from app.schemas.aqi import AQIResponse
from app.services.aqi.service import AQIService
from app.services.impact.health_lookup import HealthLookup
from app.core.security import get_current_user_optional

router = APIRouter()
_health_lookup = HealthLookup()


@router.get("/", response_model=AQIResponse)
async def get_aqi(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    redis=Depends(get_redis),
    _user=Depends(get_current_user_optional),
):
    """
    Fetch current AQI and pollutant data for a location.
    Returns cached data (≤5 min old) or fetches fresh from APIs.
    """
    import httpx
    async with httpx.AsyncClient() as http:
        svc = AQIService(redis=redis, http_client=http)
        return await svc.get_aqi(lat=lat, lon=lon)


@router.get("/category")
async def get_aqi_category(aqi: int = Query(..., ge=0, le=500)):
    """Return CPCB AQI category metadata for a given AQI value."""
    return _health_lookup.aqi_category_text(aqi)


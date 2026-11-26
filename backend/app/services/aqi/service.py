"""AQI Service — fetches, normalises, and caches air quality data.

Priority cascade:
  1. Redis cache (TTL 5 min)
  2. CPCB / Sameer API (India-specific)
  3. OpenAQ v3
  4. Open-Meteo (meteorology supplement)
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

import httpx
from redis.asyncio import Redis

from app.core.config import settings
from app.schemas.aqi import AQIResponse, AQISource

logger = logging.getLogger(__name__)


def _round_location(lat: float, lon: float) -> tuple[float, float]:
    """Round to configured precision for caching and privacy."""
    dp = settings.LOCATION_PRECISION_DP
    return round(lat, dp), round(lon, dp)


def _cache_key(lat: float, lon: float) -> str:
    return f"aqi:{lat}:{lon}"


class AQIService:
    def __init__(self, redis: Redis, http_client: httpx.AsyncClient):
        self._redis = redis
        self._http = http_client

    async def get_aqi(self, lat: float, lon: float) -> AQIResponse:
        lat_r, lon_r = _round_location(lat, lon)
        cache_key = _cache_key(lat_r, lon_r)

        # 1. Try cache
        cached = await self._redis.get(cache_key)
        if cached:
            data = json.loads(cached)
            data["from_cache"] = True
            return AQIResponse(**data)

        # 2. Try OpenAQ
        aqi_data = await self._fetch_openaq(lat_r, lon_r)
        if aqi_data is None:
            aqi_data = await self._fetch_open_meteo(lat_r, lon_r)

        response = aqi_data or AQIResponse(
            lat=lat_r, lon=lon_r,
            source=AQISource.UNAVAILABLE,
            observed_at=datetime.now(timezone.utc),
            aqi=None, pm25=None, pm10=None, no2=None,
            temperature_c=None, humidity_pct=None, wind_speed_ms=None,
            from_cache=False, data_age_minutes=None,
        )

        # 3. Cache result
        await self._redis.setex(
            cache_key,
            settings.AQI_CACHE_TTL_SECONDS,
            response.model_dump_json(),
        )
        return response

    async def _fetch_openaq(self, lat: float, lon: float) -> AQIResponse | None:
        try:
            resp = await self._http.get(
                f"{settings.OPENAQ_BASE_URL}/locations",
                params={"coordinates": f"{lat},{lon}", "radius": 25000, "limit": 1},
                headers={"X-API-Key": settings.OPENAQ_API_KEY},
                timeout=8.0,
            )
            resp.raise_for_status()
            data = resp.json()
            if not data.get("results"):
                return None

            loc = data["results"][0]
            params_map: dict[str, float] = {}
            for p in loc.get("parameters", []):
                params_map[p["parameter"]] = p.get("lastValue", None)

            # Compute CPCB-style AQI from PM2.5 if available
            pm25 = params_map.get("pm25")
            aqi, aqi_category = _pm25_to_aqi(pm25) if pm25 else (None, None)

            return AQIResponse(
                lat=lat, lon=lon,
                source=AQISource.OPENAQ,
                station_id=str(loc.get("id", "")),
                observed_at=datetime.fromisoformat(
                    loc.get("lastUpdated", datetime.now(timezone.utc).isoformat())
                ),
                aqi=aqi,
                aqi_category=aqi_category,
                pm25=pm25,
                pm10=params_map.get("pm10"),
                no2=params_map.get("no2"),
                so2=params_map.get("so2"),
                co=params_map.get("co"),
                o3=params_map.get("o3"),
                temperature_c=None,
                humidity_pct=None,
                wind_speed_ms=None,
                from_cache=False,
                data_age_minutes=None,
            )
        except Exception as exc:
            logger.warning("OpenAQ fetch failed: %s", exc)
            return None

    async def _fetch_open_meteo(self, lat: float, lon: float) -> AQIResponse | None:
        """Fetch meteorological data as fallback / supplement."""
        try:
            resp = await self._http.get(
                f"{settings.OPEN_METEO_BASE_URL}/air-quality",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "pm10,pm2_5,european_aqi,nitrogen_dioxide,wind_speed_10m,temperature_2m,relative_humidity_2m",
                    "timezone": "Asia/Kolkata",
                },
                timeout=8.0,
            )
            resp.raise_for_status()
            d = resp.json().get("current", {})
            pm25 = d.get("pm2_5")
            aqi, cat = _pm25_to_aqi(pm25) if pm25 else (None, None)

            return AQIResponse(
                lat=lat, lon=lon,
                source=AQISource.OPEN_METEO,
                observed_at=datetime.now(timezone.utc),
                aqi=aqi, aqi_category=cat,
                pm25=pm25,
                pm10=d.get("pm10"),
                no2=d.get("nitrogen_dioxide"),
                so2=None, co=None, o3=None,
                temperature_c=d.get("temperature_2m"),
                humidity_pct=d.get("relative_humidity_2m"),
                wind_speed_ms=d.get("wind_speed_10m"),
                from_cache=False,
                data_age_minutes=0,
            )
        except Exception as exc:
            logger.warning("Open-Meteo fetch failed: %s", exc)
            return None


def _pm25_to_aqi(pm25: float) -> tuple[int, str]:
    """CPCB PM2.5 → AQI sub-index (linear interpolation per CPCB 2014)."""
    breakpoints = [
        # (c_lo, c_hi, aqi_lo, aqi_hi, category)
        (0,    30,    0,   50,  "Good"),
        (30,   60,   51,  100, "Satisfactory"),
        (60,   90,  101,  200, "Moderate"),
        (90,  120,  201,  300, "Poor"),
        (120, 250,  301,  400, "Very Poor"),
        (250, 380,  401,  500, "Severe"),
    ]
    for c_lo, c_hi, aqi_lo, aqi_hi, category in breakpoints:
        if pm25 <= c_hi:
            aqi = aqi_lo + (pm25 - c_lo) * (aqi_hi - aqi_lo) / (c_hi - c_lo)
            return int(round(aqi)), category
    return 500, "Severe"


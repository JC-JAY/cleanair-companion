"""Pydantic v2 schemas for AQI data."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AQISource(str, Enum):
    OPENAQ = "openaq"
    CPCB = "cpcb"
    OPEN_METEO = "open_meteo"
    UNAVAILABLE = "unavailable"


class AQIResponse(BaseModel):
    lat: float
    lon: float
    source: AQISource
    station_id: Optional[str] = None
    observed_at: datetime
    aqi: Optional[int] = Field(None, ge=0, le=500)
    aqi_category: Optional[str] = None
    pm25: Optional[float] = Field(None, ge=0, description="µg/m³")
    pm10: Optional[float] = Field(None, ge=0, description="µg/m³")
    no2: Optional[float] = Field(None, ge=0, description="µg/m³")
    so2: Optional[float] = Field(None, ge=0, description="µg/m³")
    co: Optional[float] = Field(None, ge=0, description="mg/m³")
    o3: Optional[float] = Field(None, ge=0, description="µg/m³")
    temperature_c: Optional[float] = None
    humidity_pct: Optional[float] = Field(None, ge=0, le=100)
    wind_speed_ms: Optional[float] = Field(None, ge=0)
    wind_direction_deg: Optional[int] = Field(None, ge=0, le=360)
    temperature_inversion: bool = False
    from_cache: bool = False
    data_age_minutes: Optional[float] = None

    model_config = {"from_attributes": True}


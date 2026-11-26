"""AQI reading — cached air quality snapshot for a location."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class AQIReading(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "aqi_readings"

    # Location key (rounded lat/lon)
    lat_rounded: Mapped[float] = mapped_column(Float, nullable=False)
    lon_rounded: Mapped[float] = mapped_column(Float, nullable=False)
    station_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False, comment="openaq|cpcb|open_meteo")

    # Observed time
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Core pollutants
    aqi: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    aqi_category: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    pm25: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="µg/m³")
    pm10: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="µg/m³")
    no2: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="µg/m³")
    so2: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="µg/m³")
    co: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="mg/m³")
    o3: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="µg/m³")

    # Meteorology
    temperature_c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    humidity_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    wind_speed_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    wind_direction_deg: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    temperature_inversion: Mapped[bool] = mapped_column(
        default=False, comment="Heuristic inversion flag from vertical temp gradient"
    )

    # Raw payload for auditability
    raw_payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        Index("ix_aqi_readings_location_time", "lat_rounded", "lon_rounded", "observed_at"),
    )


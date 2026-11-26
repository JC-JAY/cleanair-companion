"""User profile — lifestyle, household, and device context for personalisation."""
from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class UserProfile(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    # ── Location (privacy: stored at ±1 km precision) ─────────────────────────
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(100), default="Maharashtra", nullable=False)
    country: Mapped[str] = mapped_column(String(100), default="India", nullable=False)
    pin_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    nearest_aqi_station_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # ── Household ─────────────────────────────────────────────────────────────
    has_children: Mapped[bool] = mapped_column(Boolean, default=False)
    has_elderly: Mapped[bool] = mapped_column(Boolean, default=False)
    has_asthma_respiratory: Mapped[bool] = mapped_column(Boolean, default=False)
    has_pregnancy: Mapped[bool] = mapped_column(Boolean, default=False)
    household_size: Mapped[int] = mapped_column(Integer, default=2)

    # ── Home type ─────────────────────────────────────────────────────────────
    # apartment | house | other
    home_type: Mapped[str] = mapped_column(String(32), default="apartment")
    # biomass | lpg | piped_gas | induction | electric
    cooking_fuel: Mapped[str] = mapped_column(String(32), default="lpg")
    has_kitchen_exhaust: Mapped[bool] = mapped_column(Boolean, default=False)
    num_windows: Mapped[int] = mapped_column(Integer, default=4)
    # coal | kerosene | electric | none
    heating_type: Mapped[str] = mapped_column(String(32), default="none")

    # ── Commute ───────────────────────────────────────────────────────────────
    # walk | cycle | two_wheeler_petrol | two_wheeler_electric | car_petrol |
    # car_diesel | car_cng | bus | metro | auto | wfh
    commute_mode: Mapped[str] = mapped_column(String(32), default="two_wheeler_petrol")
    commute_distance_km: Mapped[float] = mapped_column(Float, default=10.0)

    # ── Budget ────────────────────────────────────────────────────────────────
    # low | medium | high
    budget_level: Mapped[str] = mapped_column(String(16), default="medium")

    # ── Available devices (stored as JSONB array for extensibility) ───────────
    available_devices: Mapped[list[str]] = mapped_column(
        JSONB, default=list,
        comment='["purifier","n95_mask","plants","fans","humidifier"]'
    )

    # Relationship
    user: Mapped["User"] = relationship(back_populates="profile")  # type: ignore[name-defined]  # noqa: F821


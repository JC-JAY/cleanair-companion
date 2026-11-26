"""Daily plan — persisted snapshot of a user's personalised clean-air plan."""
from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class DailyPlan(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "daily_plans"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    plan_date: Mapped[date] = mapped_column(Date, nullable=False)
    aqi_reading_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("aqi_readings.id"), nullable=True
    )

    # Plan payload (full structured JSON — see schemas/plan.py)
    plan_json: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Aggregate impact numbers (denormalised for community dashboard)
    total_pm25_reduction_ug_m3_h: Mapped[float] = mapped_column(Float, default=0.0)
    total_co2e_avoided_kg: Mapped[float] = mapped_column(Float, default=0.0)
    total_pm_avoided_kg: Mapped[float] = mapped_column(Float, default=0.0)

    # Plan quality
    confidence_level: Mapped[str] = mapped_column(String(16), default="medium")
    llm_model_used: Mapped[str] = mapped_column(String(64), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="daily_plans")  # type: ignore[name-defined]  # noqa: F821


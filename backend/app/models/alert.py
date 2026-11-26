"""Alert subscription and delivery log models."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class AlertSubscription(UUIDPKMixin, TimestampMixin, Base):
    """User's alert preferences and delivery channel credentials."""

    __tablename__ = "alert_subscriptions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Channels
    push_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    push_subscription_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, comment="WebPush subscription object")
    whatsapp_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    whatsapp_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    sms_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    sms_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Thresholds
    aqi_threshold: Mapped[int] = mapped_column(Integer, default=200, comment="Alert when AQI >= this value")
    alert_best_window: Mapped[bool] = mapped_column(Boolean, default=True, comment="Daily best outdoor window reminder")
    quiet_start_hour: Mapped[int] = mapped_column(Integer, default=22, comment="No alerts after this hour (local)")
    quiet_end_hour: Mapped[int] = mapped_column(Integer, default=7, comment="No alerts before this hour (local)")

    user: Mapped["User"] = relationship(back_populates="alert_subscriptions")  # type: ignore[name-defined]  # noqa: F821
    deliveries: Mapped[list["AlertDelivery"]] = relationship(back_populates="subscription", cascade="all, delete-orphan")


class AlertDelivery(UUIDPKMixin, TimestampMixin, Base):
    """Log of sent notifications for deduplication and analytics."""

    __tablename__ = "alert_deliveries"

    subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("alert_subscriptions.id", ondelete="CASCADE"), nullable=False
    )
    # aqi_threshold | best_window | severe_advisory
    alert_type: Mapped[str] = mapped_column(String(32), nullable=False)
    # push | whatsapp | sms
    channel: Mapped[str] = mapped_column(String(16), nullable=False)
    # sent | failed | skipped
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    payload_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    subscription: Mapped["AlertSubscription"] = relationship(back_populates="deliveries")


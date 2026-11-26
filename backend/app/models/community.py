"""Community groups, memberships, challenges and leaderboard models."""
from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class Community(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "communities"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # neighbourhood | school | office | city
    community_type: Mapped[str] = mapped_column(String(32), default="neighbourhood")
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    invite_code: Mapped[Optional[str]] = mapped_column(String(16), unique=True, nullable=True)

    # Aggregate stats (updated by Celery job)
    total_co2e_avoided_kg: Mapped[float] = mapped_column(Float, default=0.0)
    total_pm25_reduction_ug_m3_h: Mapped[float] = mapped_column(Float, default=0.0)
    member_count: Mapped[int] = mapped_column(Integer, default=0)

    members: Mapped[list["CommunityMember"]] = relationship(back_populates="community", cascade="all, delete-orphan")
    challenges: Mapped[list["Challenge"]] = relationship(back_populates="community", cascade="all, delete-orphan")


class CommunityMember(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "community_members"

    community_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("communities.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    # member | admin | moderator
    role: Mapped[str] = mapped_column(String(16), default="member")

    # Weekly score (rolling, updated by Celery)
    weekly_score: Mapped[float] = mapped_column(Float, default=0.0)
    total_score: Mapped[float] = mapped_column(Float, default=0.0)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)

    community: Mapped["Community"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="community_memberships")  # type: ignore[name-defined]  # noqa: F821


class Challenge(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "challenges"

    community_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("communities.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    # active | completed | upcoming
    status: Mapped[str] = mapped_column(String(16), default="upcoming")
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    target_co2e_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    achieved_co2e_kg: Mapped[float] = mapped_column(Float, default=0.0)
    badge_icon: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    community: Mapped["Community"] = relationship(back_populates="challenges")


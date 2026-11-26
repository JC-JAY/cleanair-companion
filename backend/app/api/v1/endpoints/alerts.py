"""Alerts endpoint — manage push, WhatsApp, and SMS alert preferences."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.alert import AlertSubscription

router = APIRouter()


class AlertPreferencesUpdate(BaseModel):
    push_enabled: Optional[bool] = None
    push_subscription_json: Optional[dict] = None
    whatsapp_enabled: Optional[bool] = None
    whatsapp_phone: Optional[str] = Field(default=None, max_length=20)
    sms_enabled: Optional[bool] = None
    sms_phone: Optional[str] = Field(default=None, max_length=20)
    aqi_threshold: Optional[int] = Field(default=None, ge=50, le=500)
    alert_best_window: Optional[bool] = None
    quiet_start_hour: Optional[int] = Field(default=None, ge=0, le=23)
    quiet_end_hour: Optional[int] = Field(default=None, ge=0, le=23)


@router.get("/")
async def get_alert_preferences(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(
        select(AlertSubscription).where(AlertSubscription.user_id == user.id)
    )
    sub = result.scalar_one_or_none()
    if not sub:
        sub = AlertSubscription(user_id=user.id)
        db.add(sub)
        await db.commit()
        await db.refresh(sub)
    return sub


@router.patch("/")
async def update_alert_preferences(
    data: AlertPreferencesUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(
        select(AlertSubscription).where(AlertSubscription.user_id == user.id)
    )
    sub = result.scalar_one_or_none()
    if not sub:
        sub = AlertSubscription(user_id=user.id)
        db.add(sub)

    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(sub, key, val)

    await db.commit()
    await db.refresh(sub)
    return sub


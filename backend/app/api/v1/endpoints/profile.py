"""Profile endpoint — CRUD for user lifestyle profile."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.profile import UserProfile
from app.schemas.profile import UserProfileCreate, UserProfileSchema, UserProfileUpdate
from app.utils.geo import round_coordinates

router = APIRouter()


@router.get("/", response_model=UserProfileSchema)
async def get_profile(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Complete onboarding.")
    return profile


@router.post("/", response_model=UserProfileSchema, status_code=status.HTTP_201_CREATED)
async def create_profile(
    data: UserProfileCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Profile already exists. Use PATCH to update.")

    lat, lon = round_coordinates(data.latitude, data.longitude, settings.LOCATION_PRECISION_DP)
    profile = UserProfile(user_id=user.id, **data.model_dump(exclude={"latitude", "longitude"}),
                          latitude=lat, longitude=lon)
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


@router.patch("/", response_model=UserProfileSchema)
async def update_profile(
    data: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    update_data = data.model_dump(exclude_unset=True)
    if "latitude" in update_data or "longitude" in update_data:
        lat, lon = round_coordinates(
            update_data.get("latitude", profile.latitude),
            update_data.get("longitude", profile.longitude),
            settings.LOCATION_PRECISION_DP,
        )
        update_data["latitude"] = lat
        update_data["longitude"] = lon

    for key, val in update_data.items():
        setattr(profile, key, val)

    await db.commit()
    await db.refresh(profile)
    return profile


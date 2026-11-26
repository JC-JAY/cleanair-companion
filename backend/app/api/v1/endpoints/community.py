"""Community endpoint — neighbourhood/school groups, challenges, and leaderboards."""
from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.community import Community, CommunityMember

router = APIRouter()


class CommunityCreate(BaseModel):
    name: str = Field(min_length=2, max_length=128)
    description: Optional[str] = None
    community_type: str = "neighbourhood"
    city: Optional[str] = "Pune"
    is_public: bool = True


@router.get("/")
async def list_communities(
    city: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Community).where(Community.is_public.is_(True))
    if city:
        stmt = stmt.where(Community.city == city)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_community(
    data: CommunityCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    community = Community(**data.model_dump(), member_count=1)
    db.add(community)
    await db.flush()
    db.add(CommunityMember(community_id=community.id, user_id=user.id, role="admin"))
    await db.commit()
    await db.refresh(community)
    return community


@router.post("/{community_id}/join")
async def join_community(
    community_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    community = await db.get(Community, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    existing = await db.execute(
        select(CommunityMember).where(
            CommunityMember.community_id == community_id,
            CommunityMember.user_id == user.id,
        )
    )
    if existing.scalar_one_or_none():
        return {"status": "already_member"}
    db.add(CommunityMember(community_id=community_id, user_id=user.id, role="member"))
    community.member_count += 1
    await db.commit()
    return {"status": "joined"}


"""Daily plan endpoint."""
from __future__ import annotations

from datetime import date

import anthropic
from fastapi import APIRouter, Depends, Query
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_db, get_redis
from app.schemas.plan import DailyPlanResponse
from app.services.aqi.service import AQIService
from app.services.plan.generator import PlanGenerator
from app.services.rag.retriever import RAGRetriever

router = APIRouter()


@router.get("/today", response_model=DailyPlanResponse)
async def get_today_plan(
    language: str = Query(default="en", pattern=r"^(en|hi|mr)$"),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    user=Depends(get_current_user),
):
    """
    Generate (or return cached) the user's personalised daily clean-air plan.
    
    - Fetches live AQI for user's location
    - Runs deterministic impact calculations
    - Retrieves grounding passages from knowledge base
    - Calls Claude to generate the plan (numbers from impact module only)
    - Persists and returns the plan
    """
    from app.models.profile import UserProfile
    from sqlalchemy import select
    import httpx

    profile_row = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = profile_row.scalar_one_or_none()
    if not profile:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Profile not set up. Complete onboarding first.")

    from app.schemas.profile import UserProfileSchema
    profile_schema = UserProfileSchema.model_validate(profile)

    async with httpx.AsyncClient() as http:
        aqi_svc = AQIService(redis=redis, http_client=http)
        aqi_data = await aqi_svc.get_aqi(
            lat=profile.latitude or 18.52,  # default: Pune
            lon=profile.longitude or 73.85,
        )

    openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())
    anthropic_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY.get_secret_value())

    rag = RAGRetriever(db_session=db, openai_client=openai_client)
    generator = PlanGenerator(rag=rag, anthropic_client=anthropic_client)

    plan = await generator.generate(
        profile=profile_schema,
        aqi=aqi_data,
        plan_date=date.today(),
    )

    # Persist plan snapshot
    from app.models.daily_plan import DailyPlan
    import json
    db_plan = DailyPlan(
        user_id=user.id,
        plan_date=date.today(),
        plan_json=plan.model_dump(),
        total_pm25_reduction_ug_m3_h=sum(
            v.get("pm25_exposure_reduction_ug_m3_h", 0)
            for v in (plan.computed_impacts or {}).values()
            if v
        ),
        total_co2e_avoided_kg=sum(
            v.get("co2e_avoided_kg", 0)
            for v in (plan.computed_impacts or {}).values()
            if v
        ),
        llm_model_used=plan.llm_model,
    )
    db.add(db_plan)
    await db.commit()
    plan.id = db_plan.id

    return plan


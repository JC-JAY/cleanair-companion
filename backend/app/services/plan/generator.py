"""Daily Plan Generator — orchestrates AQI + impact + RAG + LLM."""
from __future__ import annotations

import json
import logging
from datetime import date, datetime, timezone

import anthropic

from app.core.config import settings
from app.prompts.daily_plan import build_daily_plan_prompt, DAILY_PLAN_SCHEMA
from app.schemas.aqi import AQIResponse
from app.schemas.plan import DailyPlanResponse, TimeWindow, Recommendation
from app.schemas.profile import UserProfileSchema
from app.services.impact.calculator import ImpactCalculator
from app.services.rag.retriever import RAGRetriever
from app.utils.sanitizer import sanitize_for_llm

logger = logging.getLogger(__name__)

_calc = ImpactCalculator()


class PlanGenerator:
    def __init__(self, rag: RAGRetriever, anthropic_client: anthropic.AsyncAnthropic):
        self._rag = rag
        self._llm = anthropic_client

    async def generate(
        self,
        profile: UserProfileSchema,
        aqi: AQIResponse,
        plan_date: date,
    ) -> DailyPlanResponse:
        # 1. Pre-compute deterministic impact bundles
        profile_ages = _build_ages(profile)
        ambient_pm25 = aqi.pm25 or 60.0  # fallback for missing data

        commute_impact = None
        if profile.commute_mode not in ("wfh", "walk", "cycle", "metro"):
            commute_impact = _calc.commute_switch_impact(
                from_mode=profile.commute_mode,
                to_mode="metro" if profile.commute_mode.startswith("car") else "bus",
                distance_km=profile.commute_distance_km,
                ambient_pm25=ambient_pm25,
                profile_ages=profile_ages,
            )

        cooking_impact = _calc.cooking_switch_impact(
            from_fuel=profile.cooking_fuel,
            to_fuel="lpg" if profile.cooking_fuel == "biomass" else "induction",
            cooking_hours_per_day=1.5,
            has_kitchen_exhaust=profile.has_kitchen_exhaust,
            profile_ages=profile_ages,
        )

        purifier_impact = None
        if "purifier" in (profile.available_devices or []):
            purifier_impact = _calc.purifier_impact(
                ambient_pm25=ambient_pm25,
                cadr_m3_h=200,
                room_volume_m3=35,
                hours_per_day=8,
                profile_ages=profile_ages,
            )

        # 2. RAG retrieval
        context_query = (
            f"AQI {aqi.aqi} PM2.5 {ambient_pm25:.0f} µg/m³ "
            f"winter smog Maharashtra indoor air quality recommendations "
            f"{'children ' if profile.has_children else ''}"
            f"{'asthma ' if profile.has_asthma_respiratory else ''}"
            f"cooking:{profile.cooking_fuel} commute:{profile.commute_mode}"
        )
        passages = await self._rag.retrieve(sanitize_for_llm(context_query), top_k=settings.RAG_TOP_K)

        # 3. Build impact bundle dict for prompt
        impact_data = {
            "commute": commute_impact.to_dict() if commute_impact else None,
            "cooking": cooking_impact.to_dict(),
            "purifier": purifier_impact.to_dict() if purifier_impact else None,
        }

        # 4. Call LLM with structured output
        prompt = build_daily_plan_prompt(profile, aqi, impact_data, passages, plan_date)

        message = await self._llm.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=settings.LLM_MAX_TOKENS,
            temperature=settings.LLM_TEMPERATURE,
            system=prompt["system"],
            messages=[{"role": "user", "content": prompt["user"]}],
            tools=[{
                "name": "emit_daily_plan",
                "description": "Emit the structured daily clean-air plan",
                "input_schema": DAILY_PLAN_SCHEMA,
            }],
            tool_choice={"type": "tool", "name": "emit_daily_plan"},
        )

        # 5. Extract and validate tool call response
        tool_use = next(
            (block for block in message.content if block.type == "tool_use"),
            None,
        )
        if tool_use is None:
            raise ValueError("LLM did not return a tool_use block")

        plan_data = tool_use.input
        # Inject pre-computed impact bundles (LLM must not invent numbers)
        plan_data["computed_impacts"] = impact_data
        plan_data["aqi_snapshot"] = aqi.model_dump()
        plan_data["llm_model"] = settings.ANTHROPIC_MODEL
        plan_data["generated_at"] = datetime.now(timezone.utc).isoformat()

        return DailyPlanResponse.model_validate(plan_data)


def _build_ages(profile: UserProfileSchema) -> list[str]:
    ages = ["adult"]
    if profile.has_children:
        ages.append("child")
    if profile.has_elderly:
        ages.append("elderly")
    return ages


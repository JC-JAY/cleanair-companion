"""Pydantic v2 schemas for daily plan responses."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class TimeWindow(BaseModel):
    label: str
    start_hour: int = Field(ge=0, le=23)
    end_hour: int = Field(ge=0, le=23)
    quality: Literal["best", "good", "avoid"]
    activities: list[str]
    reasoning: str


class ImpactCard(BaseModel):
    pm25_exposure_reduction_ug_m3_h: float
    co2e_avoided_kg: float
    pm_avoided_kg: float
    no2_avoided_g: float
    health_meaning: str
    confidence_level: str
    assumptions: list[str]
    sources: list[str]


class Recommendation(BaseModel):
    category: Literal[
        "commute", "cooking", "indoor_air", "outdoor_timing",
        "purifier", "sustainable_alt", "community"
    ]
    title: str
    description: str
    impact_key: Optional[str] = None
    impact_explanation: Optional[str] = None
    impact_card: Optional[ImpactCard] = None
    cost_level: Literal["free", "low", "medium", "high"]
    effort_level: Literal["easy", "moderate", "hard"]
    priority: int = Field(ge=1, le=10)
    sources: list[str] = Field(default_factory=list)


class IndoorAirHack(BaseModel):
    title: str
    description: str
    cost_level: Literal["free", "low", "medium", "high"]
    effort_level: Literal["easy", "moderate", "hard"]
    source: Optional[str] = None


class DailyPlanResponse(BaseModel):
    id: Optional[uuid.UUID] = None
    plan_date: Optional[str] = None
    summary: str
    aqi_level_advice: dict
    time_windows: list[TimeWindow]
    recommendations: list[Recommendation]
    indoor_air_hacks: list[IndoorAirHack] = Field(default_factory=list)
    computed_impacts: Optional[dict[str, Any]] = None
    aqi_snapshot: Optional[dict] = None
    disclaimer: str
    llm_model: Optional[str] = None
    generated_at: Optional[str] = None

    model_config = {"from_attributes": True}


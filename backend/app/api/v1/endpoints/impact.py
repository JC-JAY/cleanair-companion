"""Impact calculator endpoint — exposes deterministic calculations directly."""
from __future__ import annotations

from typing import Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.impact.calculator import ImpactCalculator

router = APIRouter()
_calc = ImpactCalculator()


class CommuteImpactRequest(BaseModel):
    from_mode: str
    to_mode: str
    distance_km: float = Field(gt=0, le=200)
    ambient_pm25: float = Field(gt=0, le=1000)
    profile_ages: list[Literal["child", "adult", "elderly"]] = ["adult"]


class CookingImpactRequest(BaseModel):
    from_fuel: str
    to_fuel: str
    cooking_hours_per_day: float = Field(default=1.5, gt=0, le=12)
    has_kitchen_exhaust: bool = False
    profile_ages: list[Literal["child", "adult", "elderly"]] = ["adult"]


class PurifierImpactRequest(BaseModel):
    ambient_pm25: float = Field(gt=0, le=1000)
    cadr_m3_h: float = Field(default=200, gt=0, le=2000)
    room_volume_m3: float = Field(default=35, gt=0, le=500)
    hours_per_day: float = Field(default=8, gt=0, le=24)
    profile_ages: list[Literal["child", "adult", "elderly"]] = ["adult"]


@router.post("/commute")
async def commute_impact(req: CommuteImpactRequest):
    """Calculate impact of switching commute mode."""
    result = _calc.commute_switch_impact(
        from_mode=req.from_mode,
        to_mode=req.to_mode,
        distance_km=req.distance_km,
        ambient_pm25=req.ambient_pm25,
        profile_ages=req.profile_ages,
    )
    return result.to_dict()


@router.post("/cooking")
async def cooking_impact(req: CookingImpactRequest):
    """Calculate impact of switching cooking fuel."""
    result = _calc.cooking_switch_impact(
        from_fuel=req.from_fuel,
        to_fuel=req.to_fuel,
        cooking_hours_per_day=req.cooking_hours_per_day,
        has_kitchen_exhaust=req.has_kitchen_exhaust,
        profile_ages=req.profile_ages,
    )
    return result.to_dict()


@router.post("/purifier")
async def purifier_impact(req: PurifierImpactRequest):
    """Calculate exposure reduction from running an air purifier."""
    result = _calc.purifier_impact(
        ambient_pm25=req.ambient_pm25,
        cadr_m3_h=req.cadr_m3_h,
        room_volume_m3=req.room_volume_m3,
        hours_per_day=req.hours_per_day,
        profile_ages=req.profile_ages,
    )
    return result.to_dict()


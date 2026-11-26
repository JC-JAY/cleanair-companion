"""Pydantic v2 schemas for user profile."""
from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserProfileCreate(BaseModel):
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    city: Optional[str] = None
    state: str = "Maharashtra"
    country: str = "India"
    pin_code: Optional[str] = None
    has_children: bool = False
    has_elderly: bool = False
    has_asthma_respiratory: bool = False
    has_pregnancy: bool = False
    household_size: int = Field(default=2, ge=1, le=20)
    home_type: str = "apartment"
    cooking_fuel: str = "lpg"
    has_kitchen_exhaust: bool = False
    num_windows: int = Field(default=4, ge=0, le=50)
    heating_type: str = "none"
    commute_mode: str = "two_wheeler_petrol"
    commute_distance_km: float = Field(default=10.0, ge=0, le=200)
    budget_level: str = "medium"
    available_devices: list[str] = Field(default_factory=list)

    @field_validator("cooking_fuel")
    @classmethod
    def validate_cooking_fuel(cls, v: str) -> str:
        valid = {"biomass", "kerosene", "lpg", "piped_gas", "induction", "electric"}
        if v not in valid:
            raise ValueError(f"cooking_fuel must be one of {valid}")
        return v

    @field_validator("commute_mode")
    @classmethod
    def validate_commute_mode(cls, v: str) -> str:
        valid = {"walk", "cycle", "two_wheeler_petrol", "two_wheeler_electric",
                 "car_petrol", "car_diesel", "car_cng", "bus", "metro", "auto", "wfh"}
        if v not in valid:
            raise ValueError(f"commute_mode must be one of {valid}")
        return v


class UserProfileSchema(UserProfileCreate):
    id: uuid.UUID
    user_id: uuid.UUID

    model_config = {"from_attributes": True}


class UserProfileUpdate(UserProfileCreate):
    """All fields optional for PATCH."""

    model_config = ConfigDict(extra="ignore")


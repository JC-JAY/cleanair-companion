"""Unit tests for user profile validation."""
from __future__ import annotations

import pytest
from pydantic import ValidationError
from app.schemas.profile import UserProfileCreate


class TestUserProfileValidation:
    def test_valid_profile_creation(self):
        p = UserProfileCreate(
            city="Pune",
            state="Maharashtra",
            commute_mode="metro",
            cooking_fuel="lpg",
            household_size=4,
        )
        assert p.city == "Pune"
        assert p.commute_mode == "metro"

    def test_invalid_commute_mode_raises(self):
        with pytest.raises(ValidationError):
            UserProfileCreate(commute_mode="rocket_ship")

    def test_invalid_cooking_fuel_raises(self):
        with pytest.raises(ValidationError):
            UserProfileCreate(cooking_fuel="nuclear_power")

    def test_latitude_longitude_bounds(self):
        with pytest.raises(ValidationError):
            UserProfileCreate(latitude=95.0)  # max is 90

"""Unit tests for CPCB AQI health lookup and WHO exposure response."""
from __future__ import annotations

import pytest
from app.services.impact.health_lookup import HealthLookup


@pytest.fixture
def health():
    return HealthLookup()


class TestHealthLookup:
    def test_aqi_good_category(self, health):
        res = health.aqi_category_text(35)
        assert res["category"] == "Good"
        assert res["hex_color"] == "#55a84f"

    def test_aqi_satisfactory_category(self, health):
        res = health.aqi_category_text(85)
        assert res["category"] == "Satisfactory"
        assert res["hex_color"] == "#a3c853"

    def test_aqi_moderate_category(self, health):
        res = health.aqi_category_text(180)
        assert res["category"] == "Moderate"
        assert res["hex_color"] == "#fff833"

    def test_aqi_poor_category(self, health):
        res = health.aqi_category_text(250)
        assert res["category"] == "Poor"
        assert res["hex_color"] == "#f29c33"

    def test_aqi_very_poor_category(self, health):
        res = health.aqi_category_text(350)
        assert res["category"] == "Very Poor"
        assert res["hex_color"] == "#e93f33"

    def test_aqi_severe_category(self, health):
        res = health.aqi_category_text(450)
        assert res["category"] == "Severe"
        assert res["hex_color"] == "#af2d24"

    def test_exposure_meaning_vulnerable_child(self, health):
        meaning = health.exposure_meaning(pm25_exposure_ug_m3_h=20.0, profile_ages=["adult", "child"])
        assert "child" in meaning.lower() or "sensitive" in meaning.lower()
        assert "not medical advice" in meaning.lower()

    def test_exposure_meaning_negligible(self, health):
        meaning = health.exposure_meaning(pm25_exposure_ug_m3_h=0.5, profile_ages=["adult"])
        assert "not medical advice" in meaning.lower()

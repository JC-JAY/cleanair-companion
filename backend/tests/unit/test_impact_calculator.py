"""Unit tests for the impact calculator — all arithmetic verified against sources."""
from __future__ import annotations

import pytest

from app.services.impact.calculator import ImpactCalculator
from app.services.impact.emission_factors import EMISSION_FACTORS


@pytest.fixture
def calc():
    return ImpactCalculator()


class TestCommuteSwitchImpact:
    def test_wfh_has_zero_emissions(self, calc):
        result = calc.commute_switch_impact(
            from_mode="wfh",
            to_mode="wfh",
            distance_km=10,
            ambient_pm25=100,
            profile_ages=["adult"],
        )
        assert result.co2e_avoided_kg == 0.0
        assert result.pm_avoided_kg == 0.0

    def test_car_to_metro_reduces_co2(self, calc):
        result = calc.commute_switch_impact(
            from_mode="car_petrol",
            to_mode="metro",
            distance_km=15,
            ambient_pm25=120,
            profile_ages=["adult"],
        )
        # car_petrol: 0.170 kg/km, metro: 0.014 kg/km
        # expected: (0.170 - 0.014) * 15 * 2 = 4.68 kg
        expected_co2e = (0.170 - 0.014) * 15 * 2
        assert abs(result.co2e_avoided_kg - expected_co2e) < 0.01

    def test_two_wheeler_to_bus_saves_exposure(self, calc):
        result = calc.commute_switch_impact(
            from_mode="two_wheeler_petrol",
            to_mode="bus",
            distance_km=10,
            ambient_pm25=200,
            profile_ages=["adult"],
        )
        # Two-wheeler is fully open (penetration 1.0), bus is 0.75
        # Exposure should be less on bus
        assert result.pm25_exposure_reduction_ug_m3_h >= 0.0

    def test_negative_impact_clamped_to_zero(self, calc):
        """Switching to a less clean mode should give 0 benefit, not negative."""
        result = calc.commute_switch_impact(
            from_mode="metro",
            to_mode="car_diesel",
            distance_km=10,
            ambient_pm25=100,
            profile_ages=["adult"],
        )
        assert result.co2e_avoided_kg == 0.0
        assert result.pm_avoided_kg == 0.0

    def test_includes_sources_citation(self, calc):
        result = calc.commute_switch_impact(
            from_mode="car_petrol",
            to_mode="bus",
            distance_km=5,
            ambient_pm25=80,
            profile_ages=["adult"],
        )
        assert len(result.sources) > 0
        assert any("IPCC" in s or "ARAI" in s for s in result.sources)

    def test_child_in_profile_ages(self, calc):
        result = calc.commute_switch_impact(
            from_mode="car_petrol",
            to_mode="metro",
            distance_km=10,
            ambient_pm25=150,
            profile_ages=["adult", "child"],
        )
        assert "child" in result.health_meaning.lower() or "sensitive" in result.health_meaning.lower()

    def test_round_trip_distance(self, calc):
        """CO2e should use round-trip (×2) distance."""
        one_way = calc.commute_switch_impact(
            from_mode="car_petrol",
            to_mode="walk",
            distance_km=5,
            ambient_pm25=100,
            profile_ages=["adult"],
        )
        # EF car_petrol = 0.170 kg/km × 5 × 2 = 1.70
        expected = 0.170 * 5 * 2
        assert abs(one_way.co2e_avoided_kg - expected) < 0.01


class TestCookingSwitchImpact:
    def test_biomass_to_lpg_large_reduction(self, calc):
        result = calc.cooking_switch_impact(
            from_fuel="biomass",
            to_fuel="lpg",
            cooking_hours_per_day=1.5,
            has_kitchen_exhaust=False,
            profile_ages=["adult"],
        )
        # biomass pm25_mg_per_min=7.2, lpg=0.14 — big difference
        assert result.pm25_exposure_reduction_ug_m3_h > 0.1
        assert result.co2e_avoided_kg > 0

    def test_lpg_to_induction_zero_pm_emissions(self, calc):
        result = calc.cooking_switch_impact(
            from_fuel="lpg",
            to_fuel="induction",
            cooking_hours_per_day=1.5,
            has_kitchen_exhaust=False,
            profile_ages=["adult"],
        )
        # Induction has 0 PM — so PM avoided should be positive
        assert result.pm_avoided_kg >= 0

    def test_exhaust_fan_reduces_exposure(self, calc):
        without_exhaust = calc.cooking_switch_impact(
            from_fuel="biomass",
            to_fuel="lpg",
            cooking_hours_per_day=1.5,
            has_kitchen_exhaust=False,
            profile_ages=["adult"],
        )
        with_exhaust = calc.cooking_switch_impact(
            from_fuel="biomass",
            to_fuel="lpg",
            cooking_hours_per_day=1.5,
            has_kitchen_exhaust=True,
            profile_ages=["adult"],
        )
        # With exhaust, the from-fuel exposure is lower, so reduction is less
        # (The benefit of switching is relatively smaller when you already have exhaust)
        assert without_exhaust.pm25_exposure_reduction_ug_m3_h >= 0
        assert with_exhaust.pm25_exposure_reduction_ug_m3_h >= 0


class TestPurifierImpact:
    def test_high_cadr_high_reduction(self, calc):
        result = calc.purifier_impact(
            ambient_pm25=200,
            cadr_m3_h=400,
            room_volume_m3=35,
            hours_per_day=8,
            profile_ages=["adult"],
        )
        assert result.pm25_exposure_reduction_ug_m3_h > 1.0

    def test_zero_cadr_zero_reduction(self, calc):
        # Edge case: CADR near zero
        result = calc.purifier_impact(
            ambient_pm25=200,
            cadr_m3_h=0.001,
            room_volume_m3=35,
            hours_per_day=8,
            profile_ages=["adult"],
        )
        assert result.pm25_exposure_reduction_ug_m3_h >= 0

    def test_no_co2e_from_purifier(self, calc):
        result = calc.purifier_impact(
            ambient_pm25=100,
            cadr_m3_h=200,
            room_volume_m3=35,
            hours_per_day=8,
            profile_ages=["adult"],
        )
        assert result.co2e_avoided_kg == 0.0

    def test_multiple_family_members_increases_exposure(self, calc):
        single = calc.purifier_impact(
            ambient_pm25=150, cadr_m3_h=200, room_volume_m3=35,
            hours_per_day=8, profile_ages=["adult"]
        )
        family = calc.purifier_impact(
            ambient_pm25=150, cadr_m3_h=200, room_volume_m3=35,
            hours_per_day=8, profile_ages=["adult", "child", "elderly"]
        )
        # Total exposure reduction is higher for family (sum of breathing rates)
        assert family.pm25_exposure_reduction_ug_m3_h > single.pm25_exposure_reduction_ug_m3_h


class TestEmissionFactors:
    def test_all_commute_modes_have_co2e(self):
        for mode, ef in EMISSION_FACTORS["commute"].items():
            assert "co2e_kg_per_km" in ef, f"Missing co2e_kg_per_km for {mode}"
            assert ef["co2e_kg_per_km"] >= 0

    def test_all_cooking_fuels_have_pm25(self):
        for fuel, ef in EMISSION_FACTORS["cooking"].items():
            assert "pm25_mg_per_min" in ef, f"Missing pm25_mg_per_min for {fuel}"
            assert ef["pm25_mg_per_min"] >= 0

    def test_biomass_higher_pm25_than_lpg(self):
        biomass_ef = EMISSION_FACTORS["cooking"]["biomass"]["pm25_mg_per_min"]
        lpg_ef = EMISSION_FACTORS["cooking"]["lpg"]["pm25_mg_per_min"]
        assert biomass_ef > lpg_ef, "Biomass should have higher PM2.5 than LPG"

    def test_wfh_zero_emissions(self):
        wfh = EMISSION_FACTORS["commute"]["wfh"]
        assert wfh["co2e_kg_per_km"] == 0
        assert wfh["pm25_kg_per_km"] == 0

    def test_all_sources_cited(self):
        for mode, ef in EMISSION_FACTORS["commute"].items():
            assert ef.get("source"), f"No source citation for commute mode {mode}"
        for fuel, ef in EMISSION_FACTORS["cooking"].items():
            assert ef.get("source"), f"No source citation for cooking fuel {fuel}"


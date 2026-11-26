"""Impact Calculator — deterministic, unit-tested.

All emission factors are documented with sources.
The LLM is NEVER called here; it may only explain these computed values.

Sources:
  [EF1] IPCC AR6 WG3, Table A.III.2 (transport emission factors, 2022)
  [EF2] MoEFCC / CPCB India — Emission Factor Database (2021)
  [EF3] WHO Global Air Quality Guidelines (2021) — exposure-response functions
  [EF4] Chafe et al. (2015) — Household cooking solid fuel PM2.5 exposure
  [EF5] ARAI India — Vehicle emission factors (2019)
  [EF6] BEE India — Building energy & cooking emission factors
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from app.services.impact.emission_factors import EMISSION_FACTORS
from app.services.impact.health_lookup import HealthLookup


@dataclass(frozen=True)
class ImpactBundle:
    """All computed impact values for a recommendation."""

    # Exposure reduction
    pm25_exposure_reduction_ug_m3_h: float  # µg/m³·h
    # Emissions avoided
    co2e_avoided_kg: float
    pm_avoided_kg: float          # PM2.5 + PM10 combined
    no2_avoided_g: float
    # Health plain-language text (computed from lookup table, not LLM)
    health_meaning: str
    # Confidence
    confidence_level: str         # high | medium | low
    assumptions: list[str]
    sources: list[str]

    def to_dict(self) -> dict:
        return {
            "pm25_exposure_reduction_ug_m3_h": round(self.pm25_exposure_reduction_ug_m3_h, 3),
            "co2e_avoided_kg": round(self.co2e_avoided_kg, 4),
            "pm_avoided_kg": round(self.pm_avoided_kg, 5),
            "no2_avoided_g": round(self.no2_avoided_g, 3),
            "health_meaning": self.health_meaning,
            "confidence_level": self.confidence_level,
            "assumptions": self.assumptions,
            "sources": self.sources,
        }


class ImpactCalculator:
    """
    Deterministic impact calculator.

    All public methods accept plain Python values, perform unit-verified
    arithmetic, and return ImpactBundle. No I/O, no randomness.
    """

    # Breathing rate by age (m³/h) — WHO 2021
    _BREATHING_RATE_M3_H = {
        "child": 0.78,
        "adult": 0.63,
        "elderly": 0.54,
    }

    # Infiltration factor (outdoor → indoor without purifier) — WHO / EPA
    _INFILTRATION_FACTOR = 0.65   # 65% of outdoor PM2.5 penetrates indoors

    def __init__(self):
        self._ef = EMISSION_FACTORS
        self._health = HealthLookup()

    # ─────────────────────────────────────────────────────────────────────────
    # Commute impact
    # ─────────────────────────────────────────────────────────────────────────

    def commute_switch_impact(
        self,
        from_mode: str,
        to_mode: str,
        distance_km: float,
        ambient_pm25: float,
        profile_ages: list[str],
    ) -> ImpactBundle:
        """
        Impact of switching from one commute mode to another.

        PM2.5 exposure reduction accounts for time-in-vehicle and in-cabin
        penetration factors (tunnel effect for 2-wheelers vs enclosed cabin).
        CO2e uses IPCC AR6 / ARAI factors per km.

        Args:
            from_mode: e.g. "two_wheeler_petrol"
            to_mode:   e.g. "metro"
            distance_km: one-way commute distance
            ambient_pm25: current outdoor PM2.5 in µg/m³
            profile_ages: list from ["child", "adult", "elderly"]
        """
        ef_from = self._ef["commute"].get(from_mode, {})
        ef_to   = self._ef["commute"].get(to_mode, {})

        # --- CO2e avoided ------------------------------------------------
        co2e_per_km_from = ef_from.get("co2e_kg_per_km", 0.0)
        co2e_per_km_to   = ef_to.get("co2e_kg_per_km", 0.0)
        # Round trip
        co2e_avoided_kg  = (co2e_per_km_from - co2e_per_km_to) * distance_km * 2

        # --- PM emissions avoided ----------------------------------------
        pm_per_km_from = ef_from.get("pm25_kg_per_km", 0.0) + ef_from.get("pm10_kg_per_km", 0.0)
        pm_per_km_to   = ef_to.get("pm25_kg_per_km", 0.0) + ef_to.get("pm10_kg_per_km", 0.0)
        pm_avoided_kg  = (pm_per_km_from - pm_per_km_to) * distance_km * 2

        # --- Exposure reduction ------------------------------------------
        # In-cabin PM2.5 penetration (open 2-wheeler = 100%, enclosed = 50%)
        in_cabin_from = ef_from.get("in_cabin_penetration", 1.0)
        in_cabin_to   = ef_to.get("in_cabin_penetration", 0.5)
        # Time in commute (h) = distance / speed
        speed_from = ef_from.get("avg_speed_kmh", 30)
        speed_to   = ef_to.get("avg_speed_kmh", 25)
        time_from_h = (distance_km * 2) / speed_from
        time_to_h   = (distance_km * 2) / speed_to

        exposure_from = ambient_pm25 * in_cabin_from * time_from_h
        exposure_to   = ambient_pm25 * in_cabin_to   * time_to_h
        pm25_exp_red  = max(0.0, exposure_from - exposure_to)

        # --- NO2 avoided ------------------------------------------------
        no2_per_km_from = ef_from.get("no2_g_per_km", 0.0)
        no2_per_km_to   = ef_to.get("no2_g_per_km", 0.0)
        no2_avoided_g   = (no2_per_km_from - no2_per_km_to) * distance_km * 2

        health_text = self._health.exposure_meaning(pm25_exp_red, profile_ages)
        confidence  = "high" if distance_km < 50 else "medium"
        assumptions = [
            f"Round-trip distance: {distance_km * 2:.1f} km",
            f"Ambient PM2.5: {ambient_pm25} µg/m³",
            f"In-cabin penetration factors: {in_cabin_from:.0%} → {in_cabin_to:.0%}",
            "Vehicle load factors per ARAI 2019 city-cycle",
        ]
        sources = ["[EF1] IPCC AR6 WG3 Table A.III.2", "[EF5] ARAI India Vehicle EF 2019"]

        return ImpactBundle(
            pm25_exposure_reduction_ug_m3_h=round(pm25_exp_red, 3),
            co2e_avoided_kg=round(max(0.0, co2e_avoided_kg), 4),
            pm_avoided_kg=round(max(0.0, pm_avoided_kg), 5),
            no2_avoided_g=round(max(0.0, no2_avoided_g), 3),
            health_meaning=health_text,
            confidence_level=confidence,
            assumptions=assumptions,
            sources=sources,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Cooking fuel switch
    # ─────────────────────────────────────────────────────────────────────────

    def cooking_switch_impact(
        self,
        from_fuel: str,
        to_fuel: str,
        cooking_hours_per_day: float,
        has_kitchen_exhaust: bool,
        profile_ages: list[str],
    ) -> ImpactBundle:
        """
        Impact of switching cooking fuel.

        Indoor PM2.5 exposure computed with Chafe et al. 2015 concentration
        model: C_indoor = EF_pm25 × fuel_burn_rate × (1 − exhaust_reduction)
        multiplied by breathing rate and time.
        """
        ef_from = self._ef["cooking"].get(from_fuel, {})
        ef_to   = self._ef["cooking"].get(to_fuel, {})

        # Indoor PM2.5 concentration produced (mg/m³ → µg/m³)
        exhaust_red = 0.65 if has_kitchen_exhaust else 0.0

        def indoor_pm25_ugm3(ef: dict) -> float:
            # emission factor in mg/min, kitchen volume ~30 m³
            return ef.get("pm25_mg_per_min", 0.0) * cooking_hours_per_day * 60 * (1 - exhaust_red) / 30 * 1000

        conc_from = indoor_pm25_ugm3(ef_from)
        conc_to   = indoor_pm25_ugm3(ef_to)
        conc_red  = max(0.0, conc_from - conc_to)

        # Exposure over cooking period for primary cook (adult)
        breath_adult = self._BREATHING_RATE_M3_H["adult"]
        pm25_exp_red = conc_red * cooking_hours_per_day * breath_adult

        co2e_per_h_from = ef_from.get("co2e_kg_per_hour", 0.0)
        co2e_per_h_to   = ef_to.get("co2e_kg_per_hour", 0.0)
        co2e_avoided    = (co2e_per_h_from - co2e_per_h_to) * cooking_hours_per_day

        pm_per_h_from = ef_from.get("pm25_mg_per_min", 0.0) * 60 / 1e6  # kg/h
        pm_per_h_to   = ef_to.get("pm25_mg_per_min", 0.0) * 60 / 1e6
        pm_avoided_kg = (pm_per_h_from - pm_per_h_to) * cooking_hours_per_day

        health_text = self._health.exposure_meaning(pm25_exp_red, profile_ages)

        return ImpactBundle(
            pm25_exposure_reduction_ug_m3_h=round(pm25_exp_red, 3),
            co2e_avoided_kg=round(max(0.0, co2e_avoided), 4),
            pm_avoided_kg=round(max(0.0, pm_avoided_kg), 5),
            no2_avoided_g=0.0,
            health_meaning=health_text,
            confidence_level="medium",
            assumptions=[
                f"Kitchen volume: 30 m³",
                f"Cooking duration: {cooking_hours_per_day} h/day",
                f"Exhaust fan reduction: {exhaust_red:.0%}",
                "Concentration model: Chafe et al. 2015",
            ],
            sources=["[EF4] Chafe et al. 2015 Lancet", "[EF6] BEE India cooking EF"],
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Indoor purifier hack
    # ─────────────────────────────────────────────────────────────────────────

    def purifier_impact(
        self,
        ambient_pm25: float,
        cadr_m3_h: float,
        room_volume_m3: float,
        hours_per_day: float,
        profile_ages: list[str],
    ) -> ImpactBundle:
        """
        Indoor exposure reduction from running an air purifier.

        CADR model: C_indoor_purified = C_outdoor × infiltration / (1 + CADR/ACH_natural)
        ACH_natural assumed 0.5 for Indian apartments (sealed).
        """
        ach_natural_m3h = room_volume_m3 * 0.5
        c_without = ambient_pm25 * self._INFILTRATION_FACTOR
        c_with    = c_without / (1 + cadr_m3_h / ach_natural_m3h)
        conc_red  = max(0.0, c_without - c_with)

        # Exposure for all age groups (sum)
        pm25_exp_red = sum(
            conc_red * hours_per_day * self._BREATHING_RATE_M3_H.get(age, 0.63)
            for age in profile_ages
        )

        health_text = self._health.exposure_meaning(pm25_exp_red / max(1, len(profile_ages)), profile_ages)

        return ImpactBundle(
            pm25_exposure_reduction_ug_m3_h=round(pm25_exp_red, 3),
            co2e_avoided_kg=0.0,
            pm_avoided_kg=0.0,
            no2_avoided_g=0.0,
            health_meaning=health_text,
            confidence_level="high",
            assumptions=[
                f"Ambient PM2.5: {ambient_pm25} µg/m³",
                f"CADR: {cadr_m3_h} m³/h, Room: {room_volume_m3} m³",
                "Infiltration factor: 0.65 (WHO/EPA sealed room)",
                "Natural ACH: 0.5 (Indian apartment estimate)",
            ],
            sources=["[EF3] WHO AQG 2021", "EPA CADR guidance 2023"],
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Outdoor timing (best vs worst window)
    # ─────────────────────────────────────────────────────────────────────────

    def outdoor_timing_impact(
        self,
        good_window_pm25: float,
        bad_window_pm25: float,
        activity_hours: float,
        profile_ages: list[str],
    ) -> ImpactBundle:
        """
        Exposure saved by choosing the best outdoor time window.
        """
        exp_bad  = sum(
            bad_window_pm25 * activity_hours * self._BREATHING_RATE_M3_H.get(a, 0.63)
            for a in profile_ages
        )
        exp_good = sum(
            good_window_pm25 * activity_hours * self._BREATHING_RATE_M3_H.get(a, 0.63)
            for a in profile_ages
        )
        pm25_exp_red = max(0.0, exp_bad - exp_good)
        health_text  = self._health.exposure_meaning(
            pm25_exp_red / max(1, len(profile_ages)), profile_ages
        )

        return ImpactBundle(
            pm25_exposure_reduction_ug_m3_h=round(pm25_exp_red, 3),
            co2e_avoided_kg=0.0,
            pm_avoided_kg=0.0,
            no2_avoided_g=0.0,
            health_meaning=health_text,
            confidence_level="medium",
            assumptions=[
                f"Good window PM2.5: {good_window_pm25} µg/m³",
                f"Bad window PM2.5: {bad_window_pm25} µg/m³",
                f"Activity duration: {activity_hours} h",
                "Breathing rates: WHO 2021",
            ],
            sources=["[EF3] WHO AQG 2021"],
        )


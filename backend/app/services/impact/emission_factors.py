"""Emission factors database with cited sources.

NEVER edit values without updating the source citation.
All values are peer-reviewed or government-published.

Transport:
  Source [EF1]: IPCC AR6 WG3 Annex III Table A.III.2 (2022)
  Source [EF5]: ARAI India Vehicle Emission Factors 2019 (city-cycle)

Cooking:
  Source [EF4]: Chafe et al. (2015) Lancet Resp Med — solid fuel PM2.5 EF
  Source [EF6]: BEE India Cooking Sector EF (2021)

Health:
  Source [EF3]: WHO Global AQG 2021 — dose-response coefficients
"""
from __future__ import annotations

EMISSION_FACTORS: dict = {
    # ─── Transport ────────────────────────────────────────────────────────────
    # co2e_kg_per_km: lifecycle CO2 equivalent per km (EF1)
    # pm25_kg_per_km, pm10_kg_per_km: tailpipe PM (EF5)
    # no2_g_per_km: nitrogen dioxide (EF5)
    # in_cabin_penetration: fraction of ambient PM2.5 inhaled (1.0 = fully open)
    # avg_speed_kmh: representative city-cycle speed
    "commute": {
        "walk": {
            "co2e_kg_per_km": 0.0,
            "pm25_kg_per_km": 0.0,
            "pm10_kg_per_km": 0.0,
            "no2_g_per_km": 0.0,
            "in_cabin_penetration": 1.0,  # fully outdoor
            "avg_speed_kmh": 5,
            "source": "EF1",
        },
        "cycle": {
            "co2e_kg_per_km": 0.0,
            "pm25_kg_per_km": 0.0,
            "pm10_kg_per_km": 0.0,
            "no2_g_per_km": 0.0,
            "in_cabin_penetration": 1.0,
            "avg_speed_kmh": 15,
            "source": "EF1",
        },
        "two_wheeler_petrol": {
            "co2e_kg_per_km": 0.057,     # EF5: 57 g CO2e/km (100cc city)
            "pm25_kg_per_km": 2.1e-5,    # EF5: 21 mg/km
            "pm10_kg_per_km": 2.8e-5,
            "no2_g_per_km": 0.21,
            "in_cabin_penetration": 1.0,
            "avg_speed_kmh": 28,
            "source": "EF5",
        },
        "two_wheeler_electric": {
            "co2e_kg_per_km": 0.027,     # grid emissions India average 2023
            "pm25_kg_per_km": 0.0,
            "pm10_kg_per_km": 0.0,
            "no2_g_per_km": 0.0,
            "in_cabin_penetration": 1.0,
            "avg_speed_kmh": 30,
            "source": "EF1",
        },
        "car_petrol": {
            "co2e_kg_per_km": 0.170,     # EF1: 170 g/km petrol compact
            "pm25_kg_per_km": 2.4e-5,
            "pm10_kg_per_km": 3.0e-5,
            "no2_g_per_km": 0.35,
            "in_cabin_penetration": 0.50, # enclosed cabin
            "avg_speed_kmh": 25,
            "source": "EF1,EF5",
        },
        "car_diesel": {
            "co2e_kg_per_km": 0.155,
            "pm25_kg_per_km": 6.0e-5,    # diesel PM significantly higher
            "pm10_kg_per_km": 8.0e-5,
            "no2_g_per_km": 0.65,
            "in_cabin_penetration": 0.50,
            "avg_speed_kmh": 25,
            "source": "EF1,EF5",
        },
        "car_cng": {
            "co2e_kg_per_km": 0.142,
            "pm25_kg_per_km": 1.0e-5,
            "pm10_kg_per_km": 1.2e-5,
            "no2_g_per_km": 0.28,
            "in_cabin_penetration": 0.50,
            "avg_speed_kmh": 25,
            "source": "EF5",
        },
        "bus": {
            "co2e_kg_per_km": 0.027,     # per-passenger occupancy 40
            "pm25_kg_per_km": 1.5e-6,
            "pm10_kg_per_km": 2.0e-6,
            "no2_g_per_km": 0.015,
            "in_cabin_penetration": 0.75,
            "avg_speed_kmh": 20,
            "source": "EF1,EF5",
        },
        "metro": {
            "co2e_kg_per_km": 0.014,     # electric, grid mix India
            "pm25_kg_per_km": 0.0,
            "pm10_kg_per_km": 0.0,
            "no2_g_per_km": 0.0,
            "in_cabin_penetration": 0.40,
            "avg_speed_kmh": 35,
            "source": "EF1",
        },
        "auto": {
            "co2e_kg_per_km": 0.085,     # CNG auto-rickshaw India
            "pm25_kg_per_km": 1.5e-5,
            "pm10_kg_per_km": 2.0e-5,
            "no2_g_per_km": 0.22,
            "in_cabin_penetration": 0.90,
            "avg_speed_kmh": 22,
            "source": "EF5",
        },
        "wfh": {
            "co2e_kg_per_km": 0.0,
            "pm25_kg_per_km": 0.0,
            "pm10_kg_per_km": 0.0,
            "no2_g_per_km": 0.0,
            "in_cabin_penetration": 0.0,
            "avg_speed_kmh": 1,
            "source": "N/A",
        },
    },

    # ─── Cooking (PM2.5 mg/min of cooking) ───────────────────────────────────
    # pm25_mg_per_min: PM2.5 emission rate (Chafe et al. 2015, Table S2)
    # co2e_kg_per_hour: greenhouse gas equivalent
    "cooking": {
        "biomass": {
            "pm25_mg_per_min": 7.2,       # EF4: unimproved biomass cookstove
            "co2e_kg_per_hour": 1.6,
            "source": "EF4",
        },
        "kerosene": {
            "pm25_mg_per_min": 2.0,
            "co2e_kg_per_hour": 0.9,
            "source": "EF4",
        },
        "lpg": {
            "pm25_mg_per_min": 0.14,      # EF6
            "co2e_kg_per_hour": 0.44,
            "source": "EF6",
        },
        "piped_gas": {
            "pm25_mg_per_min": 0.10,
            "co2e_kg_per_hour": 0.40,
            "source": "EF6",
        },
        "induction": {
            "pm25_mg_per_min": 0.0,
            "co2e_kg_per_hour": 0.30,     # India grid electricity
            "source": "EF6",
        },
        "electric": {
            "pm25_mg_per_min": 0.0,
            "co2e_kg_per_hour": 0.30,
            "source": "EF6",
        },
    },
}


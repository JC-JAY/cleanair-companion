"""Daily Plan LLM prompt template with strict JSON output schema.

The LLM MUST NOT invent numbers. It receives pre-computed impact_data
and may only write explanatory text referencing those values.
"""
from __future__ import annotations

from datetime import date

from app.schemas.aqi import AQIResponse
from app.schemas.profile import UserProfileSchema
from app.services.rag.retriever import RetrievedPassage


DAILY_PLAN_SCHEMA = {
    "type": "object",
    "required": [
        "summary", "aqi_level_advice", "time_windows",
        "recommendations", "disclaimer"
    ],
    "properties": {
        "summary": {
            "type": "string",
            "description": "2-3 sentence plain-language summary of today's air quality situation and top action."
        },
        "aqi_level_advice": {
            "type": "object",
            "required": ["category", "general_advice", "vulnerable_advice"],
            "properties": {
                "category": {"type": "string"},
                "general_advice": {"type": "string"},
                "vulnerable_advice": {"type": "string",
                    "description": "Specific advice for children, elderly, or respiratory patients if present."}
            }
        },
        "time_windows": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["label", "start_hour", "end_hour", "quality", "activities", "reasoning"],
                "properties": {
                    "label": {"type": "string", "description": "e.g. 'Best window for outdoor activity'"},
                    "start_hour": {"type": "integer", "minimum": 0, "maximum": 23},
                    "end_hour": {"type": "integer", "minimum": 0, "maximum": 23},
                    "quality": {"type": "string", "enum": ["best", "good", "avoid"]},
                    "activities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "e.g. ['school drop', 'exercise', 'commute']"
                    },
                    "reasoning": {"type": "string"}
                }
            }
        },
        "recommendations": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["category", "title", "description", "impact_key",
                             "cost_level", "effort_level", "priority"],
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["commute", "cooking", "indoor_air", "outdoor_timing",
                                 "purifier", "sustainable_alt", "community"]
                    },
                    "title": {"type": "string"},
                    "description": {"type": "string",
                        "description": "Plain language. Refer to computed impact values using placeholders like {commute.co2e_avoided_kg:.2f} — do NOT invent numbers."},
                    "impact_key": {"type": "string",
                        "description": "Key into computed_impacts: commute | cooking | purifier | null"},
                    "impact_explanation": {"type": "string",
                        "description": "Human-friendly explanation of the impact. Must reference impact_key values only."},
                    "cost_level": {"type": "string", "enum": ["free", "low", "medium", "high"]},
                    "effort_level": {"type": "string", "enum": ["easy", "moderate", "hard"]},
                    "priority": {"type": "integer", "minimum": 1, "maximum": 10},
                    "sources": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "indoor_air_hacks": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["title", "description", "cost_level", "effort_level"],
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "cost_level": {"type": "string", "enum": ["free", "low", "medium", "high"]},
                    "effort_level": {"type": "string", "enum": ["easy", "moderate", "hard"]},
                    "source": {"type": "string"}
                }
            }
        },
        "disclaimer": {
            "type": "string",
            "description": "MUST include non-medical-advice disclaimer."
        }
    }
}


_SYSTEM_PROMPT = """You are CleanAir Companion's daily plan assistant for Maharashtra, India.

CRITICAL SAFETY RULES (NEVER violate these):
1. You MUST NOT invent, estimate, or extrapolate any numeric values for PM2.5, CO2e, 
   emissions, or health statistics. ALL numbers come from the computed_impacts dict 
   provided to you. Reference them by exact key path.
2. Always include a disclaimer that this is not medical advice.
3. For users with children, elderly, pregnancy, or respiratory conditions — apply extra 
   caution and use 'vulnerable_advice' fields.
4. If AQI > 300 (Very Poor), ALWAYS advise staying indoors as the first recommendation.
5. Only cite sources from the retrieved knowledge passages. Do not invent citations.
6. Write in simple, accessible language (Grade 8 reading level).
7. Respond in the language requested: {language}"""


def build_daily_plan_prompt(
    profile: UserProfileSchema,
    aqi: AQIResponse,
    impact_data: dict,
    passages: list[RetrievedPassage],
    plan_date: date,
    language: str = "en",
) -> dict:
    """Build the system + user message dict for the daily plan LLM call."""

    # Format knowledge base passages with sanitized text
    passages_text = "\n\n".join(
        f"[Source: {p.source_title}]\n{p.text}"
        for p in passages
    )

    vulnerable_flags = []
    if profile.has_children: vulnerable_flags.append("children")
    if profile.has_elderly: vulnerable_flags.append("elderly")
    if profile.has_asthma_respiratory: vulnerable_flags.append("asthma/respiratory")
    if profile.has_pregnancy: vulnerable_flags.append("pregnancy")

    user_msg = f"""Generate today's personalised clean-air plan for {plan_date}.

USER PROFILE:
- Location: {profile.city}, {profile.state}
- Household: {profile.household_size} people | Vulnerable: {', '.join(vulnerable_flags) or 'none'}
- Home: {profile.home_type} | Cooking: {profile.cooking_fuel} | Kitchen exhaust: {profile.has_kitchen_exhaust}
- Commute: {profile.commute_mode} | {profile.commute_distance_km} km each way
- Budget: {profile.budget_level} | Devices: {profile.available_devices}

CURRENT AIR QUALITY (DO NOT MODIFY THESE VALUES):
- AQI: {aqi.aqi} ({aqi.aqi_category})
- PM2.5: {aqi.pm25} µg/m³ | PM10: {aqi.pm10} µg/m³ | NO2: {aqi.no2} µg/m³
- Temperature: {aqi.temperature_c}°C | Humidity: {aqi.humidity_pct}% | Wind: {aqi.wind_speed_ms} m/s
- Temperature inversion: {aqi.temperature_inversion}
- Data source: {aqi.source} | Observed at: {aqi.observed_at}

PRE-COMPUTED IMPACT DATA (reference these exact values, never invent alternatives):
{impact_data}

KNOWLEDGE BASE PASSAGES (cite sources from these only):
{passages_text}

INSTRUCTIONS:
- Use the emit_daily_plan tool to return a structured plan
- For impact_explanation fields: explain the computed numbers in plain language
- Rank time_windows based on typical Maharashtra winter AQI patterns (worst: 7-10am, best: 1-4pm)
- Rank recommendations by priority: vulnerable household members first
- Indoor air hacks: rank by cost (free first) then effort
- Language: {language}"""

    return {
        "system": _SYSTEM_PROMPT.format(language=language),
        "user": user_msg,
    }


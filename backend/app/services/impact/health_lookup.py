"""Health lookup — deterministic plain-language health meanings.

Based on WHO AQG 2021 dose-response functions and CPCB AQI health categories.
The LLM is never used here; these are lookup-table results.

Source: WHO Global Air Quality Guidelines 2021, Chapter 3 (PM2.5)
        CPCB AQI Health Categories (2014, updated 2021)
"""
from __future__ import annotations


# WHO AQG 2021 — approximate excess risk per µg/m³·h PM2.5 exposure
# These thresholds drive the plain-language tiers below.
# Reference: WHO AQG 2021 Section 3.3 Short-term exposure
_TIERS = [
    # (max_ug_m3_h_per_person, tier_key)
    (1.0,   "negligible"),
    (5.0,   "low"),
    (15.0,  "moderate"),
    (40.0,  "high"),
    (float("inf"), "very_high"),
]

_HEALTH_TEXTS = {
    # tier_key → {has_vulnerable: text, default: text}
    "negligible": {
        "default": "Very little additional exposure saved — air is relatively clean for this activity.",
        "vulnerable": "Some benefit for sensitive household members, though air quality is acceptable.",
    },
    "low": {
        "default": "Modest reduction in PM2.5 inhalation — roughly equivalent to breathing clean air 1–2 hours longer.",
        "vulnerable": "Meaningful protection for children or elderly: reduces coughing and respiratory irritation risk.",
    },
    "moderate": {
        "default": "Noticeable reduction in PM2.5 exposure — lowers risk of short-term respiratory symptoms.",
        "vulnerable": "Important for children and elderly: significantly reduces coughing, wheezing, and eye irritation risk today.",
    },
    "high": {
        "default": "Substantial exposure reduction — reduces risk of chest tightness, fatigue, and reduced lung function.",
        "vulnerable": "Critical for sensitive household members: protects against serious respiratory symptoms and asthma triggers.",
    },
    "very_high": {
        "default": "Very large exposure reduction — protects lung function and reduces cardiovascular stress.",
        "vulnerable": "Strongly protective for children, elderly, and those with asthma: avoids serious health risk today.",
    },
}

_VULNERABLE_AGES = {"child", "elderly"}


class HealthLookup:
    """Map computed PM2.5 exposure (µg/m³·h) to plain-language health text."""

    def exposure_meaning(
        self,
        pm25_exposure_ug_m3_h: float,
        profile_ages: list[str],
    ) -> str:
        """
        Return a plain-language health meaning for a given PM2.5 exposure
        reduction value and household age composition.

        Args:
            pm25_exposure_ug_m3_h: per-person PM2.5 exposure reduction in µg/m³·h
            profile_ages: list from ["child", "adult", "elderly"]

        Returns:
            Plain English sentence (non-medical, non-diagnostic).
        """
        tier_key = "negligible"
        for max_val, key in _TIERS:
            if pm25_exposure_ug_m3_h <= max_val:
                tier_key = key
                break

        has_vulnerable = bool(set(profile_ages) & _VULNERABLE_AGES)
        texts = _HEALTH_TEXTS[tier_key]

        base = texts["vulnerable"] if has_vulnerable else texts["default"]
        disclaimer = " (This is a general health guide, not medical advice.)"
        return base + disclaimer

    def aqi_category_text(self, aqi: int) -> dict:
        """Return CPCB AQI category metadata for a given AQI value."""
        ranges = [
            (50,  "Good",        "green",   "#55a84f", "Minimal impact."),
            (100, "Satisfactory","lgreen",  "#a3c853", "Minor breathing discomfort for sensitive people."),
            (200, "Moderate",    "yellow",  "#fff833", "May cause breathing discomfort with prolonged exposure."),
            (300, "Poor",        "orange",  "#f29c33", "Breathing discomfort for most. Avoid prolonged outdoor activity."),
            (400, "Very Poor",   "red",     "#e93f33", "Respiratory illness possible on prolonged exposure."),
            (500, "Severe",      "darkred", "#af2d24", "Affects healthy people. Serious impact on those with disease."),
        ]
        for threshold, category, color_name, hex_color, advice in ranges:
            if aqi <= threshold:
                return {
                    "category": category,
                    "color_name": color_name,
                    "hex_color": hex_color,
                    "advice": advice,
                    "source": "CPCB AQI Health Categories 2021",
                }
        return {
            "category": "Severe",
            "color_name": "darkred",
            "hex_color": "#af2d24",
            "advice": "Emergency health conditions. Stay indoors.",
            "source": "CPCB AQI Health Categories 2021",
        }


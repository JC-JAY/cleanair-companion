"""Geo utilities — coordinate rounding and validation."""
from __future__ import annotations

from typing import Optional


def round_coordinates(
    lat: Optional[float],
    lon: Optional[float],
    decimal_places: int = 2,
) -> tuple[Optional[float], Optional[float]]:
    """
    Round lat/lon to `decimal_places` for privacy (default ±1 km at 2dp).
    Returns None for None inputs.
    """
    r_lat = round(lat, decimal_places) if lat is not None else None
    r_lon = round(lon, decimal_places) if lon is not None else None
    return r_lat, r_lon


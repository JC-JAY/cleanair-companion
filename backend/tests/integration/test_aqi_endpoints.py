"""Integration tests for the AQI endpoint (uses TestClient with mock external APIs)."""
from __future__ import annotations

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.schemas.aqi import AQIResponse, AQISource
from datetime import datetime, timezone


@pytest.fixture
def mock_aqi_response():
    return AQIResponse(
        lat=18.52,
        lon=73.85,
        source=AQISource.OPENAQ,
        observed_at=datetime.now(timezone.utc),
        aqi=185,
        aqi_category="Moderate",
        pm25=65.0,
        pm10=90.0,
        no2=42.0,
        temperature_c=16.5,
        humidity_pct=72.0,
        wind_speed_ms=1.2,
        from_cache=False,
    )


@pytest.mark.asyncio
async def test_aqi_endpoint_returns_data(mock_aqi_response):
    with patch("app.services.aqi.service.AQIService.get_aqi", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_aqi_response
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/aqi/?lat=18.52&lon=73.85")
    assert response.status_code == 200
    data = response.json()
    assert data["aqi"] == 185
    assert data["pm25"] == 65.0
    assert data["aqi_category"] == "Moderate"


@pytest.mark.asyncio
async def test_aqi_endpoint_validates_latitude():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/aqi/?lat=200&lon=73.85")
    assert response.status_code == 422  # validation error


@pytest.mark.asyncio
async def test_aqi_category_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/aqi/category?aqi=250")
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "Poor"
    assert "hex_color" in data


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_impact_commute_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/impact/commute", json={
            "from_mode": "car_petrol",
            "to_mode": "metro",
            "distance_km": 10,
            "ambient_pm25": 120,
            "profile_ages": ["adult", "child"]
        })
    assert response.status_code == 200
    data = response.json()
    assert "co2e_avoided_kg" in data
    assert "health_meaning" in data
    assert "sources" in data
    assert data["co2e_avoided_kg"] > 0  # car_petrol → metro always saves CO2


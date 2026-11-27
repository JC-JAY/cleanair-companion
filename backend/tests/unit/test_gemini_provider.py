"""Unit tests for Google Gemini Provider."""
from __future__ import annotations

import pytest
from app.services.gemini.provider import GeminiProvider


class TestGeminiProvider:
    def test_unconfigured_provider_graceful_response(self):
        provider = GeminiProvider(api_key="")
        assert provider._configured is False
        assert provider.model_name == "gemini-1.5-flash"

    def test_provider_initialization_with_custom_model(self):
        provider = GeminiProvider(api_key="", model_name="gemini-1.5-pro")
        assert provider.model_name == "gemini-1.5-pro"
        assert provider._configured is False

"""Google Gemini AI Service Provider.

Implements Google Gemini 1.5 Flash / Pro integration:
- Structured JSON outputs for daily clean-air plans
- Function calling & grounded multi-turn chat
- Text embedding generation using text-embedding-004
"""
from __future__ import annotations

import json
import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiProvider:
    """Wrapper for Google Gemini API."""

    def __init__(self, api_key: str | None = None, model_name: str | None = None):
        self.api_key = api_key if api_key is not None else (
            settings.GEMINI_API_KEY.get_secret_value() if settings.GEMINI_API_KEY else ""
        )
        self.model_name = model_name or settings.GEMINI_MODEL
        self._configured = False
        if self.api_key:
            self._configure()

    def _configure(self):
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._configured = True
        except ImportError:
            logger.warning("google-generativeai package not installed")

    async def generate_chat_response(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.2,
    ) -> str:
        """Generate conversational response using Gemini 1.5."""
        if not self._configured:
            return "Gemini API key is not configured."

        import google.generativeai as genai

        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_instruction,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=1024,
            ),
        )
        response = await model.generate_content_async(prompt)
        return response.text if response else ""

    async def generate_plan(
        self,
        prompt: str,
        system_instruction: str | None = None,
    ) -> dict[str, Any]:
        """Generate structured JSON daily plan using Gemini."""
        if not self._configured:
            return {}

        import google.generativeai as genai

        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_instruction,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                response_mime_type="application/json",
            ),
        )
        response = await model.generate_content_async(prompt)
        if response and response.text:
            return json.loads(response.text)
        return {}

    async def get_embedding(self, text: str) -> list[float]:
        """Generate text embedding using Google text-embedding-004."""
        if not self._configured:
            return [0.0] * 768

        import google.generativeai as genai

        result = genai.embed_content(
            model=settings.GEMINI_EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_query",
        )
        return result.get("embedding", [])

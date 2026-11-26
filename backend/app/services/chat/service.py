"""Chat service — conversational Q&A with RAG grounding and citation.

SAFETY:
  - Refuses to answer if no relevant passage found (not_grounded flag)
  - Never generates health statistics; always defers to impact module
  - Medical escalation for severe symptoms
  - Prompt injection protection on all user inputs
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import anthropic

from app.core.config import settings
from app.prompts.chat_assistant import build_chat_prompt
from app.schemas.chat import ChatMessage, ChatResponse
from app.services.rag.retriever import RAGRetriever, RetrievedPassage
from app.utils.sanitizer import sanitize_for_llm

logger = logging.getLogger(__name__)

SEVERE_SYMPTOM_KEYWORDS = {
    "can't breathe", "cannot breathe", "chest pain", "unconscious",
    "emergency", "hospital", "blue lips", "coughing blood",
}

MEDICAL_ESCALATION_RESPONSE = (
    "⚠️ Based on what you've described, please seek immediate medical attention "
    "or call emergency services. This app provides general air quality guidance "
    "only and cannot replace professional medical care. 🏥"
)


class ChatService:
    def __init__(self, rag: RAGRetriever, anthropic_client: anthropic.AsyncAnthropic):
        self._rag = rag
        self._llm = anthropic_client

    async def respond(
        self,
        messages: list[ChatMessage],
        user_query: str,
        language: str = "en",
    ) -> ChatResponse:
        # 1. Safety check — severe symptoms
        lower_query = user_query.lower()
        if any(kw in lower_query for kw in SEVERE_SYMPTOM_KEYWORDS):
            return ChatResponse(
                reply=MEDICAL_ESCALATION_RESPONSE,
                citations=[],
                is_grounded=True,
                not_grounded=False,
                is_medical_escalation=True,
            )

        # 2. Sanitize input
        clean_query = sanitize_for_llm(user_query)

        # 3. RAG retrieval
        passages = await self._rag.retrieve(clean_query, top_k=settings.RAG_TOP_K)
        is_grounded = len(passages) > 0 and passages[0].similarity >= 0.72

        if not is_grounded:
            return ChatResponse(
                reply=(
                    "I don't have specific information in my knowledge base to answer that. "
                    "Please consult official sources like the CPCB website (cpcb.nic.in) "
                    "or WHO guidelines for authoritative guidance."
                ),
                citations=[],
                is_grounded=False,
                not_grounded=True,
                is_medical_escalation=False,
            )

        # 4. Build prompt and call LLM
        prompt = build_chat_prompt(messages, clean_query, passages, language)

        llm_response = await self._llm.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=1024,
            temperature=0.2,
            system=prompt["system"],
            messages=prompt["messages"],
        )

        reply_text = llm_response.content[0].text if llm_response.content else ""

        # 5. Build citations
        citations = [
            {"title": p.source_title, "url": p.source_url, "type": p.source_type}
            for p in passages[:3]
        ]

        return ChatResponse(
            reply=reply_text,
            citations=citations,
            is_grounded=True,
            not_grounded=False,
            is_medical_escalation=False,
        )


"""Chat assistant prompt — grounded in RAG passages, with refusal logic."""
from __future__ import annotations

from app.schemas.chat import ChatMessage
from app.services.rag.retriever import RetrievedPassage


_SYSTEM_PROMPT = """You are CleanAir Companion's conversational assistant.

RULES (never violate):
1. Only answer questions using the KNOWLEDGE BASE PASSAGES provided. If the answer 
   is not in the passages, say clearly that you don't have that information and 
   direct the user to official sources (CPCB, WHO, state health dept).
2. NEVER invent statistics, PM2.5 values, AQI thresholds, or health claims not 
   present in the passages.
3. Always cite your source (passage title) at the end of your answer.
4. For any symptom descriptions, add: "This is general information only — 
   please consult a doctor for personal health advice."
5. Keep answers short, clear, and accessible (Grade 8 reading level).
6. If asked about something outside air quality, indoor air, commute, or health 
   related to pollution — politely decline and redirect.
7. Respond in the requested language: {language}

ABOUT THE APP:
CleanAir Companion helps families in Maharashtra (and across India) navigate 
winter smog with personalised, evidence-based guidance on indoor air quality, 
commute choices, and low-emission routines."""


def build_chat_prompt(
    history: list[ChatMessage],
    user_query: str,
    passages: list[RetrievedPassage],
    language: str = "en",
) -> dict:
    """Build the messages list for the chat LLM call."""

    passages_text = "\n\n".join(
        f"[{i+1}] SOURCE: {p.source_title} (similarity: {p.similarity:.2f})\n{p.text}"
        for i, p in enumerate(passages)
    )

    # Inject knowledge base into the system context
    system = _SYSTEM_PROMPT.format(language=language)
    system += f"\n\nKNOWLEDGE BASE (use ONLY these sources):\n{passages_text}"

    # Build conversation history
    messages = []
    for msg in history[-10:]:  # last 10 turns to keep context manageable
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": user_query})

    return {"system": system, "messages": messages}


"""Pydantic v2 schemas for chat."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(max_length=2000, description="User's question")
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)
    language: str = Field(default="en", pattern=r"^(en|hi|mr)$")


class CitationSchema(BaseModel):
    title: str
    url: Optional[str] = None
    type: str


class ChatResponse(BaseModel):
    reply: str
    citations: list[CitationSchema | dict]
    is_grounded: bool
    not_grounded: bool
    is_medical_escalation: bool


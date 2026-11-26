"""Chat endpoint."""
from __future__ import annotations

import anthropic
from fastapi import APIRouter, Depends
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_current_user_optional
from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat.service import ChatService
from app.services.rag.retriever import RAGRetriever

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_optional),
):
    """
    Conversational Q&A grounded in the curated knowledge base.
    - Refuses if no relevant passage found
    - Escalates severe symptoms to medical advice
    - Always cites sources
    """
    openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())
    anthropic_client = anthropic.AsyncAnthropic(
        api_key=settings.ANTHROPIC_API_KEY.get_secret_value()
    )
    rag = RAGRetriever(db_session=db, openai_client=openai_client)
    svc = ChatService(rag=rag, anthropic_client=anthropic_client)

    return await svc.respond(
        messages=request.history,
        user_query=request.message,
        language=request.language,
    )


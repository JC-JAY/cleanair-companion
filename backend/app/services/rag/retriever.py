"""RAG Retriever — pgvector cosine similarity search for grounded context."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from openai import AsyncOpenAI
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.knowledge_chunk import KnowledgeChunk

logger = logging.getLogger(__name__)


@dataclass
class RetrievedPassage:
    text: str
    source_title: str
    source_url: str | None
    source_type: str
    similarity: float


class RAGRetriever:
    def __init__(self, db_session: AsyncSession, openai_client: AsyncOpenAI):
        self._db = db_session
        self._openai = openai_client

    async def retrieve(
        self,
        query: str,
        top_k: int = 8,
        source_type_filter: list[str] | None = None,
    ) -> list[RetrievedPassage]:
        """
        Embed query and retrieve top-k chunks by cosine similarity using pgvector.

        Args:
            query: User query or context string (must be pre-sanitized)
            top_k: Number of passages to return
            source_type_filter: Optional list of source types to restrict to

        Returns:
            List of RetrievedPassage ordered by similarity descending
        """
        # 1. Embed the query
        embedding_resp = await self._openai.embeddings.create(
            input=query,
            model=settings.EMBEDDING_MODEL,
            dimensions=settings.EMBEDDING_DIMENSIONS,
        )
        query_vec = embedding_resp.data[0].embedding

        # 2. pgvector cosine similarity search
        vec_literal = "[" + ",".join(str(v) for v in query_vec) + "]"

        filters = ""
        if source_type_filter:
            types_sql = ",".join(f"'{t}'" for t in source_type_filter)
            filters = f"AND source_type IN ({types_sql})"

        sql = text(f"""
            SELECT
                id, text, source_title, source_url, source_type,
                1 - (embedding <=> :vec::vector) AS similarity
            FROM knowledge_chunks
            WHERE 1=1 {filters}
            ORDER BY embedding <=> :vec::vector
            LIMIT :top_k
        """)

        result = await self._db.execute(sql, {"vec": vec_literal, "top_k": top_k})
        rows = result.mappings().all()

        passages = [
            RetrievedPassage(
                text=row["text"],
                source_title=row["source_title"],
                source_url=row["source_url"],
                source_type=row["source_type"],
                similarity=float(row["similarity"]),
            )
            for row in rows
        ]
        logger.info("RAG retrieved %d passages for query (top sim=%.3f)",
                    len(passages), passages[0].similarity if passages else 0.0)
        return passages


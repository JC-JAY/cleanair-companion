"""Knowledge base chunk — stores embedded text for RAG retrieval."""
from __future__ import annotations

from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.db.base import Base, TimestampMixin, UUIDPKMixin


class KnowledgeChunk(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_chunks"

    # Source document
    source_title: Mapped[str] = mapped_column(String(256), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    # who_guidelines | cpcb | ashrae | research | health_advisory | local
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    # Topic tags for pre-filter: pm25, pm10, indoor, cooking, commute, children…
    tags: Mapped[list[str]] = mapped_column(JSONB, default=list)

    # Content
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Vector embedding
    embedding: Mapped[list[float]] = mapped_column(
        Vector(settings.EMBEDDING_DIMENSIONS), nullable=False
    )

    __table_args__ = (
        Index(
            "ix_knowledge_chunks_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


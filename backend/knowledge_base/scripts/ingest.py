"""Knowledge base ingestion pipeline.

Processes raw documents (PDF, Markdown, plain text), chunks them, 
generates embeddings via OpenAI, and upserts into pgvector.

Usage:
    python -m knowledge_base.scripts.ingest \
        --source-dir knowledge_base/raw \
        --source-type who_guidelines \
        --dry-run

Sources to ingest:
  - WHO Global Air Quality Guidelines 2021
  - CPCB AQI Health Categories
  - ASHRAE 62.1 ventilation guidance (excerpts)
  - Mask selection guide (N95 / P100)
  - Air purifier CADR guidance (EPA)
  - Indoor plant PM2.5 research (Wolverton 1989 — caveated)
  - Open burning advisories (CPCB Maharashtra)
  - Inversion meteorology explainer (IMD)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
from pathlib import Path

import tiktoken
from openai import AsyncOpenAI
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CHUNK_SIZE_TOKENS = 400
CHUNK_OVERLAP_TOKENS = 50
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536

_enc = tiktoken.encoding_for_model("gpt-3.5-turbo")


def tokenize(text: str) -> list[int]:
    return _enc.encode(text)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE_TOKENS, overlap: int = CHUNK_OVERLAP_TOKENS) -> list[str]:
    """Split text into overlapping token chunks."""
    tokens = tokenize(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunks.append(_enc.decode(chunk_tokens))
        if end == len(tokens):
            break
        start += chunk_size - overlap
    return chunks


async def embed_batch(client: AsyncOpenAI, texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts (max 100 per request)."""
    response = await client.embeddings.create(
        input=texts,
        model=EMBEDDING_MODEL,
        dimensions=EMBEDDING_DIMENSIONS,
    )
    return [item.embedding for item in sorted(response.data, key=lambda x: x.index)]


def load_document(path: Path) -> str:
    """Load text from PDF or text file."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        try:
            import pdfminer.high_level as pdfminer
            return pdfminer.extract_text(str(path))
        except ImportError:
            logger.warning("pdfminer not installed; treating %s as plain text", path)
    return path.read_text(encoding="utf-8", errors="replace")


async def ingest_document(
    db: AsyncSession,
    openai_client: AsyncOpenAI,
    source_path: Path,
    metadata: dict,
    dry_run: bool = False,
) -> int:
    """Chunk, embed, and upsert a single document. Returns chunk count."""
    text = load_document(source_path)
    chunks = chunk_text(text)
    logger.info("Document %s → %d chunks", source_path.name, len(chunks))

    if dry_run:
        for i, chunk in enumerate(chunks[:3]):
            logger.info("  Chunk %d (preview): %s…", i, chunk[:80])
        return len(chunks)

    # Remove existing chunks for this source
    from app.models.knowledge_chunk import KnowledgeChunk  # noqa: PLC0415
    await db.execute(
        delete(KnowledgeChunk).where(KnowledgeChunk.source_title == metadata["source_title"])
    )

    # Embed in batches of 50
    batch_size = 50
    inserted = 0
    for batch_start in range(0, len(chunks), batch_size):
        batch = chunks[batch_start : batch_start + batch_size]
        embeddings = await embed_batch(openai_client, batch)

        for idx, (chunk_text_item, embedding) in enumerate(zip(batch, embeddings)):
            chunk = KnowledgeChunk(
                source_title=metadata["source_title"],
                source_url=metadata.get("source_url"),
                source_type=metadata["source_type"],
                tags=metadata.get("tags", []),
                chunk_index=batch_start + idx,
                text=chunk_text_item,
                token_count=len(tokenize(chunk_text_item)),
                embedding=embedding,
            )
            db.add(chunk)
            inserted += 1

        await db.commit()
        logger.info("  Committed batch %d–%d", batch_start, batch_start + len(batch) - 1)

    return inserted


# ── Manifest of documents to ingest ──────────────────────────────────────────
KNOWLEDGE_BASE_MANIFEST = [
    {
        "filename": "who_aqg_2021_summary.md",
        "source_title": "WHO Global Air Quality Guidelines 2021",
        "source_url": "https://www.who.int/publications/i/item/9789240034228",
        "source_type": "who_guidelines",
        "tags": ["pm25", "pm10", "no2", "o3", "health", "guideline"],
    },
    {
        "filename": "cpcb_aqi_categories.md",
        "source_title": "CPCB AQI Health Categories",
        "source_url": "https://cpcb.nic.in/air-quality-index/",
        "source_type": "cpcb",
        "tags": ["aqi", "health", "india", "cpcb"],
    },
    {
        "filename": "mask_selection_guide.md",
        "source_title": "N95 and P100 Mask Selection Guide",
        "source_url": "https://www.cdc.gov/niosh/topics/air/pdf/filtering_facepiece.pdf",
        "source_type": "health_advisory",
        "tags": ["mask", "n95", "pm25", "protection"],
    },
    {
        "filename": "indoor_air_quality_guide.md",
        "source_title": "Indoor Air Quality: WHO Household Guidelines",
        "source_url": "https://www.who.int/publications/i/item/9789241598759",
        "source_type": "who_guidelines",
        "tags": ["indoor", "cooking", "ventilation", "pm25"],
    },
    {
        "filename": "air_purifier_cadr_guide.md",
        "source_title": "EPA Guide to Air Cleaners in the Home",
        "source_url": "https://www.epa.gov/indoor-air-quality-iaq/guide-air-cleaners-home",
        "source_type": "health_advisory",
        "tags": ["purifier", "cadr", "hepa", "indoor", "pm25"],
    },
    {
        "filename": "maharashtra_smog_advisory.md",
        "source_title": "Maharashtra Winter Smog Advisory (CPCB / MPCB)",
        "source_url": "https://mpcb.gov.in/",
        "source_type": "local",
        "tags": ["maharashtra", "pune", "winter", "smog", "inversion"],
    },
    {
        "filename": "cooking_fuels_health.md",
        "source_title": "Household Cooking Fuels and Health — WHO Evidence Review",
        "source_url": "https://www.who.int/news-room/fact-sheets/detail/household-air-pollution-and-health",
        "source_type": "who_guidelines",
        "tags": ["cooking", "biomass", "lpg", "indoor", "pm25", "children"],
    },
    {
        "filename": "temperature_inversion_explainer.md",
        "source_title": "Temperature Inversion and Urban Air Pollution — IMD/IITM",
        "source_url": "https://www.imd.gov.in/",
        "source_type": "research",
        "tags": ["inversion", "smog", "maharashtra", "winter", "meteorology"],
    },
]


async def main(source_dir: str, dry_run: bool, source_filter: str | None):
    import os
    db_url = os.environ.get("DATABASE_URL", "postgresql+asyncpg://cleanair:cleanair@localhost:5432/cleanair")
    openai_key = os.environ.get("OPENAI_API_KEY", "")

    engine = create_async_engine(db_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    openai_client = AsyncOpenAI(api_key=openai_key)

    source_path = Path(source_dir)
    total = 0

    async with session_factory() as db:
        for doc_meta in KNOWLEDGE_BASE_MANIFEST:
            if source_filter and doc_meta["source_type"] != source_filter:
                continue
            doc_path = source_path / doc_meta["filename"]
            if not doc_path.exists():
                logger.warning("Missing file: %s — skipping", doc_path)
                continue
            count = await ingest_document(db, openai_client, doc_path, doc_meta, dry_run=dry_run)
            total += count
            logger.info("✓ %s → %d chunks", doc_meta["source_title"], count)

    logger.info("Ingestion complete. Total chunks: %d", total)
    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest knowledge base into pgvector")
    parser.add_argument("--source-dir", default="knowledge_base/raw")
    parser.add_argument("--source-type", default=None, help="Filter by source type")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    asyncio.run(main(args.source_dir, args.dry_run, args.source_type))


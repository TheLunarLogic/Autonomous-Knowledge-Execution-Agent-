"""
Knowledge ingestion — loads JSON and CSV files into PostgreSQL and ChromaDB.
"""

import csv
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.db.models import KnowledgeItem
from app.knowledge.vector_store import get_vector_store
from app.utils.helpers import content_hash


async def load_json(session: AsyncSession, file_path: str | Path) -> int:
    """Load a JSON file into knowledge_items table and ChromaDB.

    Returns the number of new items inserted.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        logger.error("JSON file not found: %s", file_path)
        return 0

    with open(file_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    inserted = 0
    documents = []
    metadatas = []
    ids = []

    for record in records:
        # Build a searchable text representation
        content = _json_record_to_text(record)
        c_hash = content_hash(content)

        # Check for duplicates in Postgres
        existing = await session.execute(
            select(KnowledgeItem.id).where(KnowledgeItem.content_hash == c_hash)
        )
        if existing.scalar_one_or_none():
            logger.debug("Skipping duplicate: %s", c_hash[:12])
            continue

        item = KnowledgeItem(
            source_type="json",
            content=content,
            content_hash=c_hash,
            metadata_=record,
        )
        session.add(item)
        inserted += 1

        # Prepare for ChromaDB batch insert
        documents.append(content)
        metadatas.append({"source": "json", "record_id": record.get("id", "")})
        ids.append(c_hash)

    await session.flush()

    # Push embeddings to ChromaDB
    if documents:
        vector_store = get_vector_store()
        vector_store.add_documents(documents=documents, metadatas=metadatas, ids=ids)
        logger.info("Pushed %d documents to ChromaDB from JSON", len(documents))

    logger.info("Loaded %d new records from %s", inserted, file_path.name)
    return inserted


async def load_csv(session: AsyncSession, file_path: str | Path) -> int:
    """Load a CSV file into knowledge_items table and ChromaDB.

    Returns the number of new items inserted.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        logger.error("CSV file not found: %s", file_path)
        return 0

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    inserted = 0
    documents = []
    metadatas = []
    ids = []

    for row in rows:
        content = _csv_row_to_text(row)
        c_hash = content_hash(content)

        existing = await session.execute(
            select(KnowledgeItem.id).where(KnowledgeItem.content_hash == c_hash)
        )
        if existing.scalar_one_or_none():
            logger.debug("Skipping duplicate: %s", c_hash[:12])
            continue

        item = KnowledgeItem(
            source_type="csv",
            content=content,
            content_hash=c_hash,
            metadata_=dict(row),
        )
        session.add(item)
        inserted += 1

        documents.append(content)
        metadatas.append({"source": "csv", "record_id": row.get("id", "")})
        ids.append(c_hash)

    await session.flush()

    if documents:
        vector_store = get_vector_store()
        vector_store.add_documents(documents=documents, metadatas=metadatas, ids=ids)
        logger.info("Pushed %d documents to ChromaDB from CSV", len(documents))

    logger.info("Loaded %d new records from %s", inserted, file_path.name)
    return inserted


def _json_record_to_text(record: dict) -> str:
    """Convert a JSON product record into a searchable text block."""
    parts = []
    if "name" in record:
        parts.append(f"Product: {record['name']}")
    if "category" in record:
        parts.append(f"Category: {record['category']}")
    if "description" in record:
        parts.append(f"Description: {record['description']}")
    if "price" in record:
        parts.append(f"Price: ${record['price']}")
    if "specs" in record:
        specs_str = ", ".join(f"{k}: {v}" for k, v in record["specs"].items())
        parts.append(f"Specs: {specs_str}")
    return "\n".join(parts)


def _csv_row_to_text(row: dict) -> str:
    """Convert a CSV employee row into a searchable text block."""
    parts = []
    if "name" in row:
        parts.append(f"Employee: {row['name']}")
    if "department" in row:
        parts.append(f"Department: {row['department']}")
    if "role" in row:
        parts.append(f"Role: {row['role']}")
    if "skills" in row:
        parts.append(f"Skills: {row['skills']}")
    if "location" in row:
        parts.append(f"Location: {row['location']}")
    if "status" in row:
        parts.append(f"Status: {row['status']}")
    return "\n".join(parts)
